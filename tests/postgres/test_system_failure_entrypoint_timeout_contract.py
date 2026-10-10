from pathlib import Path


ENTRYPOINTS = (
    Path("examples/run_pg_business_change_massive_backfill_scenario.py"),
    Path("examples/run_pg_resource_governance_audit_logging_scenario.py"),
    Path("examples/run_pg_system_failure_io_checkpoint_spikes_scenario.py"),
    Path("examples/run_pg_system_failure_fd_exhaustion_scenario.py"),
)


def test_experiment_managed_entrypoints_do_not_install_competing_watchdogs():
    for entrypoint in ENTRYPOINTS:
        source = entrypoint.read_text(encoding="utf-8")
        assert "signal.alarm" not in source
        assert "SIGALRM" not in source
        assert "HARD_TIMEOUT_SEC" not in source
