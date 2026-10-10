# TiDB metrics, network, storage, plugins, and repair flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/command-line-flags-for-tidb-configuration.md`
- Source Title: `Configuration Options`
- Source Heading Path: `Configuration Options > `--metrics-addr` | Configuration Options > `--metrics-interval` | Configuration Options > `-P` | Configuration Options > `--path` | Configuration Options > `--proxy-protocol-fallbackable` | Configuration Options > `--proxy-protocol-networks` | Configuration Options > `--proxy-protocol-header-timeout` | Configuration Options > `--report-status` | Configuration Options > `--run-ddl` | Configuration Options > `--socket string` | Configuration Options > `--status` | Configuration Options > `--status-host` | Configuration Options > `--store` | Configuration Options > `--temp-dir` | Configuration Options > `--tidb-service-scope` | Configuration Options > `--token-limit` | Configuration Options > `-V` | Configuration Options > `--plugin-dir` | Configuration Options > `--plugin-load` | Configuration Options > `--affinity-cpus` | Configuration Options > `--redact` | Configuration Options > `--repair-mode` | Configuration Options > `--repair-list``
- Source Line Ranges: `93-240`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `shared`
- Topic Tags: `metrics`, `prometheus`, `port`, `status-endpoint`, `pprof`, `proxy-protocol`, `reverse-proxy`, `storage-engine`, `pd-address`, `ddl`, `unix-socket`, `service-scope`, `concurrency-control`, `plugins`, `cpu-affinity`, `log-redaction`, `repair-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0060_b978a74efe`
- Source ID: `tidb-docs-8.1:command-line-flags-for-tidb-configuration.md#metrics-addr`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8171c7d39090b86cf6a8e64e159c243b611724d2af6e7f6ad81ec037023d7eff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration#metrics-addr
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/command-line-flags-for-tidb-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB command-line flags for metrics and status endpoints, storage and PD path settings, PROXY protocol behavior, DDL execution, unix socket, service scope, concurrency limits, plugins, CPU affinity, log redaction, or repair mode.
- Retrieval Keywords: --metrics-addr, --metrics-interval, -P, --path, --proxy-protocol-fallbackable, --proxy-protocol-networks, --proxy-protocol-header-timeout, --report-status, --run-ddl, --socket string, --status, --status-host, --store, --temp-dir, --tidb-service-scope, --token-limit, -V, --plugin-dir, --plugin-load, --affinity-cpus, --redact, --repair-mode, --repair-list, Prometheus Pushgateway, PROXY protocol, HAProxy, AWS Network Load Balancer, proxy_protocol_v2.client_to_server.header_place, pprof, /metrics, /debug/pprof, unistore, tikv, PD address, tidb_service_scope, collect-log
- Follow-up Guidance: The content includes related details such as the status URLs for Prometheus metrics and pprof, the warning and note for PROXY protocol settings, and that `--proxy-protocol-header-timeout` is deprecated since v6.3.0.
- Classification Note: This is reference content because it lists TiDB operational command-line flags and defaults for metrics, networking, storage, plugins, redaction, and repair-related behavior.

## Official Source Content

## `--metrics-addr`

- The Prometheus Pushgateway address
- Default: `""`
- Leaving it empty stops the Prometheus client from pushing.
- The format is `--metrics-addr=192.168.100.115:9091`.
## `--metrics-interval`

- The Prometheus client push interval in seconds
- Default: `15s`
- Setting the value to 0 stops the Prometheus client from pushing.
## `-P`

- The monitoring port of TiDB services
- Default: `"4000"`
- The TiDB server accepts MySQL client requests from this port.
## `--path`

- The path to the data directory for local storage engine like "unistore"
- For `--store = tikv`, you must specify the path; for `--store = unistore`, the default value is used if you do not specify the path.
- For the distributed storage engine like TiKV, `--path` specifies the actual PD address. Assuming that you deploy the PD server on 192.168.100.113:2379, 192.168.100.114:2379 and 192.168.100.115:2379, the value of `--path` is "192.168.100.113:2379, 192.168.100.114:2379, 192.168.100.115:2379".
- Default: `"/tmp/tidb"`
- You can use `tidb-server --store=unistore --path=""` to enable a pure in-memory TiDB.
## `--proxy-protocol-fallbackable`

- Controls whether to enable PROXY protocol fallback mode. When this parameter is set to `true`, TiDB accepts client connections that belong to `--proxy-protocol-networks` without using the PROXY protocol specification or without sending a PROXY protocol header. By default, TiDB only accepts client connections that belong to `--proxy-protocol-networks` and send a PROXY protocol header.
- Default value: `false`
## `--proxy-protocol-networks`

- The list of proxy server's IP addresses allowed to connect to TiDB using the [PROXY protocol](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt).
- Default: `""`
- In general cases, when you access TiDB behind a reverse proxy, TiDB takes the IP address of the reverse proxy server as the IP address of the client. By enabling the PROXY protocol, reverse proxies that support this protocol such as HAProxy can pass the real client IP address to TiDB.
- After configuring this flag, TiDB allows the configured source IP address to connect to TiDB using the PROXY protocol; if a protocol other than PROXY is used, this connection will be denied; other addresses are allowed to connect to TiDB without the PROXY protocol. If this flag is left empty, no IP address can connect to TiDB using the PROXY protocol. The value can be the IP address (192.168.1.50) or CIDR (192.168.1.0/24) with `,` as the separator. `*` means any IP addresses.

> **Warning:**
>
> Use `*` with caution because it might introduce security risks by allowing a client of any IP address to report its IP address. In addition, using `*` might also cause the internal component that directly connects to TiDB (such as TiDB Dashboard) to be unavailable unless `--proxy-protocol-fallbackable` is set to `true`.

> **Note:**
>
> To use an AWS Network Load Balancer (NLB) with the PROXY protocol enabled, you need to configure the `target group` property of NLB. Specifically, set `proxy_protocol_v2.client_to_server.header_place` to `on_first_ack`. At the same time, you need to submit a ticket to AWS Support. Note that after the PROXY protocol is enabled, the client will fail to obtain handshake packets from the server and the packets are blocked until the client times out. This is because NLB sends proxy packets only after the client sends data. However, before the client sends any data packets, data packets sent by the server are dropped in the internal network.
## `--proxy-protocol-header-timeout`

- Timeout for the PROXY protocol header read
- Default: `5` (seconds)

> **Warning:**
>
> Since v6.3.0, this parameter is deprecated. It is no longer used because the PROXY protocol header will be read upon the first time network data is read. Deprecating this parameter avoids affecting the timeout set when network data is read for the first time.

> **Note:**
>
> Do not set the value to `0`. Use the default value except for special situations.
## `--report-status`

- Enables (`true`) or disables (`false`) the status report and pprof tool
- Default: `true`
- When set to `true`, this parameter enables metrics and pprof. When set to `false`, this parameter disables metrics and pprof.
## `--run-ddl`

- To see whether the `tidb-server` runs DDL statements, and set when the number of `tidb-server` is over two in the cluster
- Default: `true`
- The value can be (true) or (false). (true) indicates the `tidb-server` runs DDL itself. (false) indicates the `tidb-server` does not run DDL itself.
## `--socket string`

- The TiDB services use the unix socket file for external connections.
- Default: `""`
- Use `/tmp/tidb.sock` to open the unix socket file.
## `--status`

- The status report port for TiDB server
- Default: `"10080"`
- This port is used to get server internal data. The data includes [Prometheus metrics](https://prometheus.io/) and [pprof](https://golang.org/pkg/net/http/pprof/).
- Prometheus metrics can be accessed by `"http://host:status_port/metrics"`.
- pprof data can be accessed by `"http://host:status_port/debug/pprof"`.
## `--status-host`

- The `HOST` used to monitor the status of TiDB service
- Default: `0.0.0.0`
## `--store`

- Specifies the storage engine used by TiDB in the bottom layer
- Default: `"unistore"`
- You can choose "unistore" or "tikv". ("unistore" is the local storage engine; "tikv" is a distributed storage engine)
## `--temp-dir`

- The temporary directory of TiDB
- Default: `"/tmp/tidb"`
## `--tidb-service-scope`

+ Specifies the initial value of [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) for the current TiDB instance.
+ Default: `""`
## `--token-limit`

- The number of sessions allowed to run concurrently in TiDB. It is used for traffic control.
- Default: `1000`
- If the number of the concurrent sessions is larger than `token-limit`, the request is blocked and waiting for the operations which have been finished to release tokens.
## `-V`

- Outputs the version of TiDB
- Default: `""`
## `--plugin-dir`

+ The storage directory for plugins.
+ Default: `"/data/deploy/plugin"`
## `--plugin-load`

+ The names of the plugins to be loaded, each separated by a comma.
+ Default: `""`
## `--affinity-cpus`

+ Sets the CPU affinity of TiDB servers, which is separated by commas. For example, "1,2,3".
+ Default: `""`
## `--redact`

+ Determines whether the TiDB server desensitizes log files when using the subcommand `collect-log`.
+ Default: false
+ When the value is `true`, it is a masking operation, and all fields wrapped in `‹ ›` mark symbols are replaced with `?`. When the value is `false`, it is a restore operation, and all mark symbols are removed. To use this feature, execute `./tidb-server --redact=xxx collect-log <input> <output>` to desensitize or restore the TiDB server log file specified by `<input>` and output it to `<output>`. For more information, see the system variable [`tidb_redact_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_redact_log).
## `--repair-mode`

+ Determines whether to enable the repair mode, which is only used in the data repair scenario.
+ Default: `false`
## `--repair-list`

+ The names of the tables to be repaired in the repair mode.
+ Default: `""`
