#!/usr/bin/env python3
"""Archive one exact TiDB official-documentation commit."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT, resolve_project_path  # noqa: E402
from src.knowledge.document_processing.source_manifest import (  # noqa: E402
    SOURCE_LOCK_FILENAME,
    write_json,
    write_source_manifest,
)


PROJECT_ROOT = REPOSITORY_ROOT


DEFAULT_REPOSITORY = "https://github.com/pingcap/docs.git"
DEFAULT_BRANCH = "release-8.1"
DEFAULT_COMMIT = "d9124e84872b8f9915123444ab4402f9a36c33c9"
CORPUS_ID = "tidb-official-docs-8.1-en"


def run(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: command={command!r}, cwd={str(cwd)!r}, "
            f"returncode={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr!r}"
        )
    return result.stdout.strip()


def require_empty_output(output_dir: Path) -> None:
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(
            f"TiDB documentation output directory must not exist or must be empty: output_dir={output_dir}"
        )


def verify_snapshot(snapshot_dir: Path) -> None:
    for required in ("README.md", "TOC.md", "LICENSE"):
        path = snapshot_dir / required
        if not path.is_file():
            raise FileNotFoundError(
                f"Required TiDB source file is missing: snapshot_dir={snapshot_dir}, required={required!r}"
            )
    markdown_files = sorted(snapshot_dir.rglob("*.md"))
    if not markdown_files:
        raise ValueError(f"TiDB source snapshot contains no Markdown files: snapshot_dir={snapshot_dir}")
    for path in markdown_files:
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"TiDB Markdown is not UTF-8: path={path}, error={exc}") from exc
    if (snapshot_dir / ".git").exists():
        raise ValueError(f"Exported TiDB snapshot contains nested .git directory: snapshot_dir={snapshot_dir}")


def archive_documentation(
    repository: str,
    branch: str,
    expected_commit: str,
    output_dir: Path,
) -> None:
    require_empty_output(output_dir)
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="tidb-docs-fetch-", dir=output_dir.parent) as temp_name:
        temp_root = Path(temp_name)
        repository_dir = temp_root / "repository"
        export_dir = temp_root / "export"
        repository_dir.mkdir()
        export_dir.mkdir()
        run(["git", "init"], repository_dir)
        run(["git", "remote", "add", "origin", repository], repository_dir)
        run(["git", "fetch", "--depth", "1", "origin", expected_commit], repository_dir)
        resolved_commit = run(["git", "rev-parse", "FETCH_HEAD^{commit}"], repository_dir)
        if resolved_commit != expected_commit:
            raise ValueError(
                f"TiDB source commit mismatch: repository={repository!r}, branch={branch!r}, "
                f"expected_commit={expected_commit!r}, resolved_commit={resolved_commit!r}"
            )
        archive_path = temp_root / "snapshot.tar"
        run(["git", "archive", "--format=tar", "-o", str(archive_path), resolved_commit], repository_dir)
        with tarfile.open(archive_path) as archive:
            archive.extractall(export_dir)
        verify_snapshot(export_dir)
        lock = {
            "corpus_id": CORPUS_ID,
            "product": "TiDB",
            "language": "en",
            "repository": repository,
            "branch": branch,
            "commit": resolved_commit,
            "website_base_url": "https://docs.pingcap.com/tidb/stable",
            "github_blob_base_url": f"https://github.com/pingcap/docs/blob/{resolved_commit}",
            "downloaded_at": datetime.now(timezone.utc).isoformat(),
            "license": "CC BY-SA 3.0",
        }
        write_json(export_dir / SOURCE_LOCK_FILENAME, lock)
        write_source_manifest(export_dir, CORPUS_ID)
        if output_dir.exists():
            output_dir.rmdir()
        shutil.move(str(export_dir), output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--branch", default=DEFAULT_BRANCH)
    parser.add_argument("--expected-commit", default=DEFAULT_COMMIT)
    parser.add_argument("--output-dir", type=Path, default=Path("knowledge/tidb_src"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    archive_documentation(
        args.repository,
        args.branch,
        args.expected_commit,
        resolve_project_path(args.output_dir),
    )
    print(f"Archived TiDB official documentation to {resolve_project_path(args.output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
