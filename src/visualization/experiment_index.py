from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


class ExperimentIndex:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def list_experiments(self) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        experiments = []
        for manifest_path in self.root.glob("*/manifest.yaml"):
            experiment_root = manifest_path.parent
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            records = self._records(experiment_root)
            experiments.append({
                "experiment_id": manifest["experiment_id"],
                "runs": len(records),
                "succeeded": sum(record["status"] == "succeeded" for record in records),
                "failed": sum(record["status"] in {"failed", "timed_out", "interrupted"} for record in records),
                "updated": max((record.get("finished_at") or record.get("started_at") or "" for record in records), default=""),
            })
        return sorted(experiments, key=lambda item: item["updated"], reverse=True)

    def query_runs(self, experiment_id: str, params: dict[str, list[str]]) -> dict[str, Any]:
        experiment_root = (self.root / experiment_id).resolve()
        experiment_root.relative_to(self.root)
        if not (experiment_root / "manifest.yaml").is_file():
            raise FileNotFoundError(f"Experiment not found: {experiment_id}")
        records = self._records(experiment_root)
        query = params.get("q", [""])[0].strip().lower()
        if query:
            records = [record for record in records if query in " ".join(
                str(record.get(key) or "")
                for key in ("run_id", "scenario_id", "case_id", "agent_id", "model")
            ).lower()]
        for parameter, field in (("scenario", "scenario_id"), ("agent", "agent_id"), ("status", "status")):
            value = params.get(parameter, [""])[0]
            if value:
                records = [record for record in records if record.get(field) == value]
        records.sort(key=lambda record: record.get("started_at") or "", reverse=True)
        total = len(records)
        offset = int(params.get("offset", ["0"])[0])
        limit = int(params.get("limit", ["100"])[0])
        if offset < 0 or limit < 1 or limit > 500:
            raise ValueError(f"Invalid pagination: offset={offset}, limit={limit}; limit must be 1..500")
        all_records = self._records(experiment_root)
        return {
            "experiment_id": experiment_id,
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": records[offset:offset + limit],
            "filters": {
                "scenarios": sorted({record["scenario_id"] for record in all_records}),
                "agents": sorted({record["agent_id"] for record in all_records}),
                "statuses": sorted({record["status"] for record in all_records}),
            },
        }

    @staticmethod
    def _records(experiment_root: Path) -> list[dict[str, Any]]:
        index_path = experiment_root / "runs.jsonl"
        if not index_path.exists():
            return []
        return [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines() if line]
