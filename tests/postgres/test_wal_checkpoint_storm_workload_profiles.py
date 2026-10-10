import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.scenarios.postgres import PgSystemFailureWalCheckpointStormScenario


def test_wal_checkpoint_storm_uses_real_workload_noise_profiles():
    scenario = PgSystemFailureWalCheckpointStormScenario()

    profiles = scenario.get_case("billing_slot_checkpoint_storm").background_workload.profiles
    names = {profile.name for profile in profiles}
    sql_text = "\n".join(profile.sql.lower() for profile in profiles)

    assert "checkpoint_log_noise_statement_timeout_dashboard_refresh" in names
    assert "checkpoint_log_noise_missing_billing_rollup" in names
    assert "checkpoint_temp_spill_order_report" in names
    assert any(name.startswith("tpcds_q") for name in names)
    assert "postgresql.log" not in sql_text
    assert "/var/log/postgresql" not in sql_text
    assert "printf" not in sql_text
