from typing import Any

from src.scenarios.evaluation.protocol import EvaluationContext


class EfficiencyCalculator:
    def calculate(self, context: EvaluationContext) -> dict[str, Any]:
        usages = context.case_run.model_usage
        if not usages:
            return {"applicable": False, "reason": "human_or_unmetered_agent"}
        result = {
            "applicable": True,
            "model_calls": len(usages),
            "input_tokens": sum(usage["input_tokens"] for usage in usages),
            "cache_input_tokens": sum(usage["cache_input_tokens"] for usage in usages),
            "output_tokens": sum(usage["output_tokens"] for usage in usages),
        }
        priced = [usage for usage in usages if "token_cost_usd" in usage]
        if priced and len(priced) != len(usages):
            raise ValueError("model usage mixes priced and unpriced calls")
        if priced:
            result["token_cost"] = {
                "applicable": True,
                "usd": sum(usage["token_cost_usd"] for usage in usages),
                "pricing_source": usages[0]["pricing_source"],
            }
        else:
            result["token_cost"] = {
                "applicable": False,
                "reason": "provider_usage_has_no_pricing",
            }
        return result
