import os
import sys
import time

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.execution.environments.postgres import PGEnv
from src.scenarios.postgres import PgQueryPerfStaleStatisticsScenario
from src.workloads.tpcds import TPCDSWorkload
from src.agents.agent import HumanAgent
from src.scenarios.runtime.orchestrator import Orchestrator

def load_queries():
    query_file = os.path.join(project_root, "data/workloads/tpcds/queries/query_0.sql")
    with open(query_file, "r") as f:
        content = f.read()

    import re
    queries = {}
    current_q = None
    current_sql = []
    for line in content.split('\n'):
        m = re.match(r'-- start query (\d+) in stream \d+ using template query(\d+)\.tpl', line)
        if m:
            current_q = f"query{m.group(2)}"
            current_sql = []
            continue
        if line.startswith('-- end query'):
            if current_q:
                # Replace + 30 days with + interval '30 days' for Postgres compatibility
                sql = '\n'.join(current_sql)
                sql = re.sub(r"\+\s*(\d+)\s*days", r"+ interval '\1 days'", sql)
                queries[current_q] = sql
                current_q = None
            continue
        if current_q:
            current_sql.append(line)
    return queries

def main():
    print("="*60)
    print("AiOpsBench TPC-DS Demo (Scale=1) - Stale Statistics")
    print("="*60)

    workload = TPCDSWorkload(scale=1)
    env = PGEnv(workload=workload, port=15432)

    # 提前部署环境，以便执行前置测试
    env.deploy()

    queries = load_queries()
    scenario = PgQueryPerfStaleStatisticsScenario()
    case = scenario.get_case("branch_order_distribution_shift")

    # 挑选出这 10 个查询进行前后对比
    target_queries = case.slow_queries

    print("\n[Demo] 1. 测试正常状态下（统计信息最新）的查询性能...")
    env.execute_sql("ANALYZE;")
    times_before = {}
    for qname in target_queries:
        sql = queries.get(qname)
        if not sql:
            continue
        env.execute_sql("SET statement_timeout = '20s';")
        start = time.time()
        env.execute_sql(sql)
        elapsed = time.time() - start
        times_before[qname] = elapsed
        print(f"  - {qname} 正常耗时: {elapsed:.3f}s")

    env.teardown()

    print("\n[Demo] 2. 通过 Orchestrator 构造统计信息陈旧故障并开始诊断...")

    agent = HumanAgent()

    orchestrator = Orchestrator(
        env=env,
        scenario=scenario,
        case=case,
        agent=agent
    )

    orchestrator.run()

if __name__ == "__main__":
    main()
