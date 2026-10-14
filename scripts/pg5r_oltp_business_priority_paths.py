"""Three-path calibration script for pg_continuous_ops_business_priority.

Runs the contract section 5 timeline for healthy / reference (scripted
oracle) / zero-action / wrong-action paths over the oltp_core driver and the
business-priority capability bindings, under the batch resource lease. The
phase-3 gate is the dataset image: everything below executes once
`aiopsbench-pg5-oltp-business:latest` exists.

    conda run -n aiops python scripts/pg5r_oltp_business_priority_paths.py \
        --path zero --image aiopsbench-pg5-oltp-business:latest --run-id pg5rbp-zero-1
"""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path

import psycopg2

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pg5r_oltp_path_common import (  # noqa: E402
    CONTAINER_PREFIX,
    ScheduledAction,
    ScheduledEvent,
    acquire_port,
    assert_lease_capacity,
    budget_assessment,
    cleanup_lease,
    collect_guc_state,
    configure_port_range,
    deploy_container,
    job_terminal_records,
    live_leased_containers,
    parse_common_args,
    require_path_schedule,
    run_timeline,
    wait_until_ready,
    write_report,
    zero_action_budget_note,
)

from src.persistent_scenarios.backend.postgres.capabilities.business_priority import (  # noqa: E402
    CAPABILITY_REGISTRY,
)
from src.persistent_scenarios.backend.postgres.workloads.business_priority.archive import (  # noqa: E402
    verify_archive_delivery,
)
from src.persistent_scenarios.backend.postgres.workloads.business_priority.config import (  # noqa: E402
    ARCHIVE_DEFERRAL_BUDGET_SECONDS,
    ARCHIVE_JOB_ID,
    ARCHIVE_RATE_CEILING_ROWS_PER_SECOND,
    ARCHIVE_SEED_BATCH_ROWS,
    ARCHIVE_SEED_RATE_ROWS_PER_SECOND,
    HISTORY_CUTOFF_CREATED_AT,
    DRIVER_CONFIG,
    PEAK_ARCHIVE_RATE_CAP_ROWS_PER_SECOND,
    PEAK_WINDOW_END_SECONDS,
    PEAK_WINDOW_START_SECONDS,
    TRADE_TIERS,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.capability import (  # noqa: E402
    CapabilityContext,
    EventOccurrence,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ledger import (  # noqa: E402
    good_fraction,
    load_order_book_snapshot,
    verify_conservation,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.ports import (  # noqa: E402
    EvidenceLedgerFile,
    TcpConnectionSource,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.runtime import (  # noqa: E402
    DriverConfig,
    OltpWorkloadDriver,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.schema import (  # noqa: E402
    generate_inventory_rows,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import run_verifier  # noqa: E402
from src.persistent_scenarios.model.loader import load_persistent_scenario  # noqa: E402
from src.persistent_scenarios.runtime.clock import RealClock  # noqa: E402


def _deliverable_deadline(spec, deliverable_id: str) -> float:
    for service in spec.services:
        for deliverable in getattr(service, "deliverables", ()):
            if deliverable.deliverable_id == deliverable_id:
                return float(deliverable.deadline_seconds)
    raise RuntimeError(
        f"No deliverable contract found for the requested deliverable: deliverable_id={deliverable_id!r}"
    )

SPEC_PATH = Path("src/persistent_scenarios/postgres/pg_continuous_ops_business_priority.yaml")

_BASE_EVENTS = (
    ScheduledEvent(480.0, "promo_ramp_up", "promo_tier", {"tier": "promo"}),
    ScheduledEvent(1200.0, "maintenance_window_start", "scheduled_maintenance",
                   {"task_id": "orders-archive-ledger-rebuild"}),
    ScheduledEvent(1440.0, "archive_job_start", "archive_job", {"job_id": ARCHIVE_JOB_ID}),
    ScheduledEvent(2640.0, "promo_peak_2", "promo_tier", {"tier": "peak"}),
    ScheduledEvent(3000.0, "promo_wind_down", "promo_tier", {"tier": "promo"}),
)

_FAULT_EVENTS = (
    ScheduledEvent(720.0, "tx_leak_1", "worker_tx_leak", {"sku": "PROMO-SKU-2", "hold_seconds": 900}),
    ScheduledEvent(960.0, "client_retry_regression", "client_config_release", {
        "config_version": 2, "request_timeout_ms": 800, "max_retries": 8,
        "retry_backoff_ms": 0, "retry_jitter_ms": 0,
    }),
    # tx_leak_2 masquerades as the scheduled stock-take purge maintenance job:
    # it borrows the application role's write grants, self-registers a
    # read-only inventory-statistics registry claim and holds the PROMO-SKU-5
    # hot row for 900s across promo_peak_2.
    ScheduledEvent(2040.0, "tx_leak_2", "worker_tx_leak", {
        "sku": "PROMO-SKU-5", "hold_seconds": 900,
        "application_name": "maintenance_stock_purge",
        "registry_task_id": "stock-take-purge",
        "registry_job_name": "库存盘点快照清理",
        "registry_scope_note": "shop.inventory 统计信息维护（只读）",
        "registry_max_transaction_seconds": 10,
    }),
)

PATH_SCHEDULES: dict[str, tuple[ScheduledEvent, ...]] = {
    "healthy": _BASE_EVENTS,
    "reference": _BASE_EVENTS + _FAULT_EVENTS,
    "zero": _BASE_EVENTS + _FAULT_EVENTS,
    "wrong": _BASE_EVENTS + _FAULT_EVENTS,
}

ORACLE_ACTIONS = (
    # 30s past the leak start so the age filter matches the orphan transaction.
    ScheduledAction(756.0, "oracle_terminate_leak_1",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'shop_app' AND state = 'idle in transaction' "
                    "AND now() - xact_start > interval '30 seconds';"),
    ScheduledAction(970.0, "oracle_restore_retry_policy",
                    "UPDATE ops.client_config SET config_version = 3, request_timeout_ms = 8000, "
                    "max_retries = 1, retry_backoff_ms = 500, retry_jitter_ms = 200 WHERE id = 1;"),
    ScheduledAction(1000.0, "oracle_role_protection",
                    "ALTER ROLE shop_app SET idle_in_transaction_session_timeout = '10s';"),
    # Scoped kill of the poisoned maintenance session (idempotent: when the
    # role protection already prevented tx_leak_2 the statement terminates 0
    # rows; it never touches maintenance_ledger_rebuild or archive_worker).
    ScheduledAction(2070.0, "oracle_terminate_poisoned_maintenance",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'maintenance_stock_purge' "
                    "AND state = 'idle in transaction' AND pid <> pg_backend_pid();"),
    ScheduledAction(2100.0, "oracle_confirm_masquerade_resolved",
                    "SELECT count(*) FROM pg_stat_activity WHERE application_name = 'maintenance_stock_purge' "
                    "AND state = 'idle in transaction';"),
    # Published delivery contract: the seed rate (130 rows/s) violates the
    # peak-window cap (100) and would miss the 3480s deadline, so the oracle
    # throttles into the window and catches up after wind-down (ceiling 400).
    ScheduledAction(2645.0, "oracle_throttle_archive_peak",
                    "UPDATE ops.archive_state SET rate_rows_per_second = 100 "
                    "WHERE job_id = 'orders-history-archive';"),
    ScheduledAction(3005.0, "oracle_archive_catch_up",
                    "UPDATE ops.archive_state SET rate_rows_per_second = 400 "
                    "WHERE job_id = 'orders-history-archive';"),
)

WRONG_ACTIONS = (
    ScheduledAction(726.0, "wrong_kill_only",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'shop_app' AND state = 'idle in transaction';"),
    ScheduledAction(2046.0, "wrong_max_connections",
                    "ALTER SYSTEM SET max_connections = 500; SELECT pg_reload_conf();"),
    ScheduledAction(2050.0, "wrong_kill_everything",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'shop_app';"),
    ScheduledAction(2052.0, "wrong_drop_durability",
                    "ALTER ROLE shop_app SET synchronous_commit = 'off';"),
    # The opposite wrong choice: defer the archive at peak arrival and never
    # resume -- burns the deferral budget and misses the delivery deadline.
    ScheduledAction(2645.0, "wrong_pause_archive_indefinitely",
                    "UPDATE ops.archive_state SET enabled = FALSE "
                    "WHERE job_id = 'orders-history-archive';"),
)


def main() -> int:
    args = parse_common_args(__doc__ or "")
    configure_port_range(args.port_lo, args.port_hi)
    assert_lease_capacity()
    schedule = require_path_schedule(PATH_SCHEDULES, args.path)
    actions = ORACLE_ACTIONS if args.path == "reference" else WRONG_ACTIONS if args.path == "wrong" else ()

    run_dir = Path("reports/pg5r-oltp") / f"{args.run_id}-{args.path}"
    evidence = EvidenceLedgerFile(run_dir / "evidence.jsonl", args.run_id)
    port = acquire_port()
    container_name = f"{CONTAINER_PREFIX}{args.path}-{args.run_id}"

    capability_cleanup_evidence = []
    activation_handles: list[tuple[str, object, object]] = []
    try:
        deploy_container({
            "container_name": container_name,
            "host_port": port,
            "image": args.image,
            "resources": {"cpus": args.cpu, "memory_mb": args.memory_mb, "shm_size": "256m",
                          "cpuset": args.cpuset},
        })
        wait_until_ready(port)

        source = TcpConnectionSource(host="localhost", port=port, user="shop_app",
                                     password="shop_app", dbname="testdb")
        admin_source = TcpConnectionSource(host="localhost", port=port, user="postgres",
                                           password="password", dbname="testdb")
        spec = load_persistent_scenario(SPEC_PATH)
        horizon_seconds = float(spec.horizon_seconds)
        warmup_seconds = float(spec.warmup_seconds)
        input_stop_seconds = float(spec.input_stop_seconds)
        archive_deadline_seconds = _deliverable_deadline(spec, ARCHIVE_JOB_ID)

        clock = RealClock()
        scoring_origin = clock.monotonic() + warmup_seconds
        driver = OltpWorkloadDriver(
            source=source,
            clock=clock,
            evidence=evidence,
            plan=TRADE_TIERS,
            config=DRIVER_CONFIG,
            run_id=args.run_id,
            scoring_origin=scoring_origin,
            horizon_seconds=horizon_seconds,
            input_stop_seconds=input_stop_seconds,
        )
        driver.start()
        origin = driver.wait_for_warmup()



        def execute_action(action: ScheduledAction) -> dict:
            connection = admin_source.connection("oracle")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(action.sql)
                    rows = cursor.fetchall() if cursor.description else []
                connection.commit()
                return {"rows": [list(row) for row in rows]}
            except psycopg2.Error as exc:
                connection.rollback()
                if not action.expect_failure:
                    raise
                return {"expected_failure": repr(exc)}
            finally:
                connection.close()

        def activate_and_track(event: ScheduledEvent) -> dict:
            try:
                capability = CAPABILITY_REGISTRY.capability(event.capability_id)
            except ValueError as exc:
                raise RuntimeError(
                    f"Event references an unregistered capability: event_id={event.event_id!r}"
                ) from exc
            context = CapabilityContext(
                run_id=args.run_id,
                occurrence=EventOccurrence(
                    event_id=event.event_id,
                    capability_id=event.capability_id,
                    occurrence_index=1,
                    entity=event.event_id,
                    params=dict(event.payload),
                ),
                clock=clock,
                source=source,
                admin_source=admin_source,
                evidence=evidence,
                driver=driver,
            )
            result = capability.activate(context)
            activation_handles.append((event.event_id, capability, result.handle))
            return {"outcome": result.outcome, **dict(result.attempt)}
        observations = run_timeline(
            origin=origin,
            clock=clock,
            schedule=schedule,
            actions=actions,
            activate=activate_and_track,
            execute_action=execute_action,
        )
        clock.wait_until(origin + horizon_seconds, threading.Event())
        summary = driver.stop_and_drain()
        verifier_connection = admin_source.connection("verifier")
        snapshot = load_order_book_snapshot(
            verifier_connection,
            initial_inventory={row["sku"]: row["qty_available"] for row in generate_inventory_rows(20000)},
            seed_order_prefix="hist-",
        )
        guc_state = collect_guc_state(verifier_connection)
        # The audit trail anchors control changes to the wall clock; the tradeoff
        # verdict maps the published peak window back through the scoring origin.
        scoring_start_epoch = time.time() - (time.monotonic() - origin)
        tradeoff = run_verifier("archive_delivery_tradeoff", {
            "job_id": ARCHIVE_JOB_ID,
            "scoring_start_epoch": scoring_start_epoch,
            "peak_window_start_seconds": PEAK_WINDOW_START_SECONDS,
            "peak_window_end_seconds": PEAK_WINDOW_END_SECONDS,
            "peak_grace_seconds": 60.0,
            "peak_rate_cap_rows_per_second": PEAK_ARCHIVE_RATE_CAP_ROWS_PER_SECOND,
            "rate_ceiling_rows_per_second": ARCHIVE_RATE_CEILING_ROWS_PER_SECOND,
            "deferral_budget_seconds": ARCHIVE_DEFERRAL_BUDGET_SECONDS,
            "total_history_rows": 300000,
            "horizon_seconds": horizon_seconds,
            "deadline_note": f"delivery deadline {archive_deadline_seconds}s",
        }, ops=driver.ledger.ops(), snapshot=snapshot, connection=verifier_connection)
        verifier_connection.close()
        chain_records = evidence.verify_chain()
        conservation = verify_conservation(driver.ledger.ops(), snapshot)
        good = good_fraction(driver.ledger.ops(), ["place_order", "pay_order"])
        archive_failures = list(verify_archive_delivery(
            snapshot, cutoff_created_at=HISTORY_CUTOFF_CREATED_AT,
            deadline_note=f"delivery deadline {archive_deadline_seconds}s",
        ))
        archive_terminals = [
            record for record in job_terminal_records(evidence.path)
            if record.get("job_id") == ARCHIVE_JOB_ID
        ]
        if len(archive_terminals) != 1:
            raise RuntimeError(
                "Archive job must have exactly one terminal record: "
                f"job_id={ARCHIVE_JOB_ID!r}, terminal_records={len(archive_terminals)}"
            )
        archive_terminal = archive_terminals[0]
        archive_on_time = (
            archive_terminal.get("status") == "completed"
            and archive_terminal.get("completed_at") is not None
            and float(archive_terminal["completed_at"]) <= origin + archive_deadline_seconds
        )
        report = {
            "scenario_id": "pg_continuous_ops_business_priority",
            "path": args.path,
            "run_id": args.run_id,
            "observations": observations,
            "evidence_chain": {"records": chain_records, "verified": True},
            "good_fraction": good,
            "conservation": {
                "conserved": conservation.conserved,
                "denominator_ops": conservation.denominator_ops,
                "committed_ops": conservation.committed_ops,
                "failures": list(conservation.failures)[:20],
            },
            "archive_delivery_failures": archive_failures[:20],
            "archive_terminal": dict(archive_terminal),
            "archive_seed_contract": {
                "rate_rows_per_second": ARCHIVE_SEED_RATE_ROWS_PER_SECOND,
                "batch_rows": ARCHIVE_SEED_BATCH_ROWS,
            },
            "post_run_guc_state": guc_state,
            "driver_summary": {
                "tiers": summary.tier_schedule,
                "config_versions": list(summary.applied_config_versions),
                "probes": len(summary.probes),
            },
            "budget_assessment": budget_assessment(items=(
                {
                    "objective": "good_fraction_place_pay",
                    "target": ">= 0.90 (promo-day order/pay failure cap 10%)",
                    "observed": good,
                    "within_budget": good >= 0.90,
                },
                {
                    "objective": "ledger_conservation",
                    "target": "conserved (hard invariant, zero tolerance)",
                    "observed": conservation.conserved,
                    "within_budget": conservation.conserved,
                },
                {
                    "objective": "archive_delivery",
                    "target": f"100% of cutoff rows migrated by {archive_deadline_seconds}s",
                    "observed": {
                        "delivery_failures": len(archive_failures),
                        "status": archive_terminal.get("status"),
                        "on_time": archive_on_time,
                    },
                    "within_budget": not archive_failures and archive_on_time,
                },
                {
                    "objective": "archive_delivery_tradeoff",
                    "target": (
                        f"peak window [{PEAK_WINDOW_START_SECONDS:.0f}s, {PEAK_WINDOW_END_SECONDS:.0f}s] "
                        f"rate <= {PEAK_ARCHIVE_RATE_CAP_ROWS_PER_SECOND} rows/s; ceiling "
                        f"{ARCHIVE_RATE_CEILING_ROWS_PER_SECOND} rows/s outside; cumulative pause <= "
                        f"{ARCHIVE_DEFERRAL_BUDGET_SECONDS:.0f}s"
                    ),
                    "observed": {
                        "passed": tradeoff["passed"],
                        "failures": list(tradeoff["failures"])[:10],
                        "peak_max_rate_rows_per_second": tradeoff["peak_max_rate_rows_per_second"],
                        "deferral_seconds": tradeoff["deferral_seconds"],
                        "control_changes": tradeoff["control_changes"],
                    },
                    "within_budget": tradeoff["passed"] is True,
                },
            )),
            "zero_action_budget_note": zero_action_budget_note() if args.path == "zero" else None,
        }
    finally:
        # Reverse-order capability cleanup before environment teardown: each
        # capability releases only what it activated, then asserts clean.
        for event_id, capability, handle in reversed(activation_handles):
            capability.cleanup(handle)
            capability_cleanup_evidence.append({
                "event_id": event_id,
                "clean": dict(capability.assert_clean(handle)),
            })
        cleanup_evidence = cleanup_lease(container_name)
    report["capability_cleanup"] = capability_cleanup_evidence
    report["cleanup"] = cleanup_evidence
    write_report(f"{args.run_id}-{args.path}", report)
    print(f"completed {args.path} path run; report=reports/pg5r-oltp/{args.run_id}-{args.path}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
