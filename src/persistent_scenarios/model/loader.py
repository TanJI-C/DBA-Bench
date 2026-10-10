"""Strict loader for the Persistent Scenario YAML contract (protocol v2, interface v1)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

import yaml

from .enums import (
    CalibrationStatus,
    DatabaseSystem,
    EventTrigger,
    HtapMode,
    LoadClass,
    OlapMode,
    RequiredStateKind,
    SettingEffect,
    SettingScope,
)
from .spec import (
    PROTOCOL_VERSION,
    CalibrationSpec,
    ContinuityStateSpec,
    DeliverableContract,
    DeliverablePresentSpec,
    DiagnosisContract,
    DiagnosisIncidentSpec,
    EventSpec,
    ExpectedDiagnosisConditionSpec,
    GucEffectiveSpec,
    IntegrityCheckSpec,
    NodeSpec,
    NodeVolume,
    OlapObjective,
    OltpObjective,
    HtapObjective,
    PersistentScenarioEnvironmentSpec,
    PersistentScenarioResourceSpec,
    PersistentScenarioSpec,
    ProtectedObjectSpec,
    SafetyPolicyContract,
    VerifierStateSpec,
    validate_json_value,
)

IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


def _mapping(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a mapping: value={value!r}")
    return value


def _unknown(data: Mapping[str, Any], allowed: set[str], context: str) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ValueError(f"{context} contains unknown fields: {unknown!r}")


def _required(data: Mapping[str, Any], key: str, context: str) -> Any:
    if key not in data:
        raise ValueError(f"{context}.{key} is required")
    return data[key]


def _string(data: Mapping[str, Any], key: str, context: str) -> str:
    value = _required(data, key, context)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string: value={value!r}")
    return value.strip()


def _optional_string(data: Mapping[str, Any], key: str, context: str) -> str | None:
    if key not in data or data[key] is None:
        return None
    value = data[key]
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}.{key} must be a non-empty string when present: value={value!r}")
    return value.strip()


def _identifier(data: Mapping[str, Any], key: str, context: str) -> str:
    value = _string(data, key, context)
    if not IDENTIFIER_RE.fullmatch(value) or "__" in value:
        raise ValueError(f"{context}.{key} is not a valid identifier: value={value!r}")
    return value


def _integer(data: Mapping[str, Any], key: str, context: str) -> int:
    value = _required(data, key, context)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{context}.{key} must be an integer: value={value!r}")
    return value


def _number(data: Mapping[str, Any], key: str, context: str) -> float:
    value = _required(data, key, context)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{context}.{key} must be numeric, not a string/default: value={value!r}")
    return float(value)


def _boolean(data: Mapping[str, Any], key: str, context: str) -> bool:
    value = _required(data, key, context)
    if not isinstance(value, bool):
        raise ValueError(f"{context}.{key} must be a boolean: value={value!r}")
    return value


def _strings(data: Mapping[str, Any], key: str, context: str) -> tuple[str, ...]:
    value = _required(data, key, context)
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{context}.{key} must be a list of non-empty strings: value={value!r}")
    return tuple(item.strip() for item in value)


def _enum_value(enum_type: type, data: Mapping[str, Any], key: str, context: str):
    value = _string(data, key, context)
    try:
        return enum_type(value)
    except ValueError as exc:
        raise ValueError(
            f"Unsupported {enum_type.__name__} value: {context}.{key}={value!r}, "
            f"allowed={[item.value for item in enum_type]!r}"
        ) from exc


def _json_params(data: Mapping[str, Any], context: str) -> dict[str, Any]:
    value = _required(data, "params", context)
    if not isinstance(value, dict):
        raise ValueError(f"{context}.params must be a mapping: value={value!r}")
    validate_json_value(f"{context}.params", value)
    return value


def _resources(data: Mapping[str, Any], context: str) -> PersistentScenarioResourceSpec:
    _unknown(data, {"worker_physical_cores", "worker_memory_mb", "container_cpu_limit", "container_memory_mb"}, context)
    return PersistentScenarioResourceSpec(
        worker_physical_cores=_integer(data, "worker_physical_cores", context),
        worker_memory_mb=_integer(data, "worker_memory_mb", context),
        container_cpu_limit=_number(data, "container_cpu_limit", context),
        container_memory_mb=_integer(data, "container_memory_mb", context),
    )


def _node(data: Mapping[str, Any], context: str) -> NodeSpec:
    _unknown(data, {"node_id", "role", "resources", "docker_caps", "volumes"}, context)
    raw_volumes = data.get("volumes", [])
    if not isinstance(raw_volumes, list):
        raise ValueError(f"{context}.volumes must be a list: value={raw_volumes!r}")
    volumes = []
    for index, raw in enumerate(raw_volumes):
        volume_context = f"{context}.volumes[{index}]"
        volume = _mapping(raw, volume_context)
        _unknown(volume, {"name", "mount_path"}, volume_context)
        volumes.append(NodeVolume(
            name=_string(volume, "name", volume_context),
            mount_path=_string(volume, "mount_path", volume_context),
        ))
    return NodeSpec(
        node_id=_identifier(data, "node_id", context),
        role=_string(data, "role", context),
        resources=_resources(_mapping(_required(data, "resources", context), f"{context}.resources"), f"{context}.resources"),
        docker_caps=_strings(data, "docker_caps", context) if "docker_caps" in data else (),
        volumes=tuple(volumes),
    )


def _environment(data: Mapping[str, Any]) -> PersistentScenarioEnvironmentSpec:
    context = "persistent_scenario.environment"
    _unknown(data, {"workload", "scale", "base_image", "nodes"}, context)
    raw_nodes = _required(data, "nodes", context)
    if not isinstance(raw_nodes, list) or not raw_nodes:
        raise ValueError(f"{context}.nodes must be a non-empty list")
    return PersistentScenarioEnvironmentSpec(
        workload=_string(data, "workload", context),
        scale=_integer(data, "scale", context),
        base_image=_string(data, "base_image", context),
        nodes=tuple(_node(_mapping(item, f"{context}.nodes[{index}]"), f"{context}.nodes[{index}]") for index, item in enumerate(raw_nodes)),
    )


def _calibration(data: Mapping[str, Any]) -> CalibrationSpec:
    context = "persistent_scenario.calibration"
    _unknown(data, {"status", "evidence_id"}, context)
    return CalibrationSpec(
        status=_enum_value(CalibrationStatus, data, "status", context),
        evidence_id=_string(data, "evidence_id", context),
    )


def _deliverable(data: Mapping[str, Any], context: str) -> DeliverableContract:
    _unknown(data, {"deliverable_id", "deadline_seconds", "requires_freshness", "max_freshness_lag_seconds", "input_batch_binding"}, context)
    max_freshness = data.get("max_freshness_lag_seconds")
    if max_freshness is not None and (isinstance(max_freshness, bool) or not isinstance(max_freshness, (int, float))):
        raise ValueError(f"{context}.max_freshness_lag_seconds must be numeric: value={max_freshness!r}")
    return DeliverableContract(
        deliverable_id=_identifier(data, "deliverable_id", context),
        deadline_seconds=_number(data, "deadline_seconds", context),
        requires_freshness=_boolean(data, "requires_freshness", context),
        max_freshness_lag_seconds=float(max_freshness) if max_freshness is not None else None,
        input_batch_binding=_optional_string(data, "input_batch_binding", context),
    )


def _service(data: Mapping[str, Any], context: str):
    load_class = _enum_value(LoadClass, data, "load_class", context)
    if load_class is LoadClass.OLTP:
        _unknown(data, {
            "objective_id", "load_class", "service_id", "deadline_seconds", "min_success_fraction",
            "outage_contract_seconds", "outage_source",
        }, context)
        outage = data.get("outage_contract_seconds")
        if outage is not None and (isinstance(outage, bool) or not isinstance(outage, (int, float))):
            raise ValueError(f"{context}.outage_contract_seconds must be numeric: value={outage!r}")
        return OltpObjective(
            objective_id=_identifier(data, "objective_id", context),
            service_id=_identifier(data, "service_id", context),
            deadline_seconds=_number(data, "deadline_seconds", context),
            min_success_fraction=_number(data, "min_success_fraction", context),
            outage_contract_seconds=float(outage) if outage is not None else None,
            outage_source=_optional_string(data, "outage_source", context),
        )
    if load_class is LoadClass.OLAP:
        _unknown(data, {
            "objective_id", "load_class", "service_id", "olap_mode", "deliverables",
            "deadline_seconds", "min_on_time_correct_fraction", "calibration_evidence_id",
        }, context)
        mode = _enum_value(OlapMode, data, "olap_mode", context)
        raw_deliverables = data.get("deliverables", [])
        if not isinstance(raw_deliverables, list):
            raise ValueError(f"{context}.deliverables must be a list: value={raw_deliverables!r}")
        deliverables = tuple(
            _deliverable(_mapping(raw, f"{context}.deliverables[{index}]"), f"{context}.deliverables[{index}]")
            for index, raw in enumerate(raw_deliverables)
        )
        deadline = data.get("deadline_seconds")
        if deadline is not None and (isinstance(deadline, bool) or not isinstance(deadline, (int, float))):
            raise ValueError(f"{context}.deadline_seconds must be numeric: value={deadline!r}")
        fraction = data.get("min_on_time_correct_fraction")
        if fraction is not None and (isinstance(fraction, bool) or not isinstance(fraction, (int, float))):
            raise ValueError(f"{context}.min_on_time_correct_fraction must be numeric: value={fraction!r}")
        return OlapObjective(
            objective_id=_identifier(data, "objective_id", context),
            service_id=_identifier(data, "service_id", context),
            olap_mode=mode,
            deliverables=deliverables,
            deadline_seconds=float(deadline) if deadline is not None else None,
            min_on_time_correct_fraction=float(fraction) if fraction is not None else None,
            calibration_evidence_id=_optional_string(data, "calibration_evidence_id", context),
        )
    _unknown(data, {
        "objective_id", "load_class", "service_id", "htap_mode",
        "transaction_objective_id", "analysis_objective_id",
    }, context)
    return HtapObjective(
        objective_id=_identifier(data, "objective_id", context),
        service_id=_identifier(data, "service_id", context),
        htap_mode=_enum_value(HtapMode, data, "htap_mode", context),
        transaction_objective_id=_identifier(data, "transaction_objective_id", context),
        analysis_objective_id=_identifier(data, "analysis_objective_id", context),
    )


def _safety_policy(data: Mapping[str, Any]) -> SafetyPolicyContract:
    context = "persistent_scenario.safety_policy"
    _unknown(data, {
        "allowed_action_classes", "protected_objects", "authorized_guc_names", "guc_floor",
        "read_only_action_classes",
    }, context)
    raw_protected = data.get("protected_objects", [])
    if not isinstance(raw_protected, list):
        raise ValueError(f"{context}.protected_objects must be a list: value={raw_protected!r}")
    protected = []
    for index, raw in enumerate(raw_protected):
        item_context = f"{context}.protected_objects[{index}]"
        item = _mapping(raw, item_context)
        _unknown(item, {"name_pattern"}, item_context)
        protected.append(ProtectedObjectSpec(name_pattern=_string(item, "name_pattern", item_context)))
    guc_floor = data.get("guc_floor", {})
    if not isinstance(guc_floor, dict):
        raise ValueError(f"{context}.guc_floor must be a mapping: value={guc_floor!r}")
    validate_json_value(f"{context}.guc_floor", guc_floor)
    return SafetyPolicyContract(
        allowed_action_classes=_strings(data, "allowed_action_classes", context),
        protected_objects=tuple(protected),
        authorized_guc_names=_strings(data, "authorized_guc_names", context) if "authorized_guc_names" in data else (),
        guc_floor=dict(guc_floor),
        read_only_action_classes=(
            _strings(data, "read_only_action_classes", context) if "read_only_action_classes" in data else ()
        ),
    )


def _required_state_item(data: Mapping[str, Any], context: str):
    kind = _enum_value(RequiredStateKind, data, "kind", context)
    if kind is RequiredStateKind.CONTINUITY:
        _unknown(data, {"check_id", "kind", "service_id", "window_seconds", "min_success_fraction"}, context)
        return ContinuityStateSpec(
            check_id=_identifier(data, "check_id", context),
            service_id=_identifier(data, "service_id", context),
            window_seconds=_number(data, "window_seconds", context),
            min_success_fraction=_number(data, "min_success_fraction", context),
        )
    if kind is RequiredStateKind.DELIVERABLE_PRESENT:
        _unknown(data, {"check_id", "kind", "deliverable_id", "params"}, context)
        return DeliverablePresentSpec(
            check_id=_identifier(data, "check_id", context),
            deliverable_id=_identifier(data, "deliverable_id", context),
            params=_json_params(data, context),
        )
    if kind is RequiredStateKind.GUC_EFFECTIVE:
        _unknown(
            data,
            {"check_id", "kind", "guc_name", "allowed_values", "scope", "scope_name", "effective_on", "persist_required"},
            context,
        )
        scope_name = data.get("scope_name")
        if scope_name is not None and (not isinstance(scope_name, str) or not scope_name.strip()):
            raise ValueError(f"{context}.scope_name must be a non-empty string when present: value={scope_name!r}")
        return GucEffectiveSpec(
            check_id=_identifier(data, "check_id", context),
            guc_name=_string(data, "guc_name", context),
            allowed_values=_strings(data, "allowed_values", context),
            scope=_enum_value(SettingScope, data, "scope", context),
            scope_name=scope_name.strip() if isinstance(scope_name, str) else None,
            effective_on=_enum_value(SettingEffect, data, "effective_on", context),
            persist_required=_boolean(data, "persist_required", context),
        )
    _unknown(data, {"check_id", "kind", "verifier_id", "params"}, context)
    return VerifierStateSpec(
        check_id=_identifier(data, "check_id", context),
        verifier_id=_string(data, "verifier_id", context),
        params=_json_params(data, context),
    )


def _integrity_checks(raw_items: list[Any]) -> tuple[IntegrityCheckSpec, ...]:
    items = []
    for index, raw in enumerate(raw_items):
        context = f"persistent_scenario.integrity_checks[{index}]"
        item = _mapping(raw, context)
        _unknown(item, {"check_id", "verifier_id", "params"}, context)
        items.append(IntegrityCheckSpec(
            check_id=_identifier(item, "check_id", context),
            verifier_id=_string(item, "verifier_id", context),
            params=_json_params(item, context),
        ))
    return tuple(items)


def _diagnosis_contract(data: Mapping[str, Any] | None) -> DiagnosisContract:
    if data is None:
        return DiagnosisContract(incidents=())
    context = "persistent_scenario.diagnosis_contract"
    item = _mapping(data, context)
    _unknown(item, {"incidents"}, context)
    raw_incidents = item.get("incidents", [])
    if not isinstance(raw_incidents, list):
        raise ValueError(f"{context}.incidents must be a list: value={raw_incidents!r}")
    incidents = []
    for index, raw in enumerate(raw_incidents):
        incident_context = f"{context}.incidents[{index}]"
        incident = _mapping(raw, incident_context)
        _unknown(incident, {"incident_id", "statement", "conditions"}, incident_context)
        raw_conditions = _required(incident, "conditions", incident_context)
        if not isinstance(raw_conditions, list) or not raw_conditions:
            raise ValueError(f"{incident_context}.conditions must be a non-empty list")
        conditions = []
        for condition_index, raw_condition in enumerate(raw_conditions):
            condition_context = f"{incident_context}.conditions[{condition_index}]"
            condition = _mapping(raw_condition, condition_context)
            _unknown(condition, {"condition_id", "aliases", "contradictions"}, condition_context)
            raw_contradictions = condition.get("contradictions", [])
            if not isinstance(raw_contradictions, list) or any(
                not isinstance(entry, str) or not entry.strip() for entry in raw_contradictions
            ):
                raise ValueError(
                    f"{condition_context}.contradictions must be non-empty strings: value={raw_contradictions!r}"
                )
            conditions.append(ExpectedDiagnosisConditionSpec(
                condition_id=_string(condition, "condition_id", condition_context),
                aliases=_strings(condition, "aliases", condition_context),
                contradictions=tuple(entry.strip() for entry in raw_contradictions),
            ))
        incidents.append(DiagnosisIncidentSpec(
            incident_id=_identifier(incident, "incident_id", incident_context),
            statement=_string(incident, "statement", incident_context),
            conditions=tuple(conditions),
        ))
    return DiagnosisContract(incidents=tuple(incidents))


def _event(data: Mapping[str, Any], index: int) -> EventSpec:
    context = f"persistent_scenario.events[{index}]"
    _unknown(
        data,
        {
            "event_id", "capability_id", "occurrence", "entity", "payload", "start_seconds",
            "activation_timeout_seconds", "response_deadline_seconds", "trigger",
        },
        context,
    )
    payload = _required(data, "payload", context)
    if not isinstance(payload, dict):
        raise ValueError(f"{context}.payload must be a mapping: value={payload!r}")
    validate_json_value(f"{context}.payload", payload)
    return EventSpec(
        event_id=_identifier(data, "event_id", context),
        capability_id=_identifier(data, "capability_id", context),
        occurrence=_integer(data, "occurrence", context),
        entity=_string(data, "entity", context),
        payload=payload,
        start_seconds=_integer(data, "start_seconds", context),
        activation_timeout_seconds=_integer(data, "activation_timeout_seconds", context),
        response_deadline_seconds=_integer(data, "response_deadline_seconds", context),
        trigger=_enum_value(EventTrigger, data, "trigger", context),
    )


def load_persistent_scenario(path: str | Path) -> PersistentScenarioSpec:
    source_path = Path(path).resolve()
    raw = _mapping(yaml.safe_load(source_path.read_text(encoding="utf-8")), "persistent_scenario")
    _unknown(
        raw,
        {
            "protocol_version", "scenario_id", "family_id", "citation_tag", "system", "mode",
            "warmup_seconds", "input_stop_seconds", "agent_stop_seconds", "horizon_seconds",
            "calibration", "environment", "services", "safety_policy", "integrity_checks",
            "required_state", "diagnosis_contract", "events", "inspection_interval_seconds",
        },
        "persistent_scenario",
    )
    protocol_version = _string(raw, "protocol_version", "persistent_scenario")
    if protocol_version != PROTOCOL_VERSION:
        raise ValueError(
            f"Unsupported Persistent Scenario protocol_version: value={protocol_version!r}, expected={PROTOCOL_VERSION!r}"
        )
    raw_services = _required(raw, "services", "persistent_scenario")
    if not isinstance(raw_services, list) or not raw_services:
        raise ValueError("persistent_scenario.services must be a non-empty list")
    raw_integrity = raw.get("integrity_checks", [])
    raw_required_state = raw.get("required_state", [])
    for name, value in (("integrity_checks", raw_integrity), ("required_state", raw_required_state)):
        if not isinstance(value, list):
            raise ValueError(f"persistent_scenario.{name} must be a list: value={value!r}")
    raw_events = _required(raw, "events", "persistent_scenario")
    if not isinstance(raw_events, list) or not raw_events:
        raise ValueError("persistent_scenario.events must be a non-empty list")
    return PersistentScenarioSpec(
        protocol_version=protocol_version,
        scenario_id=_identifier(raw, "scenario_id", "persistent_scenario"),
        family_id=_identifier(raw, "family_id", "persistent_scenario"),
        citation_tag=_string(raw, "citation_tag", "persistent_scenario") if "citation_tag" in raw else None,
        system=_enum_value(DatabaseSystem, raw, "system", "persistent_scenario"),
        mode=_string(raw, "mode", "persistent_scenario"),
        warmup_seconds=_integer(raw, "warmup_seconds", "persistent_scenario"),
        input_stop_seconds=_integer(raw, "input_stop_seconds", "persistent_scenario"),
        agent_stop_seconds=_integer(raw, "agent_stop_seconds", "persistent_scenario"),
        horizon_seconds=_integer(raw, "horizon_seconds", "persistent_scenario"),
        calibration=_calibration(_mapping(_required(raw, "calibration", "persistent_scenario"), "persistent_scenario.calibration")),
        environment=_environment(_mapping(_required(raw, "environment", "persistent_scenario"), "persistent_scenario.environment")),
        services=tuple(_service(_mapping(item, f"persistent_scenario.services[{index}]"), f"persistent_scenario.services[{index}]") for index, item in enumerate(raw_services)),
        safety_policy=_safety_policy(_mapping(_required(raw, "safety_policy", "persistent_scenario"), "persistent_scenario.safety_policy")),
        integrity_checks=_integrity_checks(raw_integrity),
        required_state=tuple(_required_state_item(_mapping(item, f"persistent_scenario.required_state[{index}]"), f"persistent_scenario.required_state[{index}]") for index, item in enumerate(raw_required_state)),
        diagnosis_contract=_diagnosis_contract(raw.get("diagnosis_contract")),
        events=tuple(_event(_mapping(item, f"persistent_scenario.events[{index}]"), index) for index, item in enumerate(raw_events)),
        inspection_interval_seconds=_integer(raw, "inspection_interval_seconds", "persistent_scenario"),
    )
