from pathlib import Path

from src.execution.deployments.postgres import PGDockerDeployment
from src.workloads.postgres import DemoWorkload


def test_demo_dataset_satisfies_the_deployment_manifest_contract(tmp_path):
    workload = DemoWorkload(workload_root=str(tmp_path))
    workload.prepare()
    deployment = PGDockerDeployment(
        workload_data_dir=workload.data_dir,
        dataset_manifest_path=workload.manifest_path,
        init_sql_path=workload.get_init_sql_path(),
    )
    first = deployment._dataset_ready_label()
    workload.prepare()
    assert deployment._dataset_ready_label() == first
    assert "/workload_data/demo_users.dat" in Path(workload.get_init_sql_path()).read_text()
