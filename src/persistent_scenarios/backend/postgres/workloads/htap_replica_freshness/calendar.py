"""Business calendar for pg_htap_replica_freshness.

Report submissions are business inputs and identical across the three paths;
freshness is a per-report contract evaluated against the external watermark
ledger. Times are seconds relative to scoring start.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReportSubmission:
    at_seconds: int
    report_kind: str
    freshness_budget_seconds: int
    deadline_seconds: int

    def __post_init__(self) -> None:
        if self.at_seconds < 0 or self.freshness_budget_seconds <= 0:
            raise ValueError(
                "Invalid report submission: "
                f"at_seconds={self.at_seconds}, freshness_budget_seconds={self.freshness_budget_seconds}"
            )
        if self.deadline_seconds <= self.at_seconds:
            raise ValueError(
                "Report deadline must follow submission: "
                f"report_kind={self.report_kind!r}, deadline={self.deadline_seconds}, submit={self.at_seconds}"
            )


@dataclass(frozen=True, slots=True)
class FreshnessBusinessCalendar:
    horizon_seconds: int
    submissions: tuple[ReportSubmission, ...]
    input_stop_seconds: int
    critical_window_start_seconds: int

    def __post_init__(self) -> None:
        if not self.submissions:
            raise ValueError("FreshnessBusinessCalendar requires report submissions")
        if not 0 < self.input_stop_seconds <= self.horizon_seconds:
            raise ValueError(
                f"input_stop_seconds must be within (0, horizon]: value={self.input_stop_seconds}, "
                f"horizon={self.horizon_seconds}"
            )
        for submission in self.submissions:
            if submission.at_seconds >= self.input_stop_seconds:
                raise ValueError(
                    "Report submission must arrive before business input stop: "
                    f"report_kind={submission.report_kind!r}, at_seconds={submission.at_seconds}"
                )

    def routine_submissions(self) -> tuple[ReportSubmission, ...]:
        return tuple(item for item in self.submissions if item.at_seconds < self.critical_window_start_seconds)

    def critical_submissions(self) -> tuple[ReportSubmission, ...]:
        return tuple(item for item in self.submissions if item.at_seconds >= self.critical_window_start_seconds)

    def compressed(self, time_scale: float) -> "FreshnessBusinessCalendar":
        """Wall-clock calendar for an engine run on a compressed timeline.

        The engine compresses wall = scenario / time_scale; report submissions
        must arrive on that same wall clock, otherwise critical reports never
        land inside the compressed horizon. Mirrors the instance three-path
        calibration's ``compressed_calendar`` (same truncation and floors) so
        the engine path drives the calibrated business shape. ``time_scale <= 1``
        is the production timeline itself.
        """
        if time_scale <= 1:
            return self
        ratio = 1.0 / time_scale

        def scaled(value: int) -> int:
            return max(1, int(value * ratio))

        routine_budget = max(20, int(120 * ratio))
        critical_budget = max(15, int(60 * ratio))
        step = max(15, int(180 * ratio))
        submissions: list[ReportSubmission] = []
        at = scaled(120)
        while at < scaled(2400):
            submissions.append(
                ReportSubmission(
                    at_seconds=at,
                    report_kind=f"routine_{at:04d}",
                    freshness_budget_seconds=routine_budget,
                    deadline_seconds=at + max(20, int(150 * ratio)),
                )
            )
            at += step
        first_critical = scaled(2520)
        for offset, kind in enumerate(("critical_exec", "critical_finance", "critical_supply", "critical_growth", "critical_final")):
            submit = first_critical + offset * step
            submissions.append(
                ReportSubmission(
                    at_seconds=submit,
                    report_kind=kind,
                    freshness_budget_seconds=critical_budget,
                    deadline_seconds=submit + max(30, int(780 * ratio)),
                )
            )
        return FreshnessBusinessCalendar(
            horizon_seconds=scaled(self.horizon_seconds),
            submissions=tuple(submissions),
            input_stop_seconds=scaled(self.input_stop_seconds),
            critical_window_start_seconds=scaled(self.critical_window_start_seconds),
        )


def _routine_chain(horizon: int) -> tuple[ReportSubmission, ...]:
    submissions = []
    at = 120
    while at < 2400:
        submissions.append(
            ReportSubmission(
                at_seconds=at,
                report_kind=f"routine_{at // 60:02d}",
                freshness_budget_seconds=120,
                deadline_seconds=at + 150,
            )
        )
        at += 180
    return tuple(submissions)


PRODUCTION_CALENDAR = FreshnessBusinessCalendar(
    horizon_seconds=5400,
    submissions=(
        *_routine_chain(5400),
        ReportSubmission(at_seconds=2520, report_kind="critical_exec", freshness_budget_seconds=60, deadline_seconds=3300),
        ReportSubmission(at_seconds=2700, report_kind="critical_finance", freshness_budget_seconds=60, deadline_seconds=3600),
        ReportSubmission(at_seconds=2880, report_kind="critical_supply", freshness_budget_seconds=60, deadline_seconds=3900),
        ReportSubmission(at_seconds=3060, report_kind="critical_growth", freshness_budget_seconds=60, deadline_seconds=4200),
        ReportSubmission(at_seconds=3240, report_kind="critical_final", freshness_budget_seconds=60, deadline_seconds=4320),
    ),
    input_stop_seconds=4560,
    critical_window_start_seconds=2520,
)
