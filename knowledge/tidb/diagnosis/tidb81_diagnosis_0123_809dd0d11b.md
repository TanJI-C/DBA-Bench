# TiProxy connectivity, migration, CPU balance, and latency troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/troubleshoot-tiproxy.md`
- Source Title: `Troubleshoot TiProxy`
- Source Heading Path: `Troubleshoot TiProxy | Troubleshoot TiProxy > Cannot connect to TiProxy | Troubleshoot TiProxy > TiProxy does not migrate connections | Troubleshoot TiProxy > Unbalanced CPU usage on TiDB server | Troubleshoot TiProxy > Latency is significantly increased`
- Source Line Ranges: `5-44`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `tidb`, `shared`
- Topic Tags: `connectivity`, `connection-migration`, `cpu-usage`, `latency`, `tls`, `proxy-protocol`, `grafana`, `logs`, `connector-compatibility`, `capacity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0123_809dd0d11b`
- Source ID: `tidb-docs-8.1:tiproxy/troubleshoot-tiproxy.md#troubleshoot-tiproxy`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7402977770b97f4aef77264f47f81b08be498649f4863cf659d79e8dff2b49c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/troubleshoot-tiproxy#troubleshoot-tiproxy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/troubleshoot-tiproxy.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiProxy connection failures, connection migration issues, unbalanced TiDB CPU usage, or significantly increased latency in a self-managed deployment.
- Retrieval Keywords: Troubleshoot TiProxy, Cannot connect to TiProxy, TiProxy does not migrate connections, Unbalanced CPU usage on TiDB server, Latency is significantly increased, No available TiDB instances, please make sure TiDB is available, Require TLS enabled on TiProxy when require-backend-tls=true, Verify TiDB capability failed, please upgrade TiDB, TiProxy fails to connect to TiDB, please make sure TiDB is available, Require TLS enabled on TiDB when require-backend-tls=true, TiProxy fails to connect to TiDB, please make sure TiDB proxy-protocol is set correctly, proxy.proxy-protocol, proxy-protocol, max-connections, connector version, authentication plugins, security.session-token-signing-cert, security.session-token-signing-key, graceful-wait-before-shutdown, TiProxy log, Grafana, network duration between TiProxy and TiDB server
- Follow-up Guidance: The content points to checking TiProxy logs, Grafana latency and backend network duration, the TiProxy limitations page, and the TiDB troubleshooting page for "Latency increases significantly" when those specific conditions apply.
- Classification Note: The chunk is classified as diagnosis because the official content is organized as troubleshooting checks for TiProxy symptoms, including connectivity, migration, CPU balance, and latency.

## Official Source Content

# Troubleshoot TiProxy

This document describes some common problems, causes, and solutions for TiProxy.
## Cannot connect to TiProxy

You can troubleshoot the issue by following these steps:

1. Check if the [connector version](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#supported-connectors) is supported. If the connector is not in the list, check if the connector supports [authentication plugins](https://dev.mysql.com/doc/refman/8.0/en/pluggable-authentication.html).
2. If the client reports `No available TiDB instances, please make sure TiDB is available`, check if there is a TiDB server and if the SQL port and HTTP status port of the TiDB server can be connected normally.
3. If the client reports `Require TLS enabled on TiProxy when require-backend-tls=true`, check if TiProxy is correctly configured with TLS certificates.
4. If the client reports `Verify TiDB capability failed, please upgrade TiDB`, check if the TiDB server version is v6.5.0 or later.
5. If the client reports `TiProxy fails to connect to TiDB, please make sure TiDB is available`, check if the TiProxy node can connect to the TiDB server.
6. If the client reports `Require TLS enabled on TiDB when require-backend-tls=true`, check if TiDB is correctly configured with TLS certificates.
7. If the client reports `TiProxy fails to connect to TiDB, please make sure TiDB proxy-protocol is set correctly`, check if [`proxy.proxy-protocol`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#proxy-protocol) is enabled on TiProxy and [`proxy-protocol`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#proxy-protocol) is not enabled on the TiDB server.
8. Check if TiProxy is configured with [`max-connections`](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#max-connections) and if the number of connections on TiProxy exceeds the maximum connection limit.
9. Check the TiProxy log for error messages.
## TiProxy does not migrate connections

You can troubleshoot the issue by following these steps:

1. Whether the [TiProxy limitations](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-overview#limitations) are not met. You can further confirm this by checking the TiProxy log.
2. Whether [`security.session-token-signing-cert`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-cert-new-in-v640), [`security.session-token-signing-key`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#session-token-signing-key-new-in-v640), and [`graceful-wait-before-shutdown`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#graceful-wait-before-shutdown-new-in-v50) are correctly configured on TiDB.
## Unbalanced CPU usage on TiDB server

Check if the number of connections on TiDB server is balanced. If not, troubleshoot by following the [TiProxy does not migrate connections](#tiproxy-does-not-migrate-connections) section.

If the number of connections is balanced, it might be that some connections occupy a high CPU usage while other connections are relatively idle. TiProxy balances connections based on the number of connections on the TiDB server, not the actual load.
## Latency is significantly increased

You can troubleshoot the issue by following these steps:

1. Check the latency on TiProxy through Grafana. If the latency on TiProxy is not high, it means that the client load is high or the network latency between the client and TiProxy is high.
2. Check the latency on the TiDB server through Grafana. If the latency on the TiDB server is high, follow the steps in [Latency increases significantly](https://docs.pingcap.com/tidb/stable/tidb-troubleshooting-map#2-latency-increases-significantly) to troubleshoot.
3. Check the [network duration between TiProxy and TiDB server](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-grafana#backend) through Grafana.
4. Check the CPU usage on TiProxy. If the CPU usage is over 90%, you need to scale out TiProxy.
