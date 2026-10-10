"""AnomalyModel - Paper Section 5.1.

Multi-metric anomaly detection with detection equations, frequency control,
and trend analysis (volatility analysis).
"""

from typing import Any, Dict, List

from src.agents.baselines.dbaiops.types import AnomalyEquation


# Paper Section 5.1: trend types for METRIC_composite
TREND_STABLE = 0
TREND_SHARP_DECLINE = 1
TREND_SLOW_DECLINE = 2
TREND_SHARP_RISE = 3
TREND_SLOW_RISE = 4
TREND_FLUCTUATING = 5


class AnomalyModel:
    """Paper Section 5.1: reusable anomaly model.

    Each model captures a specific database anomaly based on multi-metric
    patterns. Includes detection equations and M/N frequency control.
    """

    def __init__(self, model_id: str, trigger_vertex_id: str,
                 equations: List[AnomalyEquation]):
        self.model_id = model_id
        self.trigger_vertex_id = trigger_vertex_id
        self.equations = equations
        # The M/N trigger frequency is configured per equation (paper Section 5.1);
        # the model requires the strictest setting across its equations.
        self.frequency_m = max(eq.frequency_m for eq in equations)
        self.frequency_n = max(eq.frequency_n for eq in equations)
        self._eval_history: List[bool] = []

    def evaluate(self, metric_values: Dict[str, Any]) -> bool:
        """Evaluate detection equations with frequency control.

        Paper formula:
        Is_Anomaly = METRIC_raw > threshold1
                     ∨ (METRIC_composite = trend ∧ METRIC_raw > threshold2)
        """
        return self._frequency_control(self.evaluate_raw(metric_values))

    def evaluate_raw(self, metric_values: Dict[str, Any]) -> bool:
        """Evaluate detection equations without M/N frequency control."""
        return self._evaluate_equations(metric_values)

    def _evaluate_equations(self, metric_values: Dict[str, Any]) -> bool:
        """Evaluate all equations (OR logic between equations)."""
        for eq in self.equations:
            raw_value = metric_values.get(eq.metric_raw)
            if raw_value is None:
                continue

            # Condition 1: METRIC_raw > threshold_1 (or < for inverted metrics)
            if isinstance(raw_value, (int, float)):
                if eq.inverted:
                    if raw_value < eq.threshold_1:
                        return True
                else:
                    if raw_value > eq.threshold_1:
                        return True

            # Condition 2: METRIC_composite = trend ∧ METRIC_raw > threshold_2
            if (eq.metric_composite is not None
                    and eq.threshold_2 is not None
                    and eq.trend_condition is not None):
                composite_value = metric_values.get(eq.metric_composite)
                if (composite_value is not None
                        and composite_value == eq.trend_condition
                        and isinstance(raw_value, (int, float))):
                    if eq.inverted:
                        if raw_value < eq.threshold_2:
                            return True
                    else:
                        if raw_value > eq.threshold_2:
                            return True

        return False

    def _frequency_control(self, current_result: bool) -> bool:
        """M/N frequency control: trigger only if M of last N evaluations are True."""
        self._eval_history.append(current_result)
        if len(self._eval_history) > self.frequency_n:
            self._eval_history = self._eval_history[-self.frequency_n:]
        true_count = sum(self._eval_history)
        return true_count >= self.frequency_m

    def reset(self):
        self._eval_history.clear()


def compute_trend(values: List[float],
                  sharp_threshold: float = 0.3,
                  slow_threshold: float = 0.1,
                  fluctuation_cv: float = 0.5) -> int:
    """Compute trend type from a value sequence.

    Paper: METRIC_composite derived via volatility analysis algorithm
    over a 10-minute window. Returns trend ∈ {0..5}.

    Thresholds are configurable as the paper does not specify exact values.
    """
    if not values or len(values) < 2:
        return TREND_STABLE

    n = len(values)
    first_half = sum(values[: n // 2]) / max(n // 2, 1)
    second_half = sum(values[n // 2:]) / max(n - n // 2, 1)
    diff = second_half - first_half

    mean = sum(values) / n
    if mean == 0:
        mean = 1.0
    relative_change = abs(diff) / abs(mean)

    # Check fluctuation: high coefficient of variation
    std = (sum((x - mean) ** 2 for x in values) / n) ** 0.5
    cv = std / abs(mean) if mean != 0 else 0
    if cv > fluctuation_cv and relative_change < slow_threshold:
        return TREND_FLUCTUATING

    # Determine direction and speed
    if diff > 0:
        if relative_change >= sharp_threshold:
            return TREND_SHARP_RISE
        elif relative_change >= slow_threshold:
            return TREND_SLOW_RISE
    elif diff < 0:
        if relative_change >= sharp_threshold:
            return TREND_SHARP_DECLINE
        elif relative_change >= slow_threshold:
            return TREND_SLOW_DECLINE

    return TREND_STABLE
