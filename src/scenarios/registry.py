from dataclasses import dataclass
from enum import Enum

from .base import BaseScenario, DatabaseSystem


class ScenarioCategory(str, Enum):
    BASIC = "basic"
    QUERY_PERF = "query_perf"
    SYSTEM_FAILURE = "system_failure"
    HEALTH_CHECK = "health_check"
    BUSINESS_CHANGE = "business_change"
    RESOURCE_GOVERNANCE = "resource_governance"


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
