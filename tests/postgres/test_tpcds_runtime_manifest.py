import json
import shutil
import subprocess
from pathlib import Path

import pytest

from src.execution.deployments.postgres import PGDockerDeployment
from src.workloads.tpcds import TPCDSWorkload, TPCDSXWorkload


def prepare_checkout(root):
    root.mkdir()
    shutil.copyfile(Path(__file__).resolve().parents[2] / ".gitignore", root / ".gitignore")
    workload_root = root / "data" / "workloads"
    source = TPCDSWorkload(str(workload_root))
    Path(source.data_dir).mkdir(parents=True)
    for table in source.REQUIRED_TABLES:
        (Path(source.data_dir) / f"{table}.dat").write_text(f"{table}|1|\n")
    Path(source.tools_dir).mkdir(parents=True)
    (Path(source.tools_dir) / "tpcds.sql").write_text("CREATE TABLE customer (c_customer_sk integer);\n")
    for workload_type in (TPCDSWorkload, TPCDSXWorkload):
        workload = workload_type(str(workload_root))
        Path(workload.workload_dir).mkdir(exist_ok=True)
        workload._generate_init_sql()
        (Path(workload.workload_dir) / "manifest.json").write_text('{"reference": "published dataset"}\n')
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run([
        "git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "commit", "-qm", "fixture",
    ], cwd=root, check=True)
    return workload_root


def dataset_label(workload):
    deployment = PGDockerDeployment(
        workload_data_dir=workload.data_dir,
        init_sql_path=workload.get_init_sql_path(),
        dataset_manifest_path=workload.manifest_path,
    )
    return deployment._dataset_ready_label()


@pytest.mark.parametrize("workload_type", [TPCDSWorkload, TPCDSXWorkload])
def test_repeated_prepare_keeps_checkout_clean_and_validates_local_data(tmp_path, workload_type):
    root = tmp_path / "checkout"
    workload = workload_type(str(prepare_checkout(root)))
    published = [root / "data" / "workloads" / name / "manifest.json" for name in ("tpcds", "tpcdsx")]
    snapshots = [path.read_bytes() for path in published]
    workload.prepare()
    original_manifest = Path(workload.manifest_path).read_bytes()
    original_label = dataset_label(workload)
    workload.prepare()
    assert Path(workload.manifest_path).read_bytes() == original_manifest
    assert dataset_label(workload) == original_label
    assert original_manifest.endswith(b"\n")
    manifest = json.loads(original_manifest)
    assert (Path(workload.manifest_path).parent / manifest["init_sql"]).resolve() == Path(workload.get_init_sql_path())

    # Generated metadata still belongs to the actual dataset: do not discard its hash.
    version = Path(workload.data_dir) / "dbgen_version.dat"
    version.write_text("2.10.0|2026-10-15|local generator command|\n")
    with pytest.raises(RuntimeError, match="Dataset data file (size|hash) differs"):
        dataset_label(workload)
    workload.prepare()
    assert dataset_label(workload) != original_label
    assert [path.read_bytes() for path in published] == snapshots
    assert subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True) == ""


@pytest.mark.parametrize("workload_type", [TPCDSWorkload, TPCDSXWorkload])
def test_runtime_fingerprint_is_independent_of_checkout_location(tmp_path, workload_type):
    labels = []
    for name in ("first", "relocated"):
        workload = workload_type(str(prepare_checkout(tmp_path / name)))
        workload.prepare()
        labels.append(dataset_label(workload))
    assert labels[0] == labels[1]


def test_pre_generated_dataset_needs_no_generator_to_write_runtime_manifest(tmp_path):
    root = tmp_path / "checkout"
    workload = TPCDSWorkload(str(prepare_checkout(root)))
    shutil.rmtree(workload.tpcds_kit_dir)
    workload.prepare()
    assert workload.load_manifest()["schema_source"] == "init.sql"
    assert dataset_label(workload).startswith("tpcds-ready-v3-")
    assert subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True) == ""
