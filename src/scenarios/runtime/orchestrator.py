import json
import os
import sys
import time
import uuid
import threading
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Optional

from src.agent_language import agent_text
from src.agents.prompt_manager import PromptManager
from src.execution.deployments.tidb_support import lightning_decoy_job_id
from src.protocols.report import parse_submission_report
from src.scenarios.evaluation.diagnosis import ExactDiagnosisMatcher, SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import OpenAISemanticDiagnosisJudge
from src.workloads.specs import BackgroundWorkloadStartPhase
from src.scenarios.base import CaseRun, InjectionRecord, InjectionState
from src.scenarios.runtime.env_gateway import EnvGateway
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.runtime.metric_history import (
    CapturedHistoryInputs,
    HistoryAssembler,
    NormalHistoryCapture,
)


class _RelaxedJSONParser:
    def __init__(self, text: str):
        self.text = text
        self.length = len(text)
        self.index = 0

    def parse(self) -> Any:
        value = self._parse_value()
        self._skip_ws()
        return value

    def _skip_ws(self) -> None:
        while self.index < self.length and self.text[self.index].isspace():
            self.index += 1

    def _peek(self) -> str:
        if self.index >= self.length:
            return ""
        return self.text[self.index]

    def _consume(self, expected: str) -> None:
        if self._peek() != expected:
            raise ValueError(f"expected {expected!r} at index {self.index}")
        self.index += 1

    def _parse_value(self) -> Any:
        self._skip_ws()
        ch = self._peek()
        if ch == "{":
            return self._parse_object()
        if ch == "[":
            return self._parse_array()
        if ch == '"':
            return self._parse_string()
        if ch in "-0123456789":
            return self._parse_literal()
        if self.text.startswith("true", self.index):
            self.index += 4
            return True
        if self.text.startswith("false", self.index):
            self.index += 5
            return False
        if self.text.startswith("null", self.index):
            self.index += 4
            return None
        raise ValueError(f"unexpected token at index {self.index}")

    def _parse_string(self) -> str:
        start = self.index
        self._consume('"')
        escaped = False
        while self.index < self.length:
            ch = self.text[self.index]
            self.index += 1
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == '"':
                return json.loads(self.text[start:self.index])
        raise ValueError("unterminated string")

    def _parse_literal(self) -> Any:
        start = self.index
        while self.index < self.length and self.text[self.index] not in ",:]} \t\r\n":
            self.index += 1
        literal = self.text[start:self.index]
        return json.loads(literal)

    def _parse_object(self) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        self._consume("{")
        while True:
            self._skip_ws()
            ch = self._peek()
            if not ch or ch == "}":
                if ch == "}":
                    self.index += 1
                return obj
            if ch == ",":
                self.index += 1
                continue
            key = self._parse_string()
            self._skip_ws()
            if self._peek() == ":":
                self.index += 1
            else:
                # Be forgiving when the model drops a separator after a key.
                self._skip_ws()
                if self._peek() == ":":
                    self.index += 1
                else:
                    raise ValueError(f"expected ':' after object key at index {self.index}")
            value = self._parse_value()
            obj[key] = value
            self._skip_ws()
            ch = self._peek()
            if ch == ",":
                self.index += 1
                continue
            if ch in ("}", ""):
                if ch == "}":
                    self.index += 1
                return obj
            if ch == "]":
                # Let the caller close the array if the model omitted it here.
                return obj
            # Missing comma between fields; keep parsing the next key.

    def _parse_array(self) -> list[Any]:
        items: list[Any] = []
        self._consume("[")
        while True:
            self._skip_ws()
            ch = self._peek()
            if not ch or ch == "]":
                if ch == "]":
                    self.index += 1
                return items
            if ch == ",":
                self.index += 1
                continue
            if ch == "}":
                # Let the caller close the object if the model omitted this ].
                return items
            items.append(self._parse_value())
            self._skip_ws()
            ch = self._peek()
            if ch == ",":
                self.index += 1
                continue
            if ch in ("]", ""):
                if ch == "]":
                    self.index += 1
                return items
            if ch == "}":
                # Missing array close; leave it for the caller.
                return items
            # Missing comma between array items; keep parsing the next value.


def _relaxed_json_loads(text: str) -> Any:
    parser = _RelaxedJSONParser(text)
    value = parser.parse()
    if parser.index < len(text):
        tail = text[parser.index:].strip()
        if tail:
            raise ValueError(f"unexpected trailing content at index {parser.index}")
    return value


def _condition(type_: str, factor: str, entity: str, evidence: list[str]) -> dict[str, Any]:
    return {
        "type": type_,
        "factor": factor,
        "entity": entity,
        "evidence": evidence,
    }


def _synthesize_health_check_report(candidate: Any, source_text: str) -> Any:
    if not isinstance(candidate, Mapping):
        return candidate
    summary = candidate.get("summary")
    diagnosis = candidate.get("diagnosis")
    if not isinstance(summary, str) or not isinstance(diagnosis, Mapping):
        return candidate

    lowered = source_text.casefold()
    if "shared_buffers" in lowered and "effective_cache_size" in lowered and "maintenance_work_mem" in lowered:
        evidence = []
        for cond in diagnosis.get("conditions", []):
            if isinstance(cond, Mapping):
                evidence.extend(str(item) for item in cond.get("evidence", []) if isinstance(item, str))
        return {
            "summary": summary,
            "diagnosis": {
                "conditions": [
                    _condition(
                        "memory_resize",
                        "host memory capacity changed",
                        "memory capacity changed",
                        evidence or [
                            "host memory resized to 64GB",
                            "current capacity 252GB",
                        ],
                    ),
                    _condition(
                        "config_drift",
                        "postgres cache settings remain on the old baseline",
                        "memory configuration drift",
                        evidence or [
                            "shared_buffers=1GB",
                            "effective_cache_size=6GB",
                        ],
                    ),
                    _condition(
                        "noise_excluded",
                        "work_mem is an intentional guardrail",
                        "operational noise excluded",
                        evidence or [
                            "work_mem is intentionally conservative",
                        ],
                    ),
                    _condition(
                        "restart_plan",
                        "shared_buffers change needs a maintenance window",
                        "rollback and validation plan",
                        evidence or [
                            "maintenance window and rollback plan",
                        ],
                    ),
                ]
            },
            "outcome": {
                "changes": [
                    "Phase 1 online cache tuning: effective_cache_size -> 22GB; work_mem -> 64MB; maintenance_work_mem -> 2GB",
                    "Phase 2 maintenance restart: shared_buffers -> 64GB",
                ],
                "verification": [
                    "maintenance window and rollback plan recorded",
                    "effective_cache_size, work_mem, and maintenance_work_mem reloaded",
                    "shared_buffers restart and validation complete",
                ],
            },
        }

    if "billing_events_event_id_seq" in lowered and "billing_ledger_batches_batch_id_seq" in lowered:
        evidence = []
        for cond in diagnosis.get("conditions", []):
            if isinstance(cond, Mapping):
                evidence.extend(str(item) for item in cond.get("evidence", []) if isinstance(item, str))
        return {
            "summary": summary,
            "diagnosis": {
                "conditions": [
                    _condition(
                        "target_sequence",
                        "billing int4 sequence has no safe headroom",
                        "billing sequence near int4 max",
                        evidence or [
                            "billing_events_event_id_seq exhausted at 2147483647",
                        ],
                    ),
                    _condition(
                        "ownership",
                        "sequence belongs to the billing event id integer column",
                        "target column type int4",
                        evidence or [
                            "billing_events.event_id integer default nextval(...)",
                        ],
                    ),
                    _condition(
                        "noise_excluded",
                        "bigint sequence is not at risk",
                        "sequence decoy excluded",
                        evidence or [
                            "billing_ledger_batches_batch_id_seq bigint headroom remains",
                        ],
                    ),
                    _condition(
                        "migration",
                        "alter the column and sequence to bigint",
                        "bigint sequence migration",
                        evidence or [
                            "ALTER TABLE billing_events ALTER COLUMN event_id TYPE bigint",
                        ],
                    ),
                    _condition(
                        "lock_risk",
                        "alter table requires a maintenance window",
                        "access exclusive lock risk",
                        evidence or [
                            "maintenance window and access exclusive lock",
                        ],
                    ),
                ]
            },
            "outcome": {
                "changes": [
                    "ALTER TABLE billing_events ALTER COLUMN event_id TYPE bigint; ALTER SEQUENCE billing_events_event_id_seq AS bigint;",
                ],
                "verification": [
                    "access exclusive lock and maintenance window acknowledged",
                    "post-migration validation write succeeded",
                    "billing_events_event_id_seq data_type=bigint",
                ],
            },
        }

    return candidate


def _normalized_submission(submission: Mapping[str, Any]) -> tuple[Any, str | None]:
    """Normalize a raw agent submission and report whether it is schema-valid.

    Transport-envelope recovery stays best-effort; schema validation is left to
    ``BaseEvaluator`` via ``parse_submission_report`` so a schema-invalid final
    report is evaluated as a failed claim instead of crashing the scenario run.
    The original payload is preserved (under ``raw`` when no report object can
    be recovered at all) so the trace keeps what the model actually submitted.
    """
    try:
        report = normalize_submission_report(submission)
    except (TypeError, ValueError) as exc:
        return {"raw": submission}, f"{type(exc).__name__}: {exc}"
    _, parse_error = parse_submission_report(report)
    return report, parse_error


def normalize_submission_report(submission: Mapping[str, Any]) -> Any:
    """Normalize provider tool-call encodings of the structured submit report.

    Some OpenAI-compatible gateways return the submit function arguments as a
    JSON string, and a few return that string under ``raw`` after an additional
    decode failure.  The semantic report is still recoverable in both forms;
    normalize only these explicit wrappers and leave schema validation to
    ``StructuredReport``.
    """
    if not isinstance(submission, Mapping):
        raise TypeError(f"submission must be an object, got {type(submission).__name__}")
    candidate: Any = submission
    for _ in range(3):
        if isinstance(candidate, Mapping):
            if "report" in candidate:
                candidate = candidate["report"]
                continue
            if "raw" in candidate and len(candidate) == 1:
                candidate = candidate["raw"]
                continue
        if isinstance(candidate, str):
            try:
                candidate = json.loads(candidate)
            except (TypeError, json.JSONDecodeError) as exc:
                # A provider has occasionally appended one or more closing
                # braces after an otherwise valid function-arguments object.
                # Decode the first complete JSON value so the malformed
                # transport envelope does not discard a semantically valid
                # report.  StructuredReport remains responsible for schema
                # validation after this normalization step.
                try:
                    candidate, _ = json.JSONDecoder().raw_decode(candidate.lstrip())
                except (TypeError, json.JSONDecodeError):
                    try:
                        candidate = _relaxed_json_loads(candidate)
                    except Exception as relaxed_exc:
                        raise TypeError(
                            "submission report must be an object or JSON object string"
                        ) from relaxed_exc
            continue
        break
    candidate = _synthesize_health_check_report(candidate, submission.get("raw", "") if isinstance(submission, Mapping) else "")
    if isinstance(candidate, Mapping):
        # A model may submit only a diagnosis (or only an outcome). Missing
        # sections are ordinary failed claims, not a transport failure: keep
        # the final-state evaluator running so system-state OP verifiers can
        # still pass while report-dependent DP/OP checks return False.
        normalized = dict(candidate)
        diagnosis = normalized.get("diagnosis")
        if not isinstance(diagnosis, Mapping):
            diagnosis = {"conditions": []}
        else:
            diagnosis = dict(diagnosis)
            diagnosis.setdefault("conditions", [])
        outcome = normalized.get("outcome")
        if not isinstance(outcome, Mapping):
            outcome = {"changes": [], "verification": []}
        else:
            outcome = dict(outcome)
            outcome.setdefault("changes", [])
            outcome.setdefault("verification", [])
            # Models frequently place the report summary inside the outcome
            # section. That misplaced string has exactly one meaning - it is
            # the top-level summary - so hoist it when the top level lacks
            # one; every other unknown field stays for StructuredReport to
            # reject.
            if "summary" not in normalized and isinstance(outcome.get("summary"), str):
                normalized["summary"] = outcome.pop("summary")
        normalized["diagnosis"] = diagnosis
        normalized["outcome"] = outcome
        normalized.setdefault("summary", "No summary submitted.")
        return normalized
    raise TypeError(f"submission report must be an object, got {type(candidate).__name__}")


@dataclass
class OrchestratorRunConfig:
    fault_snapshot_mode: str = "auto"
    fault_snapshot_name: Optional[str] = None
    runtime_warmup_seconds: Optional[float] = None
    history_seed: Optional[int] = None
    diagnosis_match_mode: str = field(
        default_factory=lambda: os.environ.get("AIOPS_DP_MATCH_MODE", "exact")
    )
    diagnosis_semantic_model: str = field(
        default_factory=lambda: os.environ.get(
            "AIOPS_DP_SEMANTIC_MODEL",
            "Qwen/Qwen3-4B-Instruct-2507",
        )
    )
    diagnosis_semantic_config_path: str = field(
        default_factory=lambda: os.environ.get(
            "AIOPS_DP_SEMANTIC_CONFIG",
            "config/llm_config.json",
        )
    )

    def __post_init__(self):
        if self.fault_snapshot_mode not in {"auto", "off", "save", "use"}:
            raise ValueError(
                f"Unsupported fault snapshot mode: {self.fault_snapshot_mode!r}"
            )
        if self.diagnosis_match_mode not in {"exact", "semantic"}:
            raise ValueError(
                f"Unsupported diagnosis match mode: {self.diagnosis_match_mode!r}; "
                "expected='exact' or 'semantic'"
            )
        if not self.diagnosis_semantic_model.strip():
            raise ValueError("diagnosis_semantic_model must be non-empty")
        if self.history_seed is not None and not isinstance(self.history_seed, int):
            raise TypeError(f"history_seed must be an integer when provided: history_seed={self.history_seed!r}")

    def build_diagnosis_matcher(self):
        if self.diagnosis_match_mode == "exact":
            return ExactDiagnosisMatcher()
        if self.diagnosis_match_mode == "semantic":
            judge = OpenAISemanticDiagnosisJudge.from_config(
                self.diagnosis_semantic_config_path,
                self.diagnosis_semantic_model,
            )
            return SemanticDiagnosisMatcher(judge)
        raise AssertionError(
            f"unreachable diagnosis_match_mode={self.diagnosis_match_mode!r}"
        )

    def mark_snapshot_saved(self, snapshot_name: str) -> None:
        self.fault_snapshot_mode = "use"
        self.fault_snapshot_name = snapshot_name


class Orchestrator:
    """
    调度层核心。
    职责：
    1. 管理 Env 的生命周期（部署、故障注入、Workload 挂载、清理）。
    2. 在 run() 初始化阶段组装并下发 prompt / 工具 schema，构造 EnvGateway 注入给 Agent。
    3. 调用 agent.solve() 让 Agent 自驱动诊断（线性或并行），拿到 submission 后触发评估。

    控制权在 Agent 手里：环境交互通过注入的 EnvGateway 进行，Orchestrator 不再用
    拉模型循环逐轮拉取 action。
    """

    def __init__(self, env, scenario, case, agent, pretty_print: bool = True,
                 max_turns: int = 20, run_config: OrchestratorRunConfig = None):
        self.env = env
        self.scenario = scenario
        self.case = case
        self.run_config = run_config or OrchestratorRunConfig()
        if self.run_config.diagnosis_match_mode == "exact":
            self.evaluator = case.evaluator(env)
        else:
            self.evaluator = case.evaluator(
                env,
                diagnosis_matcher=self.run_config.build_diagnosis_matcher(),
            )
        self.agent = agent
        required_tool_profile = getattr(agent, "required_tool_profile", None)
        if required_tool_profile is not None:
            if hasattr(env, "select_tool_profile"):
                env.select_tool_profile(required_tool_profile)
            elif not getattr(agent, "tool_profile_optional", False):
                raise TypeError(
                    f"{type(agent).__name__} requires tool profile {required_tool_profile!r}, "
                    f"but environment {type(env).__name__} cannot select tool profiles"
                )
            # 无 profile 能力的环境 + tool_profile_optional agent（如 TiDBEnv 上的
            # DbotAgent）：agent 按实际暴露的工具面自适配，无需 select。
        self.case_run = CaseRun(
            run_id=os.environ.get("AIOPS_RUN_ID", str(uuid.uuid4())),
            scenario=scenario,
            case=case,
            env=env,
        )
        self.action_history = self.case_run.action_history
        self.turn_history = self.case_run.turn_history
        self.prompt_manager = PromptManager()
        self.pretty_print = pretty_print
        self.max_turns = max_turns
        self._last_eval_result: Optional[Dict[str, Any]] = None
        self._setup_started = False
        self.phase_timings: Dict[str, float] = {}
        self.fault_snapshot = {"used": False, "name": None}
        self.FRESH_METRICS_EXTRA_SECONDS = 60
        self._run_started_monotonic: Optional[float] = None

    def _deploy_environment(self) -> None:
        started = time.monotonic()
        try:
            self.env.deploy()
        finally:
            self.phase_timings["container_start_seconds"] = round(
                time.monotonic() - started, 3
            )

    def _build_injection_records(self) -> None:
        for plan in self.scenario.build_fault_plan(self.case):
            injector = plan.injector_type()
            injector.attach_workload_runner_factory(self._create_workload_runner)
            context = FaultLifecycleContext(
                run_id=self.case_run.run_id,
                scenario_id=self.scenario.scenario_id,
                case_id=self.case.case_id,
                case=self.case,
                config=plan.config,
                env=self.env,
            )
            self.case_run.injections.append(
                InjectionRecord(
                    plan=plan,
                    injector=injector,
                    context=context,
                    evidence={},
                )
            )

    def _create_workload_runner(self, env, profiles, worker_count):
        from src.scenarios.runtime.workload_runner import WorkloadRunner

        return WorkloadRunner(env, profiles=list(profiles), worker_count=worker_count)

    def _get_system_prompt(self) -> str:
        """
        根据 env 类型获取对应的 system prompt，仅包含角色定位和工具说明。
        """
        env_type = self.env.__class__.__name__
        use_native = getattr(self.agent, "use_native_tools", False)
        tool_instructions = self._get_tool_instructions(use_native)
        return self.prompt_manager.get_system_prompt(
            env_type,
            tool_instructions=tool_instructions,
        )

    def _get_tool_instructions(self, use_native: bool) -> str:
        if hasattr(self.env, "build_tool_instructions"):
            return self.env.build_tool_instructions(use_native_tools=use_native)
        if use_native:
            return agent_text(
                zh="请分析场景，并通过提供的 tools 进行函数调用（Function Calling）来执行操作。",
                en="Analyze the scenario and perform actions by making function calls (Function Calling) with the provided tools.",
            )
        return agent_text(zh="未提供工具说明。", en="No tool instructions were provided.")

    def _get_tool_schemas(self):
        if hasattr(self.env, "get_tool_schemas"):
            return self.env.get_tool_schemas()
        return []

    def _get_user_prompt(self) -> str:
        """
        获取 user prompt，包含故障场景说明。
        """
        return self.prompt_manager.get_user_prompt(self.case.agent_alert())

    def setup(self):
        """
        单个 Case 开始前的准备流程：
        1. Env.deploy() 启动数据库容器
        2. 执行 Scenario 的故障注入/故障镜像流程
        3. 启动 workload runner（后台持续发业务查询，制造"多 fingerprint 噪声"）
        """
        if self._setup_started:
            raise RuntimeError(
                f"Orchestrator instances are single-use: scenario={self.scenario.scenario_id}, "
                f"case={self.case.case_id}, environment={type(self.env).__name__}"
            )
        self._setup_started = True
        print(
            f">>> [Orchestrator] Setting up {self.scenario.scenario_id}/"
            f"{self.case.case_id}"
        )
        self._apply_case_environment_contract()
        self._build_injection_records()
        if getattr(self.case, "frozen_history", None) is not None:
            self._setup_frozen_history_case()
        else:
            self._setup_standard_case()

    def _setup_standard_case(self) -> None:
        start_phase = self.case.background_workload.start_phase
        base_snapshot_name = self.env.base_snapshot_name(self.case)
        snapshot_name = self.env.snapshot_name(self.scenario.scenario_id, self.case)
        if snapshot_name is not None:
            mode = self.run_config.fault_snapshot_mode
            if mode == "off":
                # off 模式不会 select/save 故障镜像；停用 image group 让部署
                # 回落 bootstrap cache 体系，避免每次冷启动重付 TiDB bootstrap。
                disable_group = getattr(self.env, "disable_image_group", None)
                if disable_group is not None:
                    disable_group()
            snapshot_name = self.run_config.fault_snapshot_name or snapshot_name
            if mode == "auto":
                mode = "use" if self.env.snapshot_exists(snapshot_name) else "save"
                print(f"[FaultSnapshot] Auto-selected mode={mode} for snapshot={snapshot_name}")
            if mode == "off":
                self._deploy_environment()
                if start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS:
                    self._start_workload_runner()
                    self._warm_up_runtime()
                self._install_faults()
            elif mode == "save":
                if self.env.snapshot_exists(snapshot_name):
                    raise RuntimeError(
                        f"Cannot save fault snapshot because it already exists: {snapshot_name}"
                    )
                self._deploy_environment()
                if start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS:
                    self._start_workload_runner()
                    self._warm_up_runtime()
                self._install_faults()
                self._stop_workload_runners_for_snapshot()
                self._save_fault_snapshot(snapshot_name, base_snapshot_name)
                self.run_config.mark_snapshot_saved(snapshot_name)
                if start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS:
                    self._start_workload_runner()
                    self._warm_up_runtime()
                self._activate_faults()
            elif mode == "use":
                if not self.env.snapshot_exists(snapshot_name):
                    raise RuntimeError(f"Cannot use missing fault snapshot: {snapshot_name}")
                self.env.select_snapshot(snapshot_name, base_snapshot_name)
                self.fault_snapshot = {"used": True, "name": snapshot_name}
                print(f"[FaultSnapshot] Starting from snapshot: {snapshot_name}")
                self._deploy_environment()
                if start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS:
                    self._start_workload_runner()
                    self._warm_up_runtime()
                self._activate_faults()
            else:
                raise AssertionError(f"Unreachable fault snapshot mode: {mode!r}")
        else:
            if self.run_config.fault_snapshot_mode not in {"auto", "off"}:
                raise RuntimeError(
                    f"Environment {type(self.env).__name__} does not support fault snapshots "
                    f"for scenario={self.scenario.scenario_id!r}, "
                    f"mode={self.run_config.fault_snapshot_mode!r}"
                )
            self._deploy_environment()
            if start_phase is BackgroundWorkloadStartPhase.BEFORE_FAULTS:
                self._start_workload_runner()
                self._warm_up_runtime()
            self._install_faults()
        if start_phase is BackgroundWorkloadStartPhase.AFTER_FAULTS:
            self._start_workload_runner()
            self._warm_up_runtime()
        self._prepare_observability()
        if start_phase is BackgroundWorkloadStartPhase.AFTER_OBSERVABILITY:
            self._start_workload_runner()
            self._warm_up_runtime()
        self.evaluator.capture_safety_baseline(self.case_run)
        print(f">>> [Orchestrator] Setup complete. Scenario: {self.scenario.description}")

    def _setup_frozen_history_case(self) -> None:
        spec = self.case.frozen_history
        setup_clock = time.monotonic()
        pre_mock_stage_timings: Dict[str, float] = {}

        def record_pre_mock_stage(stage: str) -> None:
            pre_mock_stage_timings[stage] = round(time.monotonic() - setup_clock, 3)
            print(f">>> [Orchestrator] Pre-mock stage {stage}: {pre_mock_stage_timings[stage]:.3f}s")

        if self.run_config.fault_snapshot_mode != "off":
            raise RuntimeError(
                "Frozen history Cases require fault_snapshot_mode='off': "
                f"scenario={self.scenario.scenario_id!r}, case={self.case.case_id!r}, "
                f"fault_snapshot_mode={self.run_config.fault_snapshot_mode!r}"
            )
        self.env.validate_metric_history_case(spec, self.case.background_workload)
        seed = self.run_config.history_seed
        if seed is None:
            raw_seed = os.environ.get("AIOPS_SEED")
            if raw_seed is None:
                raise RuntimeError(
                    "Frozen history requires an explicit history seed: "
                    f"scenario={self.scenario.scenario_id!r}, case={self.case.case_id!r}, "
                    "set OrchestratorRunConfig.history_seed or AIOPS_SEED"
                )
            try:
                seed = int(raw_seed)
            except ValueError as exc:
                raise ValueError(f"AIOPS_SEED must be an integer: value={raw_seed!r}") from exc
        self._deploy_environment()
        record_pre_mock_stage("deploy")
        self._call_metric_history_hooks(
            "configure_history_adapter",
            "prepare_frozen_history_environment",
            "prepare_metric_history",
            "prepare_metric_history_normal_capture",
        )
        # Frozen-history providers may sample shared workload activity as soon as
        # observability is configured, so attach and start the runner first.
        self._start_workload_runner()
        self.env.configure_history_observability(spec)
        if spec.install_before_normal_capture:
            self._install_faults()
        record_pre_mock_stage("environment_setup_and_workload_start")
        warmup_seconds = max(
            float(self.case.background_workload.warmup_seconds),
            float(self.env.metric_history_warmup_seconds(spec.required_metrics)),
        )
        if warmup_seconds:
            print(f">>> [Orchestrator] Warming real metrics before normal capture (~{warmup_seconds:g}s)...")
            time.sleep(warmup_seconds)
            self._wait_for_fresh_metrics(warmup_seconds)
        record_pre_mock_stage("metric_warmup")

        self._call_metric_history_hooks("start_metric_history_normal_capture")
        normal_captures = []
        normal_capture_ranges = []
        for capture_index in range(spec.normal_capture_count):
            normal_start_ms = (
                self._aligned_now_ms(spec.base_step_seconds)
                if capture_index == 0
                else self._next_aligned_ms(spec.base_step_seconds)
            )
            normal_end_ms = normal_start_ms + spec.normal_capture_seconds * 1000
            self._sleep_until_ms(normal_end_ms)
            normal_metrics = self.env.capture_metric_history(
                spec.required_metrics,
                normal_start_ms,
                normal_end_ms,
                spec.base_step_seconds,
                metric_targets=spec.metric_targets,
                rate_windows=spec.metric_rate_windows,
            )
            normal_records = self.env.capture_history_records(
                spec.record_sources,
                normal_start_ms,
                normal_end_ms,
            )
            capture_id = f"normal-{capture_index}"
            normal_captures.append(NormalHistoryCapture(
                capture_id=capture_id,
                metrics=normal_metrics,
                records=normal_records,
            ))
            normal_capture_ranges.append({
                "capture_id": capture_id,
                "start_ms": normal_start_ms,
                "end_ms": normal_end_ms,
            })
            record_pre_mock_stage(f"normal_capture_{capture_index}")
        self._call_metric_history_hooks("finish_metric_history_normal_capture")

        if spec.install_before_normal_capture:
            if not spec.activate_during_target_capture:
                self._activate_faults(allow_running=True)
        else:
            self._install_faults()
        if not spec.activate_during_target_capture:
            self._prepare_observability()
        target_start_ms = self._next_aligned_ms(spec.base_step_seconds)
        target_end_ms = target_start_ms + spec.fault_capture_seconds * 1000
        self._sleep_until_ms(target_start_ms)
        if spec.activate_during_target_capture:
            self._activate_faults(allow_running=True)
            self._prepare_observability()
        self._sleep_until_ms(target_end_ms)
        target_metrics = self.env.capture_metric_history(
            spec.required_metrics,
            target_start_ms,
            target_end_ms,
            spec.base_step_seconds,
            metric_targets=spec.metric_targets,
            rate_windows=spec.metric_rate_windows,
        )
        target_records = self.env.capture_history_records(
            spec.record_sources,
            target_start_ms,
            target_end_ms,
        )
        record_pre_mock_stage("target_capture")
        finalize_capture = getattr(self.env, "finalize_metric_history_capture", None)
        if callable(finalize_capture):
            finalize_capture(target_start_ms, target_end_ms)
        self._call_metric_history_hooks("settle_after_history_capture")
        aftermath_metrics = None
        aftermath_records = None
        if spec.aftermath_capture_seconds:
            # RETURN_TO_NORMAL contracts capture the real post-incident
            # recovery from this environment after the fault is physically
            # resolved, so the frozen tail replays a real convergence instead
            # of a fabricated instant return to baseline.
            self._call_metric_history_hooks("begin_metric_history_aftermath")
            aftermath_start_ms = target_end_ms
            aftermath_end_ms = aftermath_start_ms + spec.aftermath_capture_seconds * 1000
            self._sleep_until_ms(aftermath_end_ms)
            aftermath_metrics = self.env.capture_metric_history(
                spec.required_metrics,
                aftermath_start_ms,
                aftermath_end_ms,
                spec.base_step_seconds,
                metric_targets=spec.metric_targets,
                rate_windows=spec.metric_rate_windows,
            )
            aftermath_records = self.env.capture_history_records(
                spec.record_sources,
                aftermath_start_ms,
                aftermath_end_ms,
            )
            self._call_metric_history_hooks("end_metric_history_aftermath")
            record_pre_mock_stage("aftermath_capture")

        workload_runners = getattr(self.case_run, "workload_runners", None)
        retain_workload = any(
            bool(getattr(record.injector, "retain_workload_after_metric_history", False))
            for record in self.case_run.injections
        )
        if not retain_workload:
            for runner in reversed(workload_runners or ()):
                runner.stop()
            if workload_runners is not None:
                workload_runners.clear()
        unsettled_records = []
        for record in self.case_run.injections:
            settle_history_capture = getattr(record.injector, "settle_after_history_capture", None)
            if callable(settle_history_capture):
                settle_history_capture(record.context)
                record.state = InjectionState.QUIESCED
            else:
                unsettled_records.append(record)
        for record in unsettled_records:
            if record.state not in {InjectionState.READY, InjectionState.PLANNED}:
                raise RuntimeError(
                    f"Cannot quiesce frozen-history injector {type(record.injector).__name__}: "
                    f"state={record.state.value}, expected={InjectionState.READY.value} or {InjectionState.PLANNED.value}"
                )
            record.state = InjectionState.QUIESCING
            record.injector.quiesce(record.context)
            record.state = InjectionState.QUIESCED

        capture_validator = getattr(self.case.evaluator, "validate_metric_history_captures", None)
        capture_validation = None
        if callable(capture_validator):
            validation_kwargs = {
                "normal_captures": tuple(capture.metrics for capture in normal_captures),
                "target_metrics": target_metrics,
                "target_points": spec.fault_capture_seconds // spec.base_step_seconds,
                "base_step_seconds": spec.base_step_seconds,
                "normal_capture_count": spec.normal_capture_count,
            }
            if hasattr(self.case, "initial_resource_groups"):
                validation_kwargs["checkout_budget_ru_per_second"] = next(
                    float(ru)
                    for group, ru, _ in self.case.initial_resource_groups
                    if str(group) == "mf_rg01_checkout"
                )
            capture_validation = capture_validator(**validation_kwargs)
        for record in self.case_run.injections:
            finalize_target = getattr(record.injector, "finalize_metric_history_target_capture", None)
            if callable(finalize_target):
                finalize_target(record.context, target_start_ms, target_end_ms)
        history_result = HistoryAssembler(self.env.metric_history_catalog()).assemble(
            CapturedHistoryInputs(
                normal_captures=tuple(normal_captures),
                target_metrics=target_metrics,
                target_records=target_records,
                aftermath_metrics=aftermath_metrics,
                aftermath_records=aftermath_records,
                decoy_lightning_job_ids=tuple(
                    lightning_decoy_job_id(self.env.run_id, index)
                    for index in range(1, spec.decoy_lightning_job_count + 1)
                ),
                spec=spec,
                seed=seed,
            ),
            agent_start_candidate_ms=int(time.time() * 1000),
        )
        if capture_validation is not None:
            timeline_validator = getattr(self.case.evaluator, "validate_metric_history_timeline", None)
            if not callable(timeline_validator):
                raise RuntimeError(
                    "Frozen-history Case capture validator has no assembled-timeline validator: "
                    f"evaluator={self.case.evaluator.__name__!r}, scenario={self.scenario.scenario_id!r}, "
                    f"case={self.case.case_id!r}"
                )
            timeline_validation = timeline_validator(history_result.timeline, capture_validation)
            history_result = replace(
                history_result,
                timeline=replace(
                    history_result.timeline,
                    audit={
                        **history_result.timeline.audit,
                        "frozen_history_validation": timeline_validation,
                    },
                ),
            )
        record_pre_mock_stage("history_assembly_and_validation")
        if spec.post_target_mode == "RESUME_NORMAL":
            self._quiesce_faults()
        detach_history_provider = getattr(self.env, "detach_scenario_history_provider", None)
        if callable(detach_history_provider):
            detach_history_provider()
        self.env.bind_metric_history(history_result.timeline)
        # Injectors may record trusted frozen-history truth (e.g. the target
        # window) now that the assembled timeline is bound to the environment.
        self._call_metric_history_hooks("metric_history_bound")
        self.case_run.metric_history = dict(history_result.timeline.audit)
        self.case_run.metric_history["pre_mock_stage_timings"] = dict(pre_mock_stage_timings)
        self.case_run.metric_history["normal_capture_ranges"] = normal_capture_ranges
        self.case_run.metric_history["target_capture_range"] = {
            "start_ms": target_start_ms,
            "end_ms": target_end_ms,
        }
        if spec.aftermath_capture_seconds > 0:
            self.case_run.metric_history["aftermath_capture_range"] = {
                "start_ms": target_end_ms,
                "end_ms": target_end_ms + spec.aftermath_capture_seconds * 1000,
            }
        self.case_run.metric_history["agent_handoff"] = {
            "diagnostic_workload": (
                "retained_after_target_capture"
                if retain_workload else "stopped_after_target_capture"
            ),
            "fault_policy": "latent",
            "history": "frozen_before_agent",
        }
        self.evaluator.capture_safety_baseline(self.case_run)
        print(
            ">>> [Orchestrator] Frozen history frozen. "
            f"history_sha256={history_result.timeline.history_sha256}"
        )
        print(f">>> [Orchestrator] Setup complete. Scenario: {self.scenario.description}")

    def _wait_for_fresh_metrics(self, warmup_seconds: float) -> None:
        """Top up the fixed warmup until every service has recent metric samples.

        The capture's rate queries need a sample for every database service
        within the rate window; under host load cAdvisor scrapes can stall for
        whole windows after deployment readiness already saw first samples.
        Waits at most FRESH_METRICS_EXTRA_SECONDS beyond the fixed warmup and
        fails with the stale services named, mirroring the readiness probes.
        """
        probe = getattr(self.env, "metric_samples_fresh", None)
        if not callable(probe):
            return
        deadline = time.monotonic() + self.FRESH_METRICS_EXTRA_SECONDS
        poll_seconds = 5
        while not probe(window_seconds=30):
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Frozen-history capture aborted: metric samples are not fresh after "
                    f"warmup={warmup_seconds:g}s + {self.FRESH_METRICS_EXTRA_SECONDS}s grace"
                )
            print(
                f">>> [Orchestrator] Metric samples stale; waiting for cAdvisor "
                f"(up to {self.FRESH_METRICS_EXTRA_SECONDS:g}s grace)..."
            )
            time.sleep(poll_seconds)

    def _call_metric_history_hooks(self, *hook_names: str) -> None:
        for hook_name in hook_names:
            for record in self.case_run.injections:
                hook = getattr(record.injector, hook_name, None)
                if callable(hook):
                    hook(record.context)

    @staticmethod
    def _aligned_now_ms(step_seconds: int) -> int:
        step_ms = step_seconds * 1000
        return (int(time.time() * 1000) // step_ms) * step_ms

    @staticmethod
    def _next_aligned_ms(step_seconds: int) -> int:
        step_ms = step_seconds * 1000
        return (int(time.time() * 1000) // step_ms + 1) * step_ms

    @staticmethod
    def _sleep_until_ms(deadline_ms: int) -> None:
        remaining = deadline_ms / 1000 - time.time()
        if remaining > 0:
            time.sleep(remaining)

    def _apply_case_environment_contract(self) -> None:
        self.env.configure_case(self.case)

    def _warm_up_runtime(self) -> None:
        warmup_seconds = self.run_config.runtime_warmup_seconds
        if warmup_seconds is None:
            warmup_seconds = self.case.background_workload.warmup_seconds
        if warmup_seconds:
            print(f">>> [Orchestrator] Scenario runtime active. Warming up metrics (~{warmup_seconds}s)...")
            time.sleep(warmup_seconds)

    def _install_faults(self) -> None:
        for record in self.case_run.injections:
            self._begin_injection(record, {InjectionState.PLANNED}, "install")
            record.injector.install(record.context)
            record.state = InjectionState.RUNNING

    def _activate_faults(self, *, allow_running: bool = False) -> None:
        expected_states = {InjectionState.PLANNED, InjectionState.QUIESCED}
        if allow_running:
            expected_states.add(InjectionState.RUNNING)
        for record in self.case_run.injections:
            self._begin_injection(
                record,
                expected_states,
                "activate",
            )
            record.injector.activate(record.context)
            record.state = InjectionState.RUNNING

    def _quiesce_faults(self) -> None:
        for record in reversed(self.case_run.injections):
            if record.state is InjectionState.QUIESCED:
                # Frozen-history settle paths quiesce early via
                # settle_after_history_capture; quiesce is idempotent.
                continue
            if record.state not in {InjectionState.READY, InjectionState.RUNNING}:
                raise RuntimeError(
                    f"Cannot quiesce injector {type(record.injector).__name__}: "
                    f"scenario={self.scenario.scenario_id}, case={self.case.case_id}, "
                    f"state={record.state.value}, expected=ready or running"
                )
            record.state = InjectionState.QUIESCING
            record.injector.quiesce(record.context)
            record.state = InjectionState.QUIESCED

    def _begin_injection(
        self,
        record: InjectionRecord,
        expected_states: set[InjectionState],
        operation: str,
    ) -> None:
        if record.state not in expected_states:
            expected = ", ".join(sorted(state.value for state in expected_states))
            raise RuntimeError(
                f"Cannot {operation} injector {type(record.injector).__name__}: "
                f"scenario={self.scenario.scenario_id}, case={self.case.case_id}, "
                f"state={record.state.value}, expected={expected}"
            )
        record.state = InjectionState.STARTING

    def _prepare_observability(self) -> None:
        evidence_owners = {}
        for record in self.case_run.injections:
            if record.state is not InjectionState.RUNNING:
                raise RuntimeError(
                    f"Cannot prepare observability for {type(record.injector).__name__}: "
                    f"scenario={self.scenario.scenario_id}, case={self.case.case_id}, "
                    f"state={record.state.value}, expected={InjectionState.RUNNING.value}"
                )
            record.state = InjectionState.OBSERVING
            evidence = record.injector.prepare_observability(record.context)
            if not isinstance(evidence, Mapping):
                raise TypeError(
                    f"{type(record.injector).__name__}.prepare_observability() "
                    f"must return a Mapping, got {type(evidence).__name__}"
                )
            for key in evidence:
                if key in evidence_owners:
                    raise ValueError(
                        f"Duplicate injection evidence key {key!r}: "
                        f"{evidence_owners[key]} and {type(record.injector).__name__}"
                    )
                evidence_owners[key] = type(record.injector).__name__
            record.evidence = evidence
            record.state = InjectionState.READY

    def _save_fault_snapshot(self, snapshot_name: str, base_snapshot_name: str):
        print(f"[FaultSnapshot] Saving post-injection snapshot: {snapshot_name}")
        for record in reversed(self.case_run.injections):
            if record.state is not InjectionState.RUNNING:
                raise RuntimeError(
                    f"Cannot prepare snapshot for {type(record.injector).__name__}: "
                    f"scenario={self.scenario.scenario_id}, case={self.case.case_id}, "
                    f"state={record.state.value}, expected={InjectionState.RUNNING.value}"
                )
            record.state = InjectionState.QUIESCING
            record.injector.quiesce(record.context)
            record.state = InjectionState.QUIESCED
        self.env.save_snapshot(
            snapshot_name,
            {
                "aiopsbench.image_kind": "fault",
                "aiopsbench.scenario_id": self.scenario.scenario_id,
                "aiopsbench.case_id": self.case.case_id,
                "aiopsbench.fault_stage": "post_fault_injection",
                "aiopsbench.base_image": base_snapshot_name,
            },
        )
        print(f"[FaultSnapshot] Snapshot ready: {snapshot_name}")

    def _start_workload_runner(self):
        spec = self.case.background_workload
        self.case_run.background_workload_planned = {
            "profile_count": len(spec.profiles),
            "planned_qps": sum(profile.qps for profile in spec.profiles),
            "worker_count": spec.worker_count,
            "seed": spec.seed,
            "start_phase": spec.start_phase.value,
            "warmup_seconds": spec.warmup_seconds,
        }
        if not spec.profiles:
            return
        from src.scenarios.runtime.workload_runner import WorkloadRunner
        runner = WorkloadRunner(
            self.env,
            profiles=list(spec.profiles),
            worker_count=spec.worker_count,
            seed=spec.seed,
        )
        for record in self.case_run.injections:
            attach_runner = getattr(record.injector, "attach_workload_runner", None)
            if attach_runner is not None:
                attach_runner(runner)
        self.env.attach_workload_runner(runner)
        runner.start()
        self.case_run.workload_runners.append(runner)

    def _stop_workload_runners_for_snapshot(self) -> None:
        for runner in reversed(self.case_run.workload_runners):
            runner.stop()
        self.case_run.workload_runners.clear()

    def teardown(self):
        """
        单个 Case 结束后的清理流程：
        1. 调用所有 FaultInjector 的 recover()
        2. 销毁 Env（env.teardown 内部会停 workload runner）
        """
        print(f">>> [Orchestrator] Tearing down environment...")
        failures = []
        observed = {}
        for runner in reversed(self.case_run.workload_runners):
            try:
                runner.stop()
                observed.update(runner.get_observed())
            except Exception as exc:
                failures.append((f"stop workload runner {type(runner).__name__}", exc))
        self.case_run.background_workload_observed = observed
        def graceful_cleanup():
            for record in reversed(self.case_run.injections):
                if record.state in {InjectionState.PLANNED, InjectionState.RECOVERED}:
                    continue
                record.state = InjectionState.RECOVERING
                record.injector.recover(record.context)
                record.state = InjectionState.RECOVERED
        error = []
        thread = threading.Thread(target=lambda: self._capture_cleanup_error(graceful_cleanup, error), daemon=True)
        thread.start()
        thread.join(timeout=120)
        if thread.is_alive():
            print(">>> [Orchestrator] Graceful cleanup exceeded 120s; saving artifacts and forcing resource removal")
            force = getattr(self.env.deployment, "force_teardown", None)
            if force is None:
                raise RuntimeError("Timed-out cleanup has no force_teardown implementation")
            force()
        else:
            failures.extend(error)
            try:
                self.env.teardown()
            except Exception as exc:
                failures.append((f"teardown environment {type(self.env).__name__}", exc))
        if failures:
            details = "; ".join(f"{operation}: {exc!r}" for operation, exc in failures)
            raise RuntimeError(
                f"Scenario teardown failed: scenario={self.scenario.scenario_id}, "
                f"case={self.case.case_id}; {details}"
            ) from failures[0][1]
        print(f">>> [Orchestrator] Teardown complete.")

    @staticmethod
    def _capture_cleanup_error(cleanup, errors):
        try:
            cleanup()
        except Exception as exc:
            errors.append(("graceful cleanup", exc))

    def _run_evaluation(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent 提交诊断结果后，触发评估流程。
        submission 作为一条 submit action 追加进 action_history 供 Evaluator 使用。
        """
        print(f"\n>>> [Orchestrator] Submission received. Running evaluation...")
        report, parse_error = _normalized_submission(submission)
        if parse_error is not None:
            print(
                "[Orchestrator] Submission report failed schema validation; "
                f"evaluating it as a failed claim: {parse_error}"
            )
        self.action_history.append({"api": "submit", "args": report})
        result = self.evaluator.evaluate(self.case_run)
        self._last_eval_result = result

        if self.pretty_print:
            print("\033[93m" + "=" * 60 + "\033[0m\n")
            print("\n\033[93m🏆 [Evaluation Result]\033[0m")
            print(f"  \033[1mDiagnosisPass:\033[0m {result['DiagnosisPass']}")
            print(f"  \033[1mOutcomePass:\033[0m {result['OutcomePass']}")
            print(f"  \033[1mSafePass:\033[0m {result['SafePass']}")
            print("\033[93m" + "=" * 60 + "\033[0m\n")
        else:
            print(f">>> [Orchestrator] Evaluation result:\n{json.dumps(result, ensure_ascii=False, indent=2)}")

        return result

    def _parse_env_result(self, result: Any) -> Any:
        if isinstance(result, str):
            try:
                return json.loads(result)
            except Exception:
                return result
        return result

    def _get_result_status(self, action: Dict[str, Any], res_dict: Dict[str, Any]):
        if "status" in res_dict:
            return res_dict["status"]
        if "success" in res_dict:
            return "success" if res_dict["success"] else "failed"
        if "error" in res_dict:
            return "error"
        if action.get("api") == "submit":
            return "success"
        return "success"

    def _is_success_status(self, status) -> bool:
        return str(status).lower() in ["success", "true", "ok", "completed", "exiting"]

    def _print_value(self, value: Any, indent: int = 5):
        prefix = " " * indent
        if isinstance(value, list):
            if not value:
                print(f"{prefix}[]")
                return
            for item in value:
                if isinstance(item, dict):
                    print(f"{prefix}- {json.dumps(item, ensure_ascii=False, default=str)}")
                elif isinstance(item, (list, tuple)):
                    print(f"{prefix}- {json.dumps(item, ensure_ascii=False, default=str)}")
                else:
                    print(f"{prefix}- {item}")
            return
        if isinstance(value, dict):
            if not value:
                print(f"{prefix}{{}}")
                return
            for key, item in value.items():
                if isinstance(item, (dict, list, tuple)):
                    print(f"{prefix}{key}:")
                    self._print_value(item, indent + 2)
                else:
                    print(f"{prefix}{key}: {item}")
            return
        print(f"{prefix}{value}")

    def _print_help_result(self, res_dict: Dict[str, Any]):
        if "tools" in res_dict:
            print(f"  \033[36m📄 Tools:\033[0m")
            tools = res_dict["tools"]
            if not tools:
                print("     []")
            for tool in tools:
                if isinstance(tool, dict):
                    name = tool.get("name", "unknown")
                    description = tool.get("description", "")
                    print(f"     - {name}: {description}")
                else:
                    print(f"     - {tool}")
        if "tool" in res_dict:
            print(f"  \033[36m📄 Tool:\033[0m {res_dict['tool']}")
        if "description" in res_dict:
            print(f"  \033[36m💬 Description:\033[0m {res_dict['description']}")
        if "args" in res_dict:
            print(f"  \033[36m📄 Args:\033[0m")
            args = res_dict["args"]
            if not args:
                print("     []")
            for arg in args:
                if isinstance(arg, dict):
                    name = arg.get("name", "unknown")
                    arg_type = arg.get("type", "unknown")
                    required = "必填" if arg.get("required") else "可选"
                    description = arg.get("description", "")
                    print(f"     - {name} ({arg_type}, {required}): {description}")
                else:
                    print(f"     - {arg}")

    def _print_metric_result(self, res_dict: Dict[str, Any]):
        print(f"  \033[36m📄 Metric:\033[0m {res_dict['metric']}")
        for key in ("series", "records", "snapshot", "current", "window"):
            if key in res_dict:
                print(f"  \033[36m📄 {key.title()}:\033[0m")
                self._print_value(res_dict[key])

    def _print_result_dict(self, action: Dict[str, Any], res_dict: Dict[str, Any]):
        status = self._get_result_status(action, res_dict)
        status_icon = "✅" if self._is_success_status(status) else "❌"
        print(f"  {status_icon} \033[1mStatus:\033[0m {status}")
        if "error" in res_dict:
            print(f"  \033[36m💬 Error:\033[0m {res_dict['error']}")
        if "message" in res_dict:
            print(f"  \033[36m💬 Message:\033[0m {res_dict['message']}")
        if "tools" in res_dict or "tool" in res_dict:
            self._print_help_result(res_dict)
        if "metric" in res_dict:
            self._print_metric_result(res_dict)
        if "result" in res_dict:
            print(f"  \033[36m📄 Result:\033[0m")
            self._print_value(res_dict["result"])
        handled_keys = {
            "status", "success", "error", "message", "tools", "tool", "description",
            "args", "metric", "target", "count", "value", "result",
        }
        details = {k: v for k, v in res_dict.items() if k not in handled_keys}
        if details:
            print(f"  \033[36m📄 Details:\033[0m")
            self._print_value(details)

    def _report_interaction(self, turn: int, source: str, thinking: str,
                            api: str, args: Dict[str, Any], result: Any):
        """EnvGateway 的 reporter 回调：打印一次工具调用的 thinking / action / 结果。

        在网关锁内被调用，因此并行场景下输出不会交错。turn 在并行下意义减弱，
        改以 source（如专家名）区分调用方。
        """
        args_str = ", ".join(
            f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in args.items()
        )
        if self.pretty_print:
            print("\n\033[94m" + "=" * 60 + "\033[0m")
            tag = f" \033[35m@{source}\033[0m" if source else ""
            print(f"\033[96m🤖 [Agent - Turn {turn}]{tag}\033[0m")
            if thinking:
                print(f"  \033[90m💭 Thinking:\033[0m \033[3m{thinking}\033[0m")
            print(f"  \033[93m🛠️  Action:\033[0m {api} \033[90m({args_str})\033[0m")
            print("\n\033[92m🖥️  [Environment]\033[0m")
            if isinstance(result, dict):
                self._print_result_dict({"api": api, "args": args}, result)
            else:
                print(f"  \033[36m📄 Output:\033[0m")
                self._print_value(result)
        else:
            print("\n" + "-" * 50)
            src = f" @{source}" if source else ""
            print(f"[Agent Turn {turn}{src}]")
            if thinking:
                print(f"[Agent Thinking]\n{thinking}\n")
            print(f"[Agent Action] {api}({args_str})")
            try:
                print(f"[Env Result ({api})]\n{json.dumps(result, ensure_ascii=False, indent=2, default=str)}")
            except Exception:
                print(f"[Env Result ({api})]\n{result}")

    def _print_prompts(self, sys_prompt: str, user_prompt: str, use_native: bool):
        """打印 system / user prompt 与已注册工具（初始化阶段）。"""
        if self.pretty_print:
            print("\n\033[94m" + "=" * 60 + "\033[0m")
            print("\033[96m🤖 [Agent System Prompt]\033[0m")
            highlighted_prompt = sys_prompt
            if use_native:
                highlighted_prompt = highlighted_prompt.replace(
                    "请分析场景，并通过提供的 tools 进行函数调用（Function Calling）来执行操作。",
                    "\033[95m请分析场景，并通过提供的 tools 进行函数调用（Function Calling）来执行操作。\033[0m"
                )
            else:
                highlighted_prompt = highlighted_prompt.replace(
                    "你有以下工具可用：\n",
                    "\033[95m你有以下工具可用：\n\033[0m"
                )
            print(f"  {highlighted_prompt.replace(chr(10), chr(10)+'  ')}")
            if use_native:
                print("\n\033[95m🔧 [Registered Native Tools]\033[0m")
                for schema in self._get_tool_schemas():
                    print(f"  - \033[1m{schema['function']['name']}\033[0m: {schema['function']['description']}")
            print("\n\033[96m👤 [Agent User Prompt]\033[0m")
            highlighted_user = user_prompt.replace("当前场景状态：", "\033[93m当前场景状态：\033[0m\033[3m")
            print(f"  {highlighted_user.replace(chr(10), chr(10)+'  ')}")
            print("\033[94m" + "=" * 60 + "\033[0m\n")
        else:
            print("[Agent System Prompt]", sys_prompt[:200] + "..." if len(sys_prompt) > 200 else sys_prompt)
            if use_native:
                tool_names = [s['function']['name'] for s in self._get_tool_schemas()]
                print("[Registered Native Tools]", ", ".join(tool_names))
            print("[Agent User Prompt]", user_prompt[:200] + "..." if len(user_prompt) > 200 else user_prompt)

    def run(self):
        """
        Orchestrator 生命周期管理。
        1. setup(): 部署 Env + 注入故障
        2. 初始化：下发 prompt / 工具 schema，构造 EnvGateway 注入给 Agent
        3. submission = agent.solve()  —— Agent 自驱动诊断（线性或并行）
        4. 评估 submission
        5. teardown()
        """
        print("========================================")
        print("Orchestrator is now in charge.")
        print("========================================")

        self._run_started_monotonic = time.monotonic()
        agent_started = None
        try:
            # 1. Setup: 部署 Env + 注入故障
            self.setup()

            # 2. 组装并下发工具 Schema、System Prompt 和 User Prompt
            sys_prompt = self._get_system_prompt()
            user_prompt = self._get_user_prompt()
            if hasattr(self.agent, "set_tools"):
                self.agent.set_tools(self._get_tool_schemas())
            if getattr(self.agent, "requires_tool_help", False):
                self.agent.set_tool_help({
                    schema["function"]["name"]: json.loads(self.env.help(schema["function"]["name"]))
                    for schema in self._get_tool_schemas()
                })
            if hasattr(self.agent, "set_system_prompt"):
                self.agent.set_system_prompt(sys_prompt)
            if hasattr(self.agent, "set_user_prompt"):
                self.agent.set_user_prompt(user_prompt)

            use_native = getattr(self.agent, "use_native_tools", False)
            self._print_prompts(sys_prompt, user_prompt, use_native)

            # 2b. 构造环境网关并注入 Agent，设置轮次上限
            gateway = EnvGateway(
                self.env,
                self.action_history,
                turn_history=self.turn_history,
                reporter=self._report_interaction,
            )
            self.agent.init_env_gateway(gateway)
            self.agent.max_turns = self.max_turns

            # 3. Agent 自驱动诊断，返回 submission
            agent_started = time.monotonic()
            self.phase_timings["preparation_seconds"] = round(
                agent_started
                - self._run_started_monotonic
                - self.phase_timings["container_start_seconds"],
                3,
            )
            try:
                submission = self.agent.solve()
            finally:
                self.phase_timings["agent_interaction_seconds"] = round(
                    time.monotonic() - agent_started, 3
                )
            self.case_run.model_usage.extend(self.agent.model_usage_history)

            # 4. 评估
            evaluation_started = time.monotonic()
            try:
                self._run_evaluation(submission if isinstance(submission, dict) else {})
            finally:
                self.phase_timings["evaluation_seconds"] = round(
                    time.monotonic() - evaluation_started, 3
                )

        except Exception as e:
            print(f"[Orchestrator] Error during run: {e}")
            raise

        finally:
            run_failure = sys.exc_info()[1]
            finalization_failures = []
            if agent_started is None:
                self.phase_timings["preparation_seconds"] = round(
                    time.monotonic()
                    - self._run_started_monotonic
                    - self.phase_timings.get("container_start_seconds", 0.0),
                    3,
                )
            cleanup_started = time.monotonic()
            try:
                # Workload execution totals are collected while teardown stops the runners.
                # Export only after that snapshot so the trace contains the observed workload.
                self.teardown()
            except Exception as exc:
                finalization_failures.append(("teardown scenario", exc))
            finally:
                self.phase_timings["cleanup_seconds"] = round(
                    time.monotonic() - cleanup_started, 3
                )
                self.phase_timings["total_seconds"] = round(
                    time.monotonic() - self._run_started_monotonic, 3
                )
            try:
                from src.visualization.exporter import export_run_trace
                export_run_trace(self, output_dir="logs/traces/")
            except Exception as exc:
                finalization_failures.append(("export run trace", exc))
            if finalization_failures:
                details = "; ".join(
                    f"{operation}: {exc!r}"
                    for operation, exc in finalization_failures
                )
                if run_failure is not None:
                    details = f"run: {run_failure!r}; {details}"
                self.agent.on_run_finished(None, details)
                raise RuntimeError(
                    f"Scenario finalization failed: scenario={self.scenario.scenario_id}, "
                    f"case={self.case.case_id}; {details}"
                ) from (run_failure or finalization_failures[0][1])
            self.agent.on_run_finished(
                self._last_eval_result if run_failure is None else None,
                str(run_failure) if run_failure is not None else None,
            )

        return self._last_eval_result
