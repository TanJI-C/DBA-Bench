from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from src.benchmark.result_identity import (
    analysis_run_filename,
    result_run_filename,
    result_run_key,
    validate_case_tag,
)

# Persistent-scenario sets declare domain: persistent_scenario and use their own
# run schema / scenario shards; the /results page renders only the bounded
# five-category contract, so declared persistent sets are excluded everywhere here.
PERSISTENT_DOMAIN = "persistent_scenario"


class ResultSetIndex:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def list_result_sets(self) -> list[dict[str, Any]]:
        if not self.root.exists():
            return []
        result_sets = []
        for manifest_path in self.root.glob("*/*/result-set.yaml"):
            manifest = self._manifest(manifest_path)
            if manifest.get("domain") == PERSISTENT_DOMAIN:
                continue
            result_sets.append({
                "result_set_id": manifest["result_set_id"],
                "system": manifest["system"],
                "state": manifest["state"],
                "categories": [item["id"] for item in manifest["categories"]],
                "models": [item["id"] for item in manifest["models"]],
                "expected_runs": manifest["expected_runs"],
            })
        return sorted(result_sets, key=lambda item: item["result_set_id"])

    def result_set(self, result_set_id: str) -> dict[str, Any]:
        root, manifest = self._find(result_set_id)
        return {
            **manifest,
            "categories": [
                {
                    **category,
                    "url": (
                        f"/api/result-sets/{result_set_id}/categories/{category['id']}"
                    ),
                }
                for category in manifest["categories"]
            ],
            "root": str(root.relative_to(self.root)),
        }

    def category(self, result_set_id: str, category_id: str) -> dict[str, Any]:
        root, manifest = self._find(result_set_id)
        categories = {item["id"]: item for item in manifest["categories"]}
        if category_id not in categories:
            raise FileNotFoundError(
                f"ResultSet category not found: result_set_id={result_set_id!r}, "
                f"category_id={category_id!r}"
            )
        catalog_path = root / "catalog" / f"{category_id}.json"
        catalog = self._json_object(catalog_path)
        if catalog.get("category_id") != category_id or not isinstance(catalog.get("cases"), list):
            raise ValueError(f"Invalid ResultSet catalog: path={catalog_path}")

        case_keys = {(case["scenario_id"], case["case_id"]) for case in catalog["cases"]}
        if len(case_keys) != len(catalog["cases"]):
            raise ValueError(f"Duplicate ScenarioCase in ResultSet catalog: path={catalog_path}")
        tags = [validate_case_tag(case) for case in catalog["cases"]]
        if len(tags) != len(set(tags)):
            raise ValueError(f"Duplicate ResultSet citation tags: path={catalog_path}, tags={tags!r}")
        invalid_difficulties = sorted({
            case.get("difficulty") for case in catalog["cases"]
            if str(case.get("difficulty", "")).lower() not in {"easy", "hard", "unknown"}
        })
        if invalid_difficulties:
            raise ValueError(
                f"ResultSet catalog difficulty must be easy or hard: "
                f"path={catalog_path}, values={invalid_difficulties!r}"
            )

        phase = "work" if manifest["state"] == "open" else "final"
        runs_dir = root / phase / "categories" / category_id
        runs = []
        model_ids = {model["id"] for model in manifest["models"]}
        if runs_dir.exists():
            for path in sorted(runs_dir.glob("models/*/runs/*.json")):
                run = self._json_object(path)
                required = {
                    "schema_version", "result_set_id", "category_id", "run_key",
                    "scenario_id", "case_id", "citation_tag", "model", "repetition", "seed",
                    "execution", "interaction", "tokens", "evaluation", "timing",
                    "fault_snapshot", "provenance",
                }
                missing = sorted(required - set(run))
                if missing:
                    raise ValueError(f"ResultSet Run is incomplete: path={path}, missing={missing!r}")
                if run["schema_version"] != "aiopsbench_result_run_v1":
                    raise ValueError(
                        f"Unsupported ResultSet Run schema: path={path}, "
                        f"schema_version={run['schema_version']!r}"
                    )
                if run["result_set_id"] != result_set_id:
                    raise ValueError(
                        f"Run ResultSet ID does not match its directory: path={path}, "
                        f"result_set_id={run['result_set_id']!r}"
                    )
                if run.get("category_id") != category_id:
                    raise ValueError(
                        f"Run category does not match its directory: path={path}, "
                        f"category_id={run.get('category_id')!r}"
                    )
                key = (run.get("scenario_id"), run.get("case_id"))
                if key not in case_keys:
                    raise ValueError(f"Run references a Case outside its catalog: path={path}, case={key!r}")
                agent_id = run["model"]["agent_id"]
                path_agent_id = path.relative_to(runs_dir).parts[1]
                if agent_id not in model_ids or agent_id != path_agent_id:
                    raise ValueError(
                        f"Run model does not match its model shard: path={path}, "
                        f"agent_id={agent_id!r}, path_agent_id={path_agent_id!r}"
                    )
                if not 1 <= run["repetition"] <= manifest["repetitions"]:
                    raise ValueError(
                        f"Run repetition is outside the ResultSet: path={path}, "
                        f"repetition={run['repetition']!r}, repetitions={manifest['repetitions']!r}"
                    )
                tag = validate_case_tag(run)
                expected_key = result_run_key(tag, agent_id, run["repetition"])
                expected_name = result_run_filename(tag, run["repetition"])
                if run["run_key"] != expected_key or path.name != expected_name:
                    raise ValueError(f"Result Run identity mismatch: path={path}, run_key={run['run_key']!r}, expected_key={expected_key!r}, expected_name={expected_name!r}")
                runs.append(run)
        run_keys = [run["run_key"] for run in runs]
        if len(run_keys) != len(set(run_keys)):
            raise ValueError(
                f"Duplicate run_key in ResultSet category: result_set_id={result_set_id!r}, "
                f"category_id={category_id!r}"
            )
        return {
            "result_set_id": result_set_id,
            "state": manifest["state"],
            "category": categories[category_id],
            "cases": catalog["cases"],
            "models": manifest["models"],
            "repetitions": manifest["repetitions"],
            "runs": runs,
        }

    def analysis(self, result_set_id: str) -> dict[str, Any]:
        root, manifest = self._find(result_set_id)
        category_ids = {item["id"] for item in manifest["categories"]}
        model_ids = {model["id"] for model in manifest["models"]}
        analyses: dict[str, Any] = {}
        for path in sorted((root / "analysis" / "diagnosis_path_review" / "runs").glob("*.json")):
            record = self._json_object(path)
            if record.get("schema_version") != "aiopsbench_run_analysis_v2":
                raise ValueError(
                    f"Unsupported ResultSet Run analysis schema: path={path}, "
                    f"schema_version={record.get('schema_version')!r}"
                )
            required = {
                "result_set_id", "category_id", "run_key", "scenario_id", "case_id", "citation_tag",
                "model", "repetition", "review_pass", "verdict", "dominant_label", "secondary_labels",
                "measurement_artifact",
            }
            missing = sorted(required - set(record))
            if missing:
                raise ValueError(
                    f"ResultSet Run analysis is incomplete: path={path}, missing={missing!r}"
                )
            if record["result_set_id"] != result_set_id:
                raise ValueError(
                    f"Run analysis ResultSet ID does not match its directory: path={path}, "
                    f"result_set_id={record['result_set_id']!r}"
                )
            if record["category_id"] not in category_ids:
                raise ValueError(
                    f"Run analysis references a category outside its ResultSet: path={path}, "
                    f"category_id={record['category_id']!r}"
                )
            agent_id = record["model"]["agent_id"]
            if agent_id not in model_ids:
                raise ValueError(
                    f"Run analysis references a model outside its ResultSet: path={path}, "
                    f"agent_id={agent_id!r}"
                )
            tag = validate_case_tag(record)
            run_key = record["run_key"]
            if (run_key != result_run_key(tag, agent_id, record["repetition"])
                    or path.name != analysis_run_filename(tag, agent_id, record["repetition"])):
                raise ValueError(f"Analysis citation identity mismatch: path={path}, run_key={run_key!r}")
            if run_key in analyses:
                raise ValueError(
                    f"Duplicate run_key in ResultSet analysis: "
                    f"result_set_id={result_set_id!r}, run_key={run_key!r}"
                )
            dominant_labels = (
                [record["dominant_label"]] if record["dominant_label"] else []
            ) + record["secondary_labels"]
            analyses[run_key] = {
                "review_pass": record["review_pass"],
                "verdict": record["verdict"],
                "dominant_labels": dominant_labels,
                "measurement_artifact": record["measurement_artifact"],
                "path": str(path.relative_to(root)),
            }
        return {"result_set_id": result_set_id, "analyses": analyses}

    def _find(self, result_set_id: str) -> tuple[Path, dict[str, Any]]:
        matches = []
        for manifest_path in self.root.glob("*/*/result-set.yaml"):
            manifest = self._manifest(manifest_path)
            if manifest.get("domain") == PERSISTENT_DOMAIN:
                continue
            if manifest["result_set_id"] == result_set_id:
                matches.append((manifest_path.parent, manifest))
        if not matches:
            raise FileNotFoundError(f"ResultSet not found: {result_set_id}")
        if len(matches) != 1:
            raise ValueError(f"ResultSet ID is not unique: result_set_id={result_set_id!r}")
        return matches[0]

    @staticmethod
    def _manifest(path: Path) -> dict[str, Any]:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError(f"ResultSet manifest must be an object: path={path}")
        if manifest.get("domain") == PERSISTENT_DOMAIN:
            return manifest
        required = {
            "result_set_id", "state", "system", "categories", "models", "repetitions", "expected_runs"
        }
        missing = sorted(required - set(manifest))
        if missing:
            raise ValueError(f"ResultSet manifest is incomplete: path={path}, missing={missing!r}")
        if manifest["state"] not in {"open", "sealed"}:
            raise ValueError(f"Invalid ResultSet state: path={path}, state={manifest['state']!r}")
        if len(manifest["categories"]) != 5:
            raise ValueError(
                f"PostgreSQL ResultSet must declare exactly five categories: "
                f"path={path}, count={len(manifest['categories'])}"
            )
        return manifest

    @staticmethod
    def _json_object(path: Path) -> dict[str, Any]:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError(f"ResultSet JSON must be an object: path={path}")
        return value
