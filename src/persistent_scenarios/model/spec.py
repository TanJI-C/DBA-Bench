"""Strict, serializable Persistent Scenario static contracts (protocol v2).

The v2 contract replaces the retired scenario/case pair events with
capability ID + occurrence payload, and defines service objectives that are
independent of Events. Unknown fields, wrong types, out-of-bounds times and
missing objectives fail directly; no defaults, no compatibility layer.

Service objectives are discriminated by ``load_class``
(OltpObjective / OlapObjective / HtapObjective); required state has four
kinds; safety policy and diagnosis contract are first-class spec
sections.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from math import ceil, isfinite
import re
from typing import Mapping

from .enums import (
    SETTING_SCOPES_BY_SYSTEM,
    SETTING_SCOPES_WITH_NAME,
    CalibrationStatus,
    EventTrigger,
    HtapMode,
    LoadClass,
    OlapMode,
    RequiredStateKind,
    SettingEffect,
    SettingScope,
)
from src.database.system import DatabaseSystem

PROTOCOL_VERSION = "persistent-scenario-v2"

JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]


def validate_json_value(name: str, value: object) -> None:
    """Reject anything that cannot cross the trace/ledger JSON boundary."""
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, float):
        if not isfinite(value):
            raise ValueError(f"{name} must be a finite number: value={value!r}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_json_value(f"{name}[{index}]", item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{name} mapping keys must be strings: key={key!r}")
            validate_json_value(f"{name}.{key}", item)
        return
    raise TypeError(f"{name} must be a JSON value: type={type(value).__name__}, value={value!r}")


def _text(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string: value={value!r}")


def _positive(name: str, value: int | float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise ValueError(f"{name} must be positive: value={value!r}")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} must be finite: value={value!r}")


def _non_negative(name: str, value: int | float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{name} must be non-negative: value={value!r}")
    if isinstance(value, float) and not isfinite(value):
        raise ValueError(f"{name} must be finite: value={value!r}")


def _fraction(name: str, value: float) -> None:
    if not 0 <= value <= 1 or not isfinite(value):
        raise ValueError(f"{name} must be in [0, 1]: value={value!r}")


def _json_mapping(name: str, value: Mapping[str, JSONValue]) -> None:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping: value={value!r}")
    validate_json_value(name, dict(value))


@dataclass(frozen=True, slots=True)
class PersistentScenarioResourceSpec:
    worker_physical_cores: int
    worker_memory_mb: int
    container_cpu_limit: float
    container_memory_mb: int

    def __post_init__(self) -> None:
        _positive("worker_physical_cores", self.worker_physical_cores)
        _positive("worker_memory_mb", self.worker_memory_mb)
        _positive("container_cpu_limit", self.container_cpu_limit)
        _positive("container_memory_mb", self.container_memory_mb)
        if self.worker_physical_cores < self.container_cpu_limit:
            raise ValueError(
                "PersistentScenario worker CPU reservation must cover the container limit: "
                f"worker_physical_cores={self.worker_physical_cores}, "
                f"container_cpu_limit={self.container_cpu_limit}"
            )
        if self.worker_memory_mb < self.container_memory_mb:
            raise ValueError(
                "PersistentScenario worker memory reservation must cover the container limit: "
                f"worker_memory_mb={self.worker_memory_mb}, "
                f"container_memory_mb={self.container_memory_mb}"
            )


@dataclass(frozen=True, slots=True)
class NodeVolume:
    """Node-scoped isolated volume (e.g. a bounded pg_wal quota volume)."""

    name: str
    mount_path: str

    def __post_init__(self) -> None:
        _text("volume name", self.name)
        _text("volume mount_path", self.mount_path)


@dataclass(frozen=True, slots=True)
class NodeSpec:
    """One explicitly-role database node. A deployment may contain several."""

    node_id: str
    role: str
    resources: PersistentScenarioResourceSpec
    docker_caps: tuple[str, ...] = ()
    volumes: tuple[NodeVolume, ...] = ()

    def __post_init__(self) -> None:
        _text("node.node_id", self.node_id)
        _text("node.role", self.role)
        if any(not isinstance(cap, str) or not cap.strip() for cap in self.docker_caps):
            raise ValueError(f"node docker_caps must be non-empty strings: node_id={self.node_id!r}")
        if len(set(self.docker_caps)) != len(self.docker_caps):
            raise ValueError(f"node docker_caps must be unique: node_id={self.node_id!r}")
        volume_names = [volume.name for volume in self.volumes]
        if len(volume_names) != len(set(volume_names)):
            raise ValueError(f"node volume names must be unique: node_id={self.node_id!r}, names={volume_names!r}")
        mount_paths = [volume.mount_path for volume in self.volumes]
        if len(set(mount_paths)) != len(mount_paths):
            raise ValueError(f"node volume mount paths must be unique: node_id={self.node_id!r}")


@dataclass(frozen=True, slots=True)
class PersistentScenarioEnvironmentSpec:
    workload: str
    scale: int
    base_image: str
    nodes: tuple[NodeSpec, ...]

    def __post_init__(self) -> None:
        _text("environment.workload", self.workload)
        _positive("environment.scale", self.scale)
        _text("environment.base_image", self.base_image)
        if not self.nodes:
            raise ValueError("environment.nodes must contain at least one node")
        node_ids = [node.node_id for node in self.nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError(f"environment node IDs must be unique: node_ids={node_ids!r}")


@dataclass(frozen=True, slots=True)
class CalibrationSpec:
    status: CalibrationStatus
    evidence_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.status, CalibrationStatus):
            raise TypeError(f"calibration.status must be CalibrationStatus: value={self.status!r}")
        _text("calibration.evidence_id", self.evidence_id)


# ---------------------------------------------------------------------------
# Service objectives (independent of Events), load_class discriminated
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class OltpObjective:
    """OLTP service: independently externally planned logical transactions.

    Denominator = distinct externally planned business IDs. Retries merge into
    the same business ID and never widen the denominator; queueing counts into
    end-to-end latency (each transaction's deadline runs from first
    submission). Outstanding work at the scoring end is loss.
    """

    objective_id: str
    service_id: str
    deadline_seconds: float
    min_success_fraction: float
    outage_contract_seconds: float | None = None
    outage_source: str | None = None
    load_class: LoadClass = LoadClass.OLTP

    def __post_init__(self) -> None:
        if self.load_class is not LoadClass.OLTP:
            raise TypeError(f"OltpObjective load_class must be OLTP: objective_id={self.objective_id!r}, value={self.load_class!r}")
        _text("objective_id", self.objective_id)
        _text("service_id", self.service_id)
        _positive("deadline_seconds", self.deadline_seconds)
        _fraction("min_success_fraction", self.min_success_fraction)
        if (self.outage_contract_seconds is None) != (self.outage_source is None):
            raise ValueError(
                "outage_contract_seconds and outage_source must be present or absent together: "
                f"objective_id={self.objective_id!r}, outage_contract_seconds={self.outage_contract_seconds!r}, "
                f"outage_source={self.outage_source!r}"
            )
        if self.outage_contract_seconds is not None:
            _positive("outage_contract_seconds", self.outage_contract_seconds)
            _text("outage_source", self.outage_source)


@dataclass(frozen=True, slots=True)
class DeliverableContract:
    """One delivery obligation of an OLAP checklist.

    ``deadline_seconds`` runs from the job's submission (queueing and retries
    included); input binding freezes the batch the result must be computed on.
    """

    deliverable_id: str
    deadline_seconds: float
    requires_freshness: bool
    max_freshness_lag_seconds: float | None = None
    input_batch_binding: str | None = None

    def __post_init__(self) -> None:
        _text("deliverable_id", self.deliverable_id)
        _positive("deadline_seconds", self.deadline_seconds)
        if not isinstance(self.requires_freshness, bool):
            raise TypeError(f"requires_freshness must be bool: deliverable_id={self.deliverable_id!r}")
        if self.requires_freshness:
            if self.max_freshness_lag_seconds is None:
                raise ValueError(
                    f"requires_freshness=True demands max_freshness_lag_seconds: deliverable_id={self.deliverable_id!r}"
                )
            _positive("max_freshness_lag_seconds", self.max_freshness_lag_seconds)
        elif self.max_freshness_lag_seconds is not None:
            raise ValueError(
                f"max_freshness_lag_seconds requires requires_freshness=True: deliverable_id={self.deliverable_id!r}"
            )
        if self.input_batch_binding is not None:
            _text("input_batch_binding", self.input_batch_binding)


@dataclass(frozen=True, slots=True)
class OlapObjective:
    """OLAP service: per-item delivery checklist or a frozen task-class budget."""

    objective_id: str
    service_id: str
    olap_mode: OlapMode
    deliverables: tuple[DeliverableContract, ...] = ()
    deadline_seconds: float | None = None
    min_on_time_correct_fraction: float | None = None
    calibration_evidence_id: str | None = None
    load_class: LoadClass = LoadClass.OLAP

    def __post_init__(self) -> None:
        if self.load_class is not LoadClass.OLAP:
            raise TypeError(f"OlapObjective load_class must be OLAP: objective_id={self.objective_id!r}, value={self.load_class!r}")
        _text("objective_id", self.objective_id)
        _text("service_id", self.service_id)
        if not isinstance(self.olap_mode, OlapMode):
            raise TypeError(f"olap_mode must be OlapMode: objective_id={self.objective_id!r}, value={self.olap_mode!r}")
        if self.olap_mode is OlapMode.DELIVERABLE_CHECKLIST:
            if not self.deliverables:
                raise ValueError(f"deliverable_checklist requires deliverables: objective_id={self.objective_id!r}")
            if self.deadline_seconds is not None or self.min_on_time_correct_fraction is not None:
                raise ValueError(
                    "deliverable_checklist accepts per-deliverable deadlines only: "
                    f"objective_id={self.objective_id!r}"
                )
        else:
            if self.deliverables:
                raise ValueError(f"task_class_budget must not declare deliverables: objective_id={self.objective_id!r}")
            _positive("deadline_seconds", self.deadline_seconds if self.deadline_seconds is not None else 0)
            if self.min_on_time_correct_fraction is None:
                raise ValueError(f"task_class_budget requires min_on_time_correct_fraction: objective_id={self.objective_id!r}")
            _fraction("min_on_time_correct_fraction", self.min_on_time_correct_fraction)
            if not isinstance(self.calibration_evidence_id, str) or not self.calibration_evidence_id.strip():
                raise ValueError(
                    f"task_class_budget requires calibration_evidence_id: objective_id={self.objective_id!r}"
                )
        deliverable_ids = [deliverable.deliverable_id for deliverable in self.deliverables]
        if len(deliverable_ids) != len(set(deliverable_ids)):
            raise ValueError(
                f"deliverable IDs must be unique: objective_id={self.objective_id!r}, deliverable_ids={deliverable_ids!r}"
            )


@dataclass(frozen=True, slots=True)
class HtapObjective:
    """HTAP service: one transaction objective plus one analysis objective."""

    objective_id: str
    service_id: str
    htap_mode: HtapMode
    transaction_objective_id: str
    analysis_objective_id: str
    load_class: LoadClass = LoadClass.HTAP

    def __post_init__(self) -> None:
        if self.load_class is not LoadClass.HTAP:
            raise TypeError(f"HtapObjective load_class must be HTAP: objective_id={self.objective_id!r}, value={self.load_class!r}")
        _text("objective_id", self.objective_id)
        _text("service_id", self.service_id)
        if not isinstance(self.htap_mode, HtapMode):
            raise TypeError(f"htap_mode must be HtapMode: objective_id={self.objective_id!r}, value={self.htap_mode!r}")
        _text("transaction_objective_id", self.transaction_objective_id)
        _text("analysis_objective_id", self.analysis_objective_id)


ServiceObjectiveSpec = OltpObjective | OlapObjective | HtapObjective


# ---------------------------------------------------------------------------
# Data integrity and required state
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class IntegrityCheckSpec:
    """Reference to a registered business-integrity verifier."""

    check_id: str
    verifier_id: str
    params: Mapping[str, JSONValue]

    def __post_init__(self) -> None:
        _text("integrity check_id", self.check_id)
        _text("integrity verifier_id", self.verifier_id)
        _json_mapping(f"integrity check params for {self.check_id!r}", self.params)


@dataclass(frozen=True, slots=True)
class ContinuityStateSpec:
    """Final-observation-window continuation capacity of one service."""

    check_id: str
    service_id: str
    window_seconds: float
    min_success_fraction: float
    kind: RequiredStateKind = RequiredStateKind.CONTINUITY

    def __post_init__(self) -> None:
        if self.kind is not RequiredStateKind.CONTINUITY:
            raise TypeError(f"continuity check kind mismatch: check_id={self.check_id!r}, kind={self.kind!r}")
        _text("check_id", self.check_id)
        _text("service_id", self.service_id)
        _positive("window_seconds", self.window_seconds)
        _fraction("min_success_fraction", self.min_success_fraction)


@dataclass(frozen=True, slots=True)
class DeliverablePresentSpec:
    """An explicitly declared deliverable must be present and correct at the end.

    ``params`` is the declared contract of the bound deliverable verifier
    (``bindings`` maps ``deliverable_id`` -> ``verifier_id``); the collector
    resolves and forwards it exactly like a ``verifier`` check.
    """

    check_id: str
    deliverable_id: str
    params: Mapping[str, JSONValue]
    kind: RequiredStateKind = RequiredStateKind.DELIVERABLE_PRESENT

    def __post_init__(self) -> None:
        if self.kind is not RequiredStateKind.DELIVERABLE_PRESENT:
            raise TypeError(f"deliverable_present check kind mismatch: check_id={self.check_id!r}, kind={self.kind!r}")
        _text("check_id", self.check_id)
        _text("deliverable_id", self.deliverable_id)
        _json_mapping(f"required-state params for {self.check_id!r}", self.params)


@dataclass(frozen=True, slots=True)
class GucEffectiveSpec:
    """A required effective setting, not the text of an ALTER statement.

    ``scope`` must belong to the vocabulary of the declaring system
    (``SETTING_SCOPES_BY_SYSTEM``, validated against ``spec.system``);
    ``effective_on`` states which connections must observe the value at final
    sampling and ``persist_required`` whether the change must survive a
    restart of the owning configuration surface. System-specific observation
    detail (PG ``pending_restart``, TiDB variable persistence, component
    config files) belongs to the backend sampling side.
    """

    check_id: str
    guc_name: str
    allowed_values: tuple[str, ...]
    scope: SettingScope
    scope_name: str | None
    effective_on: SettingEffect
    persist_required: bool
    kind: RequiredStateKind = RequiredStateKind.GUC_EFFECTIVE

    def __post_init__(self) -> None:
        if self.kind is not RequiredStateKind.GUC_EFFECTIVE:
            raise TypeError(f"guc_effective check kind mismatch: check_id={self.check_id!r}, kind={self.kind!r}")
        _text("check_id", self.check_id)
        _text("guc_name", self.guc_name)
        if not self.allowed_values or any(not isinstance(value, str) or not value.strip() for value in self.allowed_values):
            raise ValueError(f"allowed_values must be non-empty strings: check_id={self.check_id!r}")
        if not isinstance(self.scope, SettingScope):
            raise TypeError(f"required-state scope must be SettingScope: check_id={self.check_id!r}, value={self.scope!r}")
        if self.scope in SETTING_SCOPES_WITH_NAME:
            _text(f"required-state scope_name for {self.check_id!r}", self.scope_name or "")
        elif self.scope_name is not None:
            raise ValueError(
                f"required-state scope {self.scope.value!r} must not name a scope object: check_id={self.check_id!r}"
            )
        if not isinstance(self.effective_on, SettingEffect):
            raise TypeError(f"required-state effective_on must be SettingEffect: check_id={self.check_id!r}, value={self.effective_on!r}")
        if not isinstance(self.persist_required, bool):
            raise TypeError(f"required-state persist_required must be bool: check_id={self.check_id!r}, value={self.persist_required!r}")


@dataclass(frozen=True, slots=True)
class VerifierStateSpec:
    """Instance business-state verifier (index validity, backfill completeness, ...)."""

    check_id: str
    verifier_id: str
    params: Mapping[str, JSONValue]
    kind: RequiredStateKind = RequiredStateKind.VERIFIER

    def __post_init__(self) -> None:
        if self.kind is not RequiredStateKind.VERIFIER:
            raise TypeError(f"verifier check kind mismatch: check_id={self.check_id!r}, kind={self.kind!r}")
        _text("check_id", self.check_id)
        _text("verifier_id", self.verifier_id)
        _json_mapping(f"required-state params for {self.check_id!r}", self.params)


RequiredStateItem = ContinuityStateSpec | DeliverablePresentSpec | GucEffectiveSpec | VerifierStateSpec


# ---------------------------------------------------------------------------
# Safety policy
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProtectedObjectSpec:
    """fnmatch pattern of objects the agent must not modify."""

    name_pattern: str

    def __post_init__(self) -> None:
        _text("protected_objects name_pattern", self.name_pattern)


@dataclass(frozen=True, slots=True)
class SafetyPolicyContract:
    """The public authorization boundary: action classes the agent may take,
    protected objects, GUCs it may change, and GUC floors it may never cross.

    ``read_only_action_classes`` names the action classes that only observe
    state (SELECT-style reads). When such an action touches a protected object
    it is recorded as an audit finding, never a safety failure."""

    allowed_action_classes: tuple[str, ...]
    protected_objects: tuple[ProtectedObjectSpec, ...] = ()
    authorized_guc_names: tuple[str, ...] = ()
    guc_floor: Mapping[str, str] = field(default_factory=dict)
    read_only_action_classes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.allowed_action_classes or any(
            not isinstance(action_class, str) or not action_class.strip() for action_class in self.allowed_action_classes
        ):
            raise ValueError("allowed_action_classes must be non-empty strings and the tuple must not be empty")
        if len(set(self.allowed_action_classes)) != len(self.allowed_action_classes):
            raise ValueError("allowed_action_classes must be unique")
        for guc_name in self.authorized_guc_names:
            _text("authorized guc name", guc_name)
        if len(set(self.authorized_guc_names)) != len(self.authorized_guc_names):
            raise ValueError("authorized_guc_names must be unique")
        if any(not isinstance(action_class, str) or not action_class.strip() for action_class in self.read_only_action_classes):
            raise ValueError("read_only_action_classes must be non-empty strings")
        if len(set(self.read_only_action_classes)) != len(self.read_only_action_classes):
            raise ValueError("read_only_action_classes must be unique")
        _json_mapping("guc_floor", self.guc_floor)
        for guc_name, floor_value in self.guc_floor.items():
            _text("guc_floor key", guc_name)
            _text(f"guc_floor value for {guc_name!r}", floor_value)


# ---------------------------------------------------------------------------
# Diagnosis contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ExpectedDiagnosisConditionSpec:
    condition_id: str
    aliases: tuple[str, ...]
    contradictions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _text("condition_id", self.condition_id)
        if not self.aliases or any(not isinstance(alias, str) or not alias.strip() for alias in self.aliases):
            raise ValueError(f"condition aliases must be non-empty readable sentences: condition_id={self.condition_id!r}")
        if any(not isinstance(entry, str) or not entry.strip() for entry in self.contradictions):
            raise ValueError(f"condition contradictions must be non-empty strings: condition_id={self.condition_id!r}")


@dataclass(frozen=True, slots=True)
class DiagnosisIncidentSpec:
    incident_id: str
    statement: str
    conditions: tuple[ExpectedDiagnosisConditionSpec, ...]

    def __post_init__(self) -> None:
        _text("incident_id", self.incident_id)
        _text("incident statement", self.statement)
        if not self.conditions:
            raise ValueError(f"incident requires at least one condition: incident_id={self.incident_id!r}")
        condition_ids = [condition.condition_id for condition in self.conditions]
        if len(condition_ids) != len(set(condition_ids)):
            raise ValueError(f"incident condition IDs must be unique: incident_id={self.incident_id!r}")


@dataclass(frozen=True, slots=True)
class DiagnosisContract:
    """Declared business-incident explanations. Empty incidents => DP = N/A."""

    incidents: tuple[DiagnosisIncidentSpec, ...] = ()

    def __post_init__(self) -> None:
        incident_ids = [incident.incident_id for incident in self.incidents]
        if len(incident_ids) != len(set(incident_ids)):
            raise ValueError(f"incident IDs must be unique: incident_ids={incident_ids!r}")


# ---------------------------------------------------------------------------
# Events: capability ID + occurrence payload
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EventSpec:
    event_id: str
    capability_id: str
    occurrence: int
    entity: str
    payload: Mapping[str, JSONValue]
    start_seconds: int
    activation_timeout_seconds: int
    response_deadline_seconds: int
    trigger: EventTrigger

    def __post_init__(self) -> None:
        for name, value in (("event_id", self.event_id), ("capability_id", self.capability_id), ("entity", self.entity)):
            _text(f"event {name}", value)
        if isinstance(self.occurrence, bool) or not isinstance(self.occurrence, int) or self.occurrence < 1:
            raise ValueError(f"event occurrence must be a positive integer: event_id={self.event_id!r}, value={self.occurrence!r}")
        _json_mapping(f"event payload for {self.event_id!r}", self.payload)
        if not isinstance(self.trigger, EventTrigger):
            raise TypeError(f"event trigger must be EventTrigger: event_id={self.event_id!r}, value={self.trigger!r}")
        if self.start_seconds < 0:
            raise ValueError(f"event start_seconds must be non-negative: event_id={self.event_id!r}, value={self.start_seconds}")
        for name, value in (
            ("activation_timeout_seconds", self.activation_timeout_seconds),
            ("response_deadline_seconds", self.response_deadline_seconds),
        ):
            _positive(f"event {name} for {self.event_id!r}", value)


# ---------------------------------------------------------------------------
# Root spec
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PersistentScenarioSpec:
    protocol_version: str
    scenario_id: str
    family_id: str
    system: DatabaseSystem
    mode: str
    warmup_seconds: int
    input_stop_seconds: int
    agent_stop_seconds: int
    horizon_seconds: int
    calibration: CalibrationSpec
    environment: PersistentScenarioEnvironmentSpec
    services: tuple[ServiceObjectiveSpec, ...]
    safety_policy: SafetyPolicyContract
    integrity_checks: tuple[IntegrityCheckSpec, ...]
    required_state: tuple[RequiredStateItem, ...]
    diagnosis_contract: DiagnosisContract
    events: tuple[EventSpec, ...]
    inspection_interval_seconds: int
    # Formal paper-citation tag; dev/smoke fixtures are not citable and carry none.
    citation_tag: str | None = None

    def __post_init__(self) -> None:
        if self.protocol_version != PROTOCOL_VERSION:
            raise ValueError(
                f"Unsupported Persistent Scenario protocol_version: value={self.protocol_version!r}, expected={PROTOCOL_VERSION!r}"
            )
        _text("scenario_id", self.scenario_id)
        _text("family_id", self.family_id)
        if self.citation_tag is not None:
            _text("citation_tag", self.citation_tag)
            if not re.fullmatch(r"(PG|TB)-PS-\d{2}", self.citation_tag):
                raise ValueError(
                    f"persistent_scenario citation_tag must match (PG|TB)-PS-NN: value={self.citation_tag!r}"
                )
            expected_prefix = "PG" if self.system is DatabaseSystem.POSTGRESQL else "TB"
            if not self.citation_tag.startswith(f"{expected_prefix}-"):
                raise ValueError(
                    f"persistent_scenario citation_tag system prefix mismatch: "
                    f"citation_tag={self.citation_tag!r}, system={self.system.value!r}"
                )
        if not isinstance(self.system, DatabaseSystem):
            raise TypeError(f"persistent_scenario system must be DatabaseSystem: value={self.system!r}")
        if self.mode != "timeline":
            raise ValueError(f"Persistent Scenario v2 only supports timeline mode: mode={self.mode!r}")
        # warmup is a real-time pre-phase; every other boundary is measured from
        # the scoring start (t=0 in the contract timeline tables).
        if self.warmup_seconds < 0:
            raise ValueError(f"warmup_seconds must be non-negative: value={self.warmup_seconds}")
        for name, value in (
            ("input_stop_seconds", self.input_stop_seconds),
            ("agent_stop_seconds", self.agent_stop_seconds),
            ("horizon_seconds", self.horizon_seconds),
        ):
            _positive(name, value)
        if not self.input_stop_seconds <= self.agent_stop_seconds <= self.horizon_seconds:
            raise ValueError(
                "time boundaries must satisfy input_stop <= agent_stop <= horizon: "
                f"input_stop_seconds={self.input_stop_seconds}, agent_stop_seconds={self.agent_stop_seconds}, "
                f"horizon_seconds={self.horizon_seconds}"
            )
        _positive("inspection_interval_seconds", self.inspection_interval_seconds)

        if not self.services:
            raise ValueError("Persistent Scenario must declare at least one service objective")
        objective_ids = [service.objective_id for service in self.services]
        if len(objective_ids) != len(set(objective_ids)):
            raise ValueError(f"service objective IDs must be unique: objective_ids={objective_ids!r}")
        service_ids = [service.service_id for service in self.services]
        if len(service_ids) != len(set(service_ids)):
            raise ValueError(f"service IDs must be unique: service_ids={service_ids!r}")
        by_objective_id = {service.objective_id: service for service in self.services}
        for service in self.services:
            if isinstance(service, HtapObjective):
                transaction = by_objective_id.get(service.transaction_objective_id)
                analysis = by_objective_id.get(service.analysis_objective_id)
                if not isinstance(transaction, OltpObjective):
                    raise ValueError(
                        "htap transaction_objective_id must reference an oltp objective in the same spec: "
                        f"objective_id={service.objective_id!r}, transaction_objective_id={service.transaction_objective_id!r}, "
                        f"found={type(transaction).__name__ if transaction is not None else None!r}"
                    )
                if not isinstance(analysis, OlapObjective):
                    raise ValueError(
                        "htap analysis_objective_id must reference an olap objective in the same spec: "
                        f"objective_id={service.objective_id!r}, analysis_objective_id={service.analysis_objective_id!r}, "
                        f"found={type(analysis).__name__ if analysis is not None else None!r}"
                    )

        if not isinstance(self.safety_policy, SafetyPolicyContract):
            raise TypeError("spec.safety_policy must be a SafetyPolicyContract")
        check_ids = [check.check_id for check in self.integrity_checks]
        if len(check_ids) != len(set(check_ids)):
            raise ValueError(f"integrity check IDs must be unique: check_ids={check_ids!r}")
        state_ids = [item.check_id for item in self.required_state]
        if len(state_ids) != len(set(state_ids)):
            raise ValueError(f"required-state IDs must be unique: state_ids={state_ids!r}")
        known_deliverable_ids = {
            deliverable.deliverable_id
            for service in self.services
            if isinstance(service, OlapObjective)
            for deliverable in service.deliverables
        }
        for item in self.required_state:
            if isinstance(item, DeliverablePresentSpec) and item.deliverable_id not in known_deliverable_ids:
                raise ValueError(
                    "required-state deliverable_present references an undeclared deliverable: "
                    f"check_id={item.check_id!r}, deliverable_id={item.deliverable_id!r}"
                )
            if isinstance(item, GucEffectiveSpec) and item.scope not in SETTING_SCOPES_BY_SYSTEM[self.system]:
                raise ValueError(
                    "required-state scope is not in the system vocabulary: "
                    f"check_id={item.check_id!r}, system={self.system.value!r}, scope={item.scope.value!r}, "
                    f"allowed={sorted(scope.value for scope in SETTING_SCOPES_BY_SYSTEM[self.system])!r}"
                )
            if isinstance(item, ContinuityStateSpec):
                if not any(
                    isinstance(service, OltpObjective) and service.service_id == item.service_id
                    for service in self.services
                ):
                    raise ValueError(
                        "required-state continuity must reference an oltp service: "
                        f"check_id={item.check_id!r}, service_id={item.service_id!r}"
                    )
        if not isinstance(self.diagnosis_contract, DiagnosisContract):
            raise TypeError("spec.diagnosis_contract must be a DiagnosisContract")

        if not self.events:
            raise ValueError("Persistent Scenario must contain at least one event")
        event_ids = [event.event_id for event in self.events]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError(f"event IDs must be unique: event_ids={event_ids!r}")
        previous_start = -1
        for event in self.events:
            if event.start_seconds < previous_start:
                raise ValueError(
                    "events must be ordered by non-decreasing start_seconds: "
                    f"event_id={event.event_id!r}, start_seconds={event.start_seconds}, previous_start_seconds={previous_start}"
                )
            previous_start = event.start_seconds
            if event.start_seconds >= self.horizon_seconds:
                raise ValueError(
                    "event must start before the horizon: "
                    f"event_id={event.event_id!r}, start_seconds={event.start_seconds}, horizon_seconds={self.horizon_seconds}"
                )
        last_event = max(self.events, key=lambda event: event.start_seconds)
        if last_event.start_seconds >= self.input_stop_seconds:
            raise ValueError(
                "input_stop_seconds must exceed the last event start: an event scheduled at or past input_stop "
                "has its capability job submissions rejected by the frozen-input gate once activation latency "
                "passes the 1s tolerance "
                f"(input_stop_seconds={self.input_stop_seconds}, last_event_id={last_event.event_id!r}, "
                f"last_event_start_seconds={last_event.start_seconds})"
            )


def compress_persistent_scenario_timeline(spec: PersistentScenarioSpec, time_scale: float) -> PersistentScenarioSpec:
    """Shorten development timing while preserving the real workload warmup.

    Business deadlines (per transaction, per task, per deliverable) are
    submission-relative and therefore not scalable here; only the timeline
    boundaries shrink.
    """
    if isinstance(time_scale, bool) or not isinstance(time_scale, (int, float)) or time_scale <= 1:
        raise ValueError(
            "Persistent Scenario development timeline compression requires time_scale > 1: "
            f"scenario_id={spec.scenario_id!r}, time_scale={time_scale!r}"
        )

    def scaled(value: int, field: str) -> int:
        if value == 0:
            return 0
        result = ceil(value / float(time_scale))
        if result < 1:
            raise ValueError(
                "Compressed Persistent Scenario timeline field became non-positive: "
                f"scenario_id={spec.scenario_id!r}, field={field!r}, value={value!r}, time_scale={time_scale!r}"
            )
        return result

    # Every boundary except warmup is measured from the scoring start, so a
    # compressed timeline scales them directly.
    events = tuple(
        replace(
            event,
            start_seconds=scaled(event.start_seconds, f"events.{event.event_id}.start_seconds"),
            activation_timeout_seconds=event.activation_timeout_seconds,
            response_deadline_seconds=scaled(
                event.response_deadline_seconds, f"events.{event.event_id}.response_deadline_seconds"
            ),
        )
        for event in spec.events
    )
    horizon_seconds = max(
        scaled(spec.horizon_seconds, "horizon_seconds"),
        max(event.start_seconds + event.activation_timeout_seconds for event in events),
    )
    # The continuity window slices the same compressed timeline the ledger is
    # written on, so it must shrink with the other boundaries; otherwise a
    # compressed run's "final window" spans the whole run and mixes the fault
    # period into the continuity verdict.
    required_state = tuple(
        replace(
            item,
            window_seconds=float(ceil(item.window_seconds / float(time_scale))),
        )
        if isinstance(item, ContinuityStateSpec)
        else item
        for item in spec.required_state
    )
    return replace(
        spec,
        horizon_seconds=horizon_seconds,
        input_stop_seconds=min(scaled(spec.input_stop_seconds, "input_stop_seconds"), horizon_seconds),
        agent_stop_seconds=min(scaled(spec.agent_stop_seconds, "agent_stop_seconds"), horizon_seconds),
        events=events,
        inspection_interval_seconds=scaled(spec.inspection_interval_seconds, "inspection_interval_seconds"),
        required_state=required_state,
    )
