"""Shared DP defaults for evaluators, scenario entry points, and persistent runs."""

import argparse
import os
from dataclasses import dataclass, field

from .diagnosis import ExactDiagnosisMatcher, NotApplicableDiagnosisMatcher, SemanticDiagnosisMatcher
from .semantic import DEFAULT_SEMANTIC_MODEL, semantic_judge_from_config


@dataclass(kw_only=True)
class DiagnosisEvaluationConfig:
    diagnosis_match_mode: str = field(
        default_factory=lambda: os.environ.get("AIOPS_DP_MATCH_MODE", "semantic")
    )
    diagnosis_semantic_model: str = field(
        default_factory=lambda: os.environ.get(
            "AIOPS_DP_SEMANTIC_MODEL",
            DEFAULT_SEMANTIC_MODEL,
        )
    )
    diagnosis_semantic_config_path: str = field(
        default_factory=lambda: os.environ.get(
            "AIOPS_DP_SEMANTIC_CONFIG",
            "config/llm_config.json",
        )
    )

    def __post_init__(self):
        if self.diagnosis_match_mode not in {"exact", "semantic"}:
            raise ValueError(
                f"Unsupported diagnosis match mode: {self.diagnosis_match_mode!r}; "
                "expected='exact' or 'semantic'"
            )
        if not self.diagnosis_semantic_model.strip():
            raise ValueError("diagnosis_semantic_model must be non-empty")

    def build_diagnosis_matcher(self, *, applicable: bool = True):
        if not applicable:
            return NotApplicableDiagnosisMatcher(self.diagnosis_match_mode)
        if self.diagnosis_match_mode == "exact":
            return ExactDiagnosisMatcher()
        if self.diagnosis_match_mode == "semantic":
            return SemanticDiagnosisMatcher(self.build_semantic_judge())
        raise AssertionError(
            f"unreachable diagnosis_match_mode={self.diagnosis_match_mode!r}"
        )

    def build_semantic_judge(self):
        return semantic_judge_from_config(
            self.diagnosis_semantic_config_path,
            self.diagnosis_semantic_model,
        )


def add_diagnosis_arguments(parser: argparse.ArgumentParser) -> None:
    """Expose the same independent judge selection in every scenario CLI."""
    defaults = DiagnosisEvaluationConfig()
    parser.add_argument(
        "--diagnosis-match-mode", choices=("exact", "semantic"),
        default=defaults.diagnosis_match_mode,
        help="DP matcher (default: semantic); use exact for deterministic regression tests.",
    )
    parser.add_argument(
        "--diagnosis-semantic-model", default=defaults.diagnosis_semantic_model,
        help="Judge model key in llm_config.json (local service or external API); independent of --model.",
    )
    parser.add_argument(
        "--diagnosis-semantic-config", "--diagnosis-semantic-config-path",
        dest="diagnosis_semantic_config_path",
        default=defaults.diagnosis_semantic_config_path,
        help="LLM config containing the selected diagnosis judge.",
    )
