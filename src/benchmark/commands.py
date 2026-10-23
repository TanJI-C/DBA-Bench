"""Target-independent command helpers shared by benchmark adapters."""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path


def container_name(prefix: str, run_id: str) -> str:
    value = f"{prefix}-{run_id}"
    if len(value) <= 120:
        return value
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{value[:107]}-{digest}"


def script_options(script_path: Path) -> set[str]:
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
    options = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "add_diagnosis_arguments":
            from src.scenarios.evaluation import config

            options.update(script_options(Path(config.__file__)))
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr == "add_argument":
            options.update(
                item.value
                for item in node.args
                if isinstance(item, ast.Constant)
                and isinstance(item.value, str)
                and item.value.startswith("--")
            )
    return options
