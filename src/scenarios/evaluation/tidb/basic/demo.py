from src.scenarios.evaluation.outcome import SqlRowsVerifier

from ..base import TidbEvaluator


class TidbDemoForMinimalHealthyEvaluatorCase(TidbEvaluator):
    scenario_id = "tidb_demo"
    case_id = "minimal_healthy"
    diagnosis_applicable = False
    diagnosis_conditions = ()
    outcome_verifiers = (
        SqlRowsVerifier(
            "database_available",
            lambda case: "SELECT 1",
            "query succeeds",
            lambda rows, case: rows in ([[1]], [(1,)]),
        ),
    )
