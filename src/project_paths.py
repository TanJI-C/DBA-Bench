"""Repository asset paths shared by source-checkout entry points.

Linked worktrees share the main checkout's Git common directory.  Resolve
repository assets from that common directory so generated data is not copied
into individual worktrees.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent.parent


def _git_common_root(source_root: Path) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        cwd=source_root,
        check=True,
        capture_output=True,
        text=True,
    )
    common_dir = Path(result.stdout.strip())
    if not common_dir.is_absolute():
        common_dir = source_root / common_dir
    return common_dir.resolve().parent


def _repository_root() -> Path:
    source_root = SOURCE_ROOT
    configured_root = os.environ.get("AIOPSBENCH_PROJECT_ROOT")
    if configured_root is not None:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=Path(configured_root),
            check=True,
            capture_output=True,
            text=True,
        )
        resolved_root = Path(result.stdout.strip()).resolve()
        expected_root = Path(configured_root).resolve()
        if resolved_root != expected_root:
            raise RuntimeError(
                "AIOPSBENCH_PROJECT_ROOT does not match the Git checkout used by the runner: "
                f"configured_root={expected_root!s}, resolved_root={resolved_root!s}"
            )
        return resolved_root
    return _git_common_root(source_root)


def _shared_repository_root() -> Path:
    source_root = Path(__file__).resolve().parent.parent
    return _git_common_root(source_root)


REPOSITORY_ROOT = _repository_root()
SHARED_REPOSITORY_ROOT = _shared_repository_root()


def persistent_scenario_definition_roots(project_root: Path = SOURCE_ROOT) -> tuple[Path, ...]:
    base = project_root / "src" / "persistent_scenarios"
    return (base / "postgres", base / "tidb")
ARTIFACTS_ROOT = REPOSITORY_ROOT / "artifacts"
EXPERIMENTS_ROOT = ARTIFACTS_ROOT / "experiments"
DATASETS_ROOT = REPOSITORY_ROOT / "datasets"
CALIBRATION_ARTIFACT_ROOT = ARTIFACTS_ROOT / "calibration"


def repository_path(*parts: str) -> Path:
    return REPOSITORY_ROOT.joinpath(*parts)


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPOSITORY_ROOT / candidate


def resolve_shared_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else SHARED_REPOSITORY_ROOT / candidate
