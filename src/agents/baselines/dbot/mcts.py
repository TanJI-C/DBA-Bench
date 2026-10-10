"""DB-GPT trajectory tree utilities.

The upstream DB-GPT code stores expert tool-use trajectories as tree nodes with
Thought, Action, Action Input, and Observation. It does not expose AiOpsBench
environment actions as a persistent remediation MCTS tree.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DiagnosisNode:
    id: int
    node_type: str
    description: str = ""
    observation: str = ""
    parent: Optional["DiagnosisNode"] = None
    children: List["DiagnosisNode"] = field(default_factory=list)
    is_terminal: bool = False
    pruned: bool = False
    values: List[float] = field(default_factory=list)
    vote_counts: List[int] = field(default_factory=list)
    reflection: List[str] = field(default_factory=list)
    input_token: Optional[int] = None
    cache_input_token: Optional[int] = None
    output_token: Optional[int] = None

    def compute_weight(self) -> float:
        if not self.values:
            return 0.0
        return sum(self.values) / len(self.values)

    def value_sum(self) -> float:
        return sum(self.values)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "node_type": self.node_type,
            "description": self.description,
            "observation": self.observation,
            "parent": self.parent.id if self.parent else None,
            "children": [child.id for child in self.children],
            "is_terminal": self.is_terminal,
            "pruned": self.pruned,
            "mean_value": self.compute_weight(),
            "value_sum": self.value_sum(),
            "mean_votes": sum(self.vote_counts) / len(self.vote_counts) if self.vote_counts else 0.0,
            "reflection": list(self.reflection),
        }
        if self.input_token is not None:
            data.update({
                "input_token": self.input_token,
                "cache_input_token": self.cache_input_token,
                "output_token": self.output_token,
            })
        return data

    def total_input_tokens(self) -> Optional[int]:
        if self.input_token is None:
            return None
        return self.input_token + self.cache_input_token


class DiagnosisTree:
    """Simple DB-GPT trajectory tree."""

    def __init__(self, alert: str = "", context: str = ""):
        self.alert = alert
        self.context = context
        self.root = DiagnosisNode(id=0, node_type="Action Input", description=alert, observation=context)
        self._next_id = 1
        self._all_nodes: Dict[int, DiagnosisNode] = {0: self.root}

    def add_child(
        self,
        parent: DiagnosisNode,
        node_type: str,
        description: str = "",
        observation: str = "",
    ) -> DiagnosisNode:
        node = DiagnosisNode(
            id=self._next_id,
            node_type=node_type,
            description=description,
            observation=observation,
            parent=parent,
        )
        parent.children.append(node)
        self._all_nodes[node.id] = node
        self._next_id += 1
        return node

    def get_node(self, node_id: int) -> DiagnosisNode:
        return self._all_nodes[node_id]

    def get_former_trace(
        self,
        start_node: DiagnosisNode,
        target_node: DiagnosisNode,
        valid_types: Optional[List[str]] = None,
    ) -> str:
        valid = set(valid_types or ["Thought", "Action", "Action Input", "Observation"])
        pieces = []
        node = target_node
        while node is not None and node is not start_node.parent:
            if node.node_type in valid:
                pieces.append(f"{node.node_type}: {node.description}")
            if node.observation and "Observation" in valid:
                pieces.append(f"Observation: {node.observation}")
            node = node.parent
        pieces.reverse()
        return "\n".join(pieces)

    def to_json_recursive(self) -> Dict[str, Any]:
        def walk(node: DiagnosisNode) -> Dict[str, Any]:
            data = node.to_dict()
            data["children"] = [walk(child) for child in node.children]
            return data

        return {
            "size": len(self._all_nodes),
            "tree": walk(self.root),
        }


@dataclass
class TreeSearchConfig:
    """DB-GPT tree-of-thought runtime parameters."""

    simulation_count: int = 2
    epsilon_new_node: float = 0.3
    vote_candidates: int = 2
    single_chain_max_step: int = 24
