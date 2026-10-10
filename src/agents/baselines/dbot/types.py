"""Code-first D-Bot data types.

These structures mirror the open-source DB-GPT implementation: D-Bot is a
multi-expert diagnosis workflow, not an external remediation MCTS controller.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


DBOT_EXPERT_NAMES = (
    "ConfigurationExpert",
    "CpuExpert",
    "DiskExpert",
    "IndexExpert",
    "IoExpert",
    "MemoryExpert",
    "QueryExpert",
    "RecoveryExpert",
    "WorkloadExpert",
)


@dataclass
class DbotToolStep:
    """One DB-GPT-style tool action and its AiOpsBench action mapping."""

    expert_name: str
    tool_name: str
    tool_input: Dict[str, Any]
    aiops_action: Dict[str, Any]
    thought: str
    observation: Optional[Dict[str, Any]] = None
    aiops_actions: List[Dict[str, Any]] = field(default_factory=list)
    db_gpt_observation: str = ""
    knowledge_items: List[Dict[str, Any]] = field(default_factory=list)
    top_metrics: List[Dict[str, Any]] = field(default_factory=list)
    input_token: Optional[int] = None
    cache_input_token: Optional[int] = None
    output_token: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "expert_name": self.expert_name,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "aiops_action": self.aiops_action,
            "aiops_actions": self.aiops_actions,
            "thought": self.thought,
            "observation": self.observation,
            "db_gpt_observation": self.db_gpt_observation,
            "knowledge_items": self.knowledge_items,
            "top_metrics": self.top_metrics,
        }
        if self.input_token is not None:
            data.update({
                "input_token": self.input_token,
                "cache_input_token": self.cache_input_token,
                "output_token": self.output_token,
            })
        return data


@dataclass
class ExpertDiagnosis:
    """Diagnosis result collected for one DB-GPT expert."""

    expert_name: str
    root_cause: str = ""
    solutions: str = ""
    knowledge: List[Dict[str, Any]] = field(default_factory=list)
    steps: List[DbotToolStep] = field(default_factory=list)
    review: str = ""
    top_metrics: List[Dict[str, Any]] = field(default_factory=list)
    selected_trajectory: str = ""
    search: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expert_name": self.expert_name,
            "root_cause": self.root_cause,
            "solutions": self.solutions,
            "knowledge": self.knowledge,
            "steps": [step.to_dict() for step in self.steps],
            "review": self.review,
            "top_metrics": self.top_metrics,
            "selected_trajectory": self.selected_trajectory,
            "search": self.search,
        }


@dataclass
class DbotReport:
    """Final DB-GPT-style report assembled by the ChiefDBA reporter."""

    title: str = ""
    anomaly_description: str = ""
    root_cause: str = ""
    solutions: str = ""
    labels: List[str] = field(default_factory=list)
    diagnosis_process: str = ""
    citations: List[Dict[str, Any]] = field(default_factory=list)
    citation_markdown: str = ""
    selected_experts: List[str] = field(default_factory=list)
    top_metrics: List[Dict[str, Any]] = field(default_factory=list)
    roundtable_reviews: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "anomaly_description": self.anomaly_description,
            "root_cause": self.root_cause,
            "solutions": self.solutions,
            "labels": self.labels,
            "diagnosis_process": self.diagnosis_process,
            "citations": self.citations,
            "citation_markdown": self.citation_markdown,
            "selected_experts": self.selected_experts,
            "top_metrics": self.top_metrics,
            "roundtable_reviews": self.roundtable_reviews,
        }
