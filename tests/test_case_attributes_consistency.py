"""case_attributes.yaml entries must agree with the code registry calibration.

The registry (``DifficultyCalibration``) is the single source of truth for
difficulty values; the yaml annotations repeat the derived attributes for the
run table and must never drift from it.
"""

from pathlib import Path

import pytest
import yaml

from src.scenarios import SCENARIO_REGISTRY

REPO_ROOT = Path(__file__).resolve().parents[1]

ATTRIBUTE_PATHS = (
    REPO_ROOT / "data/scenarios/postgres_case_attributes.yaml",
    REPO_ROOT / "data/scenarios/tidb_case_attributes.yaml",
)


def _registry_index() -> dict[tuple[str, str], object]:
    index: dict[tuple[str, str], object] = {}
    for registration in SCENARIO_REGISTRY:
        for case in registration.scenario.cases:
            index[(registration.scenario_id, case.case_id)] = case
    return index


def _yaml_entries():
    entries = []
    for path in ATTRIBUTE_PATHS:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        for entry in payload["cases"]:
            entries.append((path.name, entry))
    return entries


def test_case_attributes_match_registry_calibration():
    index = _registry_index()
    failures = []
    for source, entry in _yaml_entries():
        if entry["case_id"] is None:
            # Persistent-scenario annotations have no bounded-registry equivalent.
            continue
        key = (entry["scenario_id"], entry["case_id"])
        case = index.get(key)
        if case is None:
            failures.append(f"{source}: {key} not in the code registry")
            continue
        calibration = case.difficulty
        if calibration is None:
            failures.append(f"{source}: {key} uncalibrated in the registry but annotated in yaml")
            continue
        depth = "deep" if calibration.diagnostic_depth > 2 else "direct"
        complexity = "high" if calibration.environmental_complexity >= 0.5 else "low"
        if entry["difficulty"] != calibration.label:
            failures.append(
                f"{source}: {key} label {entry['difficulty']!r} != registry {calibration.label!r}"
            )
        if entry["diagnostic_depth"] != depth:
            failures.append(
                f"{source}: {key} diagnostic_depth {entry['diagnostic_depth']!r} != registry {depth!r} "
                f"(diagnostic_depth={calibration.diagnostic_depth})"
            )
        if entry["environmental_complexity"] != complexity:
            failures.append(
                f"{source}: {key} environmental_complexity {entry['environmental_complexity']!r} != "
                f"registry {complexity!r} (complexity={calibration.environmental_complexity})"
            )
    assert not failures, "\n".join(failures)


def test_yaml_labels_follow_the_depth_complexity_rule():
    for source, entry in _yaml_entries():
        expected = (
            "hard"
            if entry["diagnostic_depth"] == "deep" and entry["environmental_complexity"] == "high"
            else "easy"
        )
        assert entry["difficulty"] == expected, (
            f"{source}: {entry['scenario_id']}/{entry['case_id']} label {entry['difficulty']!r} "
            f"contradicts depth={entry['diagnostic_depth']!r}/complexity={entry['environmental_complexity']!r}"
        )
