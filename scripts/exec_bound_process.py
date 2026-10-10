#!/usr/bin/env python3
"""Bind one benchmark process and record the kernel-observed affinity."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.benchmark.isolation import expand_linux_set


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpuset-cpus", required=True)
    parser.add_argument("--audit-path", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if not args.command or args.command[0] != "--":
        raise ValueError(
            "Bound process command must follow --: "
            f"command={args.command!r}"
        )
    command = args.command[1:]
    requested = sorted(expand_linux_set(args.cpuset_cpus, "bound process cpuset"))
    os.sched_setaffinity(0, requested)
    observed = sorted(os.sched_getaffinity(0))
    if observed != requested:
        raise RuntimeError(
            "Bound process affinity mismatch: "
            f"requested={requested!r}, observed={observed!r}"
        )
    Path(args.audit_path).write_text(
        json.dumps(
            {
                "schema": "aiopsbench_process_runtime_v1",
                "pid": os.getpid(),
                "command": command,
                "requested_cpuset_cpus": args.cpuset_cpus,
                "observed_affinity_cpus": observed,
                "affinity_matches": True,
            },
            ensure_ascii=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    os.execvpe(command[0], command, os.environ)
    raise AssertionError("os.execvpe returned unexpectedly")


if __name__ == "__main__":
    raise SystemExit(main())
