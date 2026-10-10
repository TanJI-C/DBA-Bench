from types import SimpleNamespace

import pytest

from src.scenarios.runtime import orchestrator as orchestrator_module
from src.scenarios.runtime.orchestrator import Orchestrator


def test_setup_completion_log_reports_environment_start_duration(monkeypatch, capsys):
    orchestrator = object.__new__(Orchestrator)
    orchestrator._setup_started_monotonic = 100.0
    orchestrator.scenario = SimpleNamespace(description="timed scenario")
    monkeypatch.setattr(orchestrator_module.time, "monotonic", lambda: 223.4567)

    orchestrator._log_setup_complete()

    assert capsys.readouterr().out == (
        ">>> [Orchestrator] Setup complete. setup_duration_seconds=123.457 "
        "Scenario: timed scenario\n"
    )


def test_setup_completion_log_rejects_missing_start_time():
    orchestrator = object.__new__(Orchestrator)
    orchestrator._setup_started_monotonic = None
    orchestrator.scenario = SimpleNamespace(description="untimed scenario")

    with pytest.raises(RuntimeError, match="before setup starts"):
        orchestrator._log_setup_complete()


def test_metric_history_target_capture_hook_receives_frozen_range():
    calls = []
    injector = SimpleNamespace(
        finalize_metric_history_target_capture=lambda context, start_ms, end_ms: calls.append(
            (context, start_ms, end_ms)
        )
    )
    context = object()
    orchestrator = object.__new__(Orchestrator)
    orchestrator.case_run = SimpleNamespace(
        injections=[SimpleNamespace(injector=injector, context=context)]
    )

    orchestrator._call_metric_history_target_capture_hooks(1_000, 2_000)

    assert calls == [(context, 1_000, 2_000)]
