"""Run PG-HC-MF02 with explicit primary/restore ports and isolated resources."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import uuid
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from src.agents.agent import MockLLMAgent
from src.agents.factory import build_experiment_agent
from src.scenarios.evaluation.protocol import EMPTY_REPORT
from src.execution.backup_rpo import RpoPGEnv, RpoTopology
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig
from src.scenarios.postgres.health_check.backup_rpo_certification import (
    PgHealthCheckBackupRpoCertificationScenario,
)

SUPPORTED_REASONING_EFFORTS = frozenset({"medium", "xhigh"})


def assert_ports_available(ports: tuple[int, ...]) -> None:
    occupied = set()
    try:
        result = subprocess.run(["ss", "-ltn"], capture_output=True, text=True, timeout=10)
        for line in result.stdout.splitlines():
            for port in ports:
                if f":{port} " in line or f":{port}\n" in line:
                    occupied.add(port)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    for port in ports:
        if port in occupied:
            raise RuntimeError(f"PG-HC-MF02 port is already occupied: {port}")
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            probe.bind(("127.0.0.1", port))
        except OSError as exc:
            raise RuntimeError(f"PG-HC-MF02 port is already occupied: {port}") from exc
        finally:
            probe.close()


@contextmanager
def run_identity(case_id: str):
    previous = os.environ.get("AIOPS_RUN_ID")
    run_id = f"rpo-{case_id}-{uuid.uuid4().hex[:10]}"
    os.environ["AIOPS_RUN_ID"] = run_id
    try:
        yield run_id
    finally:
        if previous is None:
            os.environ.pop("AIOPS_RUN_ID", None)
        else:
            os.environ["AIOPS_RUN_ID"] = previous


def build_env(case, *, primary_port: int, restore_port: int, run_id: str | None = None) -> RpoPGEnv:
    if run_id is None:
        run_id = f"rpo-{case.case_id}-{uuid.uuid4().hex[:10]}"
    topology = RpoTopology.for_run(
        run_id=run_id,
        case_id=case.case_id,
        primary_port=primary_port,
        restore_port=restore_port,
    )
    return RpoPGEnv(topology=topology, image_name=case.base_image_name)


def mock_reference_report(target_window: tuple[str, str]) -> dict:
    """Reference diagnosis report for the located stall window.

    The frozen-history DP contract (time location, root cause, RPO impact) is
    satisfied by citing the located UTC window in the condition evidence; no
    structured window field or tool-level anchor exists.
    """
    start, end = target_window
    return {
        "diagnosis": {"conditions": [
            {
                "type": "incident_window",
                "factor": "archive delivery stall window",
                "entity": "archive_repository",
                "evidence": [
                    f"archive_backlog oldest_age_sec climbs from the normal baseline into its "
                    f"sustained plateau across {start}/{end}; this located window anchors the "
                    f"certification boundary",
                ],
            },
            {
                "type": "root_cause",
                "factor": "wal generation outpaced archive delivery",
                "entity": "archive_repository",
                "evidence": [
                    f"wal_generation stays above durable archive_delivery while oldest_age_sec "
                    f"keeps rising during {start}/{end}; ready WAL segments accumulated in the "
                    f"archive repository",
                    "operation events in the same window show business marker commits continuing "
                    "without matching repository delivery",
                ],
            },
            {
                "type": "impact",
                "factor": "oldest unarchived wal age exceeded the 60 second rpo promise",
                "entity": "rpo_certification",
                "evidence": [
                    f"oldest_age_sec reaches the plateau above the 60 second rpo promise during "
                    f"{start}/{end}, so the certified RPO contract was violated inside the "
                    f"located stall window",
                ],
            },
        ]},
        "outcome": {
            "changes": ["restored archive delivery capacity and ran isolated PITR"],
            "verification": ["manifest, inventory continuity, hidden marker and checksum passed"],
        },
        "summary": (
            "Frozen-history window location, cross-metric causality and the trusted isolated "
            "PITR establish the RPO certification decision."
        ),
    }


def _standard_route_command(route_records: dict) -> str:
    """Extract the standard archive route binding from frozen-history records.

    The standard delivery tier exists only inside the frozen history's
    normal-window route-config operation events; the current instance state
    never publishes it, so the reference path derives the binding from there.
    """
    records = route_records.get("records") if isinstance(route_records, dict) else None
    commands = [
        str(record["details"]["archive_command"])
        for record in (records or ())
        if isinstance(record, dict)
        and str(record.get("action", "")) == "route_config"
        and isinstance(record.get("details"), dict)
        and record["details"].get("archive_command")
    ]
    if not commands:
        raise RuntimeError(
            "RPO frozen history has no route-config record carrying the standard "
            f"archive route binding: records={len(records or ())}"
        )
    return commands[-1]


def _archive_command_setting(settings_result: dict) -> str:
    """Read the live archive_command value from a pg_settings result."""
    columns = settings_result.get("columns", []) if isinstance(settings_result, dict) else []
    if "setting" not in [str(column).casefold() for column in columns]:
        raise RuntimeError(f"pg_settings result has no setting column: {settings_result!r}")
    setting_index = [str(column).casefold() for column in columns].index("setting")
    name_index = [str(column).casefold() for column in columns].index("name")
    for row in settings_result.get("result", ()):
        if len(row) > max(setting_index, name_index) and str(row[name_index]).casefold() == "archive_command":
            return str(row[setting_index])
    raise RuntimeError(f"pg_settings result has no archive_command row: {settings_result!r}")


class FrozenHistoryRpoMockAgent(MockLLMAgent):
    """Deterministic example agent that follows the public metric/history workflow."""

    @staticmethod
    def _history_bounds(help_result: dict) -> tuple[datetime, datetime]:
        runtime = help_result.get("definition", {}).get("runtime", {})
        available_start = runtime.get("available_start")
        available_end = runtime.get("available_end")
        if not available_start or not available_end:
            raise RuntimeError("frozen-history help did not expose the frozen history range")
        return (
            datetime.strptime(available_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
            datetime.strptime(available_end, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc),
        )

    @staticmethod
    def _overview_values(result: dict, field: str) -> tuple[tuple[datetime, float], ...]:
        series = result.get("series", {}) if isinstance(result, dict) else {}
        if not series:
            raise RuntimeError(f"metric overview did not contain a series: field={field!r}, result={result!r}")
        values = next(iter(series.values()))
        timestamp_spec = values.get("timestamps", ())
        samples = values.get(field, ())
        if isinstance(timestamp_spec, dict):
            start_text = timestamp_spec.get("start")
            step_seconds = int(timestamp_spec.get("step_seconds", 0) or 0)
            count = int(timestamp_spec.get("count", 0) or 0)
            if not start_text or step_seconds <= 0 or count <= 0:
                raise RuntimeError(
                    f"metric overview timestamp grid is incomplete: field={field!r}, result={result!r}"
                )
            start = datetime.strptime(start_text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            timestamps = [start + timedelta(seconds=step_seconds * index) for index in range(count)]
        else:
            timestamps = [
                datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                for timestamp in timestamp_spec
            ]
        if len(timestamps) != len(samples) or not timestamps:
            raise RuntimeError(f"metric overview field is incomplete: field={field!r}, result={result!r}")
        return tuple(
            (timestamp, float(value))
            for timestamp, value in zip(timestamps, samples)
        )

    @classmethod
    def _overview_points(
        cls,
        result: dict,
        field: str,
    ) -> dict[datetime, float]:
        return dict(cls._overview_values(result, field))

    @staticmethod
    def _median(values: tuple[float, ...] | list[float]) -> float:
        ordered = sorted(values)
        return ordered[len(ordered) // 2]

    @classmethod
    def _overview_candidates(cls, backlog_result: dict) -> tuple[datetime, ...]:
        """Funnel stage 1: coarse overview candidates.

        Candidate valleys replay the incident window's own depth and duration,
        so every overview point where the archive backlog climbs above the
        normal regime is only a candidate. Records and ordered causality —
        never statistics — separate the true stall window from them.
        """
        backlog = cls._overview_points(backlog_result, "oldest_age_sec")
        if not backlog:
            raise RuntimeError("RPO overview is missing backlog samples")
        stamps = sorted(backlog)
        if len(stamps) < 4:
            raise RuntimeError("RPO overview contains too few aligned samples")
        median_age = cls._median([backlog[stamp] for stamp in stamps])
        if median_age <= 0:
            raise RuntimeError(
                f"RPO overview shows no usable normal backlog regime: median_age={median_age}"
            )
        candidates = tuple(stamp for stamp in stamps if backlog[stamp] > 1.5 * median_age)
        if not candidates:
            raise RuntimeError(
                "RPO overview shows no archive backlog peak above the normal regime; the "
                f"certification reference path cannot name a candidate window: median={median_age}"
            )
        return candidates

    @classmethod
    def _bounded_window(
        cls,
        history_help: dict,
        center: datetime,
        *,
        before_seconds: int = 180,
        after_seconds: int = 0,
    ) -> tuple[str, str]:
        available_start, available_end = cls._history_bounds(history_help)
        start = max(available_start, center - timedelta(seconds=before_seconds))
        end = min(available_end, center + timedelta(seconds=after_seconds))
        if end - start > timedelta(seconds=900):
            end = start + timedelta(seconds=900)
        if end - start < timedelta(seconds=60):
            raise RuntimeError(
                "RPO candidate window collapsed inside the frozen history bounds: "
                f"center={center.isoformat()}, start={start.isoformat()}, end={end.isoformat()}"
            )
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _window_series(result: dict, field: str) -> tuple[float, ...]:
        series = result.get("series", {}) if isinstance(result, dict) else {}
        if not series:
            raise RuntimeError(f"candidate window did not contain a series: field={field!r}, result={result!r}")
        values = next(iter(series.values()))
        samples = values.get(field, ())
        if not samples:
            raise RuntimeError(f"candidate window field is incomplete: field={field!r}, result={result!r}")
        return tuple(float(value) for value in samples)

    @classmethod
    def _candidate_is_the_stall(
        cls,
        backlog_result: dict,
        wal_result: dict,
        events_result: dict,
    ) -> bool:
        """Formal exclusion rules: record evidence plus ordered causality.

        Candidate valleys replay the incident window's metric depth, duration,
        and signature, so statistics cannot decide. The true window must carry
        the complete evidence chain: business marker commits continuing through
        the stall (the RPO-impact story the valleys cannot replay), a real
        archive failure-and-retry sequence, and the ordered causality that WAL
        generation kept flowing while the backlog climbed and stayed above the
        approved RPO horizon under a still collapsed delivery.
        """
        backlog = cls._window_series(backlog_result, "oldest_age_sec")
        wal = cls._window_series(wal_result, "bytes_per_sec")
        records = events_result.get("records", ()) if isinstance(events_result, dict) else ()
        marker_commits = [record for record in records if record.get("event_type") == "marker_commit"]
        archive_failures = [
            record for record in records
            if record.get("event_type") == "archive_attempt" and record.get("status") == "failed"
        ]
        archive_successes = [
            record for record in records
            if record.get("event_type") == "archive_attempt" and record.get("status") == "success"
        ]
        if len(marker_commits) < 2:
            # Business continuity is the RPO story: markers must have kept
            # committing while delivery was stalled. The valleys replay none.
            return False
        if not archive_failures or not archive_successes:
            # The incident carries a genuine retry/error sequence.
            return False
        if cls._median(wal) <= 0:
            # Generation stopped, so this cannot be a throughput-gap stall
            # with continued business writes.
            return False
        if max(wal) <= 1.5 * cls._median(wal):
            # The generating burst is missing: a flat normal-regime WAL channel
            # cannot have produced a delivery gap (missing-precursor valley).
            return False
        if backlog[-1] < backlog[0] or backlog[-1] - min(backlog) < 60:
            # The backlog must climb and stay elevated; a fall under a still
            # collapsed delivery is causally impossible for a sustained stall.
            return False
        return True

    @staticmethod
    def _healthy_route_tier(events_result: dict) -> str:
        """Derive the publication route tier from the frozen pre-incident records."""
        routes = []
        for record in events_result.get("records", ()):
            if record.get("event_type") != "archive_attempt" or record.get("status") != "success":
                continue
            route = str((record.get("details") or {}).get("route", "")).strip()
            if route:
                routes.append(route)
        if not routes:
            raise RuntimeError(
                "frozen pre-incident records did not expose a healthy archive route tier: "
                f"records={len(events_result.get('records', ()) or ())}"
            )
        return Counter(routes).most_common(1)[0][0]

    @staticmethod
    def _show_archive_command(result: dict) -> str:
        rows = result.get("result") or []
        value = rows[0][0] if rows and rows[0] else None
        if not value:
            raise RuntimeError(f"archive_command catalog query returned no value: result={result!r}")
        return str(value)

    @staticmethod
    def _publication_archive_command(current_command: str, healthy_route: str) -> str:
        if "--route=emergency" not in current_command:
            raise RuntimeError(
                "the current archive_command does not expose the emergency route residual: "
                f"current_command={current_command!r}"
            )
        return current_command.replace("--route=emergency", f"--route={healthy_route}")

    @classmethod
    def _candidate_history_window(
        cls,
        history_help: dict,
        backlog_result: dict,
    ) -> tuple[str, str]:
        available_start, available_end = cls._history_bounds(history_help)
        backlog = dict(cls._overview_values(backlog_result, "oldest_age_sec"))
        common = sorted(backlog)
        if not common:
            raise RuntimeError("RPO backlog overview is empty")
        # Anchor the certification window on the archive-backlog rise: walk back
        # from the peak age through the sustained non-decreasing climb while the
        # values stay above half of the peak.  This locates the onset of the
        # delivery failure instead of an arbitrary plateau tick, stays
        # independent of absolute backlog scales across runs, and does not slide
        # across an ascending-but-healthy baseline segment.
        peak = max(backlog[timestamp] for timestamp in common)
        if peak <= 0:
            raise RuntimeError("RPO overview shows no archive backlog to investigate")
        peak_time = next(timestamp for timestamp in common if backlog[timestamp] == peak)
        rise_threshold = peak / 2.0
        onset_index = common.index(peak_time)
        while (
            onset_index > 0
            and rise_threshold <= backlog[common[onset_index - 1]] <= backlog[common[onset_index]]
        ):
            onset_index -= 1
        # The declared bounded-window budget is 1200 seconds; keep the evidence
        # window inside it while still covering the rise from onset to peak.
        start = max(available_start, common[onset_index] - timedelta(minutes=5))
        end = min(available_end, peak_time + timedelta(minutes=5), start + timedelta(minutes=15))
        if end <= start:
            raise RuntimeError(
                "RPO backlog onset window is empty: "
                f"available_start={available_start}, available_end={available_end}, "
                f"onset={common[onset_index]}, peak={peak_time}"
            )
        # Keep a bounded recovery comparison window after the target.  When
        # the peak lands on the newest sample, clamping the target to
        # available_end leaves no room for that required post-target window.
        post_target_room = available_end - end
        if post_target_room < timedelta(minutes=1):
            shift = timedelta(minutes=1) - post_target_room
            end = min(available_end - timedelta(minutes=1), end - shift)
            start = max(available_start, end - timedelta(minutes=10))
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def _comparison_windows(
        cls,
        history_help: dict,
        target_start: str,
        target_end: str,
    ) -> tuple[tuple[str, str], ...]:
        available_start, available_end = cls._history_bounds(history_help)
        target_start_dt = datetime.strptime(target_start, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        target_end_dt = datetime.strptime(target_end, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        # The frozen timeline ends at the target window's end (the captured
        # fault window is the certification moment), so every comparison
        # window must fit at or before the target end.
        raw_windows = (
            (target_start_dt, target_end_dt),
            (target_start_dt - timedelta(minutes=2), target_start_dt),
            (target_start_dt, target_start_dt + timedelta(minutes=1)),
            (target_start_dt - timedelta(minutes=3), target_start_dt - timedelta(minutes=2)),
        )
        windows: list[tuple[str, str]] = []
        for start, end in raw_windows:
            bounded_start = max(available_start, start)
            bounded_end = min(available_end, end)
            if bounded_end - bounded_start < timedelta(seconds=40):
                continue
            window = (
                bounded_start.strftime("%Y-%m-%d %H:%M:%S"),
                bounded_end.strftime("%Y-%m-%d %H:%M:%S"),
            )
            if window not in windows:
                windows.append(window)
        if len(windows) != 4:
            raise RuntimeError(f"RPO history did not provide one target and three comparison windows: {windows!r}")
        return tuple(windows)

    def _observe(self, thinking: str, api: str, args: dict) -> dict:
        result = self.execute(api, args, thinking=thinking)
        self._conversation_history.append({
            "role": "user",
            "content": f"[Tool result] {api}: {json.dumps(result, ensure_ascii=False, default=str)}",
        })
        return result

    def _solve_throughput_gap(self) -> dict:
        history_help = self._observe(
            "Read the frozen history range, overview semantics, and query budget before investigating.",
            "help",
            {"tool_name": "query_metrics"},
        )
        overviews = {}
        for metric in ("wal_generation", "archive_delivery", "archive_backlog"):
            overviews[metric] = self._observe(
                "Read the coarse overview across the whole frozen history to shortlist candidate windows.",
                "query_metrics",
                {"metric_type": metric},
            )
        candidates = self._overview_candidates(overviews["archive_backlog"])
        accepted = None
        for candidate in candidates:
            candidate_start, candidate_end = self._bounded_window(history_help, candidate)
            backlog_window = self._observe(
                "Raise this overview candidate onto the base grid and read the backlog trajectory.",
                "query_metrics",
                {
                    "metric_type": "archive_backlog",
                    "target": None,
                    "start_timestamp": candidate_start,
                    "end_timestamp": candidate_end,
                    "step_seconds": 2,
                },
            )
            self._observe(
                "Confirm the delivery collapse across the same candidate window.",
                "query_metrics",
                {
                    "metric_type": "archive_delivery",
                    "target": None,
                    "start_timestamp": candidate_start,
                    "end_timestamp": candidate_end,
                    "step_seconds": 2,
                },
            )
            wal_window = self._observe(
                "Check the WAL generation that must precede and span a sustained delivery collapse.",
                "query_metrics",
                {
                    "metric_type": "wal_generation",
                    "target": None,
                    "start_timestamp": candidate_start,
                    "end_timestamp": candidate_end,
                    "step_seconds": 2,
                },
            )
            events = self._observe(
                "Read the candidate window's operation events: marker continuity and the retry/error sequence separate the incident from same-shape valleys.",
                "read_log",
                {
                    "log_type": "operation_event",
                    "start_timestamp": candidate_start,
                    "end_timestamp": candidate_end,
                    "target": "postgres",
                    "filters": {},
                    "lines": 100,
                },
            )
            if self._candidate_is_the_stall(backlog_window, wal_window, events):
                accepted = (candidate_start, candidate_end, events)
        if accepted is None:
            raise RuntimeError(
                "RPO candidate evaluation did not isolate one stall window: "
                f"accepted=0, candidates={len(candidates)}"
            )
        start_timestamp, end_timestamp, accepted_events = accepted
        accepted_start_dt = datetime.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        # The pre-incident strip sits between the candidate-valley segment and
        # the accepted window's onset. Bounding the read inside that strip keeps
        # valley-replayed records and incident attempts out of the healthy-tier
        # derivation.
        strip_end = (accepted_start_dt - timedelta(seconds=2)).strftime("%Y-%m-%d %H:%M:%S")
        strip_start = (accepted_start_dt - timedelta(seconds=116)).strftime("%Y-%m-%d %H:%M:%S")
        strip_events = self._observe(
            "Read the frozen pre-incident records to derive the healthy archive route tier the certification must restore.",
            "read_log",
            {
                "log_type": "operation_event",
                "start_timestamp": strip_start,
                "end_timestamp": strip_end,
                "target": "postgres",
                "filters": {},
                "lines": 100,
            },
        )
        healthy_route = self._healthy_route_tier(strip_events)
        self._observe(
            "Check the current repository status without treating a caught-up backlog as historical proof.",
            "manage_instance",
            {"action": "archive_status", "target": "archive_repository"},
        )
        recovery = self._observe(
            "Restore archive delivery, then verify the repository converged; the certification capacity replay must meet the publication envelope.",
            "manage_instance",
            {"action": "recover_archive", "target": "archive_repository"},
        )
        if recovery.get("status") != "success":
            current_command = self._show_archive_command(self._observe(
                "The capacity replay missed the publication envelope: inspect the live archive route configuration.",
                "execute_sql",
                {"sql_query": "SELECT setting FROM pg_settings WHERE name = 'archive_command';"},
            ))
            standard_command = self._publication_archive_command(current_command, healthy_route)
            self._observe(
                "Re-point the archive route at the healthy tier derived from the frozen pre-incident records.",
                "execute_sql",
                {"sql_query": f"ALTER SYSTEM SET archive_command = '{standard_command}';"},
            )
            self._observe(
                "Reload the instance configuration so the restored route tier takes effect.",
                "execute_sql",
                {"sql_query": "SELECT pg_reload_conf();"},
            )
            recovery = self._observe(
                "Recover the archive again so the capacity replay verifies the restored publication tier.",
                "manage_instance",
                {"action": "recover_archive", "target": "archive_repository"},
            )
        for _ in range(2):
            if recovery.get("status") == "success":
                break
            self._observe(
                "The previous archive recovery did not converge; check the current repository state before retrying.",
                "manage_instance",
                {"action": "archive_status", "target": "archive_repository"},
            )
            recovery = self._observe(
                "Retry the bounded archive recovery so the stalled segments become durable before the restore.",
                "manage_instance",
                {"action": "recover_archive", "target": "archive_repository"},
            )
        self._observe(
            "Validate the physical backup manifest and WAL inventory before attempting the business restore.",
            "manage_instance",
            {"action": "validate_backup", "target": "backup_repository"},
        )
        self._observe(
            "Run PITR in the isolated restore resource at the evaluator-selected business marker.",
            "manage_instance",
            {"action": "pitr_restore", "target": "evaluator_selected"},
        )
        certification_report = json.loads(json.dumps(EMPTY_REPORT))
        certification_report["diagnosis"]["conditions"] = [
            {
                "type": "finding",
                "factor": "archive delivery stall",
                "entity": "archive_repository",
                "evidence": [
                    f"archive_backlog oldest_age_sec climbs above the normal regime while "
                    f"durable archive_delivery collapses from {start_timestamp} to {end_timestamp} "
                    f"in the frozen history, marking the archive delivery stall window",
                ],
            },
            {
                "type": "finding",
                "factor": "archive delivery throughput fell behind wal generation",
                "entity": "archive_repository",
                "evidence": [
                    f"wal_generation kept outrunning durable archive_delivery from "
                    f"{start_timestamp} to {end_timestamp} because the archive route was "
                    f"downgraded to the emergency transmission tier and the archive delay "
                    f"exceeded archive timeout, so wal segments queued undelivered",
                ],
            },
            {
                "type": "finding",
                "factor": "recovery point lag exceeded the approved 60 second rpo",
                "entity": "archive_repository",
                "evidence": [
                    f"the undelivered backlog from {start_timestamp} to {end_timestamp} "
                    f"kept the recoverable point more than 60 seconds behind the present, "
                    f"an rpo violation risk the certification must refuse to sign off",
                ],
            },
        ]
        certification_report["outcome"]["changes"] = [
            "restored the healthy archive route tier and archive delivery capacity, then ran isolated PITR",
        ]
        certification_report["outcome"]["verification"] = [
            "capacity replay met the publication envelope; manifest, inventory continuity, hidden marker and checksum passed",
        ]
        submission = {"report": certification_report}
        output = json.dumps({
            "thinking": "Submit the structured certification after metric, operation-event, and PITR evidence.",
            "action": {"api": "submit", "args": {"report": certification_report}},
        }, ensure_ascii=False)
        self._last_llm_output = output
        self._conversation_history.append({"role": "assistant", "content": output})
        self.record_action(output, {"api": "submit", "args": {"report": certification_report}})
        return submission

    def solve(self) -> dict:
        if getattr(self, "rpo_case_id", "throughput_gap") == "throughput_gap_simple":
            return self._solve_throughput_gap_simple()
        return self._solve_throughput_gap()

    def _solve_throughput_gap_simple(self) -> dict:
        self._observe(
            "Read the bound metric catalog before investigating the certification window.",
            "help",
            {"tool_name": "query_metrics"},
        )
        history_help = self._observe(
            "Read the frozen history range and query budget before selecting an aligned window.",
            "help",
            {"tool_name": "query_metrics"},
        )
        overviews = {}
        for metric in ("wal_generation", "archive_delivery", "archive_backlog"):
            overviews[metric] = self._observe(
                "Start with a bounded overview and compare generation, durable delivery, and archive age before selecting a window.",
                "query_metrics",
                {"metric_type": metric, "limit": 100},
            )
        # The stall signature lives only inside its own window in the frozen
        # history, so the coarse tail view cannot be relied on to show it.
        # Sweep the whole visible range with one bounded 150-second-step scan
        # (finer than the longest possible stall) to locate the backlog rise
        # before drilling in.
        available_start, available_end = self._history_bounds(history_help)
        sweep = self._observe(
            "Sweep the frozen history with one bounded full-range scan at 150-second resolution to find the archive-backlog rise.",
            "query_metrics",
            {
                "metric_type": "archive_backlog",
                "start_timestamp": available_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_timestamp": available_end.strftime("%Y-%m-%d %H:%M:%S"),
                "step_seconds": 150,
            },
        )
        start_timestamp, end_timestamp = self._candidate_history_window(
            history_help,
            sweep,
        )
        windows = self._comparison_windows(history_help, start_timestamp, end_timestamp)
        target_window = windows[0]
        for metric in (
            "wal_generation",
            "archive_delivery",
            "archive_backlog",
            "business_commits",
            "oltp_service",
            "backup_progress",
        ):
            self._observe(
                "Compare the historical throughput metric against the normal window and exclude benign burst or checksum I/O windows.",
                "query_metrics",
                {
                    "metric_type": metric,
                    "target": None,
                    "start_timestamp": target_window[0],
                    "end_timestamp": target_window[1],
                    "step_seconds": 2,
                },
            )
        for comparison_start, comparison_end in windows[1:]:
            self._observe(
                "Compare this bounded historical window with the candidate and exclude windows without the same archive-backlog propagation.",
                "query_metrics",
                {
                    "metric_type": "wal_generation",
                    "target": None,
                    "start_timestamp": comparison_start,
                    "end_timestamp": comparison_end,
                    "step_seconds": 20,
                },
            )
        self._observe(
            "Correlate archive attempts, marker commits, and repository sync events across the candidate and comparison windows before deciding whether the RPO boundary is trusted.",
            "read_log",
            {
                "log_type": "operation_event",
                "start_timestamp": min(window[0] for window in windows),
                "end_timestamp": max(window[1] for window in windows),
                "target": "postgres",
                "filters": {},
                "lines": 100,
            },
        )
        self._observe(
            "Check the current repository status without treating a caught-up backlog as historical proof.",
            "manage_instance",
            {"action": "archive_status", "target": "archive_repository"},
        )
        # The capacity replay is accepted at the standard delivery tier. Run it
        # once first: with the incident close-out route still bound to the
        # emergency transport tier the replay fails, and that physical failure
        # is the attribution signal before retrying.
        self._observe(
            "Run the archive capacity replay before certifying; a throttled delivery tier must fail this acceptance.",
            "manage_instance",
            {"action": "recover_archive", "target": "archive_repository"},
        )
        # Attribute the replay failure: derive the standard route binding from
        # the frozen history's route-config records. Those records are
        # published only in the pre-incident strip — the normal blocks within
        # 480s before the located target window — so this read physically
        # depends on having located the incident neighborhood first; a window
        # disjoint from the strip returns zero route-config records. The
        # bounded read below (900s <= the public per-query budget) covers the
        # strip with margin.
        route_window_start = max(
            available_start,
            datetime.strptime(target_window[0], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            - timedelta(seconds=900),
        )
        route_records = self._observe(
            "Read the pre-incident strip right before the located stall window to recover the standard archive route binding.",
            "read_log",
            {
                "log_type": "operation_event",
                "start_timestamp": route_window_start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_timestamp": target_window[0],
                "target": "postgres",
                "filters": {"event_type": "repository_sync", "action": "route_config"},
                "lines": 20,
            },
        )
        standard_command = _standard_route_command(route_records)
        current_settings = self._observe(
            "Inspect the live archive route configuration before restoring the standard tier.",
            "execute_sql",
            {"sql_query": "SELECT name, setting, source FROM pg_settings WHERE name = 'archive_command'"},
        )
        current_command = _archive_command_setting(current_settings)
        if current_command != standard_command:
            self._observe(
                "Rebind the archive route to the standard delivery tier derived from the frozen history.",
                "execute_sql",
                {"sql_query": f"ALTER SYSTEM SET archive_command = '{standard_command}'"},
            )
            self._observe(
                "Reload the instance configuration so the archiver picks up the standard route.",
                "execute_sql",
                {"sql_query": "SELECT pg_reload_conf()"},
            )
        # The first replay under the restored tier can still fail once: the
        # stale emergency-bound segment from the failed attempt still occupies
        # the serial archiver (~90s pacing), delaying the post-restore canary
        # beyond the acceptance window. The retry passes once that queue is
        # drained — under the residual emergency tier every retry keeps
        # failing, so the queue drain does not mask the attribution gate.
        self._observe(
            "Rerun the archive capacity replay under the restored standard delivery tier.",
            "manage_instance",
            {"action": "recover_archive", "target": "archive_repository"},
        )
        self._observe(
            "Rerun the archive capacity replay again after the serial archiver drains the stale emergency segment.",
            "manage_instance",
            {"action": "recover_archive", "target": "archive_repository"},
        )
        self._observe(
            "Validate the physical backup manifest and WAL inventory before attempting the business restore.",
            "manage_instance",
            {"action": "validate_backup", "target": "backup_repository"},
        )
        self._observe(
            "Run PITR in the isolated restore resource at the evaluator-selected business marker.",
            "manage_instance",
            {"action": "pitr_restore", "target": "evaluator_selected"},
        )
        report = mock_reference_report(windows[0])
        submission = {"report": report}
        output = json.dumps({
            "thinking": "Submit the structured certification after metric, operation-event, and PITR evidence.",
            "action": {"api": "submit", "args": {"report": report}},
        }, ensure_ascii=False)
        self._last_llm_output = output
        self._conversation_history.append({"role": "assistant", "content": output})
        self.record_action(output, {"api": "submit", "args": {"report": report}})
        return submission


ZERO_RESPONSES = [
    {
        "thinking": "Attempt an unsafe in-place restore and then submit without verifying the chain.",
        "action": {"api": "manage_instance", "args": {"action": "pitr_restore", "target": "primary"}},
    },
    {"thinking": "Submit without a valid certification.", "action": {"api": "submit", "args": {"report": EMPTY_REPORT}}},
]


def run_case(
    *,
    mode: str,
    case_id: str,
    primary_port: int,
    restore_port: int,
    model: str | None = None,
    reasoning_effort: str | None = None,
    config_path: str = "config/llm_config.json",
    max_turns: int = 20,
    fault_snapshot_mode: str = "off",
    seed: int | None = None,
    run_config: OrchestratorRunConfig | None = None,
) -> dict:
    assert_ports_available((primary_port, restore_port))
    scenario = PgHealthCheckBackupRpoCertificationScenario()
    case = scenario.get_case(case_id)
    with run_identity(case_id) as run_id:
        env = build_env(case, primary_port=primary_port, restore_port=restore_port, run_id=run_id)
        if mode == "mock":
            agent = FrozenHistoryRpoMockAgent(
                url="mock",
                api_key="mock",
                system_prompt="You are a DBA agent.",
                use_native_tools=False,
            )
            agent.rpo_case_id = case_id
        elif mode == "zero":
            agent = MockLLMAgent(url="mock", api_key="mock", system_prompt="You are a DBA agent.", use_native_tools=False)
            agent.set_mock_responses(ZERO_RESPONSES)
        elif mode == "llm":
            if (reasoning_effort or "").casefold() not in SUPPORTED_REASONING_EFFORTS:
                raise ValueError(
                    "This HC2 entrypoint only permits reasoning_effort in "
                    f"{sorted(SUPPORTED_REASONING_EFFORTS)!r}; "
                    f"got {reasoning_effort!r}"
                )
            agent = build_experiment_agent(
                model=model,
                config_path=config_path,
                use_native_tools=True,
                reasoning_effort=reasoning_effort if os.environ.get("AIOPS_AGENT_MODE") in {"llm", "v-expel"} else None,
            )
        else:
            raise ValueError(f"unsupported mode: {mode}")
        effective_run_config = run_config or OrchestratorRunConfig(
            fault_snapshot_mode=fault_snapshot_mode,
            history_seed=seed,
        )
        if run_config is not None and seed is not None and run_config.history_seed is None:
            effective_run_config = replace(run_config, history_seed=seed)
        orchestrator = Orchestrator(
            env=env,
            scenario=scenario,
            case=case,
            agent=agent,
            max_turns=min(max_turns, 30),
            run_config=effective_run_config,
        )
        result = orchestrator.run()
    print(
        f"[Evaluation:{mode}] case={case_id} "
        f"DP={result['DiagnosisPass']} OP={result['OutcomePass']} SP={result['SafePass']}"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PG-HC-MF02 backup/RPO certification.")
    parser.add_argument("--mode", choices=("mock", "zero", "llm"), default="mock")
    parser.add_argument("--case", choices=("throughput_gap", "throughput_gap_simple"), required=True)
    parser.add_argument("--primary-port", type=int, default=15811)
    parser.add_argument("--restore-port", type=int, default=15812)
    parser.add_argument("--model", required=True, help="LLM model name")
    parser.add_argument("--reasoning-effort", default=None)
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=20)
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    result = run_case(
        mode=args.mode,
        case_id=args.case,
        primary_port=args.primary_port,
        restore_port=args.restore_port,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        config_path=args.config_path,
        max_turns=args.max_turns,
        fault_snapshot_mode=args.fault_snapshot_mode,
        seed=args.seed,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
