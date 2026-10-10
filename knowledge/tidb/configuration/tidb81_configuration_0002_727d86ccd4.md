# Protect internal component ports with network policies

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices-for-security-configuration.md`
- Source Title: `Best Practices for TiDB Security Configuration`
- Source Heading Path: `Best Practices for TiDB Security Configuration > Protect internal ports`
- Source Line Ranges: `63-119`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dm`, `ticdc`, `lightning`, `operator`, `dashboard`
- Topic Tags: `security`, `ports`, `firewall`, `iptables`, `network-policy`, `internal-communication`, `reverse-proxy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0002_727d86ccd4`
- Source ID: `tidb-docs-8.1:best-practices-for-security-configuration.md#protect-internal-ports`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d28ca7a1c6a04a5980f742799167c00a24ed404d6f7b40da4e398a918f6c0e5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices-for-security-configuration#protect-internal-ports
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices-for-security-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving which TiDB ecosystem ports are internal by default and how the documentation suggests limiting external access with firewalls or network security policies.
- Retrieval Keywords: Protect internal ports, default listening ports, TiDB 4000, TiDB 10080, TiKV 20160, TiKV 20180, PD 2379, PD 2380, TiFlash 3930, TiFlash 20170, TiFlash 20292, TiFlash 8234, DM master 8261, DM master 8291, DM worker 8262, TiCDC 8300, TiDB Lightning 8289, TiDB Operator 6060, TiDB Dashboard 2379, TiDB Binlog 8250, TiDB Binlog 8249, Prometheus 9090, Grafana 3000, AlertManager 9093, AlertManager 9094, Node Exporter 9100, Blackbox Exporter 9115, NG Monitoring 12020, iptables, only expose 4000, 9000 port for the Grafana dashboard, reverse proxy
- Follow-up Guidance: The content includes an example iptables policy and separately notes that TiDB Dashboard access for external networks can be provided through a reverse proxy on a separate port.
- Classification Note: This is classified as configuration because the content lists default service ports and gives concrete network policy and firewall configuration examples for restricting access.

## Official Source Content

## Protect internal ports

By default, TiDB installation includes several privileged interfaces for inter-component communication. These ports typically do not need to be accessible to users, because they are primarily for internal communication. Exposing these ports on public networks increases the attack surface, violates the principle of least privilege, and raises the risk of security vulnerabilities. The following table lists the default listening ports in a TiDB cluster:

| Component         | Default port| Protocol   |
|-------------------|-------------|------------|
| TiDB              | 4000        | MySQL      |
| TiDB              | 10080       | HTTP       |
| TiKV              | 20160       | Protocol   |
| TiKV              | 20180       | HTTP       |
| PD                | 2379        | HTTP/Protocol|
| PD                | 2380        | Protocol   |
| TiFlash           | 3930        | Protocol   |
| TiFlash           | 20170       | Protocol   |
| TiFlash           | 20292       | HTTP       |
| TiFlash           | 8234        | HTTP       |
| DM master         | 8261        | HTTP       |
| DM master         | 8291        | HTTP       |
| DM worker         | 8262        | HTTP       |
| TiCDC             | 8300        | HTTP       |
| TiDB Lightning    | 8289        | HTTP       |
| TiDB Operator     | 6060        | HTTP       |
| TiDB Dashboard    | 2379        | HTTP       |
| TiDB Binlog       |  8250       | HTTP       |
| TiDB Binlog       |  8249       | HTTP       |
| TMS               | 8082        | HTTP       |
| TEM               | 8080        | HTTP       |
| TEM               | 8000        | HTTP       |
| TEM               | 4110        | HTTP       |
| TEM               | 4111        | HTTP       |
| TEM               | 4112        | HTTP       |
| TEM               | 4113        | HTTP       |
| TEM               | 4124        | HTTP       |
| Prometheus        | 9090        | HTTP       |
| Grafana           | 3000        | HTTP       |
| AlertManager      | 9093        | HTTP       |
| AlertManager      | 9094        | Protocol   |
| Node Exporter     | 9100        | HTTP       |
| Blackbox Exporter | 9115        | HTTP       |
| NG Monitoring     | 12020       | HTTP       |

It is recommended to only expose the `4000` port for the database and the `9000` port for the Grafana dashboard to ordinary users, while restricting access to other ports using network security policies or firewalls. The following is an example of using `iptables` to restrict port access:

```shell
# Allow internal port communication from the whitelist of component IP addresses
sudo iptables -A INPUT -s internal IP address range -j ACCEPT

# Only open ports 4000 and 9000 to external users
sudo iptables -A INPUT -p tcp --dport 4000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9000 -j ACCEPT

# Deny all other traffic by default
sudo iptables -P INPUT DROP
```

If you need to access TiDB Dashboard, it is recommended to [configure a reverse proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy#use-tidb-dashboard-behind-a-reverse-proxy) to securely provide services to external networks on a separate port.
