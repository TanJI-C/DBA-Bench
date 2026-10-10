from src.scenarios.runtime.orchestrator import Orchestrator


def inject_case(scenario, case, env, actions=None):
    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        evaluator=None,
        agent=None,
        pretty_print=False,
    )
    orchestrator.action_history.extend(actions or [])
    try:
        orchestrator.setup()
    except Exception:
        orchestrator.teardown()
        raise
    return orchestrator


def recover_case(orchestrator):
    orchestrator.teardown()
