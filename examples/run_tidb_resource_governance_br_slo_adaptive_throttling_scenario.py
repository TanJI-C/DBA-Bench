import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.agent import BaseAgent
from src.agents.factory import build_experiment_agent
from src.protocols.report import StructuredReport
from src.scenarios.tidb import TidbResourceGovernanceBrSloAdaptiveThrottlingScenario
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.runtime.orchestrator import Orchestrator, OrchestratorRunConfig


PASS_REPORT = {
    "diagnosis": {"conditions": []},
    "outcome": {
        "changes": [
            "kept the maintenance budget bounded while preserving foreground latency, storage safety, and data integrity",
        ],
        "verification": [
            "the maintenance artifact completed with all ranges and checksum 100%",
            "the local artifact exists and remains within the space budget",
            "foreground query p95 recovered below the stated SLO",
            "business table integrity is unchanged",
        ],
    },
    "summary": "The live maintenance window was governed with a bounded official resource budget while preserving SLO, space safety, and business truth.",
}
StructuredReport.from_mapping(PASS_REPORT)
class ResourceGovernanceFullMockAgent(BaseAgent):
    def __init__(self, case):
        super().__init__()
        self.case = case

    def solve(self):
        case = self.case
        if case.case_no == 1:
            steps = [
                (
                    "query_metrics",
                    {"metric_type": "query_latency", "target": None},
                    "确认前台 p95 仍处于违约状态。",
                ),
                (
                    "execute_sql",
                    {
                        "sql_query": (
                            "SHOW CONFIG WHERE type = 'tikv' "
                            "AND name IN ('backup.enable-auto-tune', 'backup.num-threads')"
                        )
                    },
                    "确认 backup auto-tune 与 num-threads 的当前预算。",
                ),
                (
                    "execute_sql",
                    {
                        "sql_query": (
                            "SELECT state, total_ranges, ranges_succeeded, ranges_failed, checksum_status "
                            f"FROM {case.database}.{case.job_table} "
                            f"WHERE job_id = '{case.job_id}'"
                        )
                    },
                    "确认维护任务仍在运行且未完成。",
                ),
                (
                    "execute_sql",
                    {"sql_query": "SET CONFIG tikv `backup.enable-auto-tune` = 'true'"},
                    "保留官方自动调速与空间保护。",
                ),
                (
                    "execute_sql",
                    {"sql_query": "SET CONFIG tikv `backup.num-threads` = '1'"},
                    "把备份线程预算限制到单 TiKV 一个线程。",
                ),
            ]
            for api, args, thinking in steps:
                self.execute(api, args, thinking=thinking)
            self._await_maintenance_completion()
            self._await_foreground_slo()
            self.execute(
                "execute_sql",
                {"sql_query": case.business_query},
                thinking="用数据库内真值校验治理没有改变业务表。",
            )
            return {"report": case.reference_report}

        self.execute(
            "query_metrics",
            {"metric_type": "active_connections", "target": None},
            thinking="先从真实业务 fingerprint 和当前执行延迟确认前台与备份窗口的共同压力。",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "query_latency", "target": None},
            thinking="检查所有 TiDB 实例的 p95，而不是只看一个瞬时 CPU 值。",
        )
        self.execute(
            "query_metrics",
            {"metric_type": "disk_io", "target": "tikv/tikv-0"},
            thinking="将 TiKV 磁盘读写与 BR 进度和前台 SLO 对齐。",
        )
        self.execute(
            "execute_sql",
            {
                "sql_query": (
                    "SHOW CONFIG WHERE type = 'tikv' "
                    "AND name IN ('backup.enable-auto-tune', 'backup.num-threads')"
                )
            },
            thinking="确认 backup auto-tune 和 backup.num-threads 的当前值及所有 TiKV 实例。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET CONFIG tikv `backup.enable-auto-tune` = 'true'"},
            thinking="保留官方自动调速保护，避免用关闭空间或调度保护换取吞吐。",
        )
        self.execute(
            "execute_sql",
            {"sql_query": "SET CONFIG tikv `backup.num-threads` = '1'"},
            thinking="将 CPU 密集型 BR 线程预算限制到单 TiKV 一个线程。",
        )
        self._await_maintenance_completion()
        self._await_foreground_slo()
        self.execute(
            "execute_sql",
            {"sql_query": case.business_query},
            thinking="用数据库内真值校验备份治理没有改变业务表。",
        )
        return {"report": case.reference_report}

    def _await_maintenance_completion(self):
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            job = self.execute(
                "execute_sql",
                {
                    "sql_query": (
                        "SELECT state, total_ranges, ranges_succeeded, ranges_failed, checksum_status "
                        f"FROM {self.case.database}.{self.case.job_table} "
                        f"WHERE job_id = '{self.case.job_id}'"
                    )
                },
                thinking="等待维护任务真实进度推进，同时保留可复核的 job 状态。",
            )
            rows = job["result"]
            if len(rows) != 1:
                raise RuntimeError(f"RG03 mock expected one BR job row, rows={rows!r}")
            state, total, succeeded, failed, checksum = rows[0]
            if str(state).upper() == "SUCCEEDED":
                if int(total) <= 0 or int(succeeded) != int(total) or int(failed) != 0 or str(checksum) != "100%":
                    raise RuntimeError(f"RG03 mock observed invalid completed BR job: row={rows[0]!r}")
                return
            if str(state).upper() == "FAILED":
                raise RuntimeError(f"RG03 mock observed failed BR job: row={rows[0]!r}")
            time.sleep(4)
        raise RuntimeError("RG03 mock BR job did not finish within 300 seconds")

    def _await_foreground_slo(self):
        slo_deadline = time.monotonic() + 120
        stable_samples = 0
        while stable_samples < 2:
            latency = self.execute(
                "query_metrics",
                {"metric_type": "query_latency", "target": None},
                thinking="确认最新前台 p95 已连续回到 SLO 内。",
            )
            latest_p95 = max(
                float(values["p95_ms"][-1])
                for values in latency["series"].values()
            )
            if latest_p95 <= self.case.slo_p95_ms:
                stable_samples += 1
            else:
                stable_samples = 0
            if time.monotonic() >= slo_deadline:
                raise RuntimeError(
                    "RG03 mock foreground SLO did not stabilize: "
                    f"latest_p95_ms={latest_p95}, slo_p95_ms={self.case.slo_p95_ms}"
                )
            if stable_samples < 2:
                time.sleep(4)


def _build_environment(args):
    if (args.storage_key is None) != (args.storage_root is None):
        raise ValueError("--storage-key and --storage-root must be supplied together")
    return TiDBEnv(
        run_id=args.container_name.removeprefix("aiopsbench-"),
        port_base=args.port,
        return_window_seconds=300,
        storage_key=args.storage_key,
        storage_root=args.storage_root,
        tidb_readiness_timeout_sec=args.cold_start_timeout,
        warm_tidb_readiness_timeout_sec=args.warm_start_timeout,
    )


def main():
    scenario = TidbResourceGovernanceBrSloAdaptiveThrottlingScenario()
    parser = argparse.ArgumentParser(description="Run TiDB RG03 BR SLO resource governance.")
    parser.add_argument("--case", required=True, choices=[case.case_id for case in scenario.cases])
    parser.add_argument("--mode", choices=("mock", "llm"), default="mock")
    parser.add_argument("--model")
    parser.add_argument("--config-path", default="config/llm_config.json")
    parser.add_argument("--max-turns", type=int, default=30)
    parser.add_argument("--port", type=int, default=18100)
    parser.add_argument("--container-name", default="tidb-rg03")
    parser.add_argument("--fault-snapshot-mode", choices=("auto", "off", "save", "use"), default="off")
    parser.add_argument("--storage-key")
    parser.add_argument("--storage-root")
    parser.add_argument("--cold-start-timeout", type=int, default=900)
    parser.add_argument("--warm-start-timeout", type=int, default=300)
    args = parser.parse_args()

    case = scenario.get_case(args.case)
    env = _build_environment(args)
    if args.mode == "mock":
        agent = ResourceGovernanceFullMockAgent(case)
    else:
        if not args.model:
            raise ValueError("--model is required when --mode=llm")
        agent = build_experiment_agent(model=args.model, config_path=args.config_path, use_native_tools=True)
    result = Orchestrator(
        env,
        scenario,
        case,
        agent,
        max_turns=args.max_turns,
        run_config=OrchestratorRunConfig(fault_snapshot_mode=args.fault_snapshot_mode),
    ).run()
    if args.mode == "mock":
        observed = tuple(result[field] for field in ("DiagnosisPass", "OutcomePass", "SafePass"))
        if observed != (None, True, True):
            raise RuntimeError(f"RG03 mock must pass None/True/True, observed={observed!r}, result={result!r}")
    print(f"Final result: {result}")


if __name__ == "__main__":
    main()
