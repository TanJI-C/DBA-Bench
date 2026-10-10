"""DB-GPT expert metadata."""

from dataclasses import dataclass
from typing import Dict, List

from src.agents.baselines.dbot.types import DBOT_EXPERT_NAMES


@dataclass(frozen=True)
class DbotExpert:
    name: str
    description: str


DBOT_EXPERTS: Dict[str, DbotExpert] = {
    "ConfigurationExpert": DbotExpert("ConfigurationExpert", "Database configuration and connection settings."),
    "CpuExpert": DbotExpert("CpuExpert", "CPU load, CPU contention, and CPU-heavy SQL."),
    "DiskExpert": DbotExpert("DiskExpert", "Disk usage, WAL growth, temp files, and table storage."),
    "IndexExpert": DbotExpert("IndexExpert", "Index availability, redundant indexes, bloat, and index selection."),
    "IoExpert": DbotExpert("IoExpert", "Read/write IO pressure and IO wait diagnosis."),
    "MemoryExpert": DbotExpert("MemoryExpert", "Memory usage, cache hit ratio, and spill-sensitive queries."),
    "QueryExpert": DbotExpert("QueryExpert", "Slow SQL, plans, joins, sorts, and query optimization."),
    "RecoveryExpert": DbotExpert("RecoveryExpert", "Restarts, crashes, recovery, and availability."),
    "WorkloadExpert": DbotExpert("WorkloadExpert", "QPS, workload shape, concurrency, and traffic shifts."),
}


def expert_names() -> List[str]:
    return list(DBOT_EXPERT_NAMES)
