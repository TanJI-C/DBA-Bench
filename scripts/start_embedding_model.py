#!/usr/bin/env python3
"""Start or inspect the shared local SentenceTransformer embedding service."""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_ROOT))

from src.project_paths import REPOSITORY_ROOT  # noqa: E402
from src.knowledge.embedding_model_runtime import (  # noqa: E402
    DEFAULT_EMBEDDING_MODEL_HOST,
    DEFAULT_EMBEDDING_MODEL_PORT,
    DEFAULT_EMBEDDING_MODEL_WAIT_SECONDS,
    ensure_embedding_model,
    probe_embedding_model,
)


PROJECT_ROOT = REPOSITORY_ROOT


class EmbeddingRequestHandler(BaseHTTPRequestHandler):
    model = None
    model_name = ""
    device = ""
    dimension = 0
    model_lock = Lock()

    def log_message(self, format: str, *args) -> None:
        sys.stderr.write(f"[embedding-model] {format % args}\n")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/health":
            self._send_json(404, {"status": "error", "error": f"Unknown endpoint: path={self.path!r}"})
            return
        self._send_json(200, {
            "status": "ready",
            "model": self.model_name,
            "device": self.device,
            "dimension": self.dimension,
        })

    def do_POST(self) -> None:
        if self.path != "/embed":
            self._send_json(404, {"status": "error", "error": f"Unknown endpoint: path={self.path!r}"})
            return
        try:
            length = int(self.headers["Content-Length"])
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            texts = payload["texts"]
            prompt_name = payload["prompt_name"]
            if not isinstance(texts, list) or not texts or any(not isinstance(text, str) for text in texts):
                raise ValueError(f"texts must be a non-empty list of strings: texts={texts!r}")
            if prompt_name not in {"query", "text"}:
                raise ValueError(f"prompt_name must be 'query' or 'text': prompt_name={prompt_name!r}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"status": "error", "error": f"Invalid embedding request: {exc}"})
            return

        try:
            with self.model_lock:
                vectors = self.model.encode(
                    texts,
                    batch_size=min(len(texts), 4),
                    prompt_name=prompt_name,
                    normalize_embeddings=True,
                ).tolist()
                if self.device.startswith("cuda"):
                    import torch

                    torch.cuda.empty_cache()
        except Exception as exc:
            self._send_json(500, {
                "status": "error",
                "error": f"Embedding model encode failed: model={self.model_name!r}, error={exc}",
            })
            return
        self._send_json(200, {
            "status": "success",
            "model": self.model_name,
            "dimension": self.dimension,
            "embeddings": vectors,
        })


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--status", action="store_true", help="check the health endpoint and exit")
    result.add_argument("--serve", action="store_true", help=argparse.SUPPRESS)
    result.add_argument("--model", default="Qwen/Qwen3-Embedding-4B")
    result.add_argument("--device", default="cpu")
    result.add_argument("--host", default=DEFAULT_EMBEDDING_MODEL_HOST)
    result.add_argument("--port", type=int, default=DEFAULT_EMBEDDING_MODEL_PORT)
    result.add_argument("--wait-seconds", type=int, default=DEFAULT_EMBEDDING_MODEL_WAIT_SECONDS)
    return result


def _load_model(model_name: str, device: str):
    from llama_index.embeddings.huggingface.utils import (
        get_query_instruct_for_model_name,
        get_text_instruct_for_model_name,
    )
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(
        model_name,
        device=device,
        prompts={
            "query": get_query_instruct_for_model_name(model_name),
            "text": get_text_instruct_for_model_name(model_name),
        },
    )
    max_seq_length = int(os.environ.get("AIOPS_EMBEDDING_MAX_SEQ_LENGTH", "1024"))
    if max_seq_length < 1:
        raise ValueError(
            f"AIOPS_EMBEDDING_MAX_SEQ_LENGTH must be positive: value={max_seq_length}"
        )
    model.max_seq_length = max_seq_length
    if device == "cpu":
        model.float()
    return model


def _serve(args: argparse.Namespace) -> int:
    model = _load_model(args.model, args.device)
    EmbeddingRequestHandler.model = model
    EmbeddingRequestHandler.model_name = args.model
    EmbeddingRequestHandler.device = args.device
    EmbeddingRequestHandler.dimension = model.get_embedding_dimension()
    server = ThreadingHTTPServer((args.host, args.port), EmbeddingRequestHandler)
    print(
        f"Embedding model service ready: endpoint=http://{args.host}:{args.port}, "
        f"model={args.model}, device={args.device}, dimension={EmbeddingRequestHandler.dimension}",
        flush=True,
    )
    server.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    base_url = f"http://{args.host}:{args.port}"
    if args.status:
        probe = probe_embedding_model(base_url, args.model)
        print(f"status={probe.status} detail={probe.detail} endpoint={base_url} model={args.model}")
        return 0 if probe.ready else 1
    if args.serve:
        return _serve(args)
    probe = ensure_embedding_model(
        args.model,
        args.device,
        base_url=base_url,
        wait_seconds=args.wait_seconds,
    )
    print(
        f"Embedding model ready: endpoint={base_url}, model={args.model}, "
        f"detail={probe.detail}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
