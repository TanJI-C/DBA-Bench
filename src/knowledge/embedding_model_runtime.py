"""Lifecycle and HTTP client for the shared local embedding model service."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from fcntl import LOCK_EX, flock

from src.project_paths import SHARED_REPOSITORY_ROOT

PROJECT_ROOT = SHARED_REPOSITORY_ROOT
DEFAULT_EMBEDDING_MODEL_HOST = "127.0.0.1"
DEFAULT_EMBEDDING_MODEL_PORT = 8765
DEFAULT_EMBEDDING_MODEL_URL = (
    f"http://{DEFAULT_EMBEDDING_MODEL_HOST}:{DEFAULT_EMBEDDING_MODEL_PORT}"
)
DEFAULT_EMBEDDING_MODEL_WAIT_SECONDS = 600


class EmbeddingModelUnavailable(RuntimeError):
    """The configured embedding service cannot serve the requested model."""


@dataclass(frozen=True, slots=True)
class EmbeddingModelProbe:
    base_url: str
    model: str
    status: str
    detail: str

    @property
    def ready(self) -> bool:
        return self.status == "ready"


def default_embedding_model_url() -> str:
    return os.environ.get(
        "AIOPS_EMBEDDING_MODEL_URL", DEFAULT_EMBEDDING_MODEL_URL
    ).rstrip("/")


def default_embedding_model_lock_path(port: int) -> Path:
    configured = os.environ.get("AIOPS_EMBEDDING_MODEL_LOCK")
    if configured:
        return Path(configured)
    return Path("/tmp") / f"aiopsbench-embedding-model-{port}.lock"


def probe_embedding_model(
    base_url: str,
    model: str,
    *,
    timeout_seconds: float = 2.0,
) -> EmbeddingModelProbe:
    endpoint = f"{base_url.rstrip('/')}/health"
    request = Request(endpoint, headers={"Accept": "application/json"}, method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return EmbeddingModelProbe(base_url, model, "invalid_response", f"HTTP {exc.code} from {endpoint}")
    except (URLError, TimeoutError, OSError) as exc:
        return EmbeddingModelProbe(base_url, model, "unavailable", f"{type(exc).__name__}: {exc}")
    except json.JSONDecodeError as exc:
        return EmbeddingModelProbe(base_url, model, "invalid_response", f"Invalid JSON from {endpoint}: {exc}")

    if not isinstance(payload, dict) or payload.get("status") != "ready":
        return EmbeddingModelProbe(
            base_url,
            model,
            "invalid_response",
            f"expected ready health response, got={payload!r}",
        )
    served_model = payload.get("model")
    if served_model != model:
        return EmbeddingModelProbe(
            base_url,
            model,
            "model_mismatch",
            f"served_model={served_model!r}, dimension={payload.get('dimension')!r}",
        )
    return EmbeddingModelProbe(base_url, model, "ready", f"dimension={payload.get('dimension')!r}")


def _host_port(base_url: str) -> tuple[str, int]:
    parsed = urlsplit(base_url)
    if parsed.scheme != "http" or parsed.hostname is None or parsed.path not in {"", "/"}:
        raise ValueError(
            "Embedding model URL must be an http URL with no path: "
            f"base_url={base_url!r}"
        )
    return parsed.hostname, parsed.port or 80


def _ensure_local_endpoint(base_url: str) -> tuple[str, int]:
    host, port = _host_port(base_url)
    if host not in {"127.0.0.1", "localhost"}:
        raise ValueError(
            "Embedding model endpoint is unavailable and cannot be auto-started because it is not local: "
            f"base_url={base_url!r}"
        )
    return host, port


def _require_endpoint_unavailable(
    probe: EmbeddingModelProbe,
    endpoint: str,
    model: str,
) -> None:
    if probe.status != "unavailable":
        raise EmbeddingModelUnavailable(
            "Embedding model endpoint is not usable and must not be replaced: "
            f"status={probe.status}, detail={probe.detail}, base_url={endpoint}, model={model}"
        )


@contextmanager
def _embedding_start_lock(port: int) -> Iterator[None]:
    lock_path = default_embedding_model_lock_path(port)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        flock(lock_file.fileno(), LOCK_EX)
        yield


def _start_command(model: str, device: str, host: str, port: int) -> list[str]:
    return [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "start_embedding_model.py"),
        "--serve",
        "--model", model,
        "--device", device,
        "--host", host,
        "--port", str(port),
    ]


def _start_detached(
    model: str,
    device: str,
    host: str,
    port: int,
    wait_seconds: int,
) -> EmbeddingModelProbe:
    command = _start_command(model, device, host, port)
    log_path = PROJECT_ROOT / "logs" / "embedding_model.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log_file:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    endpoint = f"http://{host}:{port}"
    deadline = time.monotonic() + wait_seconds
    while True:
        if process.poll() is not None:
            raise RuntimeError(
                f"Embedding model server exited before ready: command={command!r}, "
                f"returncode={process.returncode}, log={log_path}"
            )
        probe = probe_embedding_model(endpoint, model)
        if probe.ready:
            return probe
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            process.send_signal(signal.SIGTERM)
            raise TimeoutError(
                f"Embedding model did not become ready within {wait_seconds}s: "
                f"endpoint={endpoint}, model={model!r}, log={log_path}, "
                f"last_status={probe.status}, detail={probe.detail}"
            )
        time.sleep(min(1.0, remaining))


def ensure_embedding_model(
    model: str,
    device: str,
    *,
    base_url: str | None = None,
    wait_seconds: int = DEFAULT_EMBEDDING_MODEL_WAIT_SECONDS,
) -> EmbeddingModelProbe:
    if wait_seconds < 1:
        raise ValueError(f"Embedding model wait_seconds must be positive: wait_seconds={wait_seconds}")
    endpoint = (base_url or default_embedding_model_url()).rstrip("/")
    probe = probe_embedding_model(endpoint, model)
    if probe.ready:
        return probe
    _require_endpoint_unavailable(probe, endpoint, model)
    host, port = _ensure_local_endpoint(endpoint)
    with _embedding_start_lock(port):
        probe = probe_embedding_model(endpoint, model)
        if probe.ready:
            return probe
        _require_endpoint_unavailable(probe, endpoint, model)
        return _start_detached(model, device, host, port, wait_seconds)


def request_embeddings(
    texts: list[str],
    model: str,
    device: str,
    *,
    prompt_name: str = "query",
    base_url: str | None = None,
) -> list[list[float]]:
    if not texts:
        raise ValueError("Embedding request requires at least one text")
    if prompt_name not in {"query", "text"}:
        raise ValueError(f"Embedding prompt_name must be 'query' or 'text': prompt_name={prompt_name!r}")
    endpoint = (base_url or default_embedding_model_url()).rstrip("/")
    ensure_embedding_model(model, device, base_url=endpoint)
    request = Request(
        f"{endpoint}/embed",
        data=json.dumps({"texts": texts, "prompt_name": prompt_name}, ensure_ascii=False).encode("utf-8"),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Embedding model request failed: endpoint={endpoint}, status={exc.code}, detail={detail}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise EmbeddingModelUnavailable(
            f"Embedding model request could not reach the ready endpoint: endpoint={endpoint}, error={exc}"
        ) from exc
    if not isinstance(payload, dict) or payload.get("status") != "success":
        raise RuntimeError(f"Embedding model returned an invalid response: endpoint={endpoint}, payload={payload!r}")
    embeddings = payload.get("embeddings")
    if not isinstance(embeddings, list) or len(embeddings) != len(texts):
        raise RuntimeError(
            f"Embedding model returned the wrong number of vectors: endpoint={endpoint}, expected={len(texts)}, actual={len(embeddings) if isinstance(embeddings, list) else type(embeddings).__name__}"
        )
    if any(not isinstance(vector, list) or not vector or any(not isinstance(value, (int, float)) for value in vector) for vector in embeddings):
        raise RuntimeError(f"Embedding model returned an empty or invalid vector: endpoint={endpoint}")
    return embeddings
