"""Public-surface vocabulary guard: development-lineage markers live in docs/ only.

The sync export set mirrors this scan scope (whitelist minus docs). docs/ is
excluded by design: the lineage standards under docs/standards/scenario/ are the
one place these terms are allowed to appear.
"""

import re
from pathlib import Path


# Anchored at this file's checkout, not src.project_paths.REPOSITORY_ROOT: linked
# worktrees resolve that to the main checkout, but each checkout must guard its
# own surface.
REPO_ROOT = Path(__file__).resolve().parents[1]

MARKER_RE = re.compile(
    r"metric[-_ ]?first|kb[-_ ]?first|knowledge[-_ ]?first|db[-_ ]?agent式",
    re.IGNORECASE,
)
SCAN_DIRS = ("src", "tests", "examples", "config", "data", "knowledge")
SCAN_SUFFIXES = {
    ".py", ".yaml", ".yml", ".json", ".js", ".css", ".html", ".md",
    ".txt", ".sh", ".toml", ".cfg", ".example",
}
# data/workloads/tpcds/tpcds-kit is vendored upstream content outside this
# repository's authoring surface.
EXCLUDED_PATHS = (
    Path("tests/test_agent_facing_text.py"),
    Path("data") / "workloads" / "tpcds" / "tpcds-kit",
)


def _is_excluded(relative: Path) -> bool:
    return any(relative == excluded or excluded in relative.parents for excluded in EXCLUDED_PATHS)


def test_public_surface_has_no_design_lineage_markers():
    hits = []
    for scan_dir in SCAN_DIRS:
        base = REPO_ROOT / scan_dir
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            relative = path.relative_to(REPO_ROOT)
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES or _is_excluded(relative):
                continue
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if MARKER_RE.search(line):
                    hits.append(f"{relative}:{lineno}: {line.strip()[:120]}")
    assert not hits, "development-lineage markers leaked outside docs/:\n" + "\n".join(hits[:40])
