from __future__ import annotations

import subprocess
from pathlib import Path


def git_worktrees(cwd: Path) -> list[Path]:
    out = subprocess.check_output(
        ["git", "-C", str(cwd), "worktree", "list", "--porcelain"],
        text=True,
    )
    return [
        Path(line.split(" ", 1)[1]).resolve()
        for line in out.splitlines()
        if line.startswith("worktree ")
    ]


def main_worktree(cwd: Path) -> Path:
    worktrees = git_worktrees(cwd)
    if not worktrees:
        raise RuntimeError(f"git reported no worktrees for {cwd}")
    return worktrees[0]


def report_path_for_workspace(report: Path, cwd: Path) -> Path:
    cwd = cwd.resolve()
    main = main_worktree(cwd)
    report = report if report.is_absolute() else cwd / report
    report = report.resolve()
    current_reports = cwd / "docs" / "reports"
    main_reports = main / "docs" / "reports"
    if cwd != main and report.is_relative_to(current_reports):
        return main_reports / report.relative_to(current_reports)
    return report


def reports_root_for(report: Path) -> Path:
    report = report.resolve()
    for parent in report.parents:
        if parent.name == "reports" and parent.parent.name == "docs":
            return parent
    raise ValueError(f"report must live under docs/reports: {report}")
