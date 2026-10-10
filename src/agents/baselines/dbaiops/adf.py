"""Adaptive Detector Function (ADF) - Paper Section 6.1.

5-step algorithm for detecting abnormal metrics on evolved graph paths.
"""

import math
from typing import List, Optional

from src.agents.baselines.dbaiops.types import ADFResult


class AdaptiveDetectorFunction:
    """Paper Section 6.1: Adaptive Detector Function.

    Given metric value sequence X = {x1, x2, ..., xn}, determines
    whether the metric exhibits abnormal behavior via 5 steps:
    1. Volatility (σ and CV) calculation
    2. Dynamic baseline (Bt) and deviation (D) computation
    3. State function adjustment
    4. Weight calculation
    5. Weighted status evaluation
    """

    def __init__(self, theta: float = 10.0, score_threshold: float = 1.2):
        self.theta = theta
        self.score_threshold = score_threshold

    def evaluate(self, values: List[float],
                 baseline: Optional[float] = None) -> ADFResult:
        """Run the 5-step ADF algorithm on a metric value sequence."""
        if not values or len(values) < 2:
            return ADFResult(
                metric="", sigma=0.0, cv=0.0, baseline=0.0,
                deviation=0.0, f_state=0.0, w1=0.0, w2=1.0,
                score=0.0, is_abnormal=False,
            )

        n = len(values)
        x_bar = sum(values) / n
        xt = values[-1]

        # Step 1: Volatility (σ and CV)
        sigma = self._compute_sigma(values, x_bar, n)
        cv = self._compute_cv(values)

        # Step 2: Dynamic baseline and deviation
        bt = baseline if baseline is not None else self._compute_baseline(values)
        deviation = abs(xt - bt)

        # Step 3: State function
        f_state = self._compute_f_state(xt, bt, sigma, deviation)

        # Step 4: Weight calculation
        w1 = sigma / (sigma + self.theta) if (sigma + self.theta) > 0 else 0.0
        w2 = 1.0 - w1

        # Step 5: Weighted status evaluation
        score = w1 * sigma + w2 * f_state

        is_abnormal = score > self.score_threshold

        return ADFResult(
            metric="",
            sigma=sigma,
            cv=cv,
            baseline=bt,
            deviation=deviation,
            f_state=f_state,
            w1=w1,
            w2=w2,
            score=score,
            is_abnormal=is_abnormal,
        )

    def _compute_sigma(self, values: List[float], x_bar: float, n: int) -> float:
        """Step 1a: standard deviation."""
        if n < 2:
            return 0.0
        variance = sum((x - x_bar) ** 2 for x in values) / (n - 1)
        return math.sqrt(variance)

    def _compute_cv(self, values: List[float]) -> float:
        """Step 1b: CV = ρV / ρR (volatility autocorrelation / random autocorrelation).

        Quantifies how persistent or random the fluctuations are.
        """
        if len(values) < 3:
            return 0.0
        volatility = [abs(values[i] - values[i - 1]) for i in range(1, len(values))]
        rho_v = self._autocorrelation(volatility)
        rho_r = 1.0 / math.sqrt(len(volatility)) if len(volatility) > 0 else 1.0
        return rho_v / rho_r if rho_r > 0 else 0.0

    def _autocorrelation(self, series: List[float]) -> float:
        """Lag-1 autocorrelation coefficient."""
        n = len(series)
        if n < 2:
            return 0.0
        mean = sum(series) / n
        numerator = sum(
            (series[i] - mean) * (series[i - 1] - mean) for i in range(1, n)
        )
        denominator = sum((x - mean) ** 2 for x in series)
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _compute_baseline(self, values: List[float]) -> float:
        """Step 2: dynamic baseline Bt.

        Paper says Bt is updated hourly. In AiOpsBench we approximate
        with a trimmed mean of earlier observations (excluding the latest value).
        """
        if len(values) <= 1:
            return values[0] if values else 0.0
        history = values[:-1]
        if len(history) >= 4:
            sorted_h = sorted(history)
            trim = max(1, len(sorted_h) // 4)
            trimmed = sorted_h[trim:-trim] if trim < len(sorted_h) // 2 else sorted_h
            return sum(trimmed) / len(trimmed)
        return sum(history) / len(history)

    def _compute_f_state(self, xt: float, bt: float, sigma: float,
                         deviation: float) -> float:
        """Step 3: state function F_state(xt, Bt).

        Paper formula:
        F_state = 1 - D/σ  if xt is near Bt (D ≤ σ)
        F_state = D/σ       if xt is far from Bt (D > σ)
        """
        if sigma == 0:
            return 0.0 if deviation == 0 else 1.0
        if deviation <= sigma:
            return max(0.0, 1.0 - deviation / sigma)
        else:
            return deviation / sigma
