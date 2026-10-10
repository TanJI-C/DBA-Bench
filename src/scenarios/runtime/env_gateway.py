import json
import threading
import time
from typing import Any, Dict, Optional


class EnvGateway:
    """Agent 访问环境的唯一通道（控制反转核心）。

    Orchestrator 在 run() 初始化阶段构造它并注入给 Agent。Agent 通过
    BaseAgent.execute() 间接驱动它，自己掌控诊断工作流（线性或并行），
    Orchestrator 不再用拉模型循环逐轮拉取 action。

    职责：
    1. 把环境工具调用串行化（DB 单连接非线程安全），支持 Agent 内并行调用。
    2. 把每次工具调用追加到 Orchestrator 持有的 action_history（Evaluator 的唯一真相源）。
    3. 通过 reporter 回调把 thinking/action/result 交给 Orchestrator 打印。

    submit / exit 是 Environment 暴露的合法终止工具。Agent 在 solve() 中截获并消费，
    不会把它们提交给普通环境执行路径；如果它们进入本网关，说明 Agent 违反终止工具协议，
    网关直接抛错。
    """

    TERMINAL_TOOLS = ("submit", "exit")

    def __init__(self, env, action_history: list, turn_history: Optional[list] = None, reporter=None):
        self._env = env
        self._history = action_history
        self._turn_history = turn_history
        self._reporter = reporter
        self._lock = threading.Lock()
        self._turn = 0

    def execute(self, api: str, args: Dict[str, Any], *,
                thinking: str = "", source: str = "", action_id: str | None = None) -> Dict[str, Any]:
        """执行一次环境工具调用，返回解析后的结果字典。

        :param api: 工具名（环境注册的 alias）
        :param args: 工具参数
        :param thinking: 本次调用对应的思考，交给 reporter 打印
        :param source: 调用方标识（如专家名），并行时用于区分输出
        """
        if api in self.TERMINAL_TOOLS:
            raise ValueError(
                f"EnvGateway 收到 Environment 终止工具 {api!r}；"
                "Agent.solve() 必须直接消费 submit/exit，不能经由 execute() 分派。"
            )
        args = args or {}
        with self._lock:
            self._turn += 1
            turn = self._turn
            turn_id = f"turn-{turn:06d}"
            action_id = action_id or f"{turn_id}-action-001"
            result_id = f"{action_id}-result"
            entry: Dict[str, Any] = {
                "turn_id": turn_id,
                "action_id": action_id,
                "api": api,
                "args": args,
            }
            if thinking:
                entry["thinking"] = thinking
            entry["raw_output"] = json.dumps(
                {
                    "thinking": thinking,
                    "source": source,
                    "action": {"api": api, "args": args},
                },
                ensure_ascii=False,
                default=str,
            )
            self._history.append(entry)

            started_at = time.time()
            raw = self._env.execute_action(api, args)
            result = self._parse_result(raw)
            finished_at = time.time()
            entry["result"] = result
            entry["result_id"] = result_id
            self._record_turn(
                turn=turn,
                turn_id=turn_id,
                action_id=action_id,
                result_id=result_id,
                source=source,
                thinking=thinking,
                api=api,
                args=args,
                result=result,
                started_at=started_at,
                finished_at=finished_at,
            )

            if self._reporter:
                self._reporter(
                    turn=turn,
                    source=source,
                    thinking=thinking,
                    api=api,
                    args=args,
                    result=result,
                )
            return result

    def _record_turn(
        self,
        *,
        turn: int,
        turn_id: str,
        action_id: str,
        result_id: str,
        source: str,
        thinking: str,
        api: str,
        args: Dict[str, Any],
        result: Any,
        started_at: float,
        finished_at: float,
    ):
        if self._turn_history is None:
            return
        self._turn_history.append({
            "turn_number": turn,
            "turn_id": turn_id,
            "timestamp_start": started_at,
            "timestamp_agent_output": started_at,
            "timestamp_end": finished_at,
            "raw_output": json.dumps(
                {
                    "thinking": thinking,
                    "source": source,
                    "action": {"api": api, "args": args},
                },
                ensure_ascii=False,
                default=str,
            ),
            "actions": [{"action_id": action_id, "api": api, "args": args}],
            "results": [{
                "result_id": result_id,
                "action_id": action_id,
                "api": api,
                "status": self._result_status(api, result),
                "data": result,
                "timestamp_start": started_at,
                "timestamp_end": finished_at,
            }],
            "should_break": False,
            "error": None,
        })

    @staticmethod
    def _result_status(api: str, result: Any) -> str:
        if isinstance(result, dict):
            if "status" in result:
                return result["status"]
            if "success" in result:
                return "success" if result["success"] else "failed"
            if "error" in result:
                return "error"
            if api == "submit":
                return "success"
        return "success"

    @staticmethod
    def _parse_result(raw: Any) -> Any:
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
        return raw
