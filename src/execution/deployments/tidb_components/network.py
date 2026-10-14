import shlex


class TiDBNetwork:
    """Network operations and run state."""

    def __init__(self, deployment):
        self.deployment = deployment
        self._pd_ingress_sources: dict[str, set[str]] = {}
        self._pd_response_egress_targets: dict[str, set[str]] = {}
        self._pd_response_egress_shadow_targets: dict[str, set[str]] = {}
        self._tidb_stale_egress_targets: dict[str, tuple[str, ...]] = {}
        self._tidb_egress_shadow_targets: dict[str, tuple[str, ...]] = {}
        self._tidb_pd_network_rehydration_targets: dict[str, tuple[str, ...]] = {}
        self._tidb_pd_network_rehydration_addresses: dict[str, tuple[str, ...]] = {}

    NETWORK_TOOL_IMAGE = (
        "docker.m.daocloud.io/nicolaka/netshoot@"
        "sha256:b09d9b21381f47a79b3cbcb30da25266dc17186ea00ae65e99fdc51396f48e70"
    )


    def arm_pd_network_rehydration(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> None:
        if target not in self.deployment.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB rehydration target: target={target!r}")
        unknown_pd_targets = tuple(
            pd_target
            for pd_target in pd_targets
            if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown PD rehydration targets: target={target!r}, pd_targets={unknown_pd_targets!r}"
            )
        hosts = " ".join(shlex.quote(self.deployment.NODES[pd_target]) for pd_target in pd_targets)
        output = self._run_network_namespace_tool(
            target,
            "set -eu; "
            f"for host in {hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
            "test -n \"$ip\"; printf '%s\\n' \"$ip\"; "
            "done",
        )
        addresses = tuple(output.splitlines())
        if len(addresses) != len(pd_targets) or any(not address for address in addresses):
            raise RuntimeError(
                "TiDB PD network rehydration address resolution is invalid: "
                f"target={target!r}, pd_targets={pd_targets!r}, addresses={addresses!r}, output={output!r}"
            )
        self._tidb_pd_network_rehydration_targets[target] = tuple(pd_targets)
        self._tidb_pd_network_rehydration_addresses[target] = addresses


    def disarm_pd_network_rehydration(self, target: str) -> None:
        self._tidb_pd_network_rehydration_targets.pop(target, None)
        self._tidb_pd_network_rehydration_addresses.pop(target, None)


    def _pd_network_rehydration_rule_script(self, addresses: tuple[str, ...]) -> str:
        commands = ["set -eu"]
        commands.extend(
            "iptables -A OUTPUT -p tcp -d "
            f"{shlex.quote(address)} --dport 2379 -j REJECT --reject-with tcp-reset"
            for address in addresses
        )
        commands.append("iptables -S OUTPUT")
        return "; ".join(commands)


    def _run_network_namespace_tool(self, target: str, script: str) -> str:
        service, = self.deployment._services(target)
        container_id = self.deployment._service_container_id(service)
        self.deployment._run(
            ["docker", "image", "inspect", self.NETWORK_TOOL_IMAGE],
            "network-helper-image",
        )
        return self.deployment._run(
            [
                "docker", "run", "--rm",
                "--network", f"container:{container_id}",
                "--cap-add", "NET_ADMIN",
                "--entrypoint", "/bin/sh",
                self.NETWORK_TOOL_IMAGE,
                "-ceu", script,
            ],
            target,
        )


    def _pd_network_rule_script(
        self,
        operation: str,
        pd_targets: tuple[str, ...] | None = None,
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD network rule operation: {operation!r}")
        pd_hosts = " ".join(
            shlex.quote(service)
            for service in (self.deployment.COMPONENTS["pd"] if pd_targets is None else pd_targets)
        )
        if operation == "-A":
            body = (
                "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
                "test -n \"$ip\"; "
                "iptables -A OUTPUT -p tcp -d \"$ip\" --dport 2379 "
                "-j REJECT --reject-with tcp-reset; "
            )
        else:
            body = (
                "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}') || true; "
                'if [ -n "$ip" ]; then '
                'rule="OUTPUT -p tcp -d $ip --dport 2379 -j REJECT --reject-with tcp-reset"; '
                'if iptables -C $rule; then iptables -D $rule; else status=$?; test "$status" -eq 1; fi; '
                'fi; '
            )
        return (
            "set -eu; "
            f"for host in {pd_hosts}; do "
            + body
            + "done; "
            "iptables -S OUTPUT"
        )


    def block_pd_network(self, target: str) -> str:
        return self._run_network_namespace_tool(
            target,
            self._pd_network_rule_script("-A"),
        )


    def _pd_response_egress_rule_script(
        self,
        operation: str,
        destination_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD response egress operation: {operation!r}")
        commands = [
            "set -eu",
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}')",
            'test -n "$source_ip"',
        ]
        for target in destination_targets:
            host = shlex.quote(self.deployment.NODES[target])
            if operation == "-A":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                ])
            else:
                commands.append(
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true"
                )
            rule = (
                'OUTPUT -p tcp -s "$source_ip" --sport 2379 -d "$ip" '
                "-m comment --comment pd-response-policy -j REJECT --reject-with tcp-reset"
            )
            if operation == "-A":
                commands.append(f"iptables -A {rule}")
            else:
                commands.append(
                    f'if [ -n "$ip" ] && iptables -C {rule}; then iptables -D {rule}; '
                    'else status=$?; test "$status" -eq 1; fi'
                )
        commands.extend(["iptables -S INPUT", "iptables -S OUTPUT"])
        return "; ".join(commands)


    def block_pd_network_response(
        self,
        pd_targets: tuple[str, ...],
        destination_target: str,
    ) -> str:
        unknown_pd_targets = tuple(
            target for target in pd_targets
            if target not in self.deployment.NODES or not target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown PD response egress sources: pd_targets={unknown_pd_targets!r}"
            )
        if destination_target not in self.deployment.NODES or not destination_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown PD response egress destination: destination_target={destination_target!r}"
            )
        output = ""
        for pd_target in pd_targets:
            self._pd_response_egress_targets.setdefault(pd_target, set()).add(destination_target)
            output = self._run_network_namespace_tool(
                pd_target,
                self._pd_response_egress_rule_script("-A", (destination_target,)),
            )
        return output


    def allow_pd_network_response(
        self,
        pd_target: str,
        destination_target: str,
    ) -> str:
        if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/"):
            raise ValueError(f"Unknown PD response egress source: pd_target={pd_target!r}")
        if destination_target not in self.deployment.NODES or not destination_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown PD response egress destination: destination_target={destination_target!r}"
            )
        output = self._run_network_namespace_tool(
            pd_target,
            self._pd_response_egress_rule_script("-D", (destination_target,)),
        )
        destinations = self._pd_response_egress_targets.get(pd_target)
        if destinations is not None:
            destinations.discard(destination_target)
            if not destinations:
                self._pd_response_egress_targets.pop(pd_target)
        return output


    def _pd_response_egress_shadow_rule_script(
        self,
        operation: str,
        destination_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD response egress shadow operation: {operation!r}")
        commands = [
            "set -eu",
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}')",
            'test -n "$source_ip"',
        ]
        for target in destination_targets:
            host = shlex.quote(self.deployment.NODES[target])
            if operation == "-A":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                ])
            else:
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true",
                ])
            accept_suffix = (
                '-p tcp -s "$source_ip" --sport 2379 -d "$ip" '
                '-j ACCEPT'
            )
            accept_rule = (
                f"OUTPUT {accept_suffix}"
            )
            reject_rule = (
                'OUTPUT -p tcp -s "$source_ip" --sport 2379 -d "$ip" '
                "-m comment --comment pd-response-shadow-policy -j REJECT "
                "--reject-with tcp-reset"
            )
            if operation == "-A":
                commands.extend([
                    f"iptables -I OUTPUT 1 {accept_suffix}",
                    f"iptables -A {reject_rule}",
                ])
            else:
                removals = "; ".join(
                    f"if iptables -C {rule}; then iptables -D {rule}; "
                    'else status=$?; test "$status" -eq 1; fi'
                    for rule in (reject_rule, accept_rule)
                )
                commands.append(f'if [ -n "$ip" ]; then {removals}; fi')
        commands.extend(["iptables -S INPUT", "iptables -S OUTPUT"])
        return "; ".join(commands)


    def block_pd_network_response_shadow(
        self,
        pd_targets: tuple[str, ...],
        destination_targets: tuple[str, ...],
    ) -> str:
        unknown_pd_targets = tuple(
            target for target in pd_targets
            if target not in self.deployment.NODES or not target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown PD response egress shadow sources: pd_targets={unknown_pd_targets!r}"
            )
        unknown_destinations = tuple(
            target for target in destination_targets
            if target not in self.deployment.NODES or not target.startswith("tidb/")
        )
        if unknown_destinations:
            raise ValueError(
                "Unknown PD response egress shadow destinations: "
                f"destination_targets={unknown_destinations!r}"
            )
        output = ""
        for pd_target in pd_targets:
            output = self._run_network_namespace_tool(
                pd_target,
                self._pd_response_egress_shadow_rule_script("-A", destination_targets),
            )
            self._pd_response_egress_shadow_targets[pd_target] = set(destination_targets)
        return output


    def allow_pd_network_response_shadow(
        self,
        pd_target: str,
        destination_targets: tuple[str, ...],
    ) -> str:
        if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/"):
            raise ValueError(f"Unknown PD response egress shadow source: pd_target={pd_target!r}")
        unknown_destinations = tuple(
            target for target in destination_targets
            if target not in self.deployment.NODES or not target.startswith("tidb/")
        )
        if unknown_destinations:
            raise ValueError(
                "Unknown PD response egress shadow destinations: "
                f"destination_targets={unknown_destinations!r}"
            )
        output = self._run_network_namespace_tool(
            pd_target,
            self._pd_response_egress_shadow_rule_script("-D", destination_targets),
        )
        self._pd_response_egress_shadow_targets.pop(pd_target, None)
        return output


    def block_pd_network_egress_shadow(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if target not in self.deployment.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB egress shadow target: target={target!r}")
        unknown_pd_targets = tuple(
            pd_target for pd_target in pd_targets
            if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown TiDB egress shadow PD targets: target={target!r}, "
                f"pd_targets={unknown_pd_targets!r}"
            )
        output = self._run_network_namespace_tool(
            target,
            self._tidb_egress_shadow_rule_script(pd_targets),
        )
        self._tidb_egress_shadow_targets[target] = tuple(pd_targets)
        return output


    def _tidb_egress_shadow_rule_script(
        self,
        pd_targets: tuple[str, ...],
    ) -> str:
        pd_hosts = " ".join(shlex.quote(self.deployment.NODES[pd_target]) for pd_target in pd_targets)
        return (
            "set -eu; "
            f"for host in {pd_hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
            'test -n "$ip"; '
            'iptables -I OUTPUT 1 -p tcp -d "$ip" --dport 2379 -j ACCEPT; '
            'iptables -A OUTPUT -p tcp -d "$ip" --dport 2379 '
            '-m comment --comment pd-client-policy -j REJECT --reject-with tcp-reset; '
            "done; iptables -S INPUT; iptables -S OUTPUT"
        )


    def allow_pd_network_egress_shadow(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if target not in self.deployment.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB egress shadow target: target={target!r}")
        pd_hosts = " ".join(shlex.quote(self.deployment.NODES[pd_target]) for pd_target in pd_targets)
        output = self._run_network_namespace_tool(
            target,
            "set -eu; "
            f"for host in {pd_hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}') || true; "
            'if [ -n "$ip" ]; then '
            'reject="OUTPUT -p tcp -d $ip --dport 2379 -m comment --comment pd-client-policy '
            '-j REJECT --reject-with tcp-reset"; '
            'accept="OUTPUT -p tcp -d $ip --dport 2379 -j ACCEPT"; '
            'if iptables -C $reject; then iptables -D $reject; else status=$?; test "$status" -eq 1; fi; '
            'if iptables -C $accept; then iptables -D $accept; else status=$?; test "$status" -eq 1; fi; '
            'fi; '
            "done; iptables -S INPUT; iptables -S OUTPUT",
        )
        self._tidb_egress_shadow_targets.pop(target, None)
        return output


    def _tidb_stale_egress_rule_script(
        self,
        operation: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-I", "-D"}:
            raise ValueError(f"Unsupported TiDB stale egress operation: {operation!r}")
        commands = ["set -eu"]
        for pd_target in pd_targets:
            host = shlex.quote(self.deployment.NODES[pd_target])
            rule = (
                '-p tcp -d "$ip" --dport 2379 '
                "-m comment --comment pd-client-stale-policy -j REJECT "
                "--reject-with tcp-reset"
            )
            if operation == "-I":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                    f"iptables -I OUTPUT 1 {rule}",
                ])
            else:
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true",
                    f'if [ -n "$ip" ] && iptables -C OUTPUT {rule}; then iptables -D OUTPUT {rule}; '
                    'else status=$?; test "$status" -eq 1; fi',
                ])
        commands.extend(["iptables -S INPUT", "iptables -S OUTPUT"])
        return "; ".join(commands)


    def block_pd_network_stale_egress(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if target not in self.deployment.NODES or not target.startswith("tidb/"):
            raise ValueError(f"Unknown TiDB stale egress target: target={target!r}")
        unknown_pd_targets = tuple(
            pd_target
            for pd_target in pd_targets
            if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/")
        )
        if unknown_pd_targets:
            raise ValueError(
                f"Unknown TiDB stale egress PD targets: target={target!r}, "
                f"pd_targets={unknown_pd_targets!r}"
            )
        output = self._run_network_namespace_tool(
            target,
            self._tidb_stale_egress_rule_script("-I", pd_targets),
        )
        self._tidb_stale_egress_targets[target] = tuple(pd_targets)
        return output


    def allow_pd_network_stale_egress(
        self,
        target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        output = self._run_network_namespace_tool(
            target,
            self._tidb_stale_egress_rule_script("-D", pd_targets),
        )
        self._tidb_stale_egress_targets.pop(target, None)
        return output


    def block_pd_network_endpoint(self, target: str, pd_target: str) -> str:
        if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD network endpoint: target={target!r}, pd_target={pd_target!r}, "
                f"expected={tuple(f'pd/{service}' for service in self.deployment.COMPONENTS['pd'])!r}"
            )
        return self._run_network_namespace_tool(
            target,
            self._pd_network_rule_script("-A", (self.deployment.NODES[pd_target],)),
        )


    def block_pd_network_address(self, target: str, address: str) -> str:
        return self._run_network_namespace_tool(
            target,
            "set -eu; "
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}'); "
            "test -n \"$source_ip\"; "
            f"iptables -A OUTPUT -s \"$source_ip\" -p tcp -d {shlex.quote(address)} --dport 2379 "
            "-j REJECT --reject-with tcp-reset; "
            "iptables -S INPUT; iptables -S OUTPUT",
        )


    def _pd_ingress_rule_script(
        self,
        operation: str,
        source_targets: tuple[str, ...],
    ) -> str:
        if operation not in {"-A", "-D"}:
            raise ValueError(f"Unsupported PD ingress rule operation: {operation!r}")
        commands = [
            "set -eu",
        ]
        for target in source_targets:
            host = shlex.quote(self.deployment.NODES[target])
            marker = shlex.quote("pd-client-policy")
            rule = (
                f"INPUT -p tcp -s \"$ip\" --dport 2379 "
                f"-m comment --comment {marker} -j REJECT --reject-with tcp-reset"
            )
            if operation == "-A":
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}')",
                    'test -n "$ip"',
                    f"iptables -A {rule}",
                ])
            else:
                commands.extend([
                    f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true",
                    f'if [ -n "$ip" ] && iptables -C {rule}; then iptables -D {rule}; '
                    'else status=$?; test "$status" -eq 1; fi',
                ])
        commands.extend([
            "iptables -S INPUT",
            "iptables -S OUTPUT",
        ])
        return "; ".join(commands)


    def block_pd_network_ingress(
        self,
        source_target: str,
        pd_targets: tuple[str, ...],
    ) -> str:
        if source_target not in self.deployment.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.deployment.COMPONENTS['tidb'])!r}"
            )
        unknown_targets = tuple(target for target in pd_targets if target not in self.deployment.NODES or not target.startswith("pd/"))
        if unknown_targets:
            raise ValueError(
                f"Unknown PD ingress targets: source_target={source_target!r}, "
                f"pd_targets={unknown_targets!r}"
            )
        output = ""
        for pd_target in pd_targets:
            self._pd_ingress_sources.setdefault(pd_target, set()).add(source_target)
            output = self._run_network_namespace_tool(
                pd_target,
                self._pd_ingress_rule_script("-A", (source_target,)),
            )
        return output


    def block_pd_network_ingress_decoy(self, source_target: str, pd_target: str) -> str:
        if source_target not in self.deployment.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress decoy source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.deployment.COMPONENTS['tidb'])!r}"
            )
        if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD ingress decoy target: source_target={source_target!r}, "
                f"pd_target={pd_target!r}, expected={tuple(f'pd/{service}' for service in self.deployment.COMPONENTS['pd'])!r}"
            )
        return self._run_network_namespace_tool(
            pd_target,
            self._pd_ingress_rule_script("-A", (source_target,)),
        )


    def allow_pd_network_ingress_decoy(self, source_target: str, pd_target: str) -> str:
        return self._run_network_namespace_tool(
            pd_target,
            self._pd_ingress_rule_script("-D", (source_target,)),
        )


    def block_pd_network_ingress_shadow(self, source_target: str, pd_target: str) -> str:
        if source_target not in self.deployment.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress shadow source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.deployment.COMPONENTS['tidb'])!r}"
            )
        if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD ingress shadow target: source_target={source_target!r}, "
                f"pd_target={pd_target!r}, expected={tuple(f'pd/{service}' for service in self.deployment.COMPONENTS['pd'])!r}"
            )
        host = shlex.quote(self.deployment.NODES[source_target])
        marker = shlex.quote("pd-client-policy")
        return self._run_network_namespace_tool(
            pd_target,
            "set -eu; "
            f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}'); "
            'test -n "$ip"; '
            'iptables -I INPUT 1 -p tcp -s "$ip" --dport 2379 -j ACCEPT; '
            f"iptables -A INPUT -p tcp -s \"$ip\" --dport 2379 -m comment --comment {marker} "
            "-j REJECT --reject-with tcp-reset; "
            "iptables -S INPUT; iptables -S OUTPUT",
        )


    def allow_pd_network_ingress_shadow(self, source_target: str, pd_target: str) -> str:
        if source_target not in self.deployment.NODES or not source_target.startswith("tidb/"):
            raise ValueError(
                f"Unknown TiDB PD ingress shadow source: source_target={source_target!r}, "
                f"expected={tuple(f'tidb/{service}' for service in self.deployment.COMPONENTS['tidb'])!r}"
            )
        if pd_target not in self.deployment.NODES or not pd_target.startswith("pd/"):
            raise ValueError(
                f"Unknown PD ingress shadow target: source_target={source_target!r}, "
                f"pd_target={pd_target!r}, expected={tuple(f'pd/{service}' for service in self.deployment.COMPONENTS['pd'])!r}"
            )
        host = shlex.quote(self.deployment.NODES[source_target])
        marker = shlex.quote("pd-client-policy")
        reject_rule = (
            f"INPUT -p tcp -s \"$ip\" --dport 2379 -m comment --comment {marker} "
            "-j REJECT --reject-with tcp-reset"
        )
        accept_rule = 'INPUT -p tcp -s "$ip" --dport 2379 -j ACCEPT'
        return self._run_network_namespace_tool(
            pd_target,
            "set -eu; "
            f"ip=$(getent ahostsv4 {host} | awk 'NR == 1 {{print $1}}') || true; "
            'if [ -n "$ip" ]; then '
            f"if iptables -C {reject_rule}; then iptables -D {reject_rule}; "
            'else status=$?; test "$status" -eq 1; fi; '
            f"if iptables -C {accept_rule}; then iptables -D {accept_rule}; "
            'else status=$?; test "$status" -eq 1; fi; '
            'fi; '
            "iptables -S INPUT; iptables -S OUTPUT",
        )


    def inspect_pd_network(self, target: str) -> str:
        return self._run_network_namespace_tool(
            target,
            "set -eu; iptables -S INPUT; iptables -S OUTPUT",
        )


    def allow_pd_network(self, target: str) -> str:
        if target.startswith("pd/"):
            source_targets = tuple(sorted(self._pd_ingress_sources.get(target, ())))
            response_targets = tuple(sorted(self._pd_response_egress_targets.get(target, ())))
            if not source_targets and not response_targets:
                return self.inspect_pd_network(target)
            output = ""
            if source_targets:
                output = self._run_network_namespace_tool(
                    target,
                    self._pd_ingress_rule_script("-D", source_targets),
                )
            for destination_target in response_targets:
                output = self.allow_pd_network_response(target, destination_target)
            return output
        pd_hosts = " ".join(shlex.quote(service) for service in self.deployment.COMPONENTS["pd"])
        script = (
            "set -eu; "
            f"for host in {pd_hosts}; do "
            "ip=$(getent ahostsv4 \"$host\" | awk 'NR == 1 {print $1}'); "
            "test -n \"$ip\"; "
            "if iptables -C OUTPUT -p tcp -d \"$ip\" --dport 2379 "
            "-j REJECT --reject-with tcp-reset; then "
            "iptables -D OUTPUT -p tcp -d \"$ip\" --dport 2379 "
            "-j REJECT --reject-with tcp-reset; "
            "else status=$?; test \"$status\" -eq 1; fi; "
            "done; "
            "iptables -S INPUT; iptables -S OUTPUT"
        )
        return self._run_network_namespace_tool(target, script)


    def allow_pd_network_address(self, target: str, address: str) -> str:
        script = (
            "set -eu; "
            "source_ip=$(ip -4 -o addr show scope global | "
            "awk 'NR == 1 {split($4, parts, \"/\"); print parts[1]}'); "
            "test -n \"$source_ip\"; "
            f"if iptables -C OUTPUT -s \"$source_ip\" -p tcp -d {shlex.quote(address)} --dport 2379 "
            "-j REJECT --reject-with tcp-reset; then "
            f"iptables -D OUTPUT -s \"$source_ip\" -p tcp -d {shlex.quote(address)} --dport 2379 "
            "-j REJECT --reject-with tcp-reset; "
            "else status=$?; test \"$status\" -eq 1; fi; "
            "iptables -S INPUT; iptables -S OUTPUT"
        )
        return self._run_network_namespace_tool(target, script)
