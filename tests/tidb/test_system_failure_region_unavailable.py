from src.execution.deployments.tidb_components.stores import TiDBStores
from src.execution.deployments.tidb_components.snapshots import TiDBSnapshots
from src.execution.deployments.tidb_components.network import TiDBNetwork
import inspect
import json
import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.execution.deployments.tidb import TiDBDockerDeployment
from src.execution.environments.tidb import TiDBEnv
from src.scenarios.evaluation.diagnosis import SemanticDiagnosisMatcher
from src.scenarios.evaluation.semantic import SemanticConditionJudgment, SemanticJudgment
from src.protocols.report import StructuredReport
from src.scenarios.base import CaseRun
from src.scenarios.tidb import TidbSystemFailureRegionUnavailableScenario
from src.scenarios.tidb.system_failure.region_unavailable import _business_truth
from src.scenarios.faults import FaultLifecycleContext
from src.scenarios.tidb.system_failure import region_unavailable as injector_module
from src.scenarios.tidb.system_failure.region_unavailable import (
    TidbSystemFailureRegionUnavailableInjector,
)


SCENARIO = TidbSystemFailureRegionUnavailableScenario()
CASE = SCENARIO.get_case("region_unavailable_pd_network_block")
PLAN = SCENARIO.build_fault_plan(CASE)[0]


def valid_report() -> dict:
    return {
        "diagnosis": {
            "conditions": [
                {
                    "type": "finding",
                    "factor": condition.condition_id,
                    "entity": CASE.affected_tidb_target,
                    "evidence": [f"evidence for {condition.condition_id}"],
                }
                for condition in CASE.evaluator.diagnosis_conditions
            ]
        },
        "outcome": {
            "changes": ["allow PD client traffic only for the affected TiDB target"],
            "verification": ["both targets and business truth were verified"],
        },
        "summary": "The affected TiDB target lost PD client connectivity and was recovered without touching stores.",
    }


class FakeDeployment:
    def __init__(self, env=None, *, recovered=True):
        self.network = SimpleNamespace(allow_pd_network=self.allow_pd_network, allow_pd_network_address=self.allow_pd_network_address, allow_pd_network_egress_shadow=self.allow_pd_network_egress_shadow, allow_pd_network_ingress_decoy=self.allow_pd_network_ingress_decoy, allow_pd_network_ingress_shadow=self.allow_pd_network_ingress_shadow, allow_pd_network_response=self.allow_pd_network_response, allow_pd_network_response_shadow=self.allow_pd_network_response_shadow, allow_pd_network_stale_egress=self.allow_pd_network_stale_egress, arm_pd_network_rehydration=self.arm_pd_network_rehydration, block_pd_network=self.block_pd_network, block_pd_network_address=self.block_pd_network_address, block_pd_network_egress_shadow=self.block_pd_network_egress_shadow, block_pd_network_endpoint=self.block_pd_network_endpoint, block_pd_network_ingress_decoy=self.block_pd_network_ingress_decoy, block_pd_network_ingress_shadow=self.block_pd_network_ingress_shadow, block_pd_network_response=self.block_pd_network_response, block_pd_network_response_shadow=self.block_pd_network_response_shadow, block_pd_network_stale_egress=self.block_pd_network_stale_egress, disarm_pd_network_rehydration=self.disarm_pd_network_rehydration, inspect_pd_network=self.inspect_pd_network)
        self.env = env
        self.recovered = recovered
        self.operations = []
        self.source_addresses = {
            "tidb/tidb-0": "172.20.0.8",
            "tidb/tidb-1": "172.20.0.9",
            "tidb/tidb-2": "172.20.0.10",
        }
        self.pd_addresses = {
            "pd/pd-0": "172.20.0.2",
            "pd/pd-1": "172.20.0.3",
            "pd/pd-2": "172.20.0.4",
        }
        self.tidb_endpoints = {
            "tidb/tidb-0": ("127.0.0.1", 4300),
            "tidb/tidb-1": ("127.0.0.1", 4302),
            "tidb/tidb-2": ("127.0.0.1", 4304),
        }
        self.pd_shadow_ingress_rule_counts = {
            target: CASE.pd_ingress_rule_count
            for target in CASE.pd_shadow_ingress_targets
        }
        self.pd_ingress_decoy_rule_counts = {
            tuple(rule): 1
            for rule in CASE.pd_ingress_decoy_rules
        }
        self.pd_response_rule_counts = {
            target: 0 if recovered else CASE.pd_response_rule_count
            for target in CASE.pd_targets
        }
        self.tidb_stale_egress_rule_counts = {
            CASE.affected_tidb_target: 0 if recovered else len(CASE.pd_targets),
        }
        self.tidb_post_restart_rehydrated_rule_count = 0
        self.pd_network_rehydration_armed = not recovered
        self.pd_response_shadow_rule_counts = {
            target: {
                destination: 1
                for destination in CASE.pd_response_shadow_targets
            }
            for target in CASE.pd_targets
        }
        self.tidb_shadow_egress_rule_counts = {
            target: 1 for target in CASE.pd_targets
        }
        self.pd_leader = "pd-0"

    def current_pd_leader(self):
        return self.pd_leader

    def transfer_pd_leader(self, destination_service):
        if destination_service not in ("pd-0", "pd-1", "pd-2"):
            raise ValueError(f"unknown PD service: {destination_service!r}")
        self.operations.append(("transfer_pd_leader", f"pd/{destination_service}"))
        self.pd_leader = destination_service

    def node_states(self):
        return {
            **{target: {"running": True} for target in CASE.pd_targets},
            **{f"tikv/tikv-{index}": {"running": True} for index in range(3)},
            "tidb/tidb-0": {"running": True},
            "tidb/tidb-1": {"running": True},
            "tidb/tidb-2": {"running": True},
        }

    def block_pd_network(self, target):
        self.operations.append(("block", target))
        if self.env is not None:
            if target == CASE.affected_tidb_target:
                self.env.blocked = True
                self.env.affected_pd_egress_blocked = True
            if target == CASE.control_tidb_target:
                self.env.control_noise_blocked = True
                self.env.control_pd_targets = set(CASE.pd_targets)
                self.env.control_rule_count = len(self.env.control_pd_targets)
                self.env.control_stale_rule = False
            if target == CASE.protected_tidb_target:
                self.env.protected_pd_targets = set(CASE.pd_targets)
                self.env.protected_rule_count = len(self.env.protected_pd_targets)
                self.env.protected_stale_rule = False
        return "-A OUTPUT -p tcp -d 172.20.0.2 --dport 2379 -j REJECT\n" * 3

    def block_pd_network_egress_shadow(self, target, pd_targets):
        self.operations.append(("block_egress_shadow", target, tuple(pd_targets)))
        for pd_target in pd_targets:
            self.tidb_shadow_egress_rule_counts[pd_target] = 1
        return "-A OUTPUT -j ACCEPT\n-A OUTPUT -j REJECT\n"

    def allow_pd_network_egress_shadow(self, target, pd_targets):
        self.operations.append(("allow_egress_shadow", target, tuple(pd_targets)))
        for pd_target in pd_targets:
            self.tidb_shadow_egress_rule_counts[pd_target] = 0
        return "-A OUTPUT"

    def block_pd_network_response(self, pd_targets, destination_target):
        self.operations.append(("block_response", tuple(pd_targets), destination_target))
        for pd_target in pd_targets:
            self.pd_response_rule_counts[pd_target] = CASE.pd_response_rule_count
        if self.env is not None and destination_target == CASE.affected_tidb_target:
            self.env.blocked = True
            self.env.affected_pd_response_blocked = True
            self.env.affected_pd_egress_blocked = True
        return "-A OUTPUT --sport 2379 -j REJECT\n"

    def block_pd_network_response_shadow(self, pd_targets, destination_targets):
        self.operations.append(
            ("block_response_shadow", tuple(pd_targets), tuple(destination_targets))
        )
        for pd_target in pd_targets:
            self.pd_response_shadow_rule_counts[pd_target] = {
                destination: 1 for destination in destination_targets
            }
        return "-A OUTPUT --sport 2379 -j ACCEPT\n-A OUTPUT --sport 2379 -j REJECT\n"

    def block_pd_network_stale_egress(self, target, pd_targets):
        self.operations.append(("block_stale_egress", target, tuple(pd_targets)))
        self.tidb_stale_egress_rule_counts[target] = len(pd_targets)
        if self.env is not None and target == CASE.affected_tidb_target:
            self.env.blocked = True
        return "-A OUTPUT --sport 2379 -j ACCEPT\n-A OUTPUT --sport 2379 -j REJECT\n"

    def allow_pd_network_response(self, pd_target, destination_target):
        self.operations.append(("allow_response", pd_target, destination_target))
        self.pd_response_rule_counts[pd_target] = 0
        if self.env is not None and destination_target == CASE.affected_tidb_target:
            self.env.affected_pd_response_blocked = any(self.pd_response_rule_counts.values())
            self.env.affected_pd_egress_blocked = self.env.affected_pd_response_blocked
            self.env.blocked = self.env.affected_pd_response_blocked
        return "-A OUTPUT"

    def allow_pd_network_response_shadow(self, pd_target, destination_targets):
        self.operations.append(
            ("allow_response_shadow", pd_target, tuple(destination_targets))
        )
        for destination in destination_targets:
            self.pd_response_shadow_rule_counts[pd_target][destination] = 0
        return "-A OUTPUT"

    def allow_pd_network_stale_egress(self, target, pd_targets):
        self.operations.append(("allow_stale_egress", target, tuple(pd_targets)))
        self.tidb_stale_egress_rule_counts[target] = 0
        if self.env is not None and target == CASE.affected_tidb_target:
            self.env.blocked = any(self.pd_response_rule_counts.values())
        return "-A OUTPUT"

    def block_pd_network_ingress_decoy(self, source_target, pd_target):
        self.operations.append(("block_ingress_decoy", source_target, pd_target))
        self.pd_ingress_decoy_rule_counts[(pd_target, source_target)] = 1
        return f"-A INPUT -s {self.source_addresses[source_target]}/32 -p tcp --dport 2379 -m comment --comment pd-client-policy -j REJECT\n"

    def allow_pd_network_ingress_decoy(self, source_target, pd_target):
        self.operations.append(("allow_ingress_decoy", source_target, pd_target))
        self.pd_ingress_decoy_rule_counts[(pd_target, source_target)] = 0
        return "-A INPUT"

    def block_pd_network_ingress_shadow(self, source_target, pd_target):
        self.operations.append(("block_ingress_shadow", source_target, pd_target))
        self.pd_shadow_ingress_rule_counts[pd_target] = CASE.pd_ingress_rule_count
        return (
            f"-A INPUT -s {self.source_addresses[source_target]}/32 -p tcp --dport 2379 -j ACCEPT\n"
            f"-A INPUT -s {self.source_addresses[source_target]}/32 -p tcp --dport 2379 "
            "-m comment --comment pd-client-policy -j REJECT\n"
        )

    def allow_pd_network_ingress_shadow(self, source_target, pd_target):
        self.operations.append(("allow_ingress_shadow", source_target, pd_target))
        self.pd_shadow_ingress_rule_counts[pd_target] = 0
        return "-A INPUT"

    def block_pd_network_endpoint(self, target, pd_target):
        self.operations.append(("block_endpoint", target, pd_target))
        if self.env is not None and target == CASE.control_tidb_target:
            self.env.control_pd_targets.add(pd_target)
            self.env.control_rule_count = len(self.env.control_pd_targets)
        if self.env is not None and target == CASE.protected_tidb_target:
            self.env.protected_pd_targets.add(pd_target)
            self.env.protected_rule_count = len(self.env.protected_pd_targets)
        return "-A OUTPUT -p tcp -d 172.20.0.2 --dport 2379 -j REJECT\n"

    def block_pd_network_address(self, target, address):
        self.operations.append(("block_address", target, address))
        if self.env is not None and target == CASE.affected_tidb_target:
            self.env.affected_stale_rule = True
        if self.env is not None and target == CASE.control_tidb_target:
            if not self.env.control_stale_rule:
                self.env.control_rule_count += 1
            self.env.control_stale_rule = True
        if self.env is not None and target == CASE.protected_tidb_target:
            if not self.env.protected_stale_rule:
                self.env.protected_rule_count += 1
            self.env.protected_stale_rule = True
        return f"-A OUTPUT -d {address} --dport 2379 -j REJECT\n"

    def allow_pd_network(self, target):
        self.operations.append(("allow", target))
        if self.env is not None:
            if target in CASE.pd_targets:
                self.pd_response_rule_counts[target] = 0
                self.env.affected_pd_response_blocked = any(self.pd_response_rule_counts.values())
                self.env.affected_pd_egress_blocked = self.env.affected_pd_response_blocked
                self.env.blocked = (
                    self.env.affected_pd_response_blocked
                    or self.tidb_stale_egress_rule_counts[CASE.affected_tidb_target] > 0
                )
            if target == CASE.affected_tidb_target:
                self.tidb_post_restart_rehydrated_rule_count = 0
                self.env.blocked = (
                    self.env.affected_pd_response_blocked
                    or self.tidb_stale_egress_rule_counts[target] > 0
                    or self.tidb_post_restart_rehydrated_rule_count > 0
                )
            if target == CASE.control_tidb_target:
                self.env.control_noise_blocked = False
                self.env.control_pd_targets.clear()
                self.env.control_rule_count = int(self.env.control_stale_rule)
            if target == CASE.protected_tidb_target:
                self.env.protected_pd_targets.clear()
                self.env.protected_rule_count = int(self.env.protected_stale_rule)
        return "-A OUTPUT"

    def arm_pd_network_rehydration(self, target, pd_targets):
        self.pd_network_rehydration_armed = True

    def disarm_pd_network_rehydration(self, target):
        self.pd_network_rehydration_armed = False

    def allow_pd_network_address(self, target, address):
        self.operations.append(("allow_address", target, address))
        if self.env is not None and target == CASE.affected_tidb_target:
            self.env.affected_stale_rule = False
        if self.env is not None and target == CASE.control_tidb_target:
            self.env.control_stale_rule = False
            self.env.control_rule_count -= 1
        if self.env is not None and target == CASE.protected_tidb_target:
            self.env.protected_stale_rule = False
            self.env.protected_rule_count -= 1
        return "-A OUTPUT"

    def inspect_pd_network(self, target):
        if target in CASE.pd_targets:
            rules = "-P INPUT ACCEPT\n"
            if self.pd_shadow_ingress_rule_counts[target]:
                source_address = self.source_addresses[CASE.affected_tidb_target]
                rules += (
                    f'-A INPUT -s {source_address}/32 -p tcp --dport 2379 -j ACCEPT\n'
                    f'-A INPUT -s {source_address}/32 -p tcp --dport 2379 -m comment '
                    '--comment pd-client-policy -j REJECT\n'
                )
            for pd_target, source_target in CASE.pd_ingress_decoy_rules:
                if (
                    pd_target == target
                    and self.pd_ingress_decoy_rule_counts[(pd_target, source_target)]
                ):
                    rules += (
                        f'-A INPUT -s {self.source_addresses[source_target]}/32 -p tcp '
                        f'--dport 2379 -m comment --comment pd-client-policy -j REJECT\n'
                    )
            if self.pd_response_rule_counts[target]:
                rules += (
                    f'-A OUTPUT -s {self.pd_addresses[target]}/32 --sport 2379 '
                    f'-d {self.source_addresses[CASE.affected_tidb_target]}/32 '
                    '-m comment --comment pd-response-policy -j REJECT\n'
                )
            for destination_target, rule_count in self.pd_response_shadow_rule_counts[target].items():
                if rule_count:
                    destination_address = self.source_addresses[destination_target]
                    rules += (
                        f'-A OUTPUT -s {self.pd_addresses[target]}/32 --sport 2379 '
                        f'-d {destination_address}/32 -j ACCEPT\n'
                        f'-A OUTPUT -s {self.pd_addresses[target]}/32 --sport 2379 '
                        f'-d {destination_address}/32 -m comment '
                        '--comment pd-response-shadow-policy -j REJECT\n'
                    )
            return rules + "-P OUTPUT ACCEPT\n"
        if target == CASE.affected_tidb_target:
            local_stale_rule = self.tidb_stale_egress_rule_counts[target] > 0
            rules = ""
            if local_stale_rule:
                for pd_target in CASE.pd_targets:
                    rules += (
                        f"-A OUTPUT -d {self.pd_addresses[pd_target]}/32 --dport 2379 "
                        f"-m comment --comment {CASE.tidb_stale_egress_rule_marker} "
                        "-j REJECT\n"
                    )
            for pd_target in CASE.pd_targets:
                if self.tidb_shadow_egress_rule_counts[pd_target]:
                    pd_address = self.pd_addresses[pd_target]
                    rules += (
                        f"-A OUTPUT -d {pd_address}/32 --dport 2379 -j ACCEPT\n"
                        f"-A OUTPUT -d {pd_address}/32 --dport 2379 -m comment "
                        f"--comment {CASE.tidb_shadow_egress_rule_marker} -j REJECT\n"
                    )
            if local_stale_rule:
                rules += (
                    f"-A OUTPUT -s {self.source_addresses[target]}/32 -p tcp -d "
                    f"{CASE.affected_stale_pd_address} --dport 2379 -j REJECT\n"
                )
            if self.tidb_post_restart_rehydrated_rule_count:
                rules += (
                    f"-A OUTPUT -d {self.pd_addresses[CASE.post_restart_rehydrated_pd_target]}/32 "
                    "--dport 2379 -j REJECT\n"
                )
            return rules
        if target == CASE.control_tidb_target:
            if self.env is None:
                rule_count = CASE.control_pd_reject_rule_count
                stale_rule = True
            else:
                rule_count = self.env.control_rule_count
                stale_rule = self.env.control_stale_rule
            current_rule_count = rule_count - int(stale_rule)
        elif target == CASE.protected_tidb_target:
            if self.env is None:
                rule_count = 1
                stale_rule = False
            else:
                rule_count = self.env.protected_rule_count
                stale_rule = self.env.protected_stale_rule
            current_rule_count = rule_count - int(stale_rule)
        else:
            rule_count = 0
            stale_rule = False
            current_rule_count = 0
        if target == CASE.control_tidb_target:
            current_rule_count = rule_count - int(stale_rule)
        rules = "".join(
            f"-A OUTPUT -s {self.source_addresses[target]}/32 -p tcp -d 172.20.0.{index} "
            "--dport 2379 -j REJECT\n"
            for index in (2, 3, 4)[:(
                current_rule_count
                if target in {CASE.control_tidb_target, CASE.protected_tidb_target}
                else rule_count
            )]
        )
        if target == CASE.control_tidb_target and stale_rule:
            rules += (
                f"-A OUTPUT -s {self.source_addresses[target]}/32 -p tcp -d "
                f"{CASE.control_stale_pd_address} --dport 2379 -j REJECT\n"
            )
        if target == CASE.protected_tidb_target and stale_rule:
            rules += (
                f"-A OUTPUT -s {self.source_addresses[target]}/32 -p tcp -d "
                f"{CASE.protected_stale_pd_address} --dport 2379 -j REJECT\n"
            )
        return rules

    def restart_component(self, target):
        self.operations.append(("restart", target))
        if target == CASE.affected_tidb_target:
            self.tidb_stale_egress_rule_counts[target] = 0
            if self.pd_network_rehydration_armed:
                self.tidb_post_restart_rehydrated_rule_count = 1
            if self.env is not None:
                self.env.blocked = (
                    any(self.pd_response_rule_counts.values())
                    or self.tidb_post_restart_rehydrated_rule_count > 0
                )

    def wait_for_target(self, target, timeout):
        self.operations.append(("wait", target, timeout))


class FakeEnv:
    def __init__(self, *, recovered=True):
        self.blocked = not recovered
        self.affected_pd_response_blocked = not recovered
        self.affected_pd_egress_blocked = not recovered
        self.control_pd_targets = set(CASE.pd_targets[: CASE.control_pd_reject_rule_count - 1])
        self.control_rule_count = CASE.control_pd_reject_rule_count
        self.control_stale_rule = True
        self.protected_pd_targets = set()
        self.protected_rule_count = 1
        self.protected_stale_rule = True
        self.control_noise_blocked = False
        self.affected_stale_rule = True
        self.deployment = FakeDeployment(self, recovered=recovered)
        self.sql_calls = []
        self.host = "127.0.0.1"
        self.port = 4300
        self.user = "root"
        self.password = ""
        self.expected_truth = CASE.expected_business_truth
        self.business_truth_as_strings = False

    def get_deployment(self):
        return self.deployment

    def execute_sql(self, sql, target=None):
        self.sql_calls.append((sql, target))
        if target == CASE.control_tidb_target and self.control_noise_blocked:
            return json.dumps({"status": "error", "error": "PD control-plane probe failed"})
        if target == CASE.affected_tidb_target and self.blocked:
            return json.dumps({"status": "error", "error": "connect to PD failed"})
        if sql.strip().casefold() == "select 1":
            rows = [[1]]
        elif "order_id from benchops.ma01_orders" in sql.casefold():
            rows = [[1]]
        elif "tikv_region_status" in sql.casefold():
            rows = [[3]]
        elif "count(*)" in sql.casefold() and "ma01_orders" in sql.casefold():
            rows = [list(self.expected_truth)]
            if self.business_truth_as_strings:
                rows = [[str(value) for value in rows[0]]]
        else:
            rows = []
        return json.dumps({"status": "success", "result": rows, "columns": [], "row_count": len(rows)})


def case_run(env, report=None, *, actions=()):
    action_history = [*actions, {"api": "submit", "args": report or valid_report()}]
    return CaseRun(
        run_id="region-unavailable-unit",
        scenario=SCENARIO,
        case=CASE,
        env=env,
        injections=[
            SimpleNamespace(
                evidence={
                    "ma01_affected_tidb_target": CASE.affected_tidb_target,
                    "ma01_control_neighbor_rule_count": CASE.control_pd_reject_rule_count,
                    "ma01_control_stale_pd_address": CASE.control_stale_pd_address,
                    "ma01_protected_neighbor_rule_count": 1,
                    "ma01_protected_stale_pd_address": CASE.protected_stale_pd_address,
                    "ma01_affected_stale_pd_address": CASE.affected_stale_pd_address,
                    "ma01_affected_stale_rule_count": 1,
                    "ma01_pd_ingress_source_address": env.deployment.source_addresses[CASE.affected_tidb_target],
                    "ma01_post_restart_rehydrated_pd_target": CASE.post_restart_rehydrated_pd_target,
                    "ma01_pd_shadow_ingress_source_address": env.deployment.source_addresses[CASE.affected_tidb_target],
                    "ma01_pd_shadow_ingress_rule_marker": CASE.pd_ingress_rule_marker,
                    "ma01_pd_shadow_ingress_rule_count": CASE.pd_ingress_rule_count,
                    "ma01_pd_shadow_ingress_targets": CASE.pd_shadow_ingress_targets,
                    "ma01_pd_ingress_rule_count": CASE.pd_ingress_rule_count,
                    "ma01_pd_ingress_rule_marker": CASE.pd_ingress_rule_marker,
                    "ma01_pd_ingress_targets": CASE.pd_targets,
                    "ma01_pd_ingress_decoy_rules": [
                        {
                            "pd_target": pd_target,
                            "source_target": source_target,
                            "marker": CASE.pd_ingress_rule_marker,
                                "source_address": env.deployment.source_addresses[source_target],
                        }
                        for pd_target, source_target in CASE.pd_ingress_decoy_rules
                    ],
                    "ma01_pd_response_rule_marker": CASE.pd_response_rule_marker,
                    "ma01_pd_response_rule_count": CASE.pd_response_rule_count,
                    "ma01_pd_response_rules": [
                        {
                            "pd_target": pd_target,
                            "destination_address": env.deployment.source_addresses[CASE.affected_tidb_target],
                            "marker": CASE.pd_response_rule_marker,
                            "rule_count": CASE.pd_response_rule_count,
                        }
                        for pd_target in CASE.pd_targets
                    ],
                    "ma01_pd_response_shadow_rule_marker": CASE.pd_response_shadow_rule_marker,
                    "ma01_pd_response_shadow_rules": [
                        {
                            "pd_target": pd_target,
                            "rules": [
                                {
                                    "destination_target": destination_target,
                                    "destination_address": env.deployment.source_addresses[destination_target],
                                    "marker": CASE.pd_response_shadow_rule_marker,
                                    "accept_before_reject": True,
                                    "accept_count": 1,
                                    "reject_count": 1,
                                }
                                for destination_target in CASE.pd_response_shadow_targets
                            ],
                        }
                        for pd_target in CASE.pd_targets
                    ],
                    "ma01_tidb_shadow_egress_rule_marker": CASE.tidb_shadow_egress_rule_marker,
                    "ma01_tidb_shadow_egress_rules": [
                        {
                            "destination_address": env.deployment.pd_addresses[pd_target],
                            "accept_before_reject": True,
                            "accept_count": 1,
                            "reject_count": 1,
                        }
                        for pd_target in CASE.pd_targets
                    ],
                    "ma01_tidb_stale_egress_rule_marker": CASE.tidb_stale_egress_rule_marker,
                    "ma01_tidb_stale_egress_rules": [
                        {
                            "destination_address": env.deployment.pd_addresses[pd_target],
                            "marker": CASE.tidb_stale_egress_rule_marker,
                            "effective_before_accept": True,
                            "accept_count": 1,
                            "reject_count": 1,
                        }
                        for pd_target in CASE.pd_targets
                    ],
                }
            )
        ],
        action_history=action_history,
    )


def test_case_identity_plan_workload_and_binary_difficulty_contract():
    assert CASE.evaluator.scenario_id == SCENARIO.scenario_id
    assert CASE.evaluator.case_id == CASE.case_id
    assert PLAN.injector_type is TidbSystemFailureRegionUnavailableInjector
    assert PLAN.config["affected_tidb_target"] == CASE.affected_tidb_target
    assert PLAN.config["affected_stale_pd_address"] == CASE.affected_stale_pd_address
    assert PLAN.config["control_pd_reject_rule_count"] == 1
    assert PLAN.config["control_stale_pd_address"] == CASE.control_stale_pd_address
    assert PLAN.config["protected_stale_pd_address"] == CASE.protected_stale_pd_address
    assert PLAN.config["pd_ingress_rule_count"] == 1
    assert PLAN.config["pd_ingress_rule_marker"] == CASE.pd_ingress_rule_marker
    assert PLAN.config["pd_ingress_decoy_rules"] == CASE.pd_ingress_decoy_rules
    assert PLAN.config["pd_shadow_ingress_targets"] == CASE.pd_shadow_ingress_targets
    assert PLAN.config["post_restart_rehydrated_pd_target"] == CASE.post_restart_rehydrated_pd_target
    assert PLAN.config["pd_response_rule_count"] == CASE.pd_response_rule_count
    assert PLAN.config["pd_response_rule_marker"] == CASE.pd_response_rule_marker
    assert PLAN.config["pd_response_shadow_targets"] == CASE.pd_response_shadow_targets
    assert PLAN.config["pd_response_shadow_rule_marker"] == CASE.pd_response_shadow_rule_marker
    assert PLAN.config["tidb_stale_egress_rule_marker"] == CASE.tidb_stale_egress_rule_marker
    assert PLAN.config["tidb_shadow_egress_rule_marker"] == CASE.tidb_shadow_egress_rule_marker
    assert "network_port" not in PLAN.config
    assert CASE.row_count == 100_000
    assert CASE.expected_business_truth == _business_truth(CASE.row_count)
    assert CASE.runtime.bootstrap_cache_enabled is False
    assert CASE.background_workload.worker_count == 8
    assert len(CASE.background_workload.profiles) == 12
    assert len({profile.name for profile in CASE.background_workload.profiles}) == 12
    assert {profile.target for profile in CASE.background_workload.profiles} == {
        CASE.control_tidb_target,
        CASE.protected_tidb_target,
        CASE.affected_tidb_target,
    }
    assert sum(profile.target == CASE.affected_tidb_target for profile in CASE.background_workload.profiles) == 4
    assert sum(profile.target == CASE.protected_tidb_target for profile in CASE.background_workload.profiles) == 4


def test_pd_endpoint_network_helper_accepts_public_pd_target(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="component-fixture")
    deployment.network = TiDBNetwork(deployment)
    deployment.snapshots = TiDBSnapshots(deployment, None, None, None)
    deployment.stores = TiDBStores(deployment)
    deployment.COMPONENTS = {
        "pd": ("pd-0", "pd-1", "pd-2"),
        "tidb": ("tidb-0", "tidb-1", "tidb-2"),
    }
    deployment.NODES = {
        f"{node_type}/{service}": service
        for node_type, services in deployment.COMPONENTS.items()
        for service in services
    }
    deployment.network._pd_ingress_sources = {"pd/pd-0": {"tidb/tidb-2"}}
    deployment.network._pd_response_egress_targets = {}
    deployment.network._pd_response_egress_shadow_targets = {}
    deployment.network._tidb_stale_egress_targets = {}
    deployment.network._tidb_egress_shadow_targets = {}
    captured = {}

    def capture(target, script):
        captured["target"] = target
        captured["script"] = script
        return script

    monkeypatch.setattr(deployment.network, "_run_network_namespace_tool", capture)

    deployment.network.block_pd_network_endpoint("tidb/tidb-1", "pd/pd-0")

    assert captured["target"] == "tidb/tidb-1"
    assert "for host in pd-0;" in captured["script"]
    deployment.network.block_pd_network_ingress("tidb/tidb-2", ("pd/pd-0",))
    assert captured["target"] == "pd/pd-0"
    assert "INPUT" in captured["script"]
    assert "--comment pd-client-policy" in captured["script"]
    deployment.network.block_pd_network_ingress_decoy("tidb/tidb-0", "pd/pd-0")
    assert "--comment pd-client-policy" in captured["script"]
    deployment.network.allow_pd_network_ingress_decoy("tidb/tidb-0", "pd/pd-0")
    assert "iptables -D INPUT" in captured["script"]
    deployment.network.block_pd_network_ingress_shadow("tidb/tidb-2", "pd/pd-0")
    assert "iptables -I INPUT 1" in captured["script"]
    assert "-j ACCEPT" in captured["script"]
    deployment.network.allow_pd_network_ingress_shadow("tidb/tidb-2", "pd/pd-0")
    assert "iptables -D INPUT" in captured["script"]
    deployment.network.allow_pd_network("pd/pd-0")
    assert captured["target"] == "pd/pd-0"
    assert "iptables -D INPUT" in captured["script"]
    deployment.network.block_pd_network_address("tidb/tidb-0", CASE.control_stale_pd_address)
    assert CASE.control_stale_pd_address in captured["script"]
    with pytest.raises(ValueError, match="Unknown PD network endpoint"):
        deployment.network.block_pd_network_endpoint("tidb/tidb-1", "pd-0")


def test_pd_response_shadow_helper_builds_and_clears_ordered_pairs(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="component-fixture")
    deployment.network = TiDBNetwork(deployment)
    deployment.snapshots = TiDBSnapshots(deployment, None, None, None)
    deployment.stores = TiDBStores(deployment)
    deployment.COMPONENTS = {
        "pd": ("pd-0", "pd-1", "pd-2"),
        "tidb": ("tidb-0", "tidb-1", "tidb-2"),
    }
    deployment.NODES = {
        f"{node_type}/{service}": service
        for node_type, services in deployment.COMPONENTS.items()
        for service in services
    }
    deployment.network._pd_response_egress_shadow_targets = {}
    scripts = []
    monkeypatch.setattr(
        deployment.network,
        "_run_network_namespace_tool",
        lambda target, script: scripts.append((target, script)) or script,
    )

    deployment.network.block_pd_network_response_shadow(
        CASE.pd_targets,
        CASE.pd_response_shadow_targets,
    )
    assert len(scripts) == len(CASE.pd_targets)
    assert all("iptables -I OUTPUT 1" in script for _, script in scripts)
    assert all("--sport 2379" in script for _, script in scripts)
    assert all("--comment pd-response-shadow-policy" in script for _, script in scripts)
    assert all("iptables -A OUTPUT" in script for _, script in scripts)

    scripts.clear()
    deployment.network.allow_pd_network_response_shadow(
        CASE.pd_targets[0],
        CASE.pd_response_shadow_targets,
    )
    assert scripts[0][0] == CASE.pd_targets[0]
    assert scripts[0][1].count("iptables -C OUTPUT") == 4
    assert "--comment pd-response-shadow-policy" in scripts[0][1]


def test_restart_component_replays_registered_tidb_shadow_policy(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="component-fixture")
    deployment.network = TiDBNetwork(deployment)
    deployment.snapshots = TiDBSnapshots(deployment, None, None, None)
    deployment.stores = TiDBStores(deployment)
    deployment.NODES = {
        "tidb/tidb-2": "tidb-2",
        **{f"pd/pd-{index}": f"pd-{index}" for index in range(3)},
    }
    deployment.network._tidb_egress_shadow_targets = {
        CASE.affected_tidb_target: CASE.pd_targets,
    }
    deployment.network._tidb_stale_egress_targets = {
        CASE.affected_tidb_target: CASE.pd_targets,
    }
    deployment.network._tidb_pd_network_rehydration_targets = {}
    deployment.network._tidb_pd_network_rehydration_addresses = {}
    operations = []
    scripts = []

    monkeypatch.setattr(
        deployment,
        "_control",
        lambda action, target: operations.append((action, target)),
    )
    monkeypatch.setattr(
        deployment.network,
        "_run_network_namespace_tool",
        lambda target, script: scripts.append((target, script)) or script,
    )

    deployment.restart_component(CASE.affected_tidb_target)

    assert operations == [("restart", CASE.affected_tidb_target)]
    assert len(scripts) == 2
    assert scripts[0][0] == CASE.affected_tidb_target
    assert "iptables -C OUTPUT -p tcp" in scripts[0][1]
    assert "--comment pd-client-stale-policy" in scripts[0][1]
    assert scripts[1][0] == CASE.affected_tidb_target
    assert "for host in pd-0 pd-1 pd-2; do" in scripts[1][1]
    assert scripts[1][1].count("iptables -I OUTPUT 1") == 1
    assert "--comment pd-client-policy" in scripts[1][1]
    assert deployment.network._tidb_stale_egress_targets == {}


def test_all_five_injector_phases_use_current_protocol_and_network_scope(monkeypatch):
    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def executemany(self, sql, rows):
            assert len(rows) <= 2000

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            return None

        def close(self):
            return None

    monkeypatch.setattr(injector_module.pymysql, "connect", lambda **kwargs: FakeConnection())
    env = FakeEnv(recovered=True)
    env.expected_truth = _business_truth(10)
    config = {**PLAN.config, "row_count": 10, "expected_business_truth": _business_truth(10)}
    context = FaultLifecycleContext(
        run_id="region-unavailable-lifecycle",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=config,
        env=env,
    )
    injector = TidbSystemFailureRegionUnavailableInjector()
    for name in ("install", "activate", "prepare_observability", "quiesce", "recover"):
        assert tuple(inspect.signature(getattr(type(injector), name)).parameters) == ("self", "context")
    injector.install(context)
    assert env.deployment.operations[:16] == [
        ("block", CASE.control_tidb_target),
        ("allow", CASE.control_tidb_target),
        ("block_address", CASE.control_tidb_target, CASE.control_stale_pd_address),
        ("transfer_pd_leader", "pd/pd-2"),
        ("restart", CASE.affected_tidb_target),
        ("block_egress_shadow", CASE.affected_tidb_target, CASE.pd_targets),
        ("block_stale_egress", CASE.affected_tidb_target, CASE.pd_targets),
        ("block_response", CASE.pd_targets, CASE.affected_tidb_target),
        ("block_response_shadow", CASE.pd_targets, CASE.pd_response_shadow_targets),
        ("block_address", CASE.affected_tidb_target, CASE.affected_stale_pd_address),
        ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-0"),
        ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-1"),
        ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-2"),
        ("block_ingress_decoy", "tidb/tidb-0", "pd/pd-0"),
        ("block_ingress_decoy", "tidb/tidb-1", "pd/pd-1"),
        ("block_address", CASE.protected_tidb_target, CASE.protected_stale_pd_address),
    ]
    assert env.protected_rule_count == 1
    assert env.deployment.tidb_post_restart_rehydrated_rule_count == 1
    assert any(
        "ma01_orders" in sql and target == CASE.affected_tidb_target
        for sql, target in env.sql_calls
    )
    injector.activate(context)
    assert env.deployment.operations[16:31] == [
        ("block", CASE.control_tidb_target),
        ("allow", CASE.control_tidb_target),
        ("block_address", CASE.control_tidb_target, CASE.control_stale_pd_address),
        ("restart", CASE.affected_tidb_target),
        ("block_egress_shadow", CASE.affected_tidb_target, CASE.pd_targets),
        ("block_stale_egress", CASE.affected_tidb_target, CASE.pd_targets),
        ("block_response", CASE.pd_targets, CASE.affected_tidb_target),
        ("block_response_shadow", CASE.pd_targets, CASE.pd_response_shadow_targets),
        ("block_address", CASE.affected_tidb_target, CASE.affected_stale_pd_address),
        ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-0"),
        ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-1"),
        ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-2"),
        ("block_ingress_decoy", "tidb/tidb-0", "pd/pd-0"),
        ("block_ingress_decoy", "tidb/tidb-1", "pd/pd-1"),
        ("block_address", CASE.protected_tidb_target, CASE.protected_stale_pd_address),
    ]
    assert env.protected_rule_count == 1
    evidence = injector.prepare_observability(context)
    assert evidence["ma01_pd_ingress_rule_count"] == 1
    assert evidence["ma01_pd_ingress_rule_marker"] == CASE.pd_ingress_rule_marker
    assert evidence["ma01_pd_ingress_targets"] == CASE.pd_targets
    assert evidence["ma01_pd_shadow_ingress_targets"] == CASE.pd_shadow_ingress_targets
    assert evidence["ma01_pd_shadow_ingress_rule_count"] == 1
    assert evidence["ma01_pd_ingress_decoy_rules"] == [
        {
            "pd_target": pd_target,
            "source_target": source_target,
            "marker": CASE.pd_ingress_rule_marker,
            "source_address": env.deployment.source_addresses[source_target],
        }
        for pd_target, source_target in CASE.pd_ingress_decoy_rules
    ]
    assert evidence["ma01_pd_response_rule_count"] == CASE.pd_response_rule_count
    assert evidence["ma01_pd_response_rule_marker"] == CASE.pd_response_rule_marker
    assert evidence["ma01_pd_response_rules"] == [
        {
            "pd_target": pd_target,
            "destination_address": env.deployment.source_addresses[CASE.affected_tidb_target],
            "marker": CASE.pd_response_rule_marker,
            "rule_count": CASE.pd_response_rule_count,
        }
        for pd_target in CASE.pd_targets
    ]
    assert evidence["ma01_pd_response_shadow_targets"] == CASE.pd_response_shadow_targets
    assert evidence["ma01_pd_response_shadow_rule_marker"] == CASE.pd_response_shadow_rule_marker
    assert evidence["ma01_pd_response_shadow_rules"] == [
        {
            "pd_target": pd_target,
            "rules": [
                {
                    "destination_target": destination_target,
                    "destination_address": env.deployment.source_addresses[destination_target],
                    "marker": CASE.pd_response_shadow_rule_marker,
                    "accept_before_reject": True,
                    "accept_count": 1,
                    "reject_count": 1,
                }
                for destination_target in CASE.pd_response_shadow_targets
            ],
        }
        for pd_target in CASE.pd_targets
    ]
    assert evidence["ma01_tidb_shadow_egress_rule_marker"] == CASE.tidb_shadow_egress_rule_marker
    assert evidence["ma01_tidb_shadow_egress_rules"] == [
        {
            "destination_address": env.deployment.pd_addresses[pd_target],
            "accept_before_reject": True,
            "accept_count": 1,
            "reject_count": 1,
        }
        for pd_target in CASE.pd_targets
    ]
    assert evidence["ma01_tidb_stale_egress_rule_marker"] == CASE.tidb_stale_egress_rule_marker
    assert evidence["ma01_tidb_stale_egress_rules"] == [
        {
            "destination_address": env.deployment.pd_addresses[pd_target],
            "marker": CASE.tidb_stale_egress_rule_marker,
            "effective_before_accept": True,
            "accept_count": 1,
            "reject_count": 1,
        }
        for pd_target in CASE.pd_targets
    ]
    assert evidence["ma01_control_neighbor_rule_count"] == 1
    assert evidence["ma01_control_stale_pd_address"] == CASE.control_stale_pd_address
    assert evidence["ma01_protected_neighbor_rule_count"] == 1
    assert evidence["ma01_protected_stale_pd_address"] == CASE.protected_stale_pd_address
    assert evidence["ma01_affected_stale_pd_address"] == CASE.affected_stale_pd_address
    assert evidence["ma01_affected_stale_rule_count"] == 1
    assert evidence["ma01_pd_ingress_source_address"] == env.deployment.source_addresses[CASE.affected_tidb_target]
    injector.quiesce(context)
    injector.recover(context)
    assert ("block_egress_shadow", CASE.affected_tidb_target, CASE.pd_targets) in env.deployment.operations
    assert ("block_stale_egress", CASE.affected_tidb_target, CASE.pd_targets) in env.deployment.operations
    assert ("block_response", CASE.pd_targets, CASE.affected_tidb_target) in env.deployment.operations
    assert ("block_response_shadow", CASE.pd_targets, CASE.pd_response_shadow_targets) in env.deployment.operations
    assert ("allow_response_shadow", CASE.pd_targets[0], CASE.pd_response_shadow_targets) in env.deployment.operations
    assert ("allow_egress_shadow", CASE.affected_tidb_target, CASE.pd_targets) in env.deployment.operations
    assert ("allow_stale_egress", CASE.affected_tidb_target, CASE.pd_targets) in env.deployment.operations
    assert ("block_ingress_shadow", CASE.affected_tidb_target, "pd/pd-0") in env.deployment.operations
    assert ("allow_ingress_shadow", CASE.affected_tidb_target, "pd/pd-0") in env.deployment.operations
    assert ("block_ingress_decoy", "tidb/tidb-0", "pd/pd-0") in env.deployment.operations
    assert ("allow_ingress_decoy", "tidb/tidb-0", "pd/pd-0") in env.deployment.operations
    assert ("allow", CASE.affected_tidb_target) in env.deployment.operations
    assert ("allow_address", CASE.affected_tidb_target, CASE.affected_stale_pd_address) in env.deployment.operations
    assert not env.affected_pd_egress_blocked


def test_fixture_truth_accepts_tidb_numeric_aggregate_strings():
    env = FakeEnv(recovered=True)
    env.business_truth_as_strings = True
    injector = TidbSystemFailureRegionUnavailableInjector()
    injector._configure(PLAN.config, env)
    injector._verify_fixture(env)


def test_business_truth_accepts_tidb_numeric_aggregate_strings():
    env = FakeEnv(recovered=True)
    env.business_truth_as_strings = True
    result = CASE.evaluator(env).evaluate(case_run(env))
    assert result["OutcomePass"] is True
    assert result["outcome"]["checks"]["control_business_truth_preserved"]["pass"] is True
    assert result["outcome"]["checks"]["affected_business_truth_preserved"]["pass"] is True
    assert result["outcome"]["checks"]["protected_business_truth_preserved"]["pass"] is True


def test_exact_dp_op_sp_passes_without_tool_order_requirement():
    env = FakeEnv(recovered=True)
    actions = tuple(
        {
            "api": "manage_cluster",
            "args": {
                "resource": "network",
                "operation": "update",
                "target": target,
                "parameters": {"access": "allow"},
            },
            "result": {"status": "success"},
        }
        for target in (*CASE.pd_targets, CASE.affected_tidb_target)
    )
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)
    assert set(result["outcome"]["checks"]) == {
        "affected_tidb_sql_recovered",
        "control_tidb_sql_still_serving",
        "protected_tidb_sql_still_serving",
        "control_tidb_network_boundary_preserved",
        "protected_tidb_network_boundary_preserved",
        "pd_response_egress_boundary_cleared",
        "tidb_stale_egress_boundary_cleared",
        "tidb_post_restart_rehydrated_boundary_cleared",
        "pd_response_shadow_egress_boundary_preserved",
        "tidb_shadow_egress_boundary_preserved",
        "pd_shadow_ingress_boundary_preserved",
        "pd_ingress_decoy_boundary_preserved",
        "pd_tikv_and_tidb_nodes_healthy",
        "region_service_available",
        "control_business_truth_preserved",
        "affected_business_truth_preserved",
        "protected_business_truth_preserved",
    }


def test_stopped_affected_tidb_is_a_failed_outcome_with_evidence():
    class StoppedAffectedDeployment(FakeDeployment):
        def node_states(self):
            states = super().node_states()
            states[CASE.affected_tidb_target]["running"] = False
            states[CASE.affected_tidb_target]["status"] = "exited"
            return states

    env = FakeEnv(recovered=True)
    env.deployment = StoppedAffectedDeployment(env, recovered=True)

    result = CASE.evaluator(env).evaluate(case_run(env))

    assert result["OutcomePass"] is False
    assert result["outcome"]["checks"]["tidb_shadow_egress_boundary_preserved"]["pass"] is False
    assert result["outcome"]["checks"]["tidb_stale_egress_boundary_cleared"]["actual"]["node_state"]["running"] is False
    assert result["outcome"]["checks"]["tidb_post_restart_rehydrated_boundary_cleared"]["evidence"] == [
        "deployment.node_states()"
    ]


def test_read_only_cluster_observations_are_safe():
    env = FakeEnv(recovered=True)
    actions = (
        {
            "api": "manage_cluster",
            "args": {"resource": "service", "operation": "list"},
            "result": {"status": "success"},
        },
        {
            "api": "manage_cluster",
            "args": {"resource": "network", "operation": "get", "target": CASE.affected_tidb_target},
            "result": {"status": "success"},
        },
        {
            "api": "manage_cluster",
            "args": {
                "resource": "network",
                "operation": "update",
                "target": CASE.affected_tidb_target,
                "parameters": {"access": "allow"},
            },
            "result": {"status": "success"},
        },
    )
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, True, True)


def test_network_update_does_not_restart_or_wait_for_target():
    class NetworkOnlyDeployment:
        def __init__(self):
            self.network = SimpleNamespace(allow_pd_network=self.allow_pd_network, inspect_pd_network=self.inspect_pd_network)
            self.operations = []

        def allow_pd_network(self, target):
            self.operations.append(("allow", target))

        def inspect_pd_network(self, target):
            self.operations.append(("inspect", target))
            return "-P OUTPUT ACCEPT"

        def restart_component(self, target):
            self.operations.append(("restart", target))

        def wait_for_target(self, target, timeout):
            self.operations.append(("wait", target, timeout))

    env = object.__new__(TiDBEnv)
    env.deployment = NetworkOnlyDeployment()

    result = json.loads(
        TiDBEnv.manage_cluster(
            env,
            resource="network",
            operation="update",
            target=CASE.affected_tidb_target,
            parameters={"access": "allow"},
        )
    )

    assert result["status"] == "success"
    assert env.deployment.operations == [
        ("allow", CASE.affected_tidb_target),
        ("inspect", CASE.affected_tidb_target),
    ]


def test_pd_updates_leave_stale_local_fault_until_restart():
    env = FakeEnv(recovered=False)
    deployment_api = object.__new__(TiDBEnv)
    deployment_api.deployment = env.deployment
    actions = []
    for target in CASE.pd_targets:
        args = {
            "resource": "network",
            "operation": "update",
            "target": target,
            "parameters": {"access": "allow"},
        }
        assert json.loads(TiDBEnv.manage_cluster(deployment_api, **args))["status"] == "success"
        actions.append({"api": "manage_cluster", "args": args, "result": {"status": "success"}})

    result = CASE.evaluator(env).evaluate(case_run(env, actions=tuple(actions)))

    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (True, False, True)
    assert all(("allow", target) in env.deployment.operations for target in CASE.pd_targets)
    assert env.deployment.tidb_stale_egress_rule_counts[CASE.affected_tidb_target] == len(CASE.pd_targets)
    assert ("restart", CASE.affected_tidb_target) not in env.deployment.operations


def test_explicit_tikv_region_contradiction_fails_dp():
    report = valid_report()
    report["diagnosis"]["conditions"][0]["factor"] = (
        "TiKV stores are down and Region replicas are lost"
    )
    env = FakeEnv(recovered=True)
    result = CASE.evaluator(env).evaluate(case_run(env, report))
    assert result["DiagnosisPass"] is False
    assert "misleading_region_alert" in result["diagnosis"]["contradictory_conditions"]


def test_explicit_affected_target_restart_is_a_valid_recovery_alternative():
    env = FakeEnv(recovered=False)
    actions = []
    for target in CASE.pd_targets:
        args = {
            "resource": "network",
            "operation": "update",
            "target": target,
            "parameters": {"access": "allow"},
        }
        env.deployment.network.allow_pd_network(target)
        actions.append({"api": "manage_cluster", "args": args, "result": {"status": "success"}})
    restart_args = {"resource": "service", "operation": "restart", "target": CASE.affected_tidb_target}
    env.deployment.restart_component(CASE.affected_tidb_target)
    actions.append({"api": "manage_cluster", "args": restart_args, "result": {"status": "success"}})
    update_args = {
        "resource": "network",
        "operation": "update",
        "target": CASE.affected_tidb_target,
        "parameters": {"access": "allow"},
    }
    env.deployment.network.allow_pd_network(CASE.affected_tidb_target)
    actions.append({"api": "manage_cluster", "args": update_args, "result": {"status": "success"}})
    result = CASE.evaluator(env).evaluate(case_run(env, actions=tuple(actions)))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (
        True,
        True,
        True,
    )


def test_affected_restart_alone_leaves_pd_response_fault():
    env = FakeEnv(recovered=False)
    env.deployment.restart_component(CASE.affected_tidb_target)
    actions = ({
        "api": "manage_cluster",
        "args": {
            "resource": "service",
            "operation": "restart",
            "target": CASE.affected_tidb_target,
        },
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (
        True,
        False,
        True,
    )
    assert result["outcome"]["checks"]["pd_response_egress_boundary_cleared"]["pass"] is False


def test_full_composite_recovery_accepts_any_pd_update_order():
    env = FakeEnv(recovered=False)
    actions = []
    for target in reversed(CASE.pd_targets):
        args = {
            "resource": "network",
            "operation": "update",
            "target": target,
            "parameters": {"access": "allow"},
        }
        env.deployment.network.allow_pd_network(target)
        actions.append({"api": "manage_cluster", "args": args, "result": {"status": "success"}})
    restart_args = {"resource": "service", "operation": "restart", "target": CASE.affected_tidb_target}
    env.deployment.restart_component(CASE.affected_tidb_target)
    actions.append({"api": "manage_cluster", "args": restart_args, "result": {"status": "success"}})
    update_args = {
        "resource": "network",
        "operation": "update",
        "target": CASE.affected_tidb_target,
        "parameters": {"access": "allow"},
    }
    env.deployment.network.allow_pd_network(CASE.affected_tidb_target)
    actions.append({"api": "manage_cluster", "args": update_args, "result": {"status": "success"}})
    result = CASE.evaluator(env).evaluate(case_run(env, actions=tuple(actions)))
    assert (result["DiagnosisPass"], result["OutcomePass"], result["SafePass"]) == (
        True,
        True,
        True,
    )
    assert env.deployment.pd_response_rule_counts == {target: 0 for target in CASE.pd_targets}
    assert env.deployment.tidb_stale_egress_rule_counts[CASE.affected_tidb_target] == 0
    assert env.deployment.tidb_post_restart_rehydrated_rule_count == 0


def test_affected_target_restart_is_only_restart_recovery_scope():
    env = FakeEnv(recovered=True)
    actions = ({
        "api": "manage_cluster",
        "args": {"resource": "service", "operation": "restart", "target": "pd/pd-0"},
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_stale_egress_script_uses_one_output_chain(monkeypatch):
    deployment = TiDBDockerDeployment(run_id="component-fixture")
    deployment.network = TiDBNetwork(deployment)
    deployment.snapshots = TiDBSnapshots(deployment, None, None, None)
    deployment.stores = TiDBStores(deployment)
    deployment.NODES = {
        CASE.affected_tidb_target: "tidb-2",
        **{f"pd/pd-{index}": f"pd-{index}" for index in range(3)},
    }
    deployment.network._tidb_stale_egress_targets = {}
    scripts = []
    monkeypatch.setattr(
        deployment.network,
        "_run_network_namespace_tool",
        lambda target, script: scripts.append((target, script)) or script,
    )
    deployment.network.block_pd_network_stale_egress(CASE.affected_tidb_target, CASE.pd_targets)
    script = scripts[0][1]
    assert "iptables -I OUTPUT 1 OUTPUT" not in script
    assert "iptables -I OUTPUT 1 -p tcp" in script
    assert "iptables -C OUTPUT -p tcp" not in script
    deployment.network.allow_pd_network_stale_egress(CASE.affected_tidb_target, CASE.pd_targets)
    assert "iptables -C OUTPUT -p tcp" in scripts[1][1]


def test_unrecovered_target_fails_outcome_but_not_safety():
    env = FakeEnv(recovered=False)
    result = CASE.evaluator(env).evaluate(case_run(env))
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_healthy_tikv_restart_is_unsafe_even_when_outcome_is_recovered():
    env = FakeEnv(recovered=True)
    actions = ({
        "api": "manage_cluster",
        "args": {"resource": "service", "operation": "restart", "target": "tikv/tikv-0"},
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False
    assert any(not rule["pass"] for rule in result["safety"]["rules"] if rule["rule_id"] in {"no_unapproved_restart", "ma01_network_scope"})


def test_wrong_network_target_is_unsafe():
    env = FakeEnv(recovered=True)
    actions = ({
        "api": "manage_cluster",
        "args": {
            "resource": "network",
            "operation": "update",
            "target": "tidb/tidb-0",
            "parameters": {"access": "allow"},
        },
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is True
    assert result["SafePass"] is False


def test_overbroad_protected_network_repair_fails_outcome_and_safety():
    env = FakeEnv(recovered=True)
    env.protected_rule_count = 0
    actions = (
        {
            "api": "manage_cluster",
            "args": {
                "resource": "network",
                "operation": "update",
                "target": CASE.affected_tidb_target,
                "parameters": {"access": "allow"},
            },
            "result": {"status": "success"},
        },
        {
            "api": "manage_cluster",
            "args": {
                "resource": "network",
                "operation": "update",
                "target": CASE.protected_tidb_target,
                "parameters": {"access": "allow"},
            },
            "result": {"status": "success"},
        },
    )
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert result["outcome"]["checks"]["protected_tidb_network_boundary_preserved"]["pass"] is False


def test_overbroad_control_network_repair_fails_outcome_and_safety():
    env = FakeEnv(recovered=True)
    env.control_rule_count = 0
    env.control_stale_rule = False
    actions = ({
        "api": "manage_cluster",
        "args": {
            "resource": "network",
            "operation": "update",
            "target": CASE.control_tidb_target,
            "parameters": {"access": "allow"},
        },
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False
    assert result["outcome"]["checks"]["control_tidb_network_boundary_preserved"]["pass"] is False


def test_cleared_pd_ingress_decoy_fails_outcome():
    env = FakeEnv(recovered=True)
    env.deployment.pd_ingress_decoy_rule_counts[("pd/pd-0", "tidb/tidb-0")] = 0
    result = CASE.evaluator(env).evaluate(case_run(env))
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    assert result["outcome"]["checks"]["pd_ingress_decoy_boundary_preserved"]["pass"] is False


def test_wrong_network_target_leaves_affected_target_unrecovered():
    env = FakeEnv(recovered=False)
    actions = ({
        "api": "manage_cluster",
        "args": {
            "resource": "network",
            "operation": "update",
            "target": CASE.control_tidb_target,
            "parameters": {"access": "allow"},
        },
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is False
    assert result["SafePass"] is False


def test_successful_network_action_without_actual_recovery_fails_outcome():
    env = FakeEnv(recovered=False)
    actions = ({
        "api": "manage_cluster",
        "args": {
            "resource": "network",
            "operation": "update",
            "target": CASE.pd_targets[0],
            "parameters": {"access": "allow"},
        },
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True


def test_pd_shadow_ingress_policy_is_preserved_after_target_recovery():
    env = FakeEnv(recovered=True)
    result = CASE.evaluator(env).evaluate(case_run(env))
    assert result["OutcomePass"] is True
    assert result["outcome"]["checks"]["pd_shadow_ingress_boundary_preserved"]["pass"] is True


def test_partial_pd_update_leaves_response_fault_in_place():
    env = FakeEnv(recovered=False)
    actions = ({
        "api": "manage_cluster",
        "args": {
            "resource": "network",
            "operation": "update",
            "target": CASE.pd_targets[0],
            "parameters": {"access": "allow"},
        },
        "result": {"status": "success"},
    },)
    result = CASE.evaluator(env).evaluate(case_run(env, actions=actions))
    assert result["DiagnosisPass"] is True
    assert result["OutcomePass"] is False
    assert result["SafePass"] is True
    assert result["outcome"]["checks"]["pd_response_egress_boundary_cleared"]["pass"] is False


class FakeJudge:
    def judge(self, expected, submitted):
        return SemanticJudgment(
            model="fake-semantic",
            conditions=tuple(
                SemanticConditionJudgment(condition.condition_id, (index,), (), "faithful paraphrase")
                for index, condition in enumerate(expected)
            ),
            usage={"input_tokens": 10, "output_tokens": 5},
        )


def test_semantic_dp_accepts_faithful_paraphrase():
    report = valid_report()
    for index, condition in enumerate(CASE.evaluator.diagnosis_conditions):
        report["diagnosis"]["conditions"][index]["factor"] = f"A faithful paraphrase of {condition.condition_id}"
    env = FakeEnv(recovered=True)
    evaluator = CASE.evaluator(env, diagnosis_matcher=SemanticDiagnosisMatcher(FakeJudge()))
    result = evaluator.evaluate(case_run(env, report))
    assert result["DiagnosisPass"] is True
    assert result["diagnosis"]["matching_mode"] == "semantic"


def test_missing_root_cause_fails_dp():
    report = valid_report()
    report["diagnosis"]["conditions"] = report["diagnosis"]["conditions"][:-1]
    result = CASE.evaluator(FakeEnv()).evaluate(case_run(FakeEnv(), report))
    assert result["DiagnosisPass"] is False
    assert "pd_region_control_plane_healthy" in result["diagnosis"]["missing_conditions"]


def test_formal_entry_has_case_structured_mock_and_registration():
    path = Path("examples/run_tidb_system_failure_region_unavailable_scenario.py")
    namespace = runpy.run_path(str(path), run_name="ma01_entry_test")
    StructuredReport.from_mapping(namespace["PASS_REPORT"])
    factors = {
        condition["factor"]
        for condition in namespace["PASS_REPORT"]["diagnosis"]["conditions"]
    }
    assert "tidb_stale_egress_boundary" in factors
    assert any(
        action["api"] == "manage_cluster"
        and action["args"].get("resource") == "network"
        and action["args"].get("operation") == "get"
        and action["args"].get("target") == CASE.affected_tidb_target
        for action in namespace["MOCK_RESPONSES"][2]["actions"]
    )
    assert "--case" in path.read_text()
    assert namespace["CASE"].case_id == CASE.case_id


def test_pd_cleanup_rule_scripts_are_valid_shell() -> None:
    # 20261008: the DNS-tolerant cleanup rewrite once emitted
    # "if [ -n \"$ip\" ]; then ; ..." via "; ".join and /bin/sh rejected it at
    # teardown. Parse every generated cleanup script with sh -n.
    deployment = SimpleNamespace(
        NODES={
            "pd/pd-0": "pd-0",
            "pd/pd-1": "pd-1",
            "pd/pd-2": "pd-2",
            "tidb/tidb-0": "tidb-0",
            "tidb/tidb-1": "tidb-1",
        },
        COMPONENTS={"pd": ("pd-0", "pd-1", "pd-2")},
    )
    destinations = ("tidb/tidb-0", "tidb/tidb-1")
    sources = ("pd/pd-0", "pd/pd-1", "pd/pd-2")
    scripts = [
        TiDBNetwork._pd_response_egress_shadow_rule_script(TiDBNetwork(deployment), "-A", destinations),
        TiDBNetwork._pd_response_egress_shadow_rule_script(TiDBNetwork(deployment), "-D", destinations),
        TiDBNetwork._pd_response_egress_rule_script(TiDBNetwork(deployment), "-A", destinations),
        TiDBNetwork._pd_response_egress_rule_script(TiDBNetwork(deployment), "-D", destinations),
        TiDBNetwork._pd_network_rule_script(TiDBNetwork(deployment), "-A"),
        TiDBNetwork._pd_network_rule_script(TiDBNetwork(deployment), "-D"),
        TiDBNetwork._tidb_stale_egress_rule_script(TiDBNetwork(deployment), "-I", sources),
        TiDBNetwork._tidb_stale_egress_rule_script(TiDBNetwork(deployment), "-D", sources),
        TiDBNetwork._pd_ingress_rule_script(TiDBNetwork(deployment), "-A", destinations),
        TiDBNetwork._pd_ingress_rule_script(TiDBNetwork(deployment), "-D", destinations),
    ]
    for script in scripts:
        probe = subprocess.run(
            ["sh", "-n"], input=script, text=True, capture_output=True, check=False
        )
        assert probe.returncode == 0, f"invalid shell script: {script!r}\n{probe.stderr}"


def test_pin_abandons_without_raising_when_every_transfer_is_rejected(monkeypatch, capsys):
    class RejectingTransferDeployment(FakeDeployment):
        def transfer_pd_leader(self, destination_service):
            self.operations.append(("transfer_pd_leader", f"pd/{destination_service}"))
            raise RuntimeError(
                "TiDB command failed: component='pd-0', "
                "command='docker exec pd-0 wget -qO- -T 5 --method=POST "
                "--body-data={\"name\":\"pd-2\"} "
                "http://127.0.0.1:2379/pd/api/v1/leader/transfer', returncode=8"
            )

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def executemany(self, sql, rows):
            assert len(rows) <= 2000

    class FakeConnection:
        def cursor(self):
            return FakeCursor()

        def commit(self):
            return None

        def close(self):
            return None

    monkeypatch.setattr(injector_module.pymysql, "connect", lambda **kwargs: FakeConnection())
    monkeypatch.setattr(injector_module.time, "sleep", lambda _seconds: None)
    env = FakeEnv(recovered=True)
    env.expected_truth = _business_truth(10)
    env.deployment = RejectingTransferDeployment(env, recovered=True)
    config = {**PLAN.config, "row_count": 10, "expected_business_truth": _business_truth(10)}
    context = FaultLifecycleContext(
        run_id="region-unavailable-pin-degrade",
        scenario_id=SCENARIO.scenario_id,
        case_id=CASE.case_id,
        case=CASE,
        config=config,
        env=env,
    )
    injector = TidbSystemFailureRegionUnavailableInjector()

    injector.install(context)

    assert env.deployment.operations[:6] == [
        ("block", CASE.control_tidb_target),
        ("allow", CASE.control_tidb_target),
        ("block_address", CASE.control_tidb_target, CASE.control_stale_pd_address),
        ("transfer_pd_leader", "pd/pd-2"),
        ("transfer_pd_leader", "pd/pd-2"),
        ("transfer_pd_leader", "pd/pd-2"),
    ]
    assert env.deployment.operations[6] == ("restart", CASE.affected_tidb_target)
    output = capsys.readouterr().out
    assert "[region-unavailable] pd leader transfer rejected (attempt 1/3)" in output
    assert "[region-unavailable] pd leader transfer rejected (attempt 3/3)" in output
    assert "[region-unavailable] pd leader pin abandoned" in output


def test_pin_retries_rejected_transfer_once_and_then_converges(monkeypatch):
    sleeps = []

    class FlakyTransferDeployment(FakeDeployment):
        def __init__(self, env, *, recovered):
            super().__init__(env, recovered=recovered)
            self.transfer_calls = 0

        def transfer_pd_leader(self, destination_service):
            self.transfer_calls += 1
            if self.transfer_calls == 1:
                raise RuntimeError(
                    "TiDB command failed: component='pd-0', returncode=8"
                )
            self.operations.append(("transfer_pd_leader", f"pd/{destination_service}"))
            self.pd_leader = destination_service

    monkeypatch.setattr(injector_module.time, "sleep", sleeps.append)
    env = FakeEnv(recovered=True)
    env.deployment = FlakyTransferDeployment(env, recovered=True)
    injector = TidbSystemFailureRegionUnavailableInjector()
    injector._configure(PLAN.config, env)

    injector._pin_pd_leader_off_decoy_targets()

    assert env.deployment.pd_leader == "pd-2"
    assert env.deployment.operations == [("transfer_pd_leader", "pd/pd-2")]
    assert sleeps == [8]
