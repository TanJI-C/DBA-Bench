import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src import cli


@pytest.fixture
def checkout(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    source = tmp_path / "source.txt"
    source.write_text("committed\n")
    subprocess.run(["git", "add", "source.txt"], cwd=tmp_path, check=True)
    subprocess.run([
        "git", "-c", "user.name=Test", "-c", "user.email=test@example.com",
        "commit", "-qm", "fixture",
    ], cwd=tmp_path, check=True)
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True,
    ).strip()
    source.write_text("local modification\n")
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    (artifacts / "output.json").write_text("{}\n")
    monkeypatch.setattr(cli, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(cli, "EXPERIMENTS_ROOT", artifacts / "experiments")
    monkeypatch.setattr(cli, "load_manifest", lambda path: SimpleNamespace(experiment_id="pilot"))
    monkeypatch.setattr(cli, "plan_runs", lambda manifest: ("run-1",))
    monkeypatch.setattr(cli, "select_specs", lambda specs, run_ids: specs)
    monkeypatch.setattr(cli, "validate_execution_plan", lambda manifest, specs: ())
    runner = Mock()
    runner.run.return_value = 0
    monkeypatch.setattr(cli, "ExperimentRunner", Mock(return_value=runner))
    return commit, runner


@pytest.mark.parametrize("resume,rerun", [(False, set()), (True, set()), (False, {"failed"})])
def test_experiment_accepts_local_changes_and_untracked_outputs(checkout, resume, rerun):
    commit, runner = checkout
    if resume or rerun:
        store = cli.ExperimentStore(cli.EXPERIMENTS_ROOT, "pilot")
        store.initialize({"experiment_id": "pilot"}, {"git_commit": commit})

    assert cli.execute_experiment(
        cli.PROJECT_ROOT / "experiment.yaml", resume=resume, rerun=rerun, run_ids=[],
    ) == 0
    runner.initialize.assert_called_once_with(("run-1",))
    runner.run.assert_called_once_with(("run-1",), rerun)


@pytest.mark.parametrize("resume,rerun", [(True, set()), (False, {"failed"})])
def test_resume_and_rerun_still_require_original_commit(checkout, resume, rerun):
    _, runner = checkout
    store = cli.ExperimentStore(cli.EXPERIMENTS_ROOT, "pilot")
    store.initialize({"experiment_id": "pilot"}, {"git_commit": "different-commit"})

    with pytest.raises(RuntimeError, match="requires its original Git commit"):
        cli.execute_experiment(
            cli.PROJECT_ROOT / "experiment.yaml", resume=resume, rerun=rerun, run_ids=[],
        )
    runner.run.assert_not_called()
