#!/usr/bin/env python3
"""Start or inspect the local Qwen3-4B semantic diagnosis judge."""

from __future__ import annotations

import argparse
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.scenarios.evaluation.semantic import (  # noqa: E402
    DEFAULT_SEMANTIC_MODEL,
    DEFAULT_SEMANTIC_MODEL_HOST,
    DEFAULT_SEMANTIC_MODEL_PORT,
    probe_semantic_model,
)


def build_vllm_command(args: argparse.Namespace) -> list[str]:
    command = [
        "vllm",
        "serve",
        args.model,
        "--served-model-name",
        args.model,
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--api-key",
        args.api_key,
        "--dtype",
        args.dtype,
        "--gpu-memory-utilization",
        str(args.gpu_memory_utilization),
        "--max-model-len",
        str(args.max_model_len),
        "--tensor-parallel-size",
        str(args.tensor_parallel_size),
    ]
    if args.quantization != "none":
        command.extend(["--quantization", args.quantization])
    return command


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Start or inspect the Qwen3-4B semantic diagnosis judge.",
    )
    result.add_argument("--status", action="store_true", help="only check GET /v1/models")
    result.add_argument("--model", default=DEFAULT_SEMANTIC_MODEL)
    result.add_argument("--host", default=DEFAULT_SEMANTIC_MODEL_HOST)
    result.add_argument("--port", type=int, default=DEFAULT_SEMANTIC_MODEL_PORT)
    result.add_argument("--api-key", default="local")
    result.add_argument("--dtype", choices=("auto", "half", "float16", "bfloat16"), default="half")
    result.add_argument("--quantization", default="none")
    result.add_argument("--gpu-memory-utilization", type=float, default=0.90)
    result.add_argument("--max-model-len", type=int, default=4096)
    result.add_argument("--tensor-parallel-size", type=int, default=1)
    result.add_argument("--detach", action="store_true", help="run vLLM in the background")
    result.add_argument("--log-path", type=Path)
    result.add_argument("--wait-seconds", type=int, default=120)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    base_url = f"http://{args.host}:{args.port}/v1"
    probe = probe_semantic_model(base_url, args.model, args.api_key)
    if args.status:
        print(f"status={probe.status} detail={probe.detail} endpoint={base_url}")
        return 0 if probe.ready else 1
    if probe.ready:
        raise RuntimeError(
            f"semantic model is already serving: model={args.model!r}, endpoint={base_url!r}"
        )
    executable = shutil.which("vllm")
    if executable is None:
        raise RuntimeError(
            "vllm executable is not installed in the current environment; "
            "install it with `conda run -n aiops pip install vllm` before starting "
            "the semantic model"
        )
    if args.wait_seconds < 1:
        raise ValueError(f"wait-seconds must be positive, got={args.wait_seconds}")
    if not 0 < args.gpu_memory_utilization <= 1:
        raise ValueError(
            "gpu-memory-utilization must be in (0, 1], "
            f"got={args.gpu_memory_utilization}"
        )
    command = build_vllm_command(args)
    print("Starting semantic model:")
    print("  " + " ".join(command))
    if not args.detach:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)
        return 0

    log_path = args.log_path or PROJECT_ROOT / "logs" / "dp_semantic_model.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log_file:
        process = subprocess.Popen(
            command,
            cwd=PROJECT_ROOT,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    print(f"pid={process.pid}")
    print(f"log={log_path}")
    deadline = time.monotonic() + args.wait_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(
                f"vllm exited before endpoint became ready: returncode={process.returncode}, "
                f"log={log_path}"
            )
        probe = probe_semantic_model(base_url, args.model, args.api_key)
        if probe.ready:
            print(f"ready endpoint={base_url} model={args.model}")
            return 0
        time.sleep(1)
    process.send_signal(signal.SIGTERM)
    raise TimeoutError(
        f"semantic model did not become ready within {args.wait_seconds}s: "
        f"endpoint={base_url}, last_status={probe.status}, log={log_path}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
