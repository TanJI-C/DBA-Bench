"""Andromeda baseline data types."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class MetricAnomaly:
    """A detected anomaly in a telemetry metric (STL residual-based)."""

    metric_name: str
    timestamp: Optional[str]
    value: float
    expected_range: Tuple[float, float]
    residual: float
    severity: float  # abs(residual) / std
    series_target: Optional[str] = None
    field: Optional[str] = None

    def to_text(self) -> str:
        """Telemetry-to-Text transformation (paper Section 2.1)."""
        direction = "above" if self.residual > 0 else "below"
        series_part = ""
        if self.series_target is not None or self.field is not None:
            series_part = f" [{self.series_target or '*'} / {self.field or '*'}]"
        return (
            f"Metric '{self.metric_name}'{series_part} is anomalous"
            f"{f' at {self.timestamp}' if self.timestamp else ''}: "
            f"observed value {self.value:.4g}, "
            f"expected range [{self.expected_range[0]:.4g}, {self.expected_range[1]:.4g}], "
            f"{direction} normal by {self.severity:.1f} standard deviations."
        )


@dataclass
class KnobRecommendation:
    """A configuration knob recommendation from Phase 2 reasoning."""

    knob_name: str
    current_value: Optional[str]
    recommended_value: str
    rationale: str


@dataclass
class AndromedaDiagnosis:
    """Final diagnosis output from the Andromeda pipeline."""

    root_cause: str
    anomalies: List[MetricAnomaly] = field(default_factory=list)
    knob_recommendations: List[KnobRecommendation] = field(default_factory=list)
    retrieved_evidence: List[str] = field(default_factory=list)
    phase1_knobs: List[str] = field(default_factory=list)
