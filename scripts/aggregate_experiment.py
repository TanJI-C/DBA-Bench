#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("AIOPSBENCH_PROJECT_ROOT", str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT))

from src.benchmark.aggregate import (
    aggregate,
    load_records,
    write_aggregate,
    write_combined_records,
)
from src.benchmark.manifest import validate_identifier
from src.benchmark.store import ExperimentStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate an AiOpsBench experiment")
    parser.add_argument("experiment_id", nargs="+")
    parser.add_argument("--artifacts-root", default="artifacts/experiments")
    parser.add_argument("--output-experiment-id")
    args = parser.parse_args()
    if len(args.experiment_id) > 1 and not args.output_experiment_id:
        raise ValueError("Multiple experiment IDs require --output-experiment-id")

    experiment_ids = [
        validate_identifier(value, "experiment_id")
        for value in args.experiment_id
    ]

    stores = [
        ExperimentStore(PROJECT_ROOT / args.artifacts_root, experiment_id)
        for experiment_id in experiment_ids
    ]
    records = load_records(stores)

    if args.output_experiment_id:
        output_experiment_id = validate_identifier(
            args.output_experiment_id,
            "output_experiment_id",
        )
        root = (PROJECT_ROOT / args.artifacts_root / output_experiment_id).resolve()
        write_combined_records(root, output_experiment_id, experiment_ids, records)
    else:
        root = stores[0].root

    write_aggregate(root, aggregate(records))
    print(root / "aggregate.json")


if __name__ == "__main__":
    main()
