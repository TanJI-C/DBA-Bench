"""Andromeda telemetry analysis module.

Implements the Troublesome Telemetry Retrieval pipeline from the paper:
1. Anomalous Telemetry Detection — STL decomposition, residual analysis
2. Telemetry-to-Text Transformation — convert anomalies to NL descriptions
3. Relevant Telemetry Selection — rank by semantic similarity to alert
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from src.agents.baselines.andromeda.types import MetricAnomaly
from src.agents.baselines.telemetry import ParsedMetricSeries, parse_metric_response, stl_period_samples

logger = logging.getLogger(__name__)


class AndromedaTelemetry:
    """STL-based telemetry anomaly detection (paper Section 2.1).

    Uses Seasonal-Trend decomposition using LOESS (STL) to detect
    anomalous metrics, then converts them to text descriptions.
    """

    def __init__(self, period: int = 60, anomaly_threshold: float = 3.0):
        self.period = period
        self.anomaly_threshold = anomaly_threshold
        self._raw_metrics: Dict[str, Any] = {}
        self._anomalies: List[MetricAnomaly] = []

    def add_metric_data(self, metric_type: str, raw_result: Any) -> None:
        """Store raw metric data from query_metrics tool result."""
        try:
            data = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
            self._raw_metrics[metric_type] = data
        except (json.JSONDecodeError, TypeError):
            self._raw_metrics[metric_type] = {"raw": raw_result}

    def detect_anomalies(self) -> List[MetricAnomaly]:
        """Run STL decomposition on all collected metrics and detect anomalies."""
        self._anomalies = []
        for metric_type, data in self._raw_metrics.items():
            anomalies = self._analyze_metric(metric_type, data)
            self._anomalies.extend(anomalies)
        return self._anomalies

    def get_anomaly_texts(self) -> List[str]:
        """Telemetry-to-Text: convert all anomalies to NL descriptions."""
        return [a.to_text() for a in self._anomalies]

    def get_anomalies_summary(self) -> str:
        """Get combined text summary of all anomalies."""
        texts = self.get_anomaly_texts()
        if not texts:
            return "No significant anomalies detected in the collected telemetry data."
        return "\n".join(f"- {t}" for t in texts)

    def _analyze_metric(self, metric_type: str, data: Any) -> List[MetricAnomaly]:
        """Analyze a single metric type for anomalies."""
        if isinstance(data, dict) and data.get("kind") == "series":
            parsed = parse_metric_response(data, metric=metric_type)
            anomalies = []
            for series in parsed:
                anomalies.extend(self._analyze_series(series))
            return anomalies
        values, timestamps = self._extract_time_series(metric_type, data)
        if values is None or len(values) < self.period * 2:
            return self._scalar_anomaly_check(metric_type, data)

        return self._stl_anomaly_detection(metric_type, values, timestamps)

    def _analyze_series(self, series: ParsedMetricSeries) -> List[MetricAnomaly]:
        values = np.asarray(series.values, dtype=float)
        timestamps = [str(timestamp) for timestamp in series.timestamps_ms]
        if len(values) < 2:
            return self._scalar_anomaly_check(series.metric, {"value": values[-1] if len(values) else None})
        required_samples = stl_period_samples(self.period, series.step_seconds)
        if len(values) < required_samples * 2:
            return self._simple_anomaly_detection(
                series.metric,
                values,
                timestamps,
                series_target=series.series_target,
                field=series.field,
            )
        return self._stl_anomaly_detection(
            series.metric,
            values,
            timestamps,
            series_target=series.series_target,
            field=series.field,
            period_samples=required_samples,
        )

    def _extract_time_series(
        self, metric_type: str, data: Any
    ) -> Tuple[Optional[np.ndarray], Optional[List[str]]]:
        """Extract time-series values from raw metric data."""
        if isinstance(data, dict):
            if data.get("status") == "error":
                return None, None
            if data.get("kind") == "series":
                target_series = next(iter(data["series"].values()))
                value_names = [name for name in target_series if name != "timestamps"]
                values = target_series[value_names[0]]
                return np.array(values, dtype=float), target_series["timestamps"]
            if "data" in data and isinstance(data["data"], list):
                points = data["data"]
                values = []
                timestamps = []
                for p in points:
                    if isinstance(p, dict):
                        v = p.get("value", p.get("val"))
                        t = p.get("timestamp", p.get("time"))
                        if v is not None:
                            try:
                                values.append(float(v))
                                timestamps.append(str(t) if t else None)
                            except (ValueError, TypeError):
                                continue
                if values:
                    return np.array(values), timestamps
            if "value" in data:
                return None, None
        return None, None

    def _stl_anomaly_detection(
        self,
        metric_type: str,
        values: np.ndarray,
        timestamps: Optional[List[str]],
        *,
        series_target: Optional[str] = None,
        field: Optional[str] = None,
        period_samples: Optional[int] = None,
    ) -> List[MetricAnomaly]:
        """Apply STL decomposition and detect anomalies from residuals."""
        try:
            from statsmodels.tsa.seasonal import STL
        except ImportError:
            logger.warning("statsmodels not available, falling back to simple detection")
            return self._simple_anomaly_detection(metric_type, values, timestamps)

        try:
            stl = STL(values, period=period_samples or self.period, robust=True)
            result = stl.fit()
            residuals = result.resid
        except Exception as e:
            logger.warning(f"STL decomposition failed for {metric_type}: {e}")
            return self._simple_anomaly_detection(metric_type, values, timestamps)

        std = np.std(residuals)
        if std == 0:
            return []

        anomalies = []
        mean = np.mean(residuals)
        for i, r in enumerate(residuals):
            severity = abs(r - mean) / std
            if severity >= self.anomaly_threshold:
                ts = timestamps[i] if timestamps and i < len(timestamps) else None
                expected_low = values[i] - r + mean - self.anomaly_threshold * std
                expected_high = values[i] - r + mean + self.anomaly_threshold * std
                anomalies.append(MetricAnomaly(
                    metric_name=metric_type,
                    timestamp=ts,
                    value=float(values[i]),
                    expected_range=(float(expected_low), float(expected_high)),
                    residual=float(r),
                    severity=float(severity),
                    series_target=series_target,
                    field=field,
                ))
        return anomalies

    def _simple_anomaly_detection(
        self,
        metric_type: str,
        values: np.ndarray,
        timestamps: Optional[List[str]],
        *,
        series_target: Optional[str] = None,
        field: Optional[str] = None,
    ) -> List[MetricAnomaly]:
        """Fallback: z-score based anomaly detection without STL."""
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return []

        anomalies = []
        for i, v in enumerate(values):
            severity = abs(v - mean) / std
            if severity >= self.anomaly_threshold:
                ts = timestamps[i] if timestamps and i < len(timestamps) else None
                anomalies.append(MetricAnomaly(
                    metric_name=metric_type,
                    timestamp=ts,
                    value=float(v),
                    expected_range=(
                        float(mean - self.anomaly_threshold * std),
                        float(mean + self.anomaly_threshold * std),
                    ),
                    residual=float(v - mean),
                    severity=float(severity),
                    series_target=series_target,
                    field=field,
                ))
        return anomalies

    def _scalar_anomaly_check(
        self, metric_type: str, data: Any
    ) -> List[MetricAnomaly]:
        """Check scalar metrics against known healthy thresholds."""
        THRESHOLDS = {
            "cache_hit_ratio": (0.90, 1.0),
            "cpu": (0.0, 80.0),
            "memory": (0.0, 85.0),
            "disk_usage": (0.0, 80.0),
        }

        value = None
        if isinstance(data, dict):
            if data.get("kind") == "series":
                target_series = next(iter(data["series"].values()))
                value_names = [name for name in target_series if name != "timestamps"]
                samples = target_series[value_names[0]]
                value = samples[-1] if samples else None
            else:
                value = data.get("value", data.get("data"))
            if isinstance(value, dict):
                value = value.get("value")
        if isinstance(data, (int, float)):
            value = data

        if value is None:
            return []

        try:
            value = float(value)
        except (ValueError, TypeError):
            return []

        threshold = THRESHOLDS.get(metric_type)
        if threshold is None:
            return []

        low, high = threshold
        if value < low or value > high:
            severity = max(abs(value - low), abs(value - high)) / max(high - low, 1)
            return [MetricAnomaly(
                metric_name=metric_type,
                timestamp=None,
                value=value,
                expected_range=(low, high),
                residual=value - (low + high) / 2,
                severity=severity,
            )]
        return []
