"""Validated calibration artifact admission for PersistentScenario model definitions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .spec import PersistentScenarioSpec
from .enums import CalibrationStatus


def _validated_calibration_artifact(spec: PersistentScenarioSpec, artifact_root: str | Path | None = None) -> Path:
    if spec.calibration.status is not CalibrationStatus.VALIDATED:
        raise ValueError(
            "Formal PersistentScenario execution requires validated calibration: "
            f"scenario_id={spec.scenario_id!r}, status={spec.calibration.status.value!r}, "
            f"evidence_id={spec.calibration.evidence_id!r}"
        )
    root = Path(artifact_root) if artifact_root is not None else Path(__file__).resolve().parents[3] / "artifacts" / "calibration"
    artifact = root / f"{spec.calibration.evidence_id}.json"
    if not artifact.is_file():
        raise FileNotFoundError(
            "Validated PersistentScenario calibration artifact does not exist: "
            f"scenario_id={spec.scenario_id!r}, evidence_id={spec.calibration.evidence_id!r}, path={artifact}"
        )
    artifact_data = json.loads(artifact.read_text(encoding="utf-8"))
    if not isinstance(artifact_data, dict) or artifact_data.get("evidence_id") != spec.calibration.evidence_id:
        raise ValueError(
            "Validated PersistentScenario calibration artifact does not match the PersistentScenario evidence ID: "
            f"scenario_id={spec.scenario_id!r}, expected={spec.calibration.evidence_id!r}, "
            f"artifact_value={artifact_data.get('evidence_id') if isinstance(artifact_data, dict) else None!r}, "
            f"path={artifact}"
        )
    return artifact


def require_validated_calibration(spec: PersistentScenarioSpec, artifact_root: str | Path | None = None) -> str:
    return hashlib.sha256(_validated_calibration_artifact(spec, artifact_root).read_bytes()).hexdigest()
