"""DB-GPT-style expert knowledge retrieval."""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class KnowledgeSnippet:
    expert_name: str
    content: str
    source: str
    metadata: Dict[str, Any]
    relevance: float = 0.0


class DbotKnowledge:
    """Load and query DB-GPT expert knowledge files.

    DB-GPT stores knowledge by expert knowledge base. AiOpsBench keeps the same
    shape when local files are provided: JSON/JSONL records with desc, metrics,
    steps, source, and optional expert_name.
    """

    def __init__(self, paths: Optional[List[str]] = None, top_k: int = 5):
        self.top_k = top_k
        self.snippets: List[KnowledgeSnippet] = []
        if paths:
            self._load_paths(paths)
            if not self.snippets:
                raise RuntimeError(f"D-Bot knowledge paths loaded no snippets: paths={paths!r}")

    def _load_paths(self, paths: Iterable[str]):
        for path in paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"D-Bot knowledge path does not exist: {path}")
            if os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for fname in sorted(files):
                        if fname.endswith((".json", ".jsonl", ".txt", ".md")):
                            self._load_file(os.path.join(root, fname))
            else:
                self._load_file(path)

    def _load_file(self, path: str):
        expert_name = self._infer_expert_name(path)
        if path.endswith(".jsonl"):
            with open(path, "r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    line = line.strip()
                    if line:
                        self._add_record(json.loads(line), path, expert_name, line_no)
            return
        if path.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for idx, record in enumerate(data, 1):
                    self._add_record(record, path, expert_name, idx)
            elif isinstance(data, dict):
                self._add_record(data, path, expert_name, 1)
            else:
                raise ValueError(f"Unsupported D-Bot knowledge JSON in {path}: {type(data).__name__}")
            return

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.snippets.append(KnowledgeSnippet(
            expert_name=expert_name,
            content=content,
            source=path,
            metadata={"source": path},
        ))

    def _add_record(self, record: Dict[str, Any], path: str, expert_name: str, index: int):
        content_parts = []
        for key in ("cause_name", "desc", "metrics", "steps"):
            value = record.get(key)
            if value:
                content_parts.append(f"{key}: {value}")
        if not content_parts:
            raise ValueError(f"D-Bot knowledge record has no usable fields: path={path}, index={index}")
        metadata = dict(record)
        metadata.setdefault("source", f"{path}:{index}")
        self.snippets.append(KnowledgeSnippet(
            expert_name=record.get("expert_name") or expert_name,
            content="\n".join(content_parts),
            source=metadata["source"],
            metadata=metadata,
        ))

    def retrieve(self, query: str, expert_name: Optional[str] = None) -> List[KnowledgeSnippet]:
        if not self.snippets:
            raise RuntimeError("D-Bot knowledge retrieval requested before any snippets were loaded")
        keywords = {kw for kw in query.lower().split() if kw}
        scored = []
        for snippet in self.snippets:
            if expert_name and snippet.expert_name.lower() != expert_name.lower():
                continue
            content = snippet.content.lower()
            score = sum(1 for kw in keywords if kw in content)
            if score > 0:
                scored.append((score, snippet))
        scored.sort(key=lambda item: item[0], reverse=True)
        results = []
        for score, snippet in scored[: self.top_k]:
            snippet.relevance = score / max(len(keywords), 1)
            results.append(snippet)
        return results

    def expert_names(self) -> List[str]:
        return sorted({snippet.expert_name for snippet in self.snippets})

    def _infer_expert_name(self, path: str) -> str:
        parts = os.path.normpath(path).split(os.sep)
        for part in reversed(parts):
            if part.endswith("Expert"):
                return part
        stem = os.path.splitext(os.path.basename(path))[0]
        if stem.endswith("Expert"):
            return stem
        return "GeneralExpert"
