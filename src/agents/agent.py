import json
import os
import re
import time
from abc import ABC, abstractmethod
from copy import deepcopy
from html import unescape
from typing import Any, Dict, List, Optional, Tuple

from src.agents.cache_breaker import (
    CacheBreakerConfig,
    CacheCircuitBreaker,
    CacheCircuitBreakerError,
)
from src.agents.context_compaction import (
    BURST_WARNING_PREFIX,
    CONTEXT_SUMMARY_SYSTEM_PROMPT,
    ContextCompactionConfig,
    ContextCompactionError,
    SUMMARY_HEADINGS,
    SUMMARY_MESSAGE_PREFIX,
    build_summary_user_prompt,
    is_burst_warning_message,
    select_compaction,
    split_history_into_rounds,
)
from src.agents.loop_guard import (
    TOOL_LOOP_ABORT_MARKER,
    LoopGuardConfig,
    check_loop,
    round_signature,
)
from src.utils import LogManager
from src.scenarios.evaluation.protocol import StructuredReport


FINAL_TURN_SUBMIT_PROMPT = (
    "Maximum diagnostic turns reached. This is your final response. "
    "Summarize the diagnosis and actions taken using the evidence collected so far, "
    "then call the `submit` tool. Do not call any other tool."
)
LLM_REQUEST_TIMEOUT_SECONDS = 300.0
LLM_REQUEST_MAX_RETRIES = 10
# Reasoning models burn output budget on hidden reasoning before emitting any
# visible action; an unset budget therefore falls back to this explicit value
# instead of the provider default.
LLM_DEFAULT_MAX_OUTPUT_TOKENS = 20000
LLM_503_RETRY_MAX = 3
LLM_503_RETRY_WAIT_SECONDS = 60.0


def split_diagnostic_token_usage(
    total_input_tokens: int,
    output_tokens: int,
    previous_total_input_tokens: Optional[int],
) -> Dict[str, int]:
    """Split cumulative LLM input into new and path-cached tokens.

    Some providers reset or rotate prompt-cache segments between turns, so their
    reported input total can be smaller than the previous path total. Treat that
    turn as a fresh input segment instead of aborting the diagnostic run.
    """
    cache_input_token = previous_total_input_tokens or 0
    if total_input_tokens < cache_input_token:
        cache_input_token = 0
    return {
        "input_token": total_input_tokens - cache_input_token,
        "cache_input_token": cache_input_token,
        "output_token": output_tokens,
    }


def require_final_submission(agent_name: str, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
    action_names = [action.get("api", "") for action in actions]
    submit_actions = [action for action in actions if action.get("api") == "submit"]
    if len(submit_actions) != 1:
        raise RuntimeError(
            f"{agent_name} final turn must contain exactly one submit: "
            f"returned_actions={action_names!r}"
        )
    return submit_actions[0]["args"]


def _normalize_tool_args(args: Dict[str, Any]) -> Dict[str, Any]:
    """LLM 走 native tools 发参时可能把可选 string 字段显式填成空串（"" 表示
    "未提供"），而工具校验只接受缺省。规范化为直接删除该键，让参数的签名默认值
    生效——部分工具的默认值本身就是 ""（如 match_diagnose_knowledge 的
    alert_metric、optimize_index_selection 的时间窗），映射成 None 会改变语义
    甚至在函数体内炸 TypeError；其余非法值仍由工具校验照常抛出。"""
    return {
        key: value
        for key, value in (args or {}).items()
        if not (isinstance(value, str) and value == "")
    }


class BaseAgent(ABC):
    """
    Agent 层抽象。
    职责：Agent 自己驱动整个诊断工作流（solve），通过 execute() 访问环境。
    控制权在 Agent 手里；Orchestrator 只负责生命周期管理、prompt/工具注入、
    构造并注入 EnvGateway，以及在 solve 返回后触发评估。

    环境交互的物理通道（EnvGateway）由 Orchestrator 在初始化阶段建立并注入，
    Agent 不直接持有 env，只通过 execute() 转一层，保持单一访问路径。
    """
    use_native_tools: bool = False

    def __init__(self, enable_log: bool = False, log_dir: Optional[str] = None):
        self.enable_log = enable_log
        self.log_dir = log_dir
        self.action_history: List[Dict[str, Any]] = []
        self.max_turns: int = 20
        self._gateway = None
        self.model_usage_history: List[Dict[str, Any]] = []
        self.logger = None
        if self.enable_log:
            self.logger = LogManager.get_logger(self.__class__.__name__, log_dir)

    def set_tools(self, tools: List[Dict[str, Any]]):
        """设置工具Schema（由Orchestrator调用）"""
        pass

    def _log(self, message: str, level: str = "info"):
        """内部日志记录方法"""
        if self.enable_log and self.logger:
            getattr(self.logger, level)(message)

    def record_action(
        self,
        raw_input: str,
        parsed_action: Dict[str, Any],
        token_usage: Optional[Dict[str, int]] = None,
    ):
        """记录action到历史记录"""
        action_id = parsed_action.get("action_id") or parsed_action.get("id")
        if action_id is None:
            action_id = f"agent-action-{len(self.action_history) + 1:06d}"
            parsed_action = {**parsed_action, "action_id": action_id}
        entry = {
            "action_id": action_id,
            "raw_input": raw_input,
            "parsed_action": parsed_action
        }
        if token_usage is not None:
            entry.update(token_usage)
        self.action_history.append(entry)
        self._log(f"Action recorded: {json.dumps(entry, ensure_ascii=False)}")

    def get_history(self) -> List[Dict[str, Any]]:
        """获取历史记录"""
        return self.action_history

    def print_history(self):
        """打印历史记录"""
        print(f"\n[{self.__class__.__name__}] Action History (共 {len(self.action_history)} 条):")
        print("-" * 60)
        for i, entry in enumerate(self.action_history, 1):
            print(f"[{i}] 原始输入: {entry['raw_input']}")
            print(f"    解析动作: {json.dumps(entry['parsed_action'], ensure_ascii=False, indent=4)}")
            print("-" * 60)

    # --- 环境交互（控制反转）---

    def init_env_gateway(self, gateway):
        """注入环境网关（由 Orchestrator 在 run() 初始化阶段调用）。"""
        self._gateway = gateway

    @property
    def gateway(self):
        return self._gateway

    def execute(self, api: str, args: Dict[str, Any], *,
                thinking: str = "", source: str = "", action_id: str | None = None) -> Dict[str, Any]:
        """通过网关执行一次环境工具调用，返回解析后的结果字典。

        Agent 子类内部所有环境访问都应走这里，而不是直接碰 env 或 gateway。
        """
        if self._gateway is None:
            raise RuntimeError(
                f"{self.__class__.__name__}.execute 调用前未注入 EnvGateway；"
                "Orchestrator 必须在 run() 初始化阶段调用 init_env_gateway。"
            )
        args = _normalize_tool_args(args)
        try:
            return self._gateway.execute(api, args, thinking=thinking, source=source, action_id=action_id)
        except TypeError as exc:
            if "unexpected keyword argument 'action_id'" not in str(exc):
                raise
            return self._gateway.execute(api, args, thinking=thinking, source=source)

    def set_system_prompt(self, system_prompt: str):
        """设置系统提示词（通常由Orchestrator调用）"""
        pass

    def set_user_prompt(self, user_prompt: str):
        """设置用户提示词（通常由Orchestrator调用）"""
        pass

    def on_run_finished(self, evaluation, error):
        """Notify interactive agents after evaluation, cleanup and trace export."""
        pass

    @abstractmethod
    def solve(self) -> Dict[str, Any]:
        """Agent 自己驱动整个诊断流程（线性或并行），返回提交的 submission。

        在 solve 内部通过 self.execute(api, args, ...) 访问环境。流程结束（相当于
        旧模型里的 submit）时返回 submission 字典作为诊断结果；Orchestrator 据此评估。
        """
        pass

    # --- 诊断路径导出（可视化协议） ---

    def export_diagnostic_trace(self) -> Dict[str, Any]:
        """收集本 agent 的诊断路径，输出符合可视化协议的字典。

        子类通过覆写下列受保护方法定制各部分，无需重写整体结构：
        _export_prompts / _export_turns / _export_structure / _export_conversation。
        协议定义见 src/agents/trace_protocol.py。
        """
        trace = {
            "agent_type": self.__class__.__name__,
            "mode": getattr(self, "mode", None),
            "prompts": self._export_prompts(),
            "tool_schema": deepcopy(getattr(self, "tools_schema", [])) or [],
            "turns": self._export_turns(),
            "diagnostic_structure": self._export_structure(),
            "conversation_history": self._export_conversation(),
            "conversation_history_raw": self._export_conversation_raw(),
            "conversation_phases": self._export_conversation_phases(),
            "llm_usage": self._export_llm_usage(),
            "llm_calls": deepcopy(getattr(self, "_llm_calls", [])),
            "context_compaction": self._export_context_compaction(),
        }
        for field in ("model", "provider", "reasoning_effort"):
            if hasattr(self, field):
                trace[field] = getattr(self, field)
        return trace

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": "", "user": ""}

    def _export_turns(self) -> List[Dict[str, Any]]:
        return self._build_turns_from_action_history()

    def _export_structure(self) -> Dict[str, Any]:
        return {"type": "linear"}

    def _export_conversation(self) -> List[Dict[str, Any]]:
        return []

    def _export_conversation_raw(self) -> List[Dict[str, Any]]:
        return self._export_conversation()

    def _export_conversation_phases(self) -> List[Dict[str, Any]]:
        return []

    def _export_llm_usage(self) -> List[Dict[str, Any]]:
        return []

    def _export_context_compaction(self) -> List[Dict[str, Any]]:
        return []

    def _build_turns_from_action_history(self) -> List[Dict[str, Any]]:
        """从 self.action_history 构建线性 turns。

        record_action 对每个 action 调用一次，同一轮的多个 action 共享相同的
        raw_input，因此按 raw_input 分组还原为一轮。
        """
        turns: List[Dict[str, Any]] = []
        for entry in self.action_history:
            raw = entry.get("raw_input", "")
            parsed = entry.get("parsed_action", {}) or {}
            action = {
                "action_id": entry.get("action_id"),
                "api": parsed.get("api", ""),
                "args": parsed.get("args", {}),
            }
            if turns and turns[-1]["_raw"] == raw:
                turns[-1]["actions"].append(action)
                turns[-1]["results"].append(
                    {"result_id": entry.get("result_id"), "action_id": action["action_id"], "api": action["api"], "status": "executed", "data": entry.get("result")}
                )
                continue
            turns.append({
                "_raw": raw,
                "turn_number": len(turns) + 1,
                "timestamp": None,
                "thinking": self._extract_thinking(raw),
                "actions": [action],
                "results": [
                    {"result_id": entry.get("result_id"), "action_id": action["action_id"], "api": action["api"], "status": "executed", "data": entry.get("result")}
                ],
            })
            for key in ("input_token", "cache_input_token", "output_token"):
                if key in entry:
                    turns[-1][key] = entry[key]
        for t in turns:
            t.pop("_raw", None)
        return turns

    @staticmethod
    def _extract_thinking(raw_input: Any) -> str:
        try:
            data = json.loads(raw_input) if isinstance(raw_input, str) else raw_input
            if isinstance(data, dict):
                return data.get("thinking", "") or ""
        except (json.JSONDecodeError, TypeError):
            pass
        return ""


class HumanAgent(BaseAgent):
    """
    人类可通过交互式终端驱动诊断的 Agent。
    人类输入命令，HumanAgent 解析成 action 并通过 execute 直接打到环境，
    输入 submit 时把累计的提交内容作为 submission 返回。
    """

    def __init__(self, enable_log: bool = False, log_dir: Optional[str] = None):
        super().__init__(enable_log, log_dir)

    def _parse_command(self, raw_input: str) -> Dict[str, Any]:
        parts = raw_input.strip().split(maxsplit=1)
        if not parts:
            return {"api": "noop", "args": {}}

        cmd = parts[0].lower()
        args_str = parts[1] if len(parts) > 1 else ""

        if cmd == "query_metrics":
            sub_parts = args_str.split(maxsplit=1)
            metric_type = sub_parts[0] if sub_parts else ""
            target = sub_parts[1] if len(sub_parts) > 1 else None
            return {"api": "query_metrics", "args": {"metric_type": metric_type, "target": target}}

        elif cmd == "execute_sql":
            return {"api": "execute_sql", "args": {"sql_query": args_str}}

        elif cmd == "manage_instance":
            sub_parts = args_str.split(maxsplit=1)
            action = sub_parts[0] if sub_parts else ""
            target = sub_parts[1] if len(sub_parts) > 1 else None
            return {"api": "manage_instance", "args": {"action": action, "target": target}}

        elif cmd in ("query_knowledge_base", "knowledge"):
            return {"api": "query_knowledge_base", "args": {"query": args_str}}

        elif cmd == "submit":
            report = json.loads(args_str)
            StructuredReport.from_mapping(report)
            return {"api": "submit", "args": {"report": report}}

        elif cmd == "exit" or cmd == "quit":
            return {"api": "exit", "args": {}}

        elif cmd == "help":
            if args_str:
                return {"api": "help", "args": {"tool_name": args_str.strip()}}
            else:
                return {"api": "help", "args": {"tool_name": None}}

        else:
            return {"api": "unknown", "args": {"raw": raw_input}}

    def solve(self) -> Dict[str, Any]:
        """交互式 REPL：读人类命令，打到环境，submit/exit 时结束并返回 submission。"""
        while True:
            try:
                raw_input_str = input("\n[HumanAgent]> ").strip()
            except EOFError:
                raise RuntimeError("HumanAgent reached EOF before a structured report was submitted")
            if not raw_input_str:
                continue
            action = self._parse_command(raw_input_str)
            api = action["api"]
            if api == "exit":
                return {}
            if api == "submit":
                return action["args"]
            if api in ("noop", "unknown"):
                print(f"[HumanAgent] 无法识别的命令: {raw_input_str}")
                continue
            self.execute(api, action["args"], source="human")


class LLMAgent(BaseAgent):
    """
    基于大模型的Agent，通过调用LLM接口解析用户意图并生成action。
    支持 OpenAI SDK 与 Anthropic SDK。

    架构说明：
    - solve(): 自驱动诊断循环，调用 LLM、解析 action、通过 execute 打到环境，
      维护对话历史，遇 submit/exit 返回 submission。
    - _next_llm_actions(): 调一次 LLM 并解析出本轮 (thinking, actions)。
    """

    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, system_prompt: str = "",
                 enable_log: bool = False, log_dir: Optional[str] = None,
                 model: Optional[str] = None, config_path: str = "config/llm_config.json",
                 use_native_tools: bool = False, provider: Optional[str] = None,
                 max_output_tokens: Optional[int] = None,
                 context_compaction: Optional[ContextCompactionConfig] = None,
                 loop_guard: Optional[LoopGuardConfig] = None,
                 reasoning_effort: Optional[str] = None):
        super().__init__(enable_log, log_dir)

        loaded_config = None
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
            except Exception as e:
                self._log(f"读取LLM配置文件失败: {str(e)}", "warning")

        # 尝试从配置文件加载 URL 和 API_KEY
        if (not url or not api_key) and loaded_config:
            if model is None:
                model = next(iter(loaded_config), None)
            if model in loaded_config:
                url = url or loaded_config[model].get('url')
                api_key = api_key or loaded_config[model].get('api_key')
                provider = provider or loaded_config[model].get('provider')
        if model is None:
            raise ValueError(
                "LLMAgent requires a model: pass model explicitly or configure one in "
                f"{config_path}"
            )
        self._cache_breaker = CacheCircuitBreaker(
            CacheBreakerConfig.from_entry((loaded_config or {}).get(model)), model)
            
        if not url or not api_key:
            raise ValueError(f"必须提供URL和API_KEY，或在配置文件 '{config_path}' 中为模型 '{model}' 配置它们。")

        if context_compaction is None:
            context_compaction = ContextCompactionConfig()
        if context_compaction.enabled and os.path.exists(config_path):
            if loaded_config is None:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
            model_config = loaded_config.get(model)
            if isinstance(model_config, dict) and "context_window_tokens" in model_config:
                context_compaction = context_compaction.bind_model_context_window(
                    model_config["context_window_tokens"]
                )

        self.url = url
        self.api_key = api_key
        self.mode = "llm"
        self.model = model
        # fixed id: the gateway's cache-injection is per metadata.user_id
        # bucket — random per-run ids stop getting cache_control injected
        self.metadata_user_id = "aiopsbench-shared"
        self.provider = (provider or self._detect_provider(self.model)).lower()
        if self.provider not in ("openai", "anthropic"):
            raise ValueError(f"不支持的LLM provider: {self.provider}，可选值为 openai 或 anthropic。")
        self.url = self._normalize_url(self.url, self.provider)
        self.system_prompt = system_prompt
        self.user_prompt = ""
        self.use_native_tools = use_native_tools
        self.max_output_tokens = max_output_tokens
        self.context_compaction = context_compaction
        self.loop_guard = loop_guard or LoopGuardConfig()
        if reasoning_effort is not None and reasoning_effort not in {"low", "medium", "high", "xhigh"}:
            raise ValueError(
                "reasoning_effort must be low, medium, high, or xhigh: "
                f"value={reasoning_effort!r}"
            )
        # effort 层级：显式参数 > 环境变量（manifest） > llm_config 按模型默认
        config_effort = None
        if isinstance(loaded_config, dict) and isinstance(loaded_config.get(model), dict):
            config_effort = loaded_config[model].get("reasoning_effort")
        self.reasoning_effort = reasoning_effort or os.environ.get("AIOPS_REASONING_EFFORT") or config_effort
        if self.reasoning_effort is not None and self.reasoning_effort not in {"low", "medium", "high", "xhigh"}:
            raise ValueError(
                "reasoning_effort must be low, medium, high, or xhigh: "
                f"value={self.reasoning_effort!r}"
            )
        self.tools_schema = None
        self._conversation_history: List[Dict[str, Any]] = [
            {"role": "system", "content": system_prompt}
        ]
        self._last_llm_output: Optional[str] = None
        self._usage_events: List[Dict[str, Any]] = []
        self._llm_calls: List[Dict[str, Any]] = []
        self._diagnostic_turn_usage: List[Dict[str, int]] = []
        self._diagnostic_usage_event_count = 0
        self._llm_request_count = 0
        # 精确 token 记账：来自每次响应的 provider usage，用于压缩触发。
        self._llm_prompt_tokens: Optional[int] = None
        self._llm_completion_tokens: Optional[int] = None
        self._llm_round_growth_tokens: List[int] = []
        self._round_signatures: List[str] = []
        self._context_compaction_events: List[Dict[str, Any]] = []
        self._conversation_raw_history: List[Dict[str, Any]] = deepcopy(self._conversation_history)
        self._conversation_phases: List[Dict[str, Any]] = [{
            "phase_index": 0,
            "messages": deepcopy(self._conversation_history),
            "compaction": None,
        }]
        self._log(
            f"LLMAgent初始化完成，url={self.url}, model={self.model}, "
            f"provider={self.provider}, use_native_tools={self.use_native_tools}"
        )

    @staticmethod
    def _detect_provider(model: str) -> str:
        if "claude" in model.lower():
            return "anthropic"
        return "openai"

    @staticmethod
    def _normalize_url(url: str, provider: str) -> str:
        url = url.rstrip("/")
        for suffix in ("/chat/completions", "/v1/messages"):
            if url.endswith(suffix):
                url = url[: -len(suffix)]
                break
        url = url.rstrip("/")
        if provider == "anthropic":
            if url.endswith("v1"):
                url = url[:-len("/v1")]
        return url

    def _is_claude_model(self) -> bool:
        return "claude" in self.model.lower()

    def _is_anthropic_native_api(self) -> bool:
        return self.provider == "anthropic"

    def set_tools(self, tools: List[Dict[str, Any]]):
        self.tools_schema = tools
        self._log("已加载 Tools Schema")

    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt
        if self._conversation_history and self._conversation_history[0].get("role") == "system":
            self._replace_conversation_message(0, {"role": "system", "content": system_prompt})
        else:
            self._conversation_history.insert(0, {"role": "system", "content": system_prompt})
            self._conversation_raw_history.insert(0, deepcopy(self._conversation_history[0]))
            self._conversation_phases[-1]["messages"].insert(0, deepcopy(self._conversation_history[0]))
        self._log("已更新 System Prompt")

    def set_user_prompt(self, user_prompt: str):
        self.user_prompt = user_prompt
        if self._conversation_history and self._conversation_history[-1].get("role") == "user":
            self._replace_conversation_message(
                len(self._conversation_history) - 1,
                {"role": "user", "content": user_prompt},
            )
        else:
            self._append_conversation_message({"role": "user", "content": user_prompt})
        self._log("已更新 LLMAgent User Prompt")

    def _append_conversation_message(self, message: Dict[str, Any]) -> None:
        self._ensure_conversation_trace()
        message_copy = deepcopy(message)
        self._conversation_history.append(message_copy)
        self._conversation_raw_history.append(deepcopy(message_copy))
        self._conversation_phases[-1]["messages"].append(deepcopy(message_copy))

    def _replace_conversation_message(self, index: int, message: Dict[str, Any]) -> None:
        self._ensure_conversation_trace()
        message_copy = deepcopy(message)
        self._conversation_history[index] = message_copy
        self._conversation_raw_history[index] = deepcopy(message_copy)
        self._conversation_phases[-1]["messages"][index] = deepcopy(message_copy)

    def _synchronize_conversation_trace(self) -> None:
        self._ensure_conversation_trace()
        current = deepcopy(self._conversation_history)
        phase_messages = self._conversation_phases[-1]["messages"]
        if current == phase_messages:
            return
        if len(current) >= len(phase_messages) and current[:len(phase_messages)] == phase_messages:
            appended = current[len(phase_messages):]
            self._conversation_raw_history.extend(deepcopy(appended))
            phase_messages.extend(deepcopy(appended))
            return
        if len(self._conversation_phases) == 1 and len(phase_messages) == 1:
            self._conversation_raw_history = current
            self._conversation_phases[0]["messages"] = deepcopy(current)
            return
        raise RuntimeError(
            "LLMAgent conversation history changed outside the conversation recorder: "
            f"model={self.model!r}, phase_index={self._conversation_phases[-1]['phase_index']}, "
            f"tracked_message_count={len(phase_messages)}, current_message_count={len(current)}"
        )

    def _ensure_conversation_trace(self) -> None:
        if hasattr(self, "_conversation_raw_history") and hasattr(self, "_conversation_phases"):
            return
        self._conversation_raw_history = deepcopy(self._conversation_history)
        self._conversation_phases = [{
            "phase_index": 0,
            "messages": deepcopy(self._conversation_history),
            "compaction": None,
        }]

    def _call_llm(
        self,
        messages: List[Dict[str, Any]],
        *,
        include_tools: Optional[bool] = None,
        purpose: str = "diagnostic",
        max_output_tokens_override: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        调用大模型API
        :param messages: 对话历史消息列表
        :return: API响应字典
        """
        if purpose not in {"diagnostic", "summary", "auxiliary"}:
            raise ValueError(f"Unsupported LLM call purpose: purpose={purpose!r}")
        if include_tools is None:
            include_tools = self.use_native_tools
        call_id = f"llm-call-{len(getattr(self, '_llm_calls', [])) + 1:06d}"
        request = deepcopy(messages)
        for attempt in range(LLM_503_RETRY_MAX + 1):
            try:
                if self.provider == "anthropic":
                    response = self._call_anthropic_llm(
                        messages,
                        include_tools=include_tools,
                        purpose=purpose,
                        max_output_tokens_override=max_output_tokens_override,
                    )
                else:
                    response = self._call_openai_llm(
                        messages,
                        include_tools=include_tools,
                        purpose=purpose,
                        max_output_tokens_override=max_output_tokens_override,
                    )
                break
            except Exception as e:
                # 网关渠道抖动(如 cc-sale 分组 503 无可用渠道)通常持续数分钟;
                # SDK 内置的 10 次退避只覆盖 ~2 分钟,这里对 503 追加应用级等待重试。
                if attempt < LLM_503_RETRY_MAX and "503" in str(e):
                    self._log(
                        f"LLM API 返回 503,{LLM_503_RETRY_WAIT_SECONDS:.0f}s 后重试 "
                        f"({attempt + 1}/{LLM_503_RETRY_MAX}): {str(e)[:200]}",
                        "warning",
                    )
                    time.sleep(LLM_503_RETRY_WAIT_SECONDS)
                    continue
                self._log(f"LLM API调用失败: {str(e)}", "error")
                self._llm_calls.append({
                    "call_id": call_id, "purpose": purpose, "provider": self.provider,
                    "model": self.model, "request": request, "response": {"error": str(e)},
                    "status": "error", "error": str(e), "timeout_seconds": LLM_REQUEST_TIMEOUT_SECONDS,
                })
                return {"error": str(e)}
        if self._cache_breaker.tripped:
            report_path = self._cache_breaker.report(os.environ.get("AIOPS_TRACE_OUTPUT_DIR"))
            self._log(
                "缓存熔断触发: " + self._cache_breaker.error_message()
                + (f"; report={report_path}" if report_path else ""),
                "error",
            )
            raise CacheCircuitBreakerError(self._cache_breaker.error_message())
        self._record_model_usage(response, purpose=purpose)
        self._llm_calls.append({
            "call_id": call_id, "purpose": purpose, "provider": self.provider,
            "model": self.model, "request": request, "response": deepcopy(response),
            "status": "success", "timeout_seconds": LLM_REQUEST_TIMEOUT_SECONDS,
        })
        return response

    def _record_model_usage(self, response: Dict[str, Any], purpose: str = "diagnostic") -> None:
        usage = response.get("usage")
        if not isinstance(usage, dict):
            raise ValueError(
                f"LLM response has no usage object: provider={self.provider!r}, model={self.model!r}"
            )
        if self.provider == "anthropic":
            record = {
                "provider": self.provider,
                "model": self.model,
                "input_tokens": int(usage["input_tokens"]),
                "cache_input_tokens": int(usage.get("cache_read_input_tokens", 0))
                + int(usage.get("cache_creation_input_tokens", 0)),
                "output_tokens": int(usage["output_tokens"]),
            }
        else:
            details = usage.get("prompt_tokens_details") or {}
            record = {
                "provider": self.provider,
                "model": self.model,
                "input_tokens": int(usage["prompt_tokens"]),
                "cache_input_tokens": int(details.get("cached_tokens", 0)),
                "output_tokens": int(usage["completion_tokens"]),
            }
        if purpose != "diagnostic":
            record["purpose"] = purpose
        self.model_usage_history.append(record)

    @staticmethod
    def _normalize_openai_messages(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized_messages = []
        for message in messages:
            normalized = dict(message)
            content = normalized.get("content")
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    block_type = block.get("type")
                    if block_type == "text":
                        text_parts.append(block.get("text", ""))
                    elif block_type == "tool_use":
                        text_parts.append(json.dumps(block, ensure_ascii=False))
                    elif block_type == "tool_result":
                        text_parts.append(block.get("content", ""))
                normalized["content"] = "\n".join(text_parts)
            normalized_messages.append(normalized)
        return normalized_messages

    def _resolve_max_output_tokens(self, override: Optional[int]) -> int:
        if override is not None:
            return override
        if self.max_output_tokens is not None:
            return self.max_output_tokens
        return LLM_DEFAULT_MAX_OUTPUT_TOKENS

    def _call_openai_llm(
        self,
        messages: List[Dict[str, Any]],
        *,
        include_tools: Optional[bool] = None,
        purpose: str = "diagnostic",
        max_output_tokens_override: Optional[int] = None,
    ) -> Dict[str, Any]:
        from openai import OpenAI

        if include_tools is None:
            include_tools = self.use_native_tools
        client = OpenAI(
            api_key=self.api_key,
            base_url=self.url,
            timeout=LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=LLM_REQUEST_MAX_RETRIES,
        )
        payload = {
            "model": self.model,
            "messages": self._normalize_openai_messages(messages),
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if self.reasoning_effort is not None:
            payload["reasoning_effort"] = self.reasoning_effort
        else:
            payload["temperature"] = 0.7
        output_tokens = self._resolve_max_output_tokens(max_output_tokens_override)
        payload["max_tokens"] = output_tokens
        if include_tools and self.tools_schema:
            payload["tools"] = self.tools_schema
        try:
            response = LLMAgent._assemble_openai_stream(client.chat.completions.create(**payload))
        except Exception as e:
            if self._should_retry_as_anthropic(e):
                self.provider = "anthropic"
                return self._call_anthropic_llm(
                    messages,
                    include_tools=include_tools,
                    purpose=purpose,
                    max_output_tokens_override=max_output_tokens_override,
                )
            raise
        dumped = self._dump_llm_response(response)
        self._record_usage(dumped, purpose=purpose)
        return dumped

    @staticmethod
    def _assemble_openai_stream(stream: Any) -> Dict[str, Any]:
        """把流式响应聚合为与非流式 model_dump 等价的响应字典，下游解析不变。"""
        content_parts: List[str] = []
        reasoning_parts: List[str] = []
        tool_calls_by_index: Dict[int, Dict[str, Any]] = {}
        finish_reason = None
        response_id = None
        created = None
        model = None
        usage = None
        for chunk in stream:
            if response_id is None and getattr(chunk, "id", None):
                response_id = chunk.id
            if created is None and getattr(chunk, "created", None):
                created = chunk.created
            if model is None and getattr(chunk, "model", None):
                model = chunk.model
            if getattr(chunk, "usage", None) is not None:
                usage = chunk.usage if isinstance(chunk.usage, dict) else chunk.usage.model_dump()
            for choice in getattr(chunk, "choices", None) or []:
                delta = getattr(choice, "delta", None)
                if delta is None:
                    continue
                content = getattr(delta, "content", None)
                if content:
                    content_parts.append(content)
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    reasoning_parts.append(reasoning)
                for tc in getattr(delta, "tool_calls", None) or []:
                    slot = tool_calls_by_index.setdefault(
                        tc.index,
                        {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
                    )
                    if getattr(tc, "id", None):
                        slot["id"] = tc.id
                    fn = getattr(tc, "function", None)
                    if fn is not None:
                        if getattr(fn, "name", None):
                            slot["function"]["name"] += fn.name
                        if getattr(fn, "arguments", None):
                            slot["function"]["arguments"] += fn.arguments
                if getattr(choice, "finish_reason", None):
                    finish_reason = choice.finish_reason
        message: Dict[str, Any] = {"role": "assistant", "content": "".join(content_parts) or None}
        if reasoning_parts:
            message["reasoning_content"] = "".join(reasoning_parts)
        if tool_calls_by_index:
            message["tool_calls"] = [
                tool_calls_by_index[index] for index in sorted(tool_calls_by_index)
            ]
        return {
            "id": response_id,
            "object": "chat.completion",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "message": message,
                "finish_reason": finish_reason,
            }],
            "usage": usage,
        }

    @staticmethod
    def _dump_llm_response(response: Any) -> Dict[str, Any]:
        if hasattr(response, "model_dump"):
            return response.model_dump()
        if isinstance(response, dict):
            return response
        if isinstance(response, str):
            return LLMAgent._parse_llm_response_text(response)
        raise TypeError(
            f"LLM SDK returned unsupported response type: {type(response).__name__}, "
            f"value={response!r}"
        )

    @staticmethod
    def _parse_llm_response_text(text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("data:"):
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("data:") and line != "data: [DONE]":
                    text = line[5:].strip()
                    break
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise TypeError(f"LLM SDK returned non-JSON string response: {text!r}") from exc
        if not isinstance(parsed, dict):
            raise TypeError(f"LLM SDK returned JSON {type(parsed).__name__}, expected object: {parsed!r}")
        return parsed

    def _should_retry_as_anthropic(self, error: Exception) -> bool:
        if not self._is_claude_model() or self.provider == "anthropic":
            return False
        message = str(error).lower()
        return "anthropic" in message or "claude" in message or "messages" in message or "not found" in message

    def _call_anthropic_llm(
        self,
        messages: List[Dict[str, Any]],
        *,
        include_tools: Optional[bool] = None,
        purpose: str = "diagnostic",
        max_output_tokens_override: Optional[int] = None,
    ) -> Dict[str, Any]:
        import anthropic

        if include_tools is None:
            include_tools = self.use_native_tools
        client = anthropic.Anthropic(
            api_key=self.api_key,
            base_url=self.url,
            timeout=LLM_REQUEST_TIMEOUT_SECONDS,
            max_retries=LLM_REQUEST_MAX_RETRIES,
        )
        system_prompt, anthropic_messages = self._build_anthropic_messages(messages)
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": self._resolve_max_output_tokens(max_output_tokens_override),
            # shared constant: the gateway's cache injection is per user_id
            # bucket, so every run must land in the same bucket
            "metadata": {"user_id": self.metadata_user_id},
        }
        if self.reasoning_effort is not None:
            # anthropic 原生 effort 走 output_config；SDK 1.5.0 不接受顶层
            # reasoning_effort（Messages.stream() 直接 TypeError）
            payload["output_config"] = {"effort": self.reasoning_effort}
        # Anthropic 推荐通过 provider 端默认采样；部分新模型直接拒绝 temperature，
        # 因此 payload 对所有 Anthropic 模型一律不带该字段。
        if system_prompt:
            # 部分 Anthropic 上游网关会停止为同前缀连续调用注入 cache_control
            # （实测 cache_creation/cache_read 全 0），但会原样透传客户端标记。
            # 在稳定前缀（tools + system）上挂 ephemeral 断点，恢复缓存熔断器
            # 所守护的缓存行为；对话消息逐轮变化，不设断点。
            payload["system"] = [{
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }]
        if include_tools and self.tools_schema:
            payload["tools"] = self._convert_tools_to_anthropic(self.tools_schema)
        with client.messages.stream(**payload) as stream:
            response = stream.get_final_message()
        dumped = self._dump_llm_response(response)
        self._record_usage(dumped, purpose=purpose)
        return dumped

    def _record_usage(self, response: Dict[str, Any], purpose: str = "diagnostic") -> None:
        usage = response.get("usage")
        if not isinstance(usage, dict):
            raise ValueError(
                f"LLM response lacks provider token usage: provider={self.provider!r}, "
                f"model={self.model!r}"
            )
        input_details = usage.get("prompt_tokens_details") or {}
        cached_input_tokens = usage.get(
            "cache_read_input_tokens",
            input_details.get("cached_tokens", 0),
        )
        cache_write_input_tokens = usage.get("cache_creation_input_tokens", 0)
        input_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
        if self.provider == "anthropic" and all(
            isinstance(value, int)
            for value in (input_tokens, cached_input_tokens, cache_write_input_tokens)
        ):
            input_tokens += cached_input_tokens + cache_write_input_tokens
        event = {
            "call_id": f"llm-call-{len(self._usage_events) + 1:06d}",
            "provider": self.provider,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "input_tokens": input_tokens,
            "output_tokens": usage.get("output_tokens", usage.get("completion_tokens")),
            "cached_input_tokens": cached_input_tokens,
            "cache_write_input_tokens": cache_write_input_tokens,
        }
        token_fields = (
            "input_tokens",
            "output_tokens",
            "cached_input_tokens",
            "cache_write_input_tokens",
        )
        invalid = {key: event[key] for key in token_fields if not isinstance(event[key], int)}
        if invalid:
            raise ValueError(
                f"LLM response has non-integer token usage: provider={self.provider!r}, "
                f"model={self.model!r}, invalid={invalid}"
            )
        if purpose != "diagnostic":
            event["purpose"] = purpose
        self._usage_events.append(event)
        self._cache_breaker.record(event["cached_input_tokens"], purpose, event["call_id"])
        usage_log = os.environ.get("AIOPS_LLM_USAGE_LOG")
        if usage_log:
            with open(usage_log, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(event, ensure_ascii=False) + "\n")
        if purpose == "diagnostic":
            self._update_context_token_chain(event["input_tokens"], event["output_tokens"])

    def llm_usage_events(self) -> List[Dict[str, Any]]:
        """Per-LLM-call provider token usage, for benchmark cost accounting."""
        return list(self._usage_events)

    def _update_context_token_chain(self, input_tokens: int, output_tokens: int) -> None:
        """维护压缩触发用的精确 token 链：每轮增量 = 本轮 prompt − 上轮 prompt − 上轮 output。

        基线缺失（首个请求或刚压缩过）时增量记 0，避免把整段历史误判为单轮突发。
        """
        if self._llm_prompt_tokens is None or self._llm_completion_tokens is None:
            growth = 0
        else:
            growth = max(0, input_tokens - self._llm_prompt_tokens - self._llm_completion_tokens)
        self._llm_round_growth_tokens.append(growth)
        self._llm_prompt_tokens = input_tokens
        self._llm_completion_tokens = output_tokens

    def get_usage_events(self) -> List[Dict[str, Any]]:
        return [dict(event) for event in self._usage_events]

    def get_last_usage_event(self) -> Dict[str, Any]:
        if not self._usage_events:
            raise RuntimeError(
                f"No LLM token usage has been recorded: provider={self.provider!r}, "
                f"model={self.model!r}"
            )
        return dict(self._usage_events[-1])

    def _accept_diagnostic_turn(self) -> None:
        diagnostic_events = [
            event
            for event in self._usage_events
            if event.get("purpose", "diagnostic") == "diagnostic"
        ]
        if len(diagnostic_events) == self._diagnostic_usage_event_count:
            return
        event = diagnostic_events[-1]
        previous_total = None
        if self._diagnostic_turn_usage:
            previous = self._diagnostic_turn_usage[-1]
            previous_total = previous["input_token"] + previous["cache_input_token"]
        self._diagnostic_turn_usage.append(
            split_diagnostic_token_usage(
                event["input_tokens"],
                event["output_tokens"],
                previous_total,
            )
        )
        self._diagnostic_usage_event_count = len(diagnostic_events)

    def diagnostic_turn_count(self) -> int:
        return len(self._diagnostic_turn_usage)

    def get_diagnostic_turn_usage_after(
        self, previous_count: int
    ) -> Optional[Dict[str, int]]:
        current_count = len(self._diagnostic_turn_usage)
        if current_count == previous_count:
            return None
        if current_count != previous_count + 1:
            raise RuntimeError(
                "Expected exactly one diagnostic LLM turn: "
                f"previous_count={previous_count}, current_count={current_count}"
            )
        return dict(self._diagnostic_turn_usage[-1])

    @staticmethod
    def _build_anthropic_messages(messages: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        system_parts = []
        anthropic_messages = []
        for message in messages:
            role = message.get("role")
            content = message.get("content", "")
            if role == "system":
                if content:
                    system_parts.append(str(content))
            elif role in ("user", "assistant"):
                normalized = {"role": role, "content": content if content is not None else ""}
                if role == "assistant" and message.get("tool_calls"):
                    normalized["content"] = LLMAgent._convert_openai_tool_calls_to_anthropic_content(message)
                LLMAgent._append_anthropic_message(anthropic_messages, normalized)
            elif role == "tool":
                tool_message = {
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": message.get("tool_call_id", ""),
                        "content": content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
                    }]
                }
                LLMAgent._append_anthropic_message(anthropic_messages, tool_message)
        return "\n\n".join(system_parts), anthropic_messages

    @staticmethod
    def _append_anthropic_message(messages: List[Dict[str, Any]], message: Dict[str, Any]):
        content = message.get("content", "")
        if content in ("", []):
            return
        if messages and messages[-1].get("role") == message.get("role"):
            previous_content = messages[-1].get("content", "")
            messages[-1]["content"] = LLMAgent._merge_anthropic_content(previous_content, content)
        else:
            messages.append(message)

    @staticmethod
    def _merge_anthropic_content(first: Any, second: Any) -> Any:
        if isinstance(first, list) or isinstance(second, list):
            first_blocks = first if isinstance(first, list) else ([{"type": "text", "text": str(first)}] if first else [])
            second_blocks = second if isinstance(second, list) else ([{"type": "text", "text": str(second)}] if second else [])
            return first_blocks + second_blocks
        return f"{first}\n\n{second}" if first else second

    @staticmethod
    def _convert_openai_tool_calls_to_anthropic_content(message: Dict[str, Any]) -> List[Dict[str, Any]]:
        content_blocks = []
        content = message.get("content")
        if content:
            content_blocks.append({"type": "text", "text": str(content)})
        for tool_call in message.get("tool_calls", []) or []:
            if hasattr(tool_call, "model_dump"):
                tool_call = tool_call.model_dump()
            elif not isinstance(tool_call, dict) and hasattr(tool_call, "dict"):
                tool_call = tool_call.dict()
            function = tool_call.get("function", {}) if isinstance(tool_call, dict) else {}
            if hasattr(function, "model_dump"):
                function = function.model_dump()
            elif not isinstance(function, dict) and hasattr(function, "dict"):
                function = function.dict()
            if not isinstance(function, dict):
                function = {}
            args_raw = function.get("arguments", "{}")
            if isinstance(args_raw, dict):
                args = args_raw
            else:
                try:
                    args = json.loads(args_raw or "{}")
                except (json.JSONDecodeError, TypeError):
                    args = {"raw": args_raw or ""}
            content_blocks.append({
                "type": "tool_use",
                "id": tool_call.get("id", ""),
                "name": function.get("name", "unknown"),
                "input": args
            })
        return content_blocks

    @staticmethod
    def _convert_tools_to_anthropic(tools_schema: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        anthropic_tools = []
        for tool in tools_schema or []:
            if hasattr(tool, "model_dump"):
                tool = tool.model_dump()
            elif not isinstance(tool, dict) and hasattr(tool, "dict"):
                tool = tool.dict()
            function = tool.get("function", {}) if isinstance(tool, dict) else {}
            if hasattr(function, "model_dump"):
                function = function.model_dump()
            elif not isinstance(function, dict) and hasattr(function, "dict"):
                function = function.dict()
            if not isinstance(function, dict) or not function:
                continue
            anthropic_tools.append({
                "name": function.get("name", ""),
                "description": function.get("description", ""),
                "input_schema": function.get("parameters", {"type": "object", "properties": {}})
            })
        return anthropic_tools

    @staticmethod
    def _strip_markdown_codeblock(text: str) -> str:
        text = text.strip()
        match = re.match(r'^```(?:json)?\s*\n?(.*?)\n?\s*```$', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return text

    @staticmethod
    def _extract_json_object(text: str) -> Optional[str]:
        depth = 0
        start = None
        for i, ch in enumerate(text):
            if ch == '{':
                if depth == 0:
                    start = i
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0 and start is not None:
                    return text[start:i + 1]
        return None

    def _text_tool_names(self) -> set[str]:
        names = set()
        for schema in self.tools_schema or []:
            function = schema.get("function", schema) if isinstance(schema, dict) else {}
            name = function.get("name") if isinstance(function, dict) else None
            if name:
                names.add(str(name))
        return names

    @staticmethod
    def _parse_text_tool_value(value: str) -> Any:
        value = unescape(value.strip())
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    def _parse_text_tool_invocation(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse the ``[TOOL_CALL]`` text markup emitted by text-protocol model responses."""
        known_tools = self._text_tool_names()
        marker_match = re.search(
            r"\[TOOL_CALL\]\s*([A-Za-z_][A-Za-z0-9_-]*)",
            text,
        )
        marker_end = marker_match.end() if marker_match else None
        if marker_match is None:
            marker_match = re.search(
                r"\[(?:tool call):\s*([A-Za-z_][A-Za-z0-9_-]*)\s*\]",
                text,
                re.IGNORECASE,
            )
            marker_end = marker_match.end() if marker_match else None
        if marker_match:
            api = marker_match.group(1)
            if api not in known_tools:
                return None
            remainder = text[marker_end:]
            args_text = remainder.lstrip(" _\n")
            if args_text.startswith("```"):
                fenced_match = re.match(
                    r"```(?:json)?\s*\n?(.*?)\n?\s*```",
                    args_text,
                    re.DOTALL | re.IGNORECASE,
                )
                if fenced_match is None:
                    raise ValueError(f"Malformed fenced text tool arguments: api={api!r}, text={text!r}")
                args_text = fenced_match.group(1).strip()
            if args_text.startswith("{"):
                extracted = self._extract_json_object(args_text)
                if extracted is None:
                    raise ValueError(f"Malformed text tool arguments: api={api!r}, text={text!r}")
                args = json.loads(extracted)
                if not isinstance(args, dict):
                    raise TypeError(f"Text tool arguments must be an object: api={api!r}, args={args!r}")
            else:
                args = {}
            return {"thinking": text[:marker_match.start()].strip(), "action": {"api": api, "args": args}}

        parameter_matches = list(
            re.finditer(
                r'<parameter\s+name=["\']([^"\']+)["\']\s*>(.*?)</parameter>',
                text,
                re.DOTALL,
            )
        )
        invoke_match = re.search(r'<invoke(?:\s+name=["\']([^"\']+)["\'])?\s*>', text)
        if parameter_matches and not (invoke_match or re.search(r'</invoke>', text)):
            return None

        api = invoke_match.group(1) if invoke_match else None
        tool_line_end = None
        if api is None:
            prefixed_tools = list(
                re.finditer(
                    r"(?m)^[ \t]*tool([A-Za-z_][A-Za-z0-9_-]*)[ \t]*(?=$|<)",
                    text,
                )
            )
            for match in reversed(prefixed_tools):
                if match.group(1) in known_tools:
                    api = match.group(1)
                    tool_line_end = match.end()
                    break
            else:
                tool_line_end = None

        if api is None:
            tool_lines = list(
                re.finditer(r"(?m)^[ \t]*([A-Za-z_][A-Za-z0-9_-]*)[ \t]*$", text)
            )
            for match in reversed(tool_lines):
                if match.group(1) in known_tools:
                    api = match.group(1)
                    tool_line_end = match.end()
                    break
            else:
                marker_match = re.search(
                    r"(?im)^\s*\*\*(?:tool call|function call):\s*"
                    r"([A-Za-z_][A-Za-z0-9_-]*)\s*\*\*\s*$",
                    text,
                )
                if marker_match and marker_match.group(1) in known_tools:
                    api = marker_match.group(1)
                    tool_line_end = marker_match.end()
                else:
                    tool_line_end = None
        if api is None:
            return None

        if parameter_matches:
            args = {
                match.group(1): self._parse_text_tool_value(match.group(2))
                for match in parameter_matches
            }
            return {"thinking": text[:parameter_matches[0].start()].strip(), "action": {"api": api, "args": args}}

        if invoke_match is not None:
            return {"thinking": text[:invoke_match.start()].strip(), "action": {"api": api, "args": {}}}

        if tool_line_end is None:
            return None
        args_text = self._extract_json_object(text[tool_line_end:])
        if args_text is None:
            return {"thinking": text[:tool_line_end].strip(), "action": {"api": api, "args": {}}}
        args = json.loads(args_text)
        if not isinstance(args, dict):
            raise TypeError(f"Text tool arguments must be an object: api={api!r}, args={args!r}")
        return {"thinking": text[:tool_line_end].strip(), "action": {"api": api, "args": args}}

    def _parse_llm_response(self, llm_output: str) -> Dict[str, Any]:
        if not llm_output or not llm_output.strip():
            return {"thinking": "", "action": {"api": "noop", "args": {}}}
        try:
            cleaned = self._strip_markdown_codeblock(llm_output)
            parsed = json.loads(cleaned)
            thinking = parsed.get("thinking", "")
            action = parsed.get("action", {"api": "noop", "args": {}})
            actions = parsed.get("actions")
            return {"thinking": thinking, "action": action, "actions": actions}
        except json.JSONDecodeError:
            text_tool = self._parse_text_tool_invocation(llm_output)
            if text_tool is not None:
                return {"thinking": text_tool["thinking"], "action": text_tool["action"], "actions": None}
            extracted = self._extract_json_object(llm_output)
            if extracted:
                try:
                    parsed = json.loads(extracted)
                    thinking = parsed.get("thinking", "")
                    action = parsed.get("action", {"api": "noop", "args": {}})
                    actions = parsed.get("actions")
                    return {"thinking": thinking, "action": action, "actions": actions}
                except json.JSONDecodeError:
                    pass
            self._log(f"JSON解析失败，原始输出: {llm_output}", "warning")
            return {
                "thinking": llm_output,
                "action": {"api": "unknown", "args": {"raw": llm_output}}
            }

    def parse_actions(self, raw_input: str) -> List[Dict[str, Any]]:
        """Parse prompt-mode JSON output into one or more standard actions."""
        parsed = self._parse_llm_response(raw_input)
        actions = parsed.get("actions")
        if not isinstance(actions, list):
            actions = [parsed.get("action", {"api": "noop", "args": {}})]

        normalized = []
        for action in actions:
            normalized_action = {
                "api": action.get("api", "noop"),
                "args": action.get("args", {}) or {},
            }
            if action.get("id") is not None:
                normalized_action["id"] = action["id"]
                normalized_action["action_id"] = action["id"]
            normalized.append(normalized_action)
            self.record_action(raw_input, normalized_action)
        return normalized

    def _format_tool_result(self, action_result: Dict[str, Any]) -> str:
        """
        格式化工具执行结果，供LLM理解
        """
        api = action_result.get("api", "unknown")
        result_str = json.dumps(action_result, ensure_ascii=False)
        return f"[工具执行结果] {api}: {result_str}"

    def _is_claude_response(self, llm_response: Dict[str, Any]) -> bool:
        return llm_response.get("type") == "message" and "content" in llm_response and isinstance(llm_response["content"], list)

    def _parse_llm_response_message(self, llm_response: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if self._is_claude_response(llm_response):
            message_obj = llm_response
            parsed = self._parse_claude_message(message_obj)
            history_msg = self._build_anthropic_assistant_history(message_obj)
        elif "choices" in llm_response:
            message_obj = llm_response.get("choices", [{}])[0].get("message", {})
            if "reasoning_content" in message_obj or "reasoning" in message_obj or "thinking" in message_obj:
                parsed = self._parse_reasoning_content_message(message_obj)
            else:
                parsed = self._parse_openai_message(message_obj)
            history_msg = message_obj
        else:
            message_obj = {"content": str(llm_response)}
            parsed = self._parse_openai_message(message_obj)
            history_msg = {"role": "assistant", "content": message_obj["content"]}
        return parsed, history_msg

    @staticmethod
    def _build_anthropic_assistant_history(message_obj: Dict[str, Any]) -> Dict[str, Any]:
        content_blocks = message_obj.get("content", [])
        history_content = []
        for block in content_blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                history_content.append({"type": "text", "text": block.get("text", "")})
            elif block_type == "tool_use":
                history_content.append({
                    "type": "tool_use",
                    "id": block.get("id", ""),
                    "name": block.get("name", ""),
                    "input": block.get("input", {})
                })
        if not history_content:
            history_content = ""
        return {"role": "assistant", "content": history_content}

    @staticmethod
    def _parse_tool_calls_raw(tool_calls_raw: List[Any]) -> List[Dict[str, Any]]:
        """
        将原始tool_calls列表解析为标准化的工具调用列表。
        """
        tool_calls = []
        for tc in tool_calls_raw or []:
            if hasattr(tc, "model_dump"):
                tc = tc.model_dump()
            elif not isinstance(tc, dict) and hasattr(tc, "dict"):
                tc = tc.dict()
            if not isinstance(tc, dict):
                continue
            func = tc.get("function", {})
            if hasattr(func, "model_dump"):
                func = func.model_dump()
            elif not isinstance(func, dict) and hasattr(func, "dict"):
                func = func.dict()
            if not isinstance(func, dict):
                func = {}
            func_name = func.get("name", "unknown")
            args_raw = func.get("arguments", "{}")
            if isinstance(args_raw, dict):
                args = args_raw
            else:
                try:
                    args = json.loads(args_raw or "{}")
                except (json.JSONDecodeError, TypeError):
                    args = {"raw": args_raw or ""}
            if func_name == "submit" and isinstance(args.get("report"), str):
                # 模型可能在 JSON 后附带解释性尾文：优先整体解析，失败则取首段合法 JSON，
                # 完全非法时保留原字符串，交由评估器按不合规提交判定。
                report_raw = args["report"]
                try:
                    args["report"] = json.loads(report_raw)
                except json.JSONDecodeError:
                    try:
                        args["report"], _ = json.JSONDecoder().raw_decode(report_raw)
                    except json.JSONDecodeError:
                        args["report"] = report_raw
            tool_calls.append({
                "api": func_name,
                "args": args,
                "id": tc.get("id")
            })
        return tool_calls

    def _parse_reasoning_content_message(self, message_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析带 reasoning_content/reasoning/thinking 扩展字段的 message 对象。
        这些字段承载推理过程，对应 thinking；不依赖模型名称判定。
        """
        reasoning = message_obj.get("reasoning_content", "") or message_obj.get("reasoning", "") or message_obj.get("thinking", "") or ""
        content = message_obj.get("content", "") or ""
        if not isinstance(reasoning, str):
            reasoning = json.dumps(reasoning, ensure_ascii=False)
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        tool_calls_raw = message_obj.get("tool_calls", [])
        tool_calls = self._parse_tool_calls_raw(tool_calls_raw)

        thinking_parts = []
        if reasoning:
            thinking_parts.append(reasoning)
        if content:
            thinking_parts.append(content)
        thinking = "\n\n".join(thinking_parts)
        if not thinking and tool_calls:
            first_tc = tool_calls[0]
            args_preview = json.dumps(first_tc.get("args", {}), ensure_ascii=False)
            if len(args_preview) > 500:
                args_preview = args_preview[:500] + "..."
            thinking = f"模型未返回可展示的thinking/content字段，直接发起工具调用：{first_tc.get('api', 'unknown')}，参数：{args_preview}"

        return {
            "thinking": thinking,
            "content": content,
            "tool_calls": tool_calls,
            "has_tool_calls": bool(tool_calls)
        }

    def _parse_claude_message(self, message_obj: Dict[str, Any]) -> Dict[str, Any]:
        content_blocks = message_obj.get("content", [])
        text_parts = []
        tool_calls = []
        thinking_parts = []

        for block in content_blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type", "")
            if block_type == "text":
                text_parts.append(block.get("text", ""))
            elif block_type == "thinking":
                thinking_parts.append(block.get("thinking", ""))
            elif block_type == "tool_use":
                tool_calls.append({
                    "api": block.get("name", "unknown"),
                    "args": block.get("input", {}),
                    "id": block.get("id")
                })

        content = "\n".join(text_parts)
        thinking = "\n\n".join(thinking_parts)
        if not thinking and content:
            thinking = content
        if not thinking and tool_calls:
            first_tc = tool_calls[0]
            args_preview = json.dumps(first_tc.get("args", {}), ensure_ascii=False)
            if len(args_preview) > 500:
                args_preview = args_preview[:500] + "..."
            thinking = f"模型未返回可展示的thinking/content字段，直接发起工具调用：{first_tc.get('api', 'unknown')}，参数：{args_preview}"

        return {
            "thinking": thinking,
            "content": content,
            "tool_calls": tool_calls,
            "has_tool_calls": bool(tool_calls)
        }

    def _parse_openai_message(self, message_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析标准OpenAI格式的message对象（GPT系列等默认格式）。
        """
        content = message_obj.get("content", "") or ""
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        tool_calls_raw = message_obj.get("tool_calls", [])
        tool_calls = self._parse_tool_calls_raw(tool_calls_raw)

        thinking_parts = []
        for key in ("reasoning_content", "reasoning", "thinking"):
            value = message_obj.get(key, "") or ""
            if value:
                if not isinstance(value, str):
                    value = json.dumps(value, ensure_ascii=False)
                thinking_parts.append(value)
        if content:
            thinking_parts.append(content)
        thinking = "\n\n".join(thinking_parts)
        if not thinking and tool_calls:
            first_tc = tool_calls[0]
            args_preview = json.dumps(first_tc.get("args", {}), ensure_ascii=False)
            if len(args_preview) > 500:
                args_preview = args_preview[:500] + "..."
            thinking = f"模型未返回可展示的thinking/content字段，直接发起工具调用：{first_tc.get('api', 'unknown')}，参数：{args_preview}"

        return {
            "thinking": thinking,
            "content": content,
            "tool_calls": tool_calls,
            "has_tool_calls": bool(tool_calls)
        }

    def solve(self, max_empty_retries: int = 2) -> Dict[str, Any]:
        """自驱动诊断循环：调用 LLM → 逐个 execute → 把结果喂回对话，
        直到 LLM 发起 submit/exit；耗尽 max_turns 后追加一次最终提交轮。"""
        self._log("LLMAgent.solve 开始驱动诊断循环...")

        if not any(m.get("role") == "user" for m in self._conversation_history):
            initial_user_msg = self.user_prompt if self.user_prompt else "请根据上述场景开始诊断。"
            self._append_conversation_message(
                {"role": "user", "content": initial_user_msg}
            )

        for turn in range(1, self.max_turns + 1):
            diagnostic_turn_count = self.diagnostic_turn_count()
            thinking, actions = self._next_llm_actions(max_empty_retries)
            token_usage = self.get_diagnostic_turn_usage_after(diagnostic_turn_count)
            if not actions:
                raise RuntimeError(
                    f"LLMAgent produced no actions before submission: max_turns={self.max_turns}"
                )
            self._check_repeated_tool_rounds(actions)

            first = True
            for action in actions:
                api = action.get("api", "")
                args = action.get("args", {}) or {}
                self.record_action(
                    json.dumps(
                        {"thinking": thinking, "action": {"api": api, "args": args}},
                        ensure_ascii=False,
                    ),
                    {"api": api, "args": args},
                    token_usage=token_usage,
                )
                if api == "exit":
                    raise RuntimeError("LLMAgent exited without submitting a diagnosis")
                if api == "submit":
                    return args
                result = self.execute(
                    api, args, thinking=(thinking if first else ""), source="",
                    action_id=self.action_history[-1]["action_id"],
                )
                first = False
                self._feed_tool_result(result, tool_call_id=action.get("id"), api=api)

        self._append_final_turn_prompt()
        _, submission = self._next_final_submission(
            max_empty_retries=max_empty_retries,
            agent_name="LLMAgent",
        )
        return submission

    def _check_repeated_tool_rounds(self, actions: List[Dict[str, Any]]) -> None:
        """止血守卫：检测诊断死循环并在执行当轮前终止。

        属于模型能力缺陷：不强制产出诊断报告。终止错误带 TOOL_LOOP_ABORT_MARKER，
        由实验 runner 归类为 model_failure。
        """
        if not actions:
            return
        self._round_signatures.append(round_signature(actions))
        reason = check_loop(self._round_signatures, self.loop_guard)
        if reason is not None:
            raise RuntimeError(
                f"{TOOL_LOOP_ABORT_MARKER}: {reason}；"
                "诊断陷入死循环，提前终止（模型能力缺陷，不强制产出诊断报告）"
            )

    def _append_final_turn_prompt(self):
        self._append_conversation_message(
            {"role": "user", "content": FINAL_TURN_SUBMIT_PROMPT}
        )

    def _next_final_submission(
        self, max_empty_retries: int, agent_name: str
    ) -> Tuple[str, Dict[str, Any]]:
        diagnostic_turn_count = self.diagnostic_turn_count()
        thinking, actions = self._next_llm_actions(max_empty_retries)
        token_usage = self.get_diagnostic_turn_usage_after(diagnostic_turn_count)
        submission = require_final_submission(agent_name, actions)
        self.record_action(
            json.dumps(
                {"thinking": thinking, "action": {"api": "submit", "args": submission}},
                ensure_ascii=False,
            ),
            {"api": "submit", "args": submission},
            token_usage=token_usage,
        )
        return thinking, submission

    def _finish_diagnostic_turn(
        self, thinking: str, actions: List[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        self._accept_diagnostic_turn()
        return thinking, actions

    def _summarize_old_history(self, old_messages: List[Dict[str, Any]]) -> str:
        summary_messages = [
            {"role": "system", "content": CONTEXT_SUMMARY_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": build_summary_user_prompt(old_messages),
            },
        ]
        response = self._call_llm(
            summary_messages,
            include_tools=False,
            purpose="summary",
            max_output_tokens_override=self.context_compaction.summary_max_output_tokens,
        )
        if "error" in response:
            raise ContextCompactionError(
                f"Context summary LLM call failed: error={response['error']!r}"
            )
        parsed, _ = self._parse_llm_response_message(response)
        if parsed["has_tool_calls"]:
            raise ContextCompactionError(
                "Context summary LLM returned tool calls instead of summary text"
            )
        summary = parsed.get("content")
        if not isinstance(summary, str) or not summary.strip():
            raise ContextCompactionError(
                "Context summary LLM returned no visible text content: "
                f"response_keys={sorted(response)}, parsed_keys={sorted(parsed)}"
            )
        missing_headings = [heading for heading in SUMMARY_HEADINGS if heading not in summary]
        if missing_headings:
            raise ContextCompactionError(
                "Context summary LLM omitted required headings: "
                f"missing={missing_headings!r}"
            )
        return summary.strip()

    def _maybe_compact_context(self) -> None:
        """基于 provider 返回的精确 token 触发压缩，不做任何字符估算。

        触发条件（满足其一）：
        - 上次请求的 prompt tokens 已达 trigger_ratio × 窗口；
        - 上一轮的增长量会填满剩余余量（下一轮请求大概率超窗）。
        压缩模式：任一轮增长 ≥ burst_ratio × 窗口 → burst（仅保留第一轮 + 丢失警告）；
        否则走摘要压缩。没有任何可用 usage（首个请求）时不压缩。
        """
        context_compaction = getattr(self, "context_compaction", None)
        if context_compaction is None or not context_compaction.enabled:
            return
        if self._llm_prompt_tokens is None:
            return
        last_growth = self._llm_round_growth_tokens[-1] if self._llm_round_growth_tokens else 0
        headroom = context_compaction.context_window_tokens - self._llm_prompt_tokens
        over_trigger = self._llm_prompt_tokens >= context_compaction.trigger_tokens
        round_fills_headroom = last_growth >= headroom
        if not (over_trigger or round_fills_headroom):
            return
        if last_growth >= context_compaction.burst_ratio * context_compaction.context_window_tokens:
            self._apply_burst_compaction(reason="round_growth_exceeded_burst_ratio")
            return
        if not self._apply_summary_compaction():
            self._apply_burst_compaction(reason="no_summarizable_old_rounds")

    def _apply_summary_compaction(self) -> bool:
        """常规摘要压缩：摘要旧轮次、保留最近 keep_recent_rounds 轮。成功返回 True。

        摘要 LLM 调用失败（例如旧轮次本身就超窗）时返回 False，由调用方回落 burst。
        """
        selection = select_compaction(self._conversation_history, self.context_compaction)
        if selection is None:
            return False
        try:
            summary = self._summarize_old_history(list(selection.old_messages))
        except ContextCompactionError as exc:
            self._log(f"摘要压缩失败，转用 burst 压缩: {exc}", "warning")
            return False
        compacted = selection.apply(summary)
        summary_message = {
            "role": "user",
            "content": SUMMARY_MESSAGE_PREFIX + summary.strip(),
        }
        compaction = {
            "mode": "summary",
            "request_index": self._llm_request_count,
            "context_window_tokens": self.context_compaction.context_window_tokens,
            "before_prompt_tokens": self._llm_prompt_tokens,
            "old_round_count": len(selection.old_rounds),
            "protected_round_count": len(selection.protected_rounds),
            "recent_round_count": len(selection.recent_rounds),
        }
        self._replace_conversation_history(compacted, summary_message, compaction)
        return True

    def _apply_burst_compaction(self, *, reason: str) -> bool:
        """突发压缩：单轮增长过大时只保留第一轮（system + 原始任务），丢弃其余全部轮次。

        被丢弃的内容不做摘要（对已超窗的 payload 再发起摘要请求同样会超窗）。
        警告消息附带已执行工具调用清单并明确禁止重复，否则模型失忆后会原样重放
        同一批超窗调用，形成 burst→重放→burst 死循环。
        """
        prefix, rounds = split_history_into_rounds(self._conversation_history)
        if not rounds:
            # 没有任何可丢弃的轮次（例如首个请求本身就超窗），burst 无事可做。
            return False
        kept_prefix = [
            message for message in prefix
            if not is_burst_warning_message(message)
        ]
        ledger_text = self._build_dropped_tool_ledger(rounds)
        warning_message = {
            "role": "user",
            "content": (
                BURST_WARNING_PREFIX + "此前工具调用返回内容过多，超出模型上下文窗口（token 上限），"
                "已触发上下文压缩：仅保留第一轮对话，其后所有轮次（包括最近的工具结果）已被丢弃，"
                "上下文压缩算法可能丢失重要信息。\n"
                + ledger_text
                + "禁止重复以上调用：它们此前已导致上下文超限，重复执行会再次超窗且结果再次被丢弃。"
                "请改用更精确、更小范围的查询，或基于现有信息继续完成原任务并提交。"
            ),
        }
        compacted = [*kept_prefix, warning_message]
        compaction = {
            "mode": "burst",
            "reason": reason,
            "request_index": self._llm_request_count,
            "context_window_tokens": self.context_compaction.context_window_tokens,
            "dropped_round_count": len(rounds),
            "before_prompt_tokens": self._llm_prompt_tokens,
        }
        self._replace_conversation_history(compacted, warning_message, compaction)
        return True

    def _build_dropped_tool_ledger(self, rounds) -> str:
        """汇总被丢弃轮次的工具调用清单（同名同参去重，限制条数与参数长度）。"""
        entries: List[str] = []
        seen = set()
        for round_ in rounds:
            for message in round_.messages:
                for api, args_text in self._iter_round_tool_calls(message):
                    key = f"{api} {args_text}"
                    if key in seen:
                        continue
                    seen.add(key)
                    if len(args_text) > 120:
                        args_text = args_text[:120] + "…"
                    entries.append(f"- {api}: {args_text}")
                    if len(entries) >= 20:
                        return "本轮诊断已执行过的工具调用：\n" + "\n".join(entries) + "\n"
        if not entries:
            return ""
        return "本轮诊断已执行过的工具调用：\n" + "\n".join(entries) + "\n"

    @staticmethod
    def _iter_round_tool_calls(message: Dict[str, Any]):
        """从单条历史消息中提取 (工具名, 参数文本)。覆盖 native/prompt/anthropic 三种形态。"""
        for tc in message.get("tool_calls") or []:
            func = tc.get("function") or {}
            name = func.get("name")
            if name:
                args_text = func.get("arguments", "")
                if not isinstance(args_text, str):
                    args_text = json.dumps(args_text, ensure_ascii=False)
                yield str(name), args_text
        content = message.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    yield str(block.get("name", "unknown")), json.dumps(
                        block.get("input", {}), ensure_ascii=False
                    )
        if message.get("role") == "assistant" and isinstance(content, str) and content.strip():
            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                return
            if not isinstance(parsed, dict):
                return
            actions = parsed.get("actions")
            if actions is None and "action" in parsed:
                actions = [parsed["action"]]
            for action in actions or []:
                if isinstance(action, dict) and action.get("api"):
                    yield str(action["api"]), json.dumps(
                        action.get("args", {}), ensure_ascii=False
                    )

    def _replace_conversation_history(
        self,
        compacted: List[Dict[str, Any]],
        injected_message: Dict[str, Any],
        compaction: Dict[str, Any],
    ) -> None:
        self._conversation_history = compacted
        self._conversation_raw_history.append(deepcopy(injected_message))
        self._conversation_phases.append({
            "phase_index": len(self._conversation_phases),
            "messages": deepcopy(compacted),
            "compaction": deepcopy(compaction),
        })
        self._context_compaction_events.append(compaction)
        # 压缩后历史与旧 usage 基线不再连续，重置精确记账。
        self._llm_prompt_tokens = None
        self._llm_completion_tokens = None
        self._llm_round_growth_tokens = []

    @staticmethod
    def _is_context_length_error(error: Any) -> bool:
        error_text = str(error).lower()
        signatures = (
            "input length",
            "context length",
            "context_length",
            "context window",
            "maximum context",
            "prompt is too long",
            "request too large",
            "too many input tokens",
            "reduce the length",
        )
        return any(signature in error_text for signature in signatures)

    def _recover_from_context_length_error(self) -> Optional[Dict[str, Any]]:
        """上下文超限后的恢复：能摘要则摘要重试，否则 burst；摘要仍超限则升级 burst。"""
        if self._apply_summary_compaction():
            mode = "summary"
        elif self._apply_burst_compaction(reason="length_error"):
            mode = "burst"
        else:
            return None
        retry_response = self._call_llm(self._conversation_history)
        if (
            "error" in retry_response
            and mode == "summary"
            and self._is_context_length_error(retry_response["error"])
        ):
            if self._apply_burst_compaction(reason="length_error_escalation"):
                retry_response = self._call_llm(self._conversation_history)
        if "error" in retry_response:
            return None
        return retry_response

    def _next_llm_actions(self, max_empty_retries: int) -> Tuple[str, List[Dict[str, Any]]]:
        """调用一次 LLM 并解析出本轮 (thinking, actions)。

        - native tools 模式：actions 来自模型返回的 tool_calls。
        - prompt 模式：action/actions 来自 JSON content。
        """
        self._log("正在调用LLM获取响应...")
        self._llm_request_count = getattr(self, "_llm_request_count", 0) + 1
        self._maybe_compact_context()
        llm_response = self._call_llm(self._conversation_history)
        if (
            "error" in llm_response
            and self.context_compaction.enabled
            and self._is_context_length_error(llm_response["error"])
        ):
            self._log("检测到上下文超限错误，尝试压缩后重试", "warning")
            recovered = self._recover_from_context_length_error()
            if recovered is not None:
                llm_response = recovered
        print(llm_response)
        if "error" in llm_response:
            raise RuntimeError(f"LLM API 调用失败: {llm_response['error']}")

        parsed, history_msg = self._parse_llm_response_message(llm_response)

        if parsed["has_tool_calls"]:
            self._append_conversation_message(history_msg)
            actions = [
                {"api": tc["api"], "args": tc["args"], "id": tc.get("id")}
                for tc in parsed["tool_calls"]
            ]
            self._last_llm_output = json.dumps(
                {"thinking": parsed["thinking"], "actions": actions}, ensure_ascii=False
            )
            self._log(f"LLM返回{len(actions)}个tool_calls: {[a['api'] for a in actions]}")
            return self._finish_diagnostic_turn(parsed["thinking"], actions)

        content = parsed["content"]
        if not content or not content.strip():
            self._log(f"LLM返回空content，尝试重试 (最多{max_empty_retries}次)...", "warning")
            for retry in range(max_empty_retries):
                retry_response = self._call_llm(self._conversation_history)
                if "error" in retry_response:
                    raise RuntimeError(f"LLM API 调用失败: {retry_response['error']}")
                retry_parsed, retry_history_msg = self._parse_llm_response_message(retry_response)
                if retry_parsed["has_tool_calls"]:
                    self._append_conversation_message(retry_history_msg)
                    actions = [
                        {"api": tc["api"], "args": tc["args"], "id": tc.get("id")}
                        for tc in retry_parsed["tool_calls"]
                    ]
                    self._log(f"重试第{retry+1}次获取到{len(actions)}个tool_calls")
                    return self._finish_diagnostic_turn(retry_parsed["thinking"], actions)
                if retry_parsed["content"] and retry_parsed["content"].strip():
                    self._append_conversation_message(retry_history_msg)
                    self._last_llm_output = retry_parsed["content"]
                    parsed_json = self._parse_llm_response(retry_parsed["content"])
                    return self._finish_diagnostic_turn(
                        parsed_json.get("thinking", ""),
                        [parsed_json.get("action", {"api": "noop", "args": {}})],
                    )
            self._append_conversation_message(history_msg)
            return parsed["thinking"], []

        self._append_conversation_message(history_msg)
        self._last_llm_output = content
        self._log(f"LLM响应: {content[:200]}...")
        parsed_json = self._parse_llm_response(content)
        return self._finish_diagnostic_turn(
            parsed_json.get("thinking", ""),
            [parsed_json.get("action", {"api": "noop", "args": {}})],
        )

    def call_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """一次性文本推理：用给定 prompt 调一次 LLM，返回纯文本内容。

        供 baseline agent 在 solve() 内部做不涉及工具的中间推理（角色分配、
        反思、报告生成等）使用，不污染主对话历史。
        """
        messages = []
        sys_p = system_prompt if system_prompt is not None else self.system_prompt
        if sys_p:
            messages.append({"role": "system", "content": sys_p})
        messages.append({"role": "user", "content": prompt})
        response = self._call_llm(messages, purpose="auxiliary")
        if "error" in response:
            raise RuntimeError(f"LLM call_text 调用失败: {response['error']}")
        parsed, _ = self._parse_llm_response_message(response)
        return parsed.get("content", "") or parsed.get("thinking", "")

    def _feed_tool_result(self, result: Dict[str, Any], tool_call_id: Optional[str] = None,
                          api: str = "unknown"):
        """将工具执行结果追加到对话历史，供下一轮 LLM 调用使用。"""
        if not isinstance(result, dict):
            result = {"output": result}
        result = dict(result)
        result["api"] = api
        result_str = json.dumps(result, ensure_ascii=False)
        if self.use_native_tools and tool_call_id:
            if self.provider == "anthropic":
                tool_message = {
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": tool_call_id,
                        "content": result_str
                    }]
                }
                self._append_anthropic_conversation_message(tool_message)
            else:
                self._append_conversation_message({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result_str
                })
            self._log(f"添加Native Tool结果到历史 (id={tool_call_id}): {result_str[:100]}...")
        else:
            formatted_result = self._format_tool_result(result)
            self._append_conversation_message(
                {"role": "user", "content": formatted_result}
            )
            self._log(f"添加Prompt Tool结果到历史: {formatted_result[:100]}...")

    def _append_anthropic_conversation_message(self, message: Dict[str, Any]) -> None:
        self._ensure_conversation_trace()
        previous = deepcopy(self._conversation_history[-1]) if self._conversation_history else None
        previous_count = len(self._conversation_history)
        self._append_anthropic_message(self._conversation_history, deepcopy(message))
        current = deepcopy(self._conversation_history[-1])
        if len(self._conversation_history) > previous_count:
            self._conversation_raw_history.append(deepcopy(current))
            self._conversation_phases[-1]["messages"].append(deepcopy(current))
        elif previous != self._conversation_history[-1]:
            self._conversation_raw_history[-1] = deepcopy(current)
            self._conversation_phases[-1]["messages"][-1] = deepcopy(current)

    def reset_conversation(self):
        """重置对话历史"""
        self._conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        self._last_llm_output = None
        self._usage_events.clear()
        self._diagnostic_turn_usage.clear()
        self._diagnostic_usage_event_count = 0
        self._llm_request_count = 0
        self._context_compaction_events.clear()
        self._conversation_raw_history = deepcopy(self._conversation_history)
        self._conversation_phases = [{
            "phase_index": 0,
            "messages": deepcopy(self._conversation_history),
            "compaction": None,
        }]
        self._log("对话历史已重置")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self._conversation_history.copy()

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": self.system_prompt or "", "user": self.user_prompt or ""}

    def _export_conversation(self) -> List[Dict[str, Any]]:
        return self.get_conversation_history()

    def get_conversation_trace(self) -> Dict[str, Any]:
        return {
            "raw": deepcopy(self._conversation_raw_history),
            "phases": deepcopy(self._conversation_phases),
        }

    def _export_conversation_raw(self) -> List[Dict[str, Any]]:
        return deepcopy(self._conversation_raw_history)

    def _export_conversation_phases(self) -> List[Dict[str, Any]]:
        return deepcopy(self._conversation_phases)

    def _export_llm_usage(self) -> List[Dict[str, Any]]:
        return self.get_usage_events()

    def _export_context_compaction(self) -> List[Dict[str, Any]]:
        return [dict(event) for event in self._context_compaction_events]


class MockLLMAgent(BaseAgent):
    """
    Mock大模型的Agent，用于测试和演示。
    模拟LLM输出固定的thinking和action内容。
    """

    def __init__(self, url: str, api_key: str, system_prompt: str,
                 enable_log: bool = False, log_dir: Optional[str] = None, use_native_tools: bool = False):
        super().__init__(enable_log, log_dir)
        self.mode = "mock"
        self.url = url
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.user_prompt = ""
        self.use_native_tools = use_native_tools
        self._conversation_history: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        self._mock_index = 0
        self._mock_responses = self._default_mock_responses()
        self._last_llm_output: Optional[str] = None
        self._log(f"MockLLMAgent初始化完成")

    def set_system_prompt(self, system_prompt: str):
        self.system_prompt = system_prompt
        if self._conversation_history and self._conversation_history[0].get("role") == "system":
            self._conversation_history[0]["content"] = system_prompt
        else:
            self._conversation_history.insert(0, {"role": "system", "content": system_prompt})
        self._log("已更新 MockLLMAgent System Prompt")

    def set_user_prompt(self, user_prompt: str):
        self.user_prompt = user_prompt
        if self._conversation_history and self._conversation_history[-1].get("role") == "user":
            self._conversation_history[-1]["content"] = user_prompt
        else:
            self._conversation_history.append({"role": "user", "content": user_prompt})
        self._log("已更新 MockLLMAgent User Prompt")

    def _default_mock_responses(self) -> List[Dict[str, Any]]:
        """
        默认的模拟响应列表，按顺序循环返回
        """
        return [
            {
                "thinking": "我需要先查询系统的CPU和内存使用情况，以了解当前资源状态。",
                "action": {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}}
            },
            {
                "thinking": "CPU使用率偏高，让我查看详细的进程信息来定位问题。",
                "action": {"api": "query_metrics", "args": {"metric_type": "process", "target": "postgres"}}
            },
            {
                "thinking": "根据监控数据分析，问题可能是连接数过多导致的资源竞争。让我执行SQL查看当前连接数。",
                "action": {"api": "execute_sql", "args": {"sql_query": "SELECT count(*) FROM pg_stat_activity;"}}
            },
            {
                "thinking": "连接数确实过多，我需要重启数据库实例来释放资源。",
                "action": {"api": "manage_instance", "args": {"action": "restart", "target": "postgres_primary"}}
            },
            {
                "thinking": "实例已重启，让我再次查询指标确认恢复情况。",
                "action": {"api": "query_metrics", "args": {"metric_type": "cpu", "target": None}}
            },
            {
                "thinking": "资源使用已恢复正常，问题已解决，准备提交。",
                "action": {
                    "api": "submit",
                    "args": {
                        "report": {
                            "diagnosis": {"conditions": [{
                                "type": "root_cause",
                                "factor": "host_cpu_saturation",
                                "entity": "postgres_primary",
                                "evidence": ["CPU metric was high before remediation"],
                            }]},
                            "outcome": {
                                "changes": ["restarted the affected instance"],
                                "verification": ["CPU metric returned to normal"],
                            },
                            "summary": "CPU pressure was diagnosed and remediated.",
                        }
                    },
                }
            }
        ]

    def set_mock_responses(self, responses: List[Dict[str, Any]]):
        """
        设置自定义的模拟响应列表
        :param responses: 响应列表，每个元素包含thinking和action
        """
        self._mock_responses = responses
        self._log(f"已设置自定义Mock响应，共{len(responses)}条")

    def solve(self) -> Dict[str, Any]:
        """按脚本顺序逐条执行 mock 响应，遇 submit/exit 结束并返回 submission。"""
        for _ in range(self.max_turns):
            response = self._mock_responses[self._mock_index % len(self._mock_responses)]
            self._mock_index += 1
            response_factory = response.get("_actions_factory") if isinstance(response, dict) else None
            thinking = response.get("thinking", "") if isinstance(response, dict) else ""
            if callable(response_factory):
                actions = response_factory(self._conversation_history)
            elif "actions" in response and isinstance(response["actions"], list):
                actions = response["actions"]
            else:
                actions = [response.get("action", {"api": "noop", "args": {}})]
            output_response = (
                {key: value for key, value in response.items() if key != "_actions_factory"}
                if isinstance(response, dict)
                else response
            )
            if callable(response_factory):
                output_response["actions"] = actions
            output = json.dumps(output_response, ensure_ascii=False)
            self._last_llm_output = output
            self._conversation_history.append({"role": "assistant", "content": output})
            self._log(f"Mock LLM输出: {output[:100]}...")

            delay_seconds = float(response.get("delay_seconds", 0) or 0)
            if delay_seconds > 0:
                time.sleep(delay_seconds)

            first = True
            for action in actions:
                api = action.get("api", "")
                args = action.get("args", {}) or {}
                self.record_action(output, {"api": api, "args": args})
                if api == "exit":
                    raise RuntimeError("MockLLMAgent exited without submitting a diagnosis")
                if api == "submit":
                    return args
                result = self.execute(
                    api, args, thinking=(thinking if first else ""), source="",
                    action_id=self.action_history[-1]["action_id"],
                )
                first = False
                formatted = (
                    f"[工具执行结果] {api}: "
                    f"{json.dumps(result, ensure_ascii=False, default=str)}"
                )
                self._conversation_history.append({"role": "user", "content": formatted})
        raise RuntimeError(
            f"MockLLMAgent reached max_turns without submission: max_turns={self.max_turns}"
        )

    def reset_conversation(self):
        """重置对话历史"""
        self._conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        self._mock_index = 0
        self._last_llm_output = None
        self._log("对话历史已重置")

    def reset_mock_index(self):
        """重置Mock响应索引"""
        self._mock_index = 0
        self._log("Mock索引已重置")

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self._conversation_history.copy()

    def _export_prompts(self) -> Dict[str, str]:
        return {"system": self.system_prompt or "", "user": self.user_prompt or ""}

    def _export_conversation(self) -> List[Dict[str, Any]]:
        return self.get_conversation_history()
