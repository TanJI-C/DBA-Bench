from pathlib import Path

from src.scenarios import ALL_SCENARIOS


EVALUATOR_ROOT = Path(__file__).parents[1] / "src" / "evaluation"


def test_scenario_evaluators_are_split_into_modules():
    assert not list(EVALUATOR_ROOT.glob("*/cases.py"))

    cases = [case for scenario in ALL_SCENARIOS for case in scenario.cases]
    identities = [(case.evaluator.scenario_id, case.evaluator.case_id) for case in cases]
    assert cases
    assert len(set(identities)) == len(identities)

    for scenario in ALL_SCENARIOS:
        for case in scenario.cases:
            assert case.evaluator.scenario_id == scenario.scenario_id
            assert case.evaluator.case_id == case.case_id
            module = Path(__import__(case.evaluator.__module__, fromlist=["__name__"]).__file__)
            assert module.name != "cases.py"
