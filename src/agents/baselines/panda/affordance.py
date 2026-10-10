"""Panda affordance mechanism: impact estimation and high-risk action flagging.

Paper: "Goal of this module is to provide user with an estimate of change in the
database performance (measured w.r.t a target metric) for a given fix that will
help them quantify how likely it is for their problem to get resolved."
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional

from src.agents.baselines.panda.types import AffordanceAssessment

HIGH_RISK_SQL_PATTERNS = [
    r"\b(DROP|DELETE|TRUNCATE|ALTER)\b",
    r"\b(UPDATE)\b.*\bSET\b",
    r"\b(GRANT|REVOKE)\b",
]

HIGH_RISK_INSTANCE_ACTIONS = {"restart", "stop", "reboot"}

NO_RISK_APIS = {"query_metrics", "read_log", "help"}

AFFORDANCE_PROMPT = """You are a database performance impact estimator.
Given a proposed remediation action and the current database context, estimate:
1. Which performance metric will be most affected (e.g., active_sessions, query_latency, cpu_util)
2. The expected direction of change (improve/degrade/neutral)
3. The estimated magnitude (e.g., "active sessions likely to decrease from ~200 to ~50")
4. Whether this action is reversible

Current context:
{context}

Proposed action:
{action}

Respond in JSON:
{{"target_metric": "...", "direction": "improve|degrade|neutral", "estimated_impact": "...", "reversible": true|false, "risk_level": "low|medium|high"}}"""


class PandaAffordance:
    """Estimates performance impact and flags high-risk actions.

    Two-tier approach (per paper):
    1. Rules-based: immediate classification for known patterns
    2. LLM-based: predict actual performance impact for remediation actions
    """

    def __init__(
        self,
        call_llm_fn: Optional[Callable] = None,
        require_evidence_for_high_risk: bool = True,
    ):
        self._call_llm = call_llm_fn
        self._require_evidence = require_evidence_for_high_risk

    def assess_action(
        self,
        action: Dict[str, Any],
        evidence_count: int = 0,
        context: str = "",
    ) -> AffordanceAssessment:
        """Assess a single action for risk and estimated performance impact."""
        api = action.get("api", "")
        args = action.get("args", {})

        if api in NO_RISK_APIS:
            return AffordanceAssessment(
                action=action, risk_level="low", approved=True, reversible=True,
            )

        if api == "execute_sql":
            assessment = self._assess_sql(action, args, evidence_count)
        elif api == "manage_instance":
            assessment = self._assess_instance_action(action, args, evidence_count)
        elif api == "submit":
            return AffordanceAssessment(
                action=action, risk_level="low", approved=True, reversible=False,
            )
        else:
            assessment = AffordanceAssessment(
                action=action, risk_level="low", approved=True, reversible=True,
            )

        # LLM-based impact estimation for non-trivial actions (per paper)
        if self._call_llm and assessment.risk_level in ("medium", "high") and context:
            impact = self._estimate_impact_with_llm(action, context)
            if impact:
                assessment.risk_description = impact

        return assessment

    def estimate_impact(
        self,
        action: Dict[str, Any],
        context: str,
    ) -> str:
        """Estimate performance impact of an action using LLM.

        Paper: "provide user with an estimate of change in the database
        performance (measured w.r.t a target metric) for a given fix"
        """
        if self._call_llm:
            return self._estimate_impact_with_llm(action, context)
        return self._estimate_impact_heuristic(action)

    def _estimate_impact_with_llm(self, action: Dict[str, Any], context: str) -> str:
        """Use LLM to predict performance impact."""
        action_str = json.dumps(action, ensure_ascii=False)
        prompt = AFFORDANCE_PROMPT.format(context=context[:1500], action=action_str)
        try:
            response = self._call_llm([
                {"role": "system", "content": "You are a database performance impact estimator."},
                {"role": "user", "content": prompt},
            ])
            match = re.search(r"\{[^}]+\}", response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                return (
                    f"Target: {data.get('target_metric', 'unknown')}, "
                    f"Direction: {data.get('direction', 'unknown')}, "
                    f"Impact: {data.get('estimated_impact', 'unknown')}"
                )
        except (json.JSONDecodeError, TypeError, Exception):
            pass
        return self._estimate_impact_heuristic(action)

    def _estimate_impact_heuristic(self, action: Dict[str, Any]) -> str:
        """Heuristic impact estimation when LLM is not available."""
        api = action.get("api", "")
        args = action.get("args", {})
        if api == "manage_instance":
            act = args.get("action", "")
            if act == "restart":
                return "Target: active_sessions, Direction: improve, Impact: sessions reset to 0 then recover; brief downtime expected"
            if act in ("set_config", "reset_config"):
                return "Target: varies, Direction: improve, Impact: configuration change takes effect after reload"
        if api == "execute_sql":
            sql = args.get("sql_query", "").upper()
            if "CREATE INDEX" in sql:
                return "Target: query_latency, Direction: improve, Impact: queries using this column will switch from seq scan to index scan"
            if "VACUUM" in sql:
                return "Target: dead_tuples, Direction: improve, Impact: reclaims space from dead tuples, may briefly increase I/O"
            if "ANALYZE" in sql:
                return "Target: query_latency, Direction: improve, Impact: updates planner statistics for better query plans"
        return ""

    def filter_actions(
        self,
        actions: List[Dict[str, Any]],
        evidence_count: int = 0,
        context: str = "",
    ) -> List[Dict[str, Any]]:
        """Annotate actions with risk assessment (per paper: highlight, not block).

        Paper: "explicitly highlighting high-risk actions" and "estimate impact".
        The affordance module informs; it does not gate execution.
        """
        annotated = []
        for action in actions:
            assessment = self.assess_action(action, evidence_count, context)
            if assessment.risk_level == "high":
                action = dict(action)
                action.setdefault("_affordance", {})
                action["_affordance"] = {
                    "risk_level": assessment.risk_level,
                    "risk_description": assessment.risk_description or "",
                    "reversible": assessment.reversible,
                    "impact_estimate": assessment.risk_description or "",
                }
            annotated.append(action)
        return annotated

    def _assess_sql(
        self, action: Dict, args: Dict, evidence_count: int
    ) -> AffordanceAssessment:
        """Assess SQL execution risk."""
        sql = args.get("sql_query", "") or args.get("sql", "")
        sql_upper = sql.upper().strip()

        if sql_upper.startswith(("SELECT", "EXPLAIN", "SHOW", "\\d")):
            return AffordanceAssessment(
                action=action, risk_level="low", approved=True, reversible=True,
            )

        for pattern in HIGH_RISK_SQL_PATTERNS:
            if re.search(pattern, sql_upper):
                approved = not self._require_evidence or evidence_count >= 3
                return AffordanceAssessment(
                    action=action,
                    risk_level="high",
                    risk_description=f"Destructive SQL detected: {sql[:80]}",
                    reversible=False,
                    approved=approved,
                )

        return AffordanceAssessment(
            action=action, risk_level="medium", approved=True, reversible=True,
        )

    def _assess_instance_action(
        self, action: Dict, args: Dict, evidence_count: int
    ) -> AffordanceAssessment:
        """Assess instance management action risk."""
        instance_action = args.get("action", "")
        if instance_action in HIGH_RISK_INSTANCE_ACTIONS:
            approved = not self._require_evidence or evidence_count >= 3
            return AffordanceAssessment(
                action=action,
                risk_level="high",
                risk_description=f"Instance {instance_action} is disruptive",
                reversible=(instance_action != "stop"),
                approved=approved,
            )
        return AffordanceAssessment(
            action=action, risk_level="low", approved=True, reversible=True,
        )
