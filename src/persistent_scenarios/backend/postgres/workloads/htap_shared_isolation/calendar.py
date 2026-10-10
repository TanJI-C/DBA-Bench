"""Business calendar for the shared-resource HTAP instance.

The calendar is the external business input schedule: it is identical across
healthy/reference/zero/wrong paths and independent of fault
injection. Timestamps are seconds relative to scoring start.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class AnalysisSubmission:
    at_seconds: int
    tenant: str
    scan_count: int
    scan_span_lines: int
    submit_export: bool
    export_rows_per_second: int

    def __post_init__(self) -> None:
        if self.at_seconds < 0 or self.scan_count < 1 or self.scan_span_lines < 1:
            raise ValueError(
                "Invalid analysis submission: "
                f"at_seconds={self.at_seconds}, scan_count={self.scan_count}, "
                f"scan_span_lines={self.scan_span_lines}"
            )


@dataclass(frozen=True, slots=True)
class HtapBusinessCalendar:
    horizon_seconds: int
    submissions: tuple[AnalysisSubmission, ...]
    input_stop_seconds: int
    analysis_deadline_seconds: int
    export_deadline_seconds: int
    export_watermark_lag_seconds: int

    def __post_init__(self) -> None:
        if self.horizon_seconds <= 0:
            raise ValueError(f"horizon_seconds must be positive: value={self.horizon_seconds}")
        for name in ("input_stop_seconds", "analysis_deadline_seconds", "export_deadline_seconds"):
            value = getattr(self, name)
            if not 0 < value <= self.horizon_seconds:
                raise ValueError(f"{name} must be within (0, horizon]: value={value}, horizon={self.horizon_seconds}")
        if not self.submissions:
            raise ValueError("HtapBusinessCalendar requires at least one analysis submission")
        for submission in self.submissions:
            if submission.at_seconds >= self.input_stop_seconds:
                raise ValueError(
                    "Analysis submission must arrive before business input stop: "
                    f"at_seconds={submission.at_seconds}, input_stop_seconds={self.input_stop_seconds}"
                )


PRODUCTION_CALENDAR = HtapBusinessCalendar(
    horizon_seconds=4500,
    submissions=(
        AnalysisSubmission(
            at_seconds=600,
            tenant="tenant_alpha",
            scan_count=2,
            scan_span_lines=600_000,
            submit_export=True,
            export_rows_per_second=8000,
        ),
        AnalysisSubmission(
            at_seconds=2760,
            tenant="tenant_beta",
            scan_count=2,
            scan_span_lines=600_000,
            submit_export=True,
            export_rows_per_second=8000,
        ),
    ),
    input_stop_seconds=3720,
    analysis_deadline_seconds=4320,
    export_deadline_seconds=4200,
    export_watermark_lag_seconds=180,
)


class CalendarClock:
    """Resolves calendar times against the monotonic scoring origin."""

    def __init__(self, calendar: HtapBusinessCalendar, scoring_origin: float, clock):
        self.calendar = calendar
        self._scoring_origin = scoring_origin
        self._clock = clock

    def now_seconds(self) -> float:
        return self._clock.monotonic() - self._scoring_origin

    def deadline_monotonic(self, at_seconds: int) -> float:
        return self._scoring_origin + at_seconds

    def due_submissions(self) -> tuple[AnalysisSubmission, ...]:
        now = self.now_seconds()
        return tuple(item for item in self.calendar.submissions if item.at_seconds <= now)

    def export_bound_watermark_seconds(self) -> float:
        return self.now_seconds() - self.calendar.export_watermark_lag_seconds


def submission_payload(submission: AnalysisSubmission) -> Mapping[str, object]:
    return {
        "tenant": submission.tenant,
        "scan_count": submission.scan_count,
        "scan_span_lines": submission.scan_span_lines,
        "submit_export": submission.submit_export,
        "export_rows_per_second": submission.export_rows_per_second,
    }
