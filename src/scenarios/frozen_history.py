"""Static contract for frozen-history procedural history Cases."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping
from typing import TYPE_CHECKING

from src.execution.history.records import HistoricalRecordSource
from src.workloads.specs import BackgroundWorkloadStartPhase

if TYPE_CHECKING:
    from src.workloads.specs import BackgroundWorkloadSpec


class DecoyKind(str, Enum):
    CAPTURED_BENIGN = "captured_benign"
    METRIC_ONLY = "metric_only"
    CANDIDATE_VALLEY = "candidate_valley"


class DecoyDirection(str, Enum):
    SPIKE = "spike"
    DIP = "dip"


@dataclass(frozen=True, slots=True, kw_only=True)
class HistoryDecoySpec:
    decoy_id: str
    kind: DecoyKind
    metric: str
    field: str
    target: str | None
    direction: DecoyDirection
    count: int
    duration_seconds: int
    amplitude_mad: float | None = None
    minimum_deviation_mad: float | None = None
    allow_reverse: bool = False
    record_event_type: str | None = None
    after_target: bool = False
    alignment_group: str | None = None
    # Candidate-valley decoys replay the real target capture's own channel
    # shapes (same depth, same duration, same signature) with a scrambled or
    # incomplete causal composition, so only record evidence and ordered
    # causality can separate them from the buried incident window.
    valley_profile: str | None = None
    baseline_metrics: tuple[str, ...] = ()
    record_event_types: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class FrozenHistorySpec:
    schema_version: int
    duration_seconds: int
    normal_capture_seconds: int
    fault_capture_seconds: int
    base_step_seconds: int
    overview_step_seconds: int
    block_min_seconds: int
    block_max_seconds: int
    transition_seconds: int
    target_age_seconds_range: tuple[int, int]
    required_metrics: tuple[str, ...]
    record_sources: tuple[HistoricalRecordSource, ...]
    decoys: tuple[HistoryDecoySpec, ...]
    max_points_per_series: int
    max_scalar_samples_per_response: int
    max_history_records_per_response: int
    max_history_query_seconds: int = 0
    normal_capture_count: int = 1
    metric_targets: Mapping[str, tuple[str | None, ...]] = field(default_factory=dict)
    metric_rate_windows: Mapping[str, int] = field(default_factory=dict)
    install_before_normal_capture: bool = False
    activate_during_target_capture: bool = False
    post_target_mode: str = "HOLD_TARGET"
    max_history_response_chars: int = 32768
    decoys_adjacent_to_target: bool = False
    aftermath: str = "RETURN_TO_NORMAL"
    # Real captured seconds taken immediately after the target capture while
    # the environment physically converges (for example the archiver draining
    # the ready backlog). When zero, the last target value is held flat to the
    # end of visible history (HOLD_TARGET plateau). When positive, the real
    # aftermath capture is inserted contiguously after the target bundle and
    # the normal background regime fills the remaining tail, so the fault
    # signature exists only inside the target window.
    aftermath_capture_seconds: int = 0
    # Pre-incident strip publication for pinned operation records. When zero,
    # every replayed normal block carries the normal capture's records as
    # before. When positive, the pinned records listed in
    # strip_pinned_record_actions are replayed only into the assembled normal
    # blocks immediately preceding the target window (the strip
    # [target_start - pre_incident_strip_seconds, target_start)), so the
    # evidence those records carry is physically coupled to the incident
    # neighborhood: a query window disjoint from the strip cannot observe them.
    pre_incident_strip_seconds: int = 0
    strip_pinned_record_actions: tuple[tuple[str, str], ...] = ()
    # Frozen-history lightning clones for seeded batch decoy jobs (RG05-mf
    # entity triage). When positive, the caller passes exactly this many
    # decoy job ids via CapturedHistoryInputs, and the assembler gives each
    # one a time-shifted, amplitude-scaled clone of the real target capture's
    # lightning series under the decoy job id. "Which job has history data"
    # then stops identifying the incident; only the cross-metric coupling of
    # the freeze window (frontend SLO storm, TiKV write pressure) does.
    decoy_lightning_job_count: int = 0

    def validate(self, background_workload: BackgroundWorkloadSpec | None = None) -> None:
        if self.schema_version <= 0:
            raise ValueError(f"Frozen history schema_version must be positive: schema_version={self.schema_version}")
        positive = {
            "duration_seconds": self.duration_seconds,
            "normal_capture_seconds": self.normal_capture_seconds,
            "fault_capture_seconds": self.fault_capture_seconds,
            "base_step_seconds": self.base_step_seconds,
            "overview_step_seconds": self.overview_step_seconds,
            "block_min_seconds": self.block_min_seconds,
            "block_max_seconds": self.block_max_seconds,
            "transition_seconds": self.transition_seconds,
            "max_points_per_series": self.max_points_per_series,
            "max_scalar_samples_per_response": self.max_scalar_samples_per_response,
            "max_history_records_per_response": self.max_history_records_per_response,
            "normal_capture_count": self.normal_capture_count,
            "max_history_response_chars": self.max_history_response_chars,
            "max_history_query_seconds": self.max_history_query_seconds or 1,
        }
        invalid = {name: value for name, value in positive.items() if value <= 0}
        if invalid:
            raise ValueError(f"Frozen history values must be positive: invalid={invalid!r}")
        if self.duration_seconds <= self.normal_capture_seconds or self.duration_seconds <= self.fault_capture_seconds:
            raise ValueError(
                "Frozen history duration must exceed both captures: "
                f"duration_seconds={self.duration_seconds}, normal_capture_seconds={self.normal_capture_seconds}, "
                f"fault_capture_seconds={self.fault_capture_seconds}"
            )
        divisible = {
            "duration_seconds": self.duration_seconds,
            "normal_capture_seconds": self.normal_capture_seconds,
            "fault_capture_seconds": self.fault_capture_seconds,
            "overview_step_seconds": self.overview_step_seconds,
            "block_min_seconds": self.block_min_seconds,
            "block_max_seconds": self.block_max_seconds,
            "transition_seconds": self.transition_seconds,
        }
        invalid_divisibility = {
            name: value
            for name, value in divisible.items()
            if value % self.base_step_seconds != 0
        }
        if invalid_divisibility:
            raise ValueError(
                "Frozen history values must be divisible by base_step_seconds: "
                f"base_step_seconds={self.base_step_seconds}, invalid={invalid_divisibility!r}"
            )
        if self.block_min_seconds > self.block_max_seconds:
            raise ValueError(
                f"Frozen history block range is reversed: min={self.block_min_seconds}, max={self.block_max_seconds}"
            )
        if self.block_max_seconds > self.normal_capture_seconds:
            raise ValueError(
                "Frozen history block_max_seconds cannot exceed normal_capture_seconds: "
                f"block_max_seconds={self.block_max_seconds}, normal_capture_seconds={self.normal_capture_seconds}"
            )
        age_low, age_high = self.target_age_seconds_range
        if age_low < self.fault_capture_seconds or age_low > age_high:
            raise ValueError(
                "Frozen-history target age must contain the full fault capture: "
                f"target_age_seconds_range={self.target_age_seconds_range}, fault_capture_seconds={self.fault_capture_seconds}"
            )
        if age_high >= self.duration_seconds:
            raise ValueError(
                "Frozen-history target age must leave target start inside visible history: "
                f"target_age_seconds_range={self.target_age_seconds_range}, duration_seconds={self.duration_seconds}"
            )
        if age_low % self.base_step_seconds or age_high % self.base_step_seconds:
            raise ValueError(
                "Frozen-history target age bounds must align to base_step_seconds: "
                f"target_age_seconds_range={self.target_age_seconds_range}, base_step_seconds={self.base_step_seconds}"
            )
        if self.post_target_mode not in {"HOLD_TARGET", "RESUME_NORMAL"}:
            raise ValueError(
                "Frozen-history post_target_mode is unsupported: "
                f"post_target_mode={self.post_target_mode!r}"
            )
        if self.aftermath not in {"PERSIST", "RETURN_TO_NORMAL"}:
            raise ValueError(
                "Frozen-history aftermath must be PERSIST or RETURN_TO_NORMAL: "
                f"aftermath={self.aftermath!r}"
            )
        if self.aftermath_capture_seconds < 0 or self.aftermath_capture_seconds % self.base_step_seconds:
            raise ValueError(
                "Frozen-history aftermath capture must be a non-negative base-step multiple: "
                f"aftermath_capture_seconds={self.aftermath_capture_seconds}, base_step_seconds={self.base_step_seconds}"
            )
        if self.aftermath == "PERSIST" and self.aftermath_capture_seconds:
            raise ValueError(
                "Frozen-history PERSIST aftermath cannot carry a real aftermath capture: "
                f"aftermath_capture_seconds={self.aftermath_capture_seconds}"
            )
        if self.aftermath_capture_seconds:
            # The overview anchor may shift the target window forward by up to
            # one overview step minus one base point; the earliest target age
            # must still leave room for the aftermath capture.
            anchor_shift_seconds = self.overview_step_seconds - self.base_step_seconds
            aftermath_room = (
                age_low
                - self.fault_capture_seconds
                - self.transition_seconds
                - anchor_shift_seconds
            )
            if self.aftermath_capture_seconds > aftermath_room:
                raise ValueError(
                    "Frozen-history aftermath capture does not fit between the earliest target "
                    "window and the visible history end: "
                    f"aftermath_capture_seconds={self.aftermath_capture_seconds}, room_seconds={aftermath_room}"
                )
            if self.post_target_mode != "HOLD_TARGET":
                raise ValueError(
                    "Frozen-history aftermath capture replaces the plateau and requires "
                    f"post_target_mode=HOLD_TARGET: post_target_mode={self.post_target_mode!r}"
                )
        if self.decoy_lightning_job_count < 0:
            raise ValueError(
                f"Frozen-history decoy_lightning_job_count must be non-negative: value={self.decoy_lightning_job_count}"
            )
        if self.pre_incident_strip_seconds:
            if self.pre_incident_strip_seconds % self.base_step_seconds:
                raise ValueError(
                    "Frozen-history pre-incident strip must align to base_step_seconds: "
                    f"pre_incident_strip_seconds={self.pre_incident_strip_seconds}, "
                    f"base_step_seconds={self.base_step_seconds}"
                )
            if not self.strip_pinned_record_actions:
                raise ValueError(
                    "Frozen-history pre-incident strip requires pinned record actions: "
                    f"strip_pinned_record_actions={self.strip_pinned_record_actions!r}"
                )
            if len(set(self.strip_pinned_record_actions)) != len(self.strip_pinned_record_actions):
                raise ValueError(
                    "Frozen-history strip pinned record actions must be unique: "
                    f"strip_pinned_record_actions={self.strip_pinned_record_actions!r}"
                )
            if any(
                not isinstance(pair, tuple)
                or len(pair) != 2
                or any(not isinstance(part, str) or not part for part in pair)
                for pair in self.strip_pinned_record_actions
            ):
                raise ValueError(
                    "Frozen-history strip pinned record actions must be (event_type, action) "
                    f"non-empty string pairs: strip_pinned_record_actions={self.strip_pinned_record_actions!r}"
                )
            if self.pre_incident_strip_seconds > duration_before_target(age_low, self.transition_seconds):
                raise ValueError(
                    "Frozen-history pre-incident strip must fit before the earliest target window: "
                    f"pre_incident_strip_seconds={self.pre_incident_strip_seconds}, "
                    f"available_seconds={duration_before_target(age_low, self.transition_seconds)}"
                )
        elif self.strip_pinned_record_actions:
            raise ValueError(
                "Frozen-history strip pinned record actions require a pre-incident strip: "
                f"strip_pinned_record_actions={self.strip_pinned_record_actions!r}"
            )
        if self.activate_during_target_capture and not self.install_before_normal_capture:
            raise ValueError(
                "Frozen-history target activation requires install_before_normal_capture=True: "
                f"install_before_normal_capture={self.install_before_normal_capture!r}, "
                f"activate_during_target_capture={self.activate_during_target_capture!r}"
            )
        canonical_metrics = tuple(str(metric).casefold() for metric in self.required_metrics)
        if not canonical_metrics or len(set(canonical_metrics)) != len(canonical_metrics):
            raise ValueError(f"Frozen-history required_metrics must be non-empty and unique: metrics={self.required_metrics!r}")
        if any(not metric for metric in canonical_metrics):
            raise ValueError(f"Frozen-history required_metrics must contain non-empty names: metrics={self.required_metrics!r}")
        self._validate_metric_targets(canonical_metrics)
        self._validate_metric_rate_windows(canonical_metrics)
        if not self.record_sources or len(set(self.record_sources)) != len(self.record_sources):
            raise ValueError(f"Frozen-history record_sources must be non-empty and unique: sources={self.record_sources!r}")
        if any(not isinstance(source, HistoricalRecordSource) for source in self.record_sources):
            raise TypeError(
                "Frozen-history record_sources must use HistoricalRecordSource values: "
                f"record_sources={self.record_sources!r}"
            )
        if len({decoy.decoy_id for decoy in self.decoys}) != len(self.decoys):
            raise ValueError(f"Frozen-history decoy IDs must be unique: decoys={self.decoys!r}")
        if any(decoy.kind is DecoyKind.CANDIDATE_VALLEY for decoy in self.decoys) and not self.decoys_adjacent_to_target:
            raise ValueError(
                "Frozen-history candidate valleys require decoys_adjacent_to_target: "
                f"decoys={self.decoys!r}"
            )
        max_pre_target_seconds = duration_before_target(age_low, self.transition_seconds)
        requested_decoy_seconds = sum(
            decoy.count * (decoy.duration_seconds + self.transition_seconds)
            for decoy in self.decoys
            if not decoy.after_target
        )
        # Each valley anchors one overview grid point into its own span, so the
        # layout must also absorb a shift of up to one overview step.
        requested_valley_anchor_seconds = sum(
            max(0, self.overview_step_seconds - decoy.duration_seconds)
            for decoy in self.decoys
            if decoy.kind is DecoyKind.CANDIDATE_VALLEY
        )
        if requested_decoy_seconds + requested_valley_anchor_seconds > max_pre_target_seconds:
            raise ValueError(
                "Frozen-history decoys cannot fit before the earliest target window: "
                f"requested_seconds={requested_decoy_seconds}, "
                f"valley_anchor_headroom_seconds={requested_valley_anchor_seconds}, "
                f"available_seconds={max_pre_target_seconds}, decoys={self.decoys!r}"
            )
        max_post_target_seconds = age_low - self.fault_capture_seconds + self.base_step_seconds
        post_decoys = [decoy for decoy in self.decoys if decoy.after_target]
        requested_post_target_seconds = sum(
            decoy.count * (decoy.duration_seconds + self.transition_seconds)
            for decoy in post_decoys
            if decoy.alignment_group is None
        )
        aligned_post_groups = {
            decoy.alignment_group
            for decoy in post_decoys
            if decoy.alignment_group is not None
        }
        requested_post_target_seconds += sum(
            max(
                decoy.duration_seconds + self.transition_seconds
                for decoy in post_decoys
                if decoy.alignment_group == alignment_group
            )
            for alignment_group in aligned_post_groups
        )
        if requested_post_target_seconds > max_post_target_seconds:
            raise ValueError(
                "Frozen-history decoys cannot fit after the earliest target window: "
                f"requested_seconds={requested_post_target_seconds}, available_seconds={max_post_target_seconds}, decoys={self.decoys!r}"
            )
        for decoy in self.decoys:
            if str(decoy.metric).casefold() not in canonical_metrics:
                raise ValueError(
                    "Frozen-history decoy metric must be included in required_metrics: "
                    f"decoy_id={decoy.decoy_id!r}, metric={decoy.metric!r}, required_metrics={self.required_metrics!r}"
                )
            self._validate_decoy(decoy)
        if background_workload is not None:
            if background_workload.start_phase is not BackgroundWorkloadStartPhase.BEFORE_FAULTS:
                raise ValueError(
                    "Frozen history requires background workload start_phase=BEFORE_FAULTS: "
                    f"actual={background_workload.start_phase.value!r}"
                )
            if not background_workload.profiles or background_workload.worker_count <= 0:
                raise ValueError(
                    "Frozen history requires a non-empty background workload: "
                    f"profiles={len(background_workload.profiles)}, worker_count={background_workload.worker_count}"
                )

    def _validate_metric_targets(self, canonical_metrics: tuple[str, ...]) -> None:
        if not isinstance(self.metric_targets, Mapping):
            raise TypeError(
                "Frozen-history metric_targets must be a mapping: "
                f"metric_targets={self.metric_targets!r}"
            )
        normalized: dict[str, tuple[str | None, ...]] = {}
        for raw_metric, raw_targets in self.metric_targets.items():
            metric = str(raw_metric).casefold()
            if metric not in canonical_metrics:
                raise ValueError(
                    "Frozen-history metric_targets contains a metric outside required_metrics: "
                    f"metric={raw_metric!r}, required_metrics={self.required_metrics!r}"
                )
            targets = tuple(raw_targets)
            if not targets or len(set(targets)) != len(targets):
                raise ValueError(
                    "Frozen-history metric_targets must contain unique targets: "
                    f"metric={raw_metric!r}, targets={raw_targets!r}"
                )
            if any(target is not None and (not isinstance(target, str) or not target) for target in targets):
                raise ValueError(
                    "Frozen-history metric_targets must use non-empty strings or None: "
                    f"metric={raw_metric!r}, targets={raw_targets!r}"
                )
            if metric in normalized:
                raise ValueError(
                    "Frozen-history metric_targets has duplicate keys after normalization: "
                    f"metric={raw_metric!r}"
                )
            normalized[metric] = targets
        object.__setattr__(self, "metric_targets", MappingProxyType(normalized))

    def _validate_metric_rate_windows(self, canonical_metrics: tuple[str, ...]) -> None:
        if not isinstance(self.metric_rate_windows, Mapping):
            raise TypeError(
                "Frozen-history metric_rate_windows must be a mapping: "
                f"metric_rate_windows={self.metric_rate_windows!r}"
            )
        normalized: dict[str, int] = {}
        for raw_metric, raw_window in self.metric_rate_windows.items():
            metric = str(raw_metric).casefold()
            if metric not in canonical_metrics:
                raise ValueError(
                    "Frozen-history metric_rate_windows contains a metric outside required_metrics: "
                    f"metric={raw_metric!r}, required_metrics={self.required_metrics!r}"
                )
            if metric in normalized:
                raise ValueError(
                    "Frozen-history metric_rate_windows has duplicate keys after normalization: "
                    f"metric={raw_metric!r}"
                )
            if not isinstance(raw_window, int) or isinstance(raw_window, bool) or raw_window <= 0:
                raise ValueError(
                    "Frozen-history metric_rate_windows values must be positive integers: "
                    f"metric={raw_metric!r}, window={raw_window!r}"
                )
            normalized[metric] = raw_window
        object.__setattr__(self, "metric_rate_windows", MappingProxyType(normalized))

    def _validate_decoy(self, decoy: HistoryDecoySpec) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", decoy.decoy_id):
            raise ValueError(f"Frozen-history decoy_id is invalid: decoy_id={decoy.decoy_id!r}")
        if not decoy.metric or not decoy.field:
            raise ValueError(f"Frozen-history decoy metric and field must be non-empty: decoy={decoy!r}")
        if decoy.count <= 0:
            raise ValueError(f"Frozen-history decoy count must be positive: decoy={decoy!r}")
        if decoy.duration_seconds <= 0 or decoy.duration_seconds % self.base_step_seconds:
            raise ValueError(
                f"Frozen-history decoy duration must be a positive base-step multiple: decoy={decoy!r}, "
                f"base_step_seconds={self.base_step_seconds}"
            )
        if decoy.kind is not DecoyKind.CANDIDATE_VALLEY and decoy.duration_seconds > self.normal_capture_seconds:
            # Normal-source decoys (captured_benign/metric_only) sample windows
            # from the normal capture; a decoy longer than the capture has no
            # placement range at all. Candidate valleys replay the target
            # capture instead and are bounded by fault_capture_seconds above.
            raise ValueError(
                "Frozen-history decoy duration cannot exceed normal_capture_seconds: "
                f"decoy={decoy!r}, normal_capture_seconds={self.normal_capture_seconds}"
            )
        if decoy.kind is DecoyKind.CAPTURED_BENIGN:
            if decoy.count * decoy.duration_seconds > self.normal_capture_seconds:
                raise ValueError(
                    "captured_benign count times duration cannot exceed normal_capture_seconds: "
                    f"decoy={decoy!r}, normal_capture_seconds={self.normal_capture_seconds}"
                )
            if decoy.amplitude_mad is not None or decoy.minimum_deviation_mad is None or decoy.minimum_deviation_mad <= 0:
                raise ValueError(
                    "captured_benign requires amplitude_mad=None and positive minimum_deviation_mad: "
                    f"decoy={decoy!r}"
                )
        elif decoy.kind is DecoyKind.METRIC_ONLY:
            if decoy.amplitude_mad is None or decoy.amplitude_mad <= 0 or decoy.minimum_deviation_mad is not None:
                raise ValueError(
                    "metric_only requires positive amplitude_mad and minimum_deviation_mad=None: "
                    f"decoy={decoy!r}"
                )
        elif decoy.kind is DecoyKind.CANDIDATE_VALLEY:
            if decoy.duration_seconds != self.fault_capture_seconds:
                raise ValueError(
                    "candidate_valley must match the fault capture duration exactly so it competes "
                    f"at the same depth and span: decoy={decoy!r}, fault_capture_seconds={self.fault_capture_seconds}"
                )
            if decoy.amplitude_mad is not None or decoy.minimum_deviation_mad is not None:
                raise ValueError(
                    "candidate_valley replays real capture shapes and takes no synthetic amplitude: "
                    f"decoy={decoy!r}"
                )
            if decoy.valley_profile not in {"shadow_copy", "scrambled_order", "missing_precursor"}:
                raise ValueError(
                    "candidate_valley profile is unsupported: "
                    f"decoy={decoy!r}, valley_profile={decoy.valley_profile!r}"
                )
            if decoy.after_target or decoy.alignment_group is not None:
                raise ValueError(
                    "candidate_valley competes before the target window only: "
                    f"decoy={decoy!r}"
                )
            if decoy.count != 1:
                raise ValueError(
                    "candidate_valley must declare count=1; distinct valleys are separate specs: "
                    f"decoy={decoy!r}"
                )
            if decoy.valley_profile == "missing_precursor" and not decoy.baseline_metrics:
                raise ValueError(
                    "missing_precursor valleys must name the baseline metrics that stay flat: "
                    f"decoy={decoy!r}"
                )
            if decoy.valley_profile != "missing_precursor" and decoy.baseline_metrics:
                raise ValueError(
                    "baseline_metrics only applies to missing_precursor valleys: "
                    f"decoy={decoy!r}"
                )
            if any(str(metric).casefold() not in {str(item).casefold() for item in self.required_metrics} for metric in decoy.baseline_metrics):
                raise ValueError(
                    "candidate_valley baseline_metrics must be included in required_metrics: "
                    f"decoy={decoy!r}, baseline_metrics={decoy.baseline_metrics!r}"
                )
        else:
            raise ValueError(f"Unknown frozen-history decoy kind: decoy={decoy!r}")
        if decoy.target is not None and not decoy.target:
            raise ValueError(f"Frozen-history decoy target must be non-empty when provided: decoy={decoy!r}")
        if decoy.alignment_group is not None:
            if not re.fullmatch(r"[a-z][a-z0-9_-]*", decoy.alignment_group):
                raise ValueError(f"Frozen-history decoy alignment_group is invalid: decoy={decoy!r}")
            if not decoy.after_target or decoy.count != 1:
                raise ValueError(
                    "Frozen-history alignment_group is only supported for one post-target decoy: "
                    f"decoy={decoy!r}"
                )
        elif decoy.after_target and any(
            item.alignment_group is not None for item in self.decoys if item.after_target
        ):
            raise ValueError(
                "Frozen-history post-target decoys must use one alignment group or none: "
                f"decoy={decoy!r}"
            )


def duration_before_target(target_age_seconds: int, transition_seconds: int) -> int:
    return target_age_seconds - transition_seconds


def validate_frozen_history_case(case: object) -> None:
    spec = getattr(case, "frozen_history", None)
    if spec is None:
        return
    spec.validate(getattr(case, "background_workload"))
