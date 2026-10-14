from dataclasses import dataclass
from enum import Enum

from src.scenarios.base import BaseScenario
from src.database.system import DatabaseSystem


class ScenarioCategory(str, Enum):
    BASIC = "basic"
    QUERY_PERF = "query_perf"
    SYSTEM_FAILURE = "system_failure"
    HEALTH_CHECK = "health_check"
    BUSINESS_CHANGE = "business_change"
    RESOURCE_GOVERNANCE = "resource_governance"
    COMPOSITE_FAULT = "composite_fault"
    MISLEADING_ALERT = "misleading_alert"


@dataclass(frozen=True, slots=True)
class ScenarioRegistration:
    scenario: BaseScenario
    category: ScenarioCategory
    entrypoint: str | None

    @property
    def system(self) -> DatabaseSystem:
        return self.scenario.system

    @property
    def scenario_id(self) -> str:
        return self.scenario.scenario_id
