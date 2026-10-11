from typing import Dict, List, Optional

from src.agent_language import agent_language, agent_text


class PromptManager:
    """
    Prompt管理器只负责环境角色模板和用户场景提示。

    工具定义、工具签名、工具可见性由 Env 层提供。Orchestrator 会把
    Env 生成的 tool_instructions 传入这里，避免 PromptManager 了解具体
    数据库工具或知识库工具。
    """

    ENV_PROMPTS = {
        "PGEnv": """你是一个专业的PostgreSQL数据库运维专家。你的任务是根据用户输入和工具返回结果，通过调用可用工具来诊断和解决数据库问题。

{tool_instructions}""",

        "PGXCEnv": """你是一个专业的PGXC分布式数据库运维专家。你的任务是根据用户输入和工具返回结果，通过调用可用工具来诊断和解决分布式数据库问题。

PGXC是分布式PostgreSQL集群，包含Coordinator和DataNode节点。

{tool_instructions}""",

        "TiDBEnv": """你是一个专业的 TiDB 分布式数据库运维专家。请基于节点拓扑、SQL、Prometheus 指标和组件日志诊断并修复问题。

{tool_instructions}""",

        "DefaultEnv": """你是一个专业的数据库运维专家。你的任务是根据用户输入和工具返回结果，通过调用可用工具来诊断和解决数据库问题。

{tool_instructions}""",
    }

    ENV_PROMPTS_EN = {
        "PGEnv": """You are a professional PostgreSQL database operations expert. Your task is to diagnose and resolve database problems by calling the available tools, based on the user input and the results returned by the tools.

{tool_instructions}""",

        "PGXCEnv": """You are a professional PGXC distributed database operations expert. Your task is to diagnose and resolve distributed database problems by calling the available tools, based on the user input and the results returned by the tools.

PGXC is a distributed PostgreSQL cluster consisting of Coordinator and DataNode nodes.

{tool_instructions}""",

        "TiDBEnv": """You are a professional TiDB distributed database operations expert. Diagnose and fix problems based on the node topology, SQL, Prometheus metrics and component logs.

{tool_instructions}""",

        "DefaultEnv": """You are a professional database operations expert. Your task is to diagnose and resolve database problems by calling the available tools, based on the user input and the results returned by the tools.

{tool_instructions}""",
    }

    def get_system_prompt(
        self,
        env_type: str,
        tool_instructions: str,
    ) -> str:
        """
        获取指定环境类型的 system prompt。
        tool_instructions 必须由 Env 根据本次启用的工具生成。
        """
        prompts = self.ENV_PROMPTS_EN if agent_language() == "en" else self.ENV_PROMPTS
        template = prompts.get(env_type, prompts["DefaultEnv"])
        return template.format(tool_instructions=tool_instructions)

    def get_user_prompt(self, scenario_description: Optional[str] = None) -> str:
        """
        获取user prompt，包含故障场景说明。
        """
        if scenario_description:
            return agent_text(
                zh=f"当前场景状态：\n{scenario_description}\n\n请根据上述场景开始诊断。",
                en=f"Current scenario state:\n{scenario_description}\n\nStart the diagnosis based on the scenario above.",
            )
        return agent_text(
            zh="初始状态：数据库运行正常，现在等待你开始诊断。",
            en="Initial state: the database is running normally and is now waiting for you to start the diagnosis.",
        )

    def build_conversation_history(self, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        return history.copy()
