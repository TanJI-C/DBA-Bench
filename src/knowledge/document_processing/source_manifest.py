"""Source-lock and file-manifest helpers for immutable documentation snapshots."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


SOURCE_LOCK_FILENAME = ".source-lock.json"
SOURCE_MANIFEST_FILENAME = ".source-manifest.json"


@dataclass(frozen=True)
class SourceFileRecord:
    path: str
    kind: str
    size: int
    sha256: str


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def file_kind(path: Path) -> str:
    return "markdown" if path.suffix.casefold() in {".md", ".markdown"} else "asset"


def iter_snapshot_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in {SOURCE_LOCK_FILENAME, SOURCE_MANIFEST_FILENAME}:
            continue
        yield path


def build_source_file_records(root: Path) -> tuple[SourceFileRecord, ...]:
    return tuple(
        SourceFileRecord(
            path=path.relative_to(root).as_posix(),
            kind=file_kind(path),
            size=path.stat().st_size,
            sha256=sha256_file(path),
        )
        for path in iter_snapshot_files(root)
    )


def write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_source_manifest(root: Path, corpus_id: str) -> Path:
    records = build_source_file_records(root)
    manifest_path = root / SOURCE_MANIFEST_FILENAME
    write_json(
        manifest_path,
        {
            "corpus_id": corpus_id,
            "file_count": len(records),
            "files": [asdict(record) for record in records],
        },
    )
    return manifest_path


def load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: path={path}, type={type(payload).__name__}")
    return payload


def verify_source_manifest(root: Path) -> dict:
    manifest_path = root / SOURCE_MANIFEST_FILENAME
    manifest = load_json(manifest_path)
    expected = manifest.get("files")
    if not isinstance(expected, list):
        raise ValueError(f"Source manifest files must be a list: path={manifest_path}")
    actual = [asdict(record) for record in build_source_file_records(root)]
    if expected != actual:
        raise ValueError(
            f"Source manifest mismatch: root={root}, expected_count={len(expected)}, "
            f"actual_count={len(actual)}"
        )
    if manifest.get("file_count") != len(actual):
        raise ValueError(
            f"Source manifest file_count mismatch: path={manifest_path}, "
            f"declared={manifest.get('file_count')!r}, actual={len(actual)}"
        )
    return manifest
