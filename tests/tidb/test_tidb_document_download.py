from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts.download_tidb_documentation import archive_documentation
from src.knowledge.document_processing.source_manifest import verify_source_manifest


def git(command: list[str], cwd: Path) -> str:
    result = subprocess.run(["git", *command], cwd=cwd, text=True, capture_output=True, check=True)
    return result.stdout.strip()


def source_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "source"
    repository.mkdir()
    git(["init", "-b", "release-8.1"], repository)
    git(["config", "user.name", "AiOpsBench Test"], repository)
    git(["config", "user.email", "aiopsbench@example.invalid"], repository)
    (repository / "README.md").write_text("# Repository\n", encoding="utf-8")
    (repository / "TOC.md").write_text("# TOC\n\n- [Guide](guide.md)\n", encoding="utf-8")
    (repository / "guide.md").write_text("# Guide\n\nOfficial content.\n", encoding="utf-8")
    (repository / "LICENSE").write_text("CC BY-SA 3.0\n", encoding="utf-8")
    (repository / "media").mkdir()
    (repository / "media" / "diagram.svg").write_text("<svg/>\n", encoding="utf-8")
    git(["add", "."], repository)
    git(["commit", "-m", "fixture"], repository)
    return repository, git(["rev-parse", "HEAD"], repository)


def test_download_archives_exact_commit_and_complete_manifest(tmp_path):
    repository, commit = source_repository(tmp_path)
    output = tmp_path / "snapshot"

    archive_documentation(str(repository), "release-8.1", commit, output)

    lock = json.loads((output / ".source-lock.json").read_text(encoding="utf-8"))
    manifest = verify_source_manifest(output)
    assert lock["language"] == "en"
    assert lock["branch"] == "release-8.1"
    assert lock["commit"] == commit
    assert manifest["file_count"] == 5
    assert not (output / ".git").exists()
    assert (output / "media" / "diagram.svg").is_file()


def test_download_refuses_existing_snapshot(tmp_path):
    repository, commit = source_repository(tmp_path)
    output = tmp_path / "snapshot"
    output.mkdir()
    (output / "existing").write_text("do not overwrite", encoding="utf-8")

    with pytest.raises(FileExistsError, match="must not exist or must be empty"):
        archive_documentation(str(repository), "release-8.1", commit, output)


def test_download_fails_on_commit_mismatch(tmp_path):
    repository, _ = source_repository(tmp_path)
    with pytest.raises(RuntimeError, match="Command failed"):
        archive_documentation(
            str(repository),
            "release-8.1",
            "0" * 40,
            tmp_path / "snapshot",
        )
