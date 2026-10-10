"""Data types for the Panda baseline agent."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TelemetryFeature:
    metric_name: str
    trend: str  # "increasing", "decreasing", "stable"
    mean: float
    p95: float
    change_points: List[int] = field(default_factory=list)
    seasonality: bool = False
    correlation_with: Dict[str, float] = field(default_factory=dict)
    text_summary: str = ""


@dataclass
class GroundingContext:
    documents: List[str] = field(default_factory=list)
    telemetry_text: List[str] = field(default_factory=list)
    schema_info: str = ""
    aggregated_prompt: str = ""


@dataclass
class VerificationResult:
    verdict: str  # "entail", "contradict", "neutral"
    confidence: float = 0.0
    citations: List[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class AffordanceAssessment:
    action: Dict[str, Any] = field(default_factory=dict)
    risk_level: str = "low"  # "low", "medium", "high"
    risk_description: str = ""
    reversible: bool = True
    approved: bool = True


@dataclass
class FeedbackEntry:
    query: str = ""
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    outcome: str = ""  # "success", "failure", "partial"
