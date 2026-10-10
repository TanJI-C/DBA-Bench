import json
from typing import Any

from src.scenarios.evaluation.base import BaseEvaluator
from src.scenarios.evaluation.outcome import build_outcome_result


def event_result(event) -> Any:
    result = event.result
    if isinstance(result, str):
        result = json.loads(result)
    return result


def event_succeeded(event) -> bool:
    result = event_result(event)
    return not isinstance(result, dict) or result.get("status") == "success"


def cluster_event(event, resource: str, operation: str, target: str | None = None) -> bool:
    if event.api != "manage_cluster":
        return False
    args = event.args
    if str(args.get("resource", "")).casefold() != resource.casefold():
        return False
    if str(args.get("operation", "")).casefold() != operation.casefold():
        return False
    return target is None or str(args.get("target", "")).casefold() == target.casefold()


class TidbEvaluator(BaseEvaluator):
    def OutcomePassFunc(self, context):
        checks = tuple(verifier.verify(context) for verifier in self.outcome_verifiers)
        return build_outcome_result(
            checks,
            trusted_artifacts_used=tuple(check.check_id for check in checks),
        )
