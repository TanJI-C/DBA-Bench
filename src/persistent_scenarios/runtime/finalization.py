"""Final evaluation ordering helpers."""

from __future__ import annotations


def seal_pre_cleanup_evaluation(run, result: dict[str, object]) -> dict[str, object]:
    run.pre_cleanup_evaluation = dict(result)
    return result
