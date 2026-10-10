"""DBAIOps type definitions.

Based on the DBAIOps paper (VLDB 2026) Section 4.1 Table 2.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class GraphNode:
    """Graph vertex. 6 types per paper Table 2."""

    id: str
    type: str  # trigger | experience | tool | metric | tag | auxiliary
    name: str
    content: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "content": self.content,
            "attributes": self.attributes,
        }


@dataclass
class GraphEdge:
    """Directed edge. 4 types: containment, relevance, diagnosis, synonym."""

    source: str
    target: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "attributes": self.attributes,
        }


@dataclass
class AnomalyEquation:
    """Paper Section 5.1: anomaly detection equation with frequency control."""

    metric_raw: str
    threshold_1: float
    metric_composite: Optional[str] = None
    threshold_2: Optional[float] = None
    trend_condition: Optional[int] = None  # 0-5
    frequency_m: int = 3
    frequency_n: int = 5
    inverted: bool = False  # True for metrics where low values are anomalous


@dataclass
class ADFResult:
    """ADF 5-step algorithm output (paper Section 6.1)."""

    metric: str
    sigma: float
    cv: float
    baseline: float
    deviation: float
    f_state: float
    w1: float
    w2: float
    score: float
    is_abnormal: bool


@dataclass
class DiagnosticPath:
    """A diagnosis path through the graph."""

    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)


@dataclass
class EvolutionState:
    """State of the two-stage graph evolution process."""

    trigger_id: str = ""
    expanded_paths: List[DiagnosticPath] = field(default_factory=list)
    accumulated_metrics: Dict[str, List[float]] = field(default_factory=dict)
    adf_results: List[ADFResult] = field(default_factory=list)
    queried_nodes: List[str] = field(default_factory=list)
    cross_edges_created: List[GraphEdge] = field(default_factory=list)
    should_continue: bool = True
    depth: int = 0
    adf_history: List[Dict[str, Any]] = field(default_factory=list)
