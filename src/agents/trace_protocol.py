"""Diagnostic trace protocol for agent-owned trace export.

Each agent implements ``export_diagnostic_trace()`` returning a ``DiagnosticTrace``
dict. The exporter writes this to JSON for the frontend to render.

The ``diagnostic_structure`` field carries the agent's reasoning topology, keyed
by ``type``:
  - "linear" — flat timeline; ``turns`` is the complete structure (LLMAgent, etc.)
  - "db_gpt_multiagent" — DB-GPT D-Bot role assignment, expert diagnoses,
    roundtable reviews, and reporter output
  - "tree"   — legacy MCTS tree search traces
  - "graph"  — knowledge-graph evolution (DBAIOpsAgent)

``turns`` is the common timeline present for every agent; the frontend can always
fall back to rendering it linearly.
"""

from typing import Any, Dict, List, Optional

try:
    from typing import Literal, TypedDict
except ImportError:  # pragma: no cover - py<3.8 fallback
    from typing_extensions import Literal, TypedDict


class TraceAction(TypedDict, total=False):
    api: str
    args: Dict[str, Any]
    id: Optional[str]


class TraceResult(TypedDict, total=False):
    api: str
    status: str
    data: Any
    id: Optional[str]


class TraceTurn(TypedDict, total=False):
    turn_number: int
    timestamp: Optional[float]
    thinking: str
    input_token: int
    cache_input_token: int
    output_token: int
    actions: List[TraceAction]
    results: List[TraceResult]


class TracePrompts(TypedDict):
    system: str
    user: str


# --- diagnostic_structure: linear ---


class LinearStructure(TypedDict):
    type: Literal["linear"]


# --- diagnostic_structure: DB-GPT multi-agent (DbotAgent) ---


class ExpertDiagnosisInfo(TypedDict, total=False):
    expert_name: str
    root_cause: str
    solutions: str
    knowledge: List[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    review: str
    top_metrics: List[Dict[str, Any]]
    selected_trajectory: str
    search: Dict[str, Any]


class DbotRoundtableReview(TypedDict, total=False):
    expert: str
    review: str


class DbotMultiAgentStructure(TypedDict, total=False):
    type: Literal["db_gpt_multiagent"]
    selected_experts: List[str]
    expert_diagnoses: List[ExpertDiagnosisInfo]
    roundtable_reviews: List[DbotRoundtableReview]
    report: Dict[str, Any]


# --- diagnostic_structure: legacy tree ---


class TreeNode(TypedDict, total=False):
    id: int
    type: str  # "Thought" | "Action"
    description: str
    observation: str
    parent: Optional[int]
    children: List[int]
    weight: float
    is_terminal: bool
    pruned: bool
    on_best_path: bool
    input_token: int
    cache_input_token: int
    output_token: int


class TreeData(TypedDict, total=False):
    nodes: List[TreeNode]
    best_path: List[int]
    terminal_node_ids: List[int]


class Hypothesis(TypedDict, total=False):
    root_cause: str
    confidence: float
    rationale: str
    evidence: List[str]


class TreeStructure(TypedDict, total=False):
    type: Literal["tree"]
    tree: TreeData
    hypotheses: List[Hypothesis]


# --- diagnostic_structure: graph (DBAIOpsAgent) ---


class GraphNodeInfo(TypedDict, total=False):
    id: str
    type: str
    name: str
    content: str


class GraphEdgeInfo(TypedDict, total=False):
    source: str
    target: str
    type: str


class GraphPath(TypedDict, total=False):
    nodes: List[GraphNodeInfo]
    edges: List[GraphEdgeInfo]


class ADFResultInfo(TypedDict, total=False):
    metric: str
    score: float
    is_abnormal: bool
    sigma: float
    deviation: float


class GraphEvolution(TypedDict, total=False):
    depth: int
    paths: List[GraphPath]
    adf_results: List[ADFResultInfo]
    cross_edges: List[GraphEdgeInfo]


class GraphStructure(TypedDict, total=False):
    type: Literal["graph"]
    trigger: Optional[GraphNodeInfo]
    evolution: GraphEvolution
    diagnosis_report: str


# --- top-level trace ---


class DiagnosticTrace(TypedDict, total=False):
    agent_type: str
    mode: Optional[str]
    prompts: TracePrompts
    turns: List[TraceTurn]
    diagnostic_structure: Dict[str, Any]
    conversation_history: List[Dict[str, Any]]
    conversation_history_raw: List[Dict[str, Any]]
    conversation_phases: List[Dict[str, Any]]
    llm_usage: List[Dict[str, Any]]
    context_compaction: List[Dict[str, Any]]
