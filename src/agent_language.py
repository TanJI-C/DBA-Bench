"""Language of the text an agent reads: prompts, tool descriptions, tool help and alerts.

Chinese is the default and the language every scenario is authored in. English is
available for PostgreSQL bounded scenarios; ``agent_text`` picks the variant for the
language the run was started with (``AIOPS_AGENT_LANGUAGE``, set by the experiment
runner from ``runtime.agent_language``).
"""
from __future__ import annotations

import os

AGENT_LANGUAGE_ENV = "AIOPS_AGENT_LANGUAGE"
DEFAULT_AGENT_LANGUAGE = "zh"
SUPPORTED_AGENT_LANGUAGES = ("zh", "en")


def validate_agent_language(value: object, context: str) -> str:
    if value not in SUPPORTED_AGENT_LANGUAGES:
        raise ValueError(
            f"{context} must be one of {', '.join(SUPPORTED_AGENT_LANGUAGES)}, got {value!r}"
        )
    return value  # type: ignore[return-value]


def agent_language() -> str:
    return validate_agent_language(
        os.environ.get(AGENT_LANGUAGE_ENV, DEFAULT_AGENT_LANGUAGE), AGENT_LANGUAGE_ENV
    )


def agent_text(*, zh: str, en: str) -> str:
    """Return the agent-facing text in the run's language."""
    return en if agent_language() == "en" else zh
