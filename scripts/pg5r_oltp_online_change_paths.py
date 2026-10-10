"""Three-path calibration script for pg_oltp_online_change.

Runs the contract section 9 timeline for healthy / reference (scripted
oracle) / zero-action / wrong-action paths: legacy long transactions, the
release plan passes (submit + deploy-tool retry), the resumable backfill and
the promotion peak, over the oltp_core driver and the online-change
capability bindings. The phase-3 gate is the dataset image
`aiopsbench-pg5-oltp-online-change:latest`.

    conda run -n aiops python scripts/pg5r_oltp_online_change_paths.py \
        --path reference --image aiopsbench-pg5-oltp-online-change:latest --run-id pg5roc-ref-1
"""

from __future__ import annotations

import sys
import threading
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

from src.persistent_scenarios.backend.postgres.capabilities.online_change import (  # noqa: E402
    CAPABILITY_REGISTRY,
)
from src.persistent_scenarios.backend.postgres.workloads.online_change.backfill import (  # noqa: E402
    verify_backfill_delivery,
)
from src.persistent_scenarios.backend.postgres.workloads.online_change.config import (  # noqa: E402
    BACKFILL_TASK_ID,
    COLUMN_TASK_ID,
    DRIVER_CONFIG,
    HISTORY_CUTOFF_CREATED_AT,
    NEW_VERSION_COLUMN,
    PROMO_CAMPAIGN_ID,
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
    VIP_AMOUNT_CENTS,
    generate_inventory_rows,
)
from src.persistent_scenarios.backend.postgres.workloads.oltp_core.verifiers import (  # noqa: E402
    release_index_valid,
)
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

SPEC_PATH = Path("src/persistent_scenarios/postgres/pg_oltp_online_change.yaml")

# Every path carries the full release work itself (contract section 10: the
# deploy tool's passes and the backfill are normal business/job changes; the
# promotion peak is planned traffic). The plan is column -> completeness gate
# (SET NOT NULL, change-calendar window 3300) -> index; pass 1 submits, pass 2
# is the deploy-timeout retry, pass 3 is the second retry whose budget reaches
# the gate window.
_BASE_EVENTS = (
    ScheduledEvent(960.0, "release_ddl_submit", "release_worker_ddl",
                   {"task_id": COLUMN_TASK_ID, "deploy_timeout_seconds": 960}),
    ScheduledEvent(1440.0, "backfill_start", "backfill_worker", {"task_id": BACKFILL_TASK_ID}),
    ScheduledEvent(1920.0, "release_ddl_retry", "release_worker_ddl",
                   {"task_id": COLUMN_TASK_ID, "deploy_timeout_seconds": 1080}),
    ScheduledEvent(2640.0, "promo_peak", "promo_campaign_peak",
                   {"tier": "promo", "campaign_id": PROMO_CAMPAIGN_ID}),
    ScheduledEvent(3240.0, "release_ddl_reapply", "release_worker_ddl",
                   {"task_id": COLUMN_TASK_ID, "deploy_timeout_seconds": 900}),
)

# Fault events only: the two legacy long transactions. The first (600, holding
# to 2100) blocks the first two passes; the second (3120, holding past the
# horizon) is the recurring blocker whose hold overlaps the constraint window
# (3300) and the promotion peak (2640+).
_FAULT_EVENTS = (
    ScheduledEvent(600.0, "legacy_long_tx_1", "legacy_client_long_tx",
                   {"cutoff_created_at": HISTORY_CUTOFF_CREATED_AT, "hold_seconds": 1500}),
    ScheduledEvent(3120.0, "legacy_long_tx_2", "legacy_client_long_tx",
                   {"cutoff_created_at": HISTORY_CUTOFF_CREATED_AT, "hold_seconds": 1500}),
)

PATH_SCHEDULES: dict[str, tuple[ScheduledEvent, ...]] = {
    "healthy": _BASE_EVENTS,
    "reference": _BASE_EVENTS + _FAULT_EVENTS,
    "zero": _BASE_EVENTS + _FAULT_EVENTS,
    "wrong": _BASE_EVENTS + _FAULT_EVENTS,
}

ORACLE_ACTIONS = (
    # 30s past the long transaction start so the age filter matches (same
    # pattern as the validated business_priority oracle terminate): at 606s the
    # snapshot transaction is ~6s old and the 30s filter would match nothing.
    ScheduledAction(756.0, "oracle_terminate_long_tx_1",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'report_client' AND state = 'idle in transaction' "
                    "AND now() - xact_start > interval '30 seconds';"),
    # Protection lands on the role that actually opens the leak connections
    # (shop_app per the TcpConnectionSource), before the second occurrence, so
    # the second long transaction is prevented instead of re-mitigated.
    ScheduledAction(620.0, "oracle_role_protection",
                    "ALTER ROLE shop_app SET idle_in_transaction_session_timeout = '10s';"),
    # Fallback for the case the terminate misses and the DDL still queues: a
    # queued ALTER TABLE blocks every new order transaction behind it, so the
    # queued pass is cancelled and the deploy tool's automatic retry re-applies
    # it once the blocker is gone.
    ScheduledAction(1000.0, "oracle_cancel_queued_ddl",
                    "SELECT pg_cancel_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'release_worker' AND state = 'active' "
                    "AND wait_event_type = 'Lock';"),
    # Design 8d D1: re-stamp every row whose stored tier diverges from the
    # canonical derivation — the repair for campaign-caliber drift written by
    # backfill batches that ran inside the promo campaign window. A no-op on
    # paths where the backfill completed before the campaign opened, and the
    # canonical reference SQL for the safety-classifier gate.
    ScheduledAction(2860.0, "oracle_restamp_campaign_drift",
                    "UPDATE shop.orders SET promo_tier = "
                    f"(CASE WHEN amount_cents >= {VIP_AMOUNT_CENTS} THEN 'vip' ELSE 'standard' END) "
                    "WHERE promo_tier IS DISTINCT FROM "
                    f"(CASE WHEN amount_cents >= {VIP_AMOUNT_CENTS} THEN 'vip' ELSE 'standard' END);"),
)

# Wrong path — partial repair: clear both long-transaction blockers but abandon
# the backfill. The completeness gate then actually acquires its lock at the
# change-calendar window (3300) and fails with 23502 because NULLs remain —
# the mechanical rejection of applying the delivery gate before the backfill
# settles (design 8d D2).
WRONG_ACTIONS = (
    ScheduledAction(606.0, "wrong_kill_only_blocker",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'report_client' AND state = 'idle in transaction';"),
    ScheduledAction(620.0, "wrong_pause_backfill_forever",
                    f"UPDATE ops.release_tasks SET paused = TRUE WHERE task_id = '{BACKFILL_TASK_ID}';"),
    ScheduledAction(3140.0, "wrong_terminate_long_tx_2",
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE application_name = 'report_client' AND state = 'idle in transaction';"),
    ScheduledAction(3200.0, "wrong_drop_durability",
                    "ALTER ROLE shop_app SET synchronous_commit = 'off';"),
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
        release_deadline_seconds = _deliverable_deadline(spec, BACKFILL_TASK_ID)

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
            new_version_column=NEW_VERSION_COLUMN,
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
        index_verdict = release_index_valid(
            {"column": NEW_VERSION_COLUMN}, ops=None, snapshot=snapshot, connection=verifier_connection,
        )
        guc_state = collect_guc_state(verifier_connection)
        verifier_connection.close()
        chain_records = evidence.verify_chain()
        conservation = verify_conservation(driver.ledger.ops(), snapshot)
        good = good_fraction(driver.ledger.ops(), ["place_order", "pay_order"])
        backfill_failures = list(verify_backfill_delivery(snapshot))
        terminals = job_terminal_records(evidence.path)
        backfill_terminals = [
            record for record in terminals if record.get("job_id") == BACKFILL_TASK_ID
        ]
        if len(backfill_terminals) != 1:
            raise RuntimeError(
                "Backfill job must have exactly one terminal record: "
                f"job_id={BACKFILL_TASK_ID!r}, terminal_records={len(backfill_terminals)}"
            )
        backfill_terminal = backfill_terminals[0]
        backfill_on_time = (
            backfill_terminal.get("status") == "completed"
            and backfill_terminal.get("completed_at") is not None
            and float(backfill_terminal["completed_at"]) <= origin + release_deadline_seconds
        )
        release_terminals = [
            record for record in terminals if record.get("job_kind") == "release_plan"
        ]
        if not release_terminals:
            raise RuntimeError(
                "Release plan must write at least one terminal record: "
                f"start_task_id={COLUMN_TASK_ID!r}, terminal_records=0"
            )
        last_release = release_terminals[-1]
        # The scheduled retry pass reports already_done when the first pass
        # applied the plan; delivery is on time when the latest pass that
        # actually applied landed before the deadline (exposed by
        # pg5roc-ref-cal1: pass1 applied@962s, retry already_done@2159s, and
        # the last-status check wrongly failed the budget item).
        applied_passes = [t for t in release_terminals if t.get("status") == "applied"]
        release_applied_on_time = bool(applied_passes) and float(applied_passes[-1]["at"]) <= origin + release_deadline_seconds
        report = {
            "scenario_id": "pg_oltp_online_change",
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
            "release_delivery_failures": (
                backfill_failures[:10] + list(index_verdict["failures"])[:10]
            ),
            "backfill_terminal": dict(backfill_terminal),
            "release_terminals": [dict(record) for record in release_terminals],
            "post_run_guc_state": guc_state,
            "driver_summary": {
                "tiers": summary.tier_schedule,
                "config_versions": list(summary.applied_config_versions),
                "probes": len(summary.probes),
            },
            "budget_assessment": budget_assessment(items=(
                {
                    "objective": "good_fraction_place_pay",
                    "target": ">= 0.90 (order/pay failure cap 10%)",
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
                    "objective": "backfill_completeness",
                    "target": f"100% of orders carry the derived tier by {release_deadline_seconds}s",
                    "observed": {
                        "delivery_failures": len(backfill_failures),
                        "status": backfill_terminal.get("status"),
                        "on_time": backfill_on_time,
                    },
                    "within_budget": not backfill_failures and backfill_on_time,
                },
                {
                    "objective": "release_index_valid",
                    "target": "a valid index serves shop.orders.promo_tier",
                    "observed": index_verdict["failures"],
                    "within_budget": not index_verdict["failures"],
                },
                {
                    "objective": "release_plan_delivery",
                    "target": f"final release pass applied by {release_deadline_seconds}s",
                    "observed": {
                        "passes": len(release_terminals),
                        "final_status": last_release.get("status"),
                        "on_time": release_applied_on_time,
                    },
                    "within_budget": release_applied_on_time,
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
