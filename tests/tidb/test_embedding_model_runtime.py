from contextlib import nullcontext

import pytest

from src.knowledge import embedding_model_runtime as runtime


def probe(status: str, model: str = "model") -> runtime.EmbeddingModelProbe:
    return runtime.EmbeddingModelProbe(
        base_url="http://127.0.0.1:8765",
        model=model,
        status=status,
        detail=status,
    )


def test_ensure_reuses_ready_service(monkeypatch):
    ready = probe("ready")
    monkeypatch.setattr(runtime, "probe_embedding_model", lambda *args, **kwargs: ready)
    monkeypatch.setattr(
        runtime,
        "_start_detached",
        lambda *args, **kwargs: pytest.fail("ready service must not be started"),
    )

    assert runtime.ensure_embedding_model("model", "cuda") is ready


def test_ensure_starts_once_after_locked_recheck(monkeypatch, tmp_path):
    unavailable = probe("unavailable")
    started = probe("ready")
    probes = iter((unavailable, unavailable))
    monkeypatch.setattr(runtime, "probe_embedding_model", lambda *args, **kwargs: next(probes))
    monkeypatch.setattr(runtime, "_embedding_start_lock", lambda port: nullcontext())
    calls = []

    def start(model, device, host, port, wait_seconds):
        calls.append((model, device, host, port, wait_seconds))
        return started

    monkeypatch.setattr(runtime, "_start_detached", start)
    monkeypatch.setenv("AIOPS_EMBEDDING_MODEL_LOCK", str(tmp_path / "embedding.lock"))

    assert runtime.ensure_embedding_model("model", "cuda", wait_seconds=17) is started
    assert calls == [("model", "cuda", "127.0.0.1", 8765, 17)]


def test_ensure_uses_locked_recheck_when_another_process_started(monkeypatch):
    unavailable = probe("unavailable")
    ready = probe("ready")
    probes = iter((unavailable, ready))
    monkeypatch.setattr(runtime, "probe_embedding_model", lambda *args, **kwargs: next(probes))
    monkeypatch.setattr(
        runtime,
        "_start_detached",
        lambda *args, **kwargs: pytest.fail("locked ready service must be reused"),
    )
    monkeypatch.setattr(runtime, "_embedding_start_lock", lambda port: nullcontext())

    assert runtime.ensure_embedding_model("model", "cuda") is ready


def test_ensure_rejects_model_mismatch_without_start(monkeypatch):
    mismatch = probe("model_mismatch")
    monkeypatch.setattr(runtime, "probe_embedding_model", lambda *args, **kwargs: mismatch)
    monkeypatch.setattr(
        runtime,
        "_start_detached",
        lambda *args, **kwargs: pytest.fail("model mismatch must not be replaced"),
    )

    with pytest.raises(runtime.EmbeddingModelUnavailable, match="must not be replaced"):
        runtime.ensure_embedding_model("model", "cuda")


def test_ensure_rejects_unavailable_remote_endpoint(monkeypatch):
    unavailable = probe("unavailable")
    monkeypatch.setattr(runtime, "probe_embedding_model", lambda *args, **kwargs: unavailable)

    with pytest.raises(ValueError, match="cannot be auto-started because it is not local"):
        runtime.ensure_embedding_model("model", "cuda", base_url="http://embedding.example:8765")
