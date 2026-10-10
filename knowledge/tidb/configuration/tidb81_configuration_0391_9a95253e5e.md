# TiProxy tiproxy.toml proxy, API, and logging settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-configuration.md`
- Source Title: `TiProxy Configuration File`
- Source Heading Path: `TiProxy Configuration File | TiProxy Configuration File > Configure the `tiproxy.toml` file | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `addr` | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `graceful-wait-before-shutdown` | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `graceful-close-conn-timeout` | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `max-connections` | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `conn-buffer-size` | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `pd-addrs` | TiProxy Configuration File > Configure the `tiproxy.toml` file > proxy > `proxy-protocol` | TiProxy Configuration File > Configure the `tiproxy.toml` file > api | TiProxy Configuration File > Configure the `tiproxy.toml` file > api > `addr` | TiProxy Configuration File > Configure the `tiproxy.toml` file > api > `proxy-protocol` | TiProxy Configuration File > Configure the `tiproxy.toml` file > log | TiProxy Configuration File > Configure the `tiproxy.toml` file > log > `level` | TiProxy Configuration File > Configure the `tiproxy.toml` file > log > `encoder` | TiProxy Configuration File > Configure the `tiproxy.toml` file > log.log-file | TiProxy Configuration File > Configure the `tiproxy.toml` file > log.log-file > `filename` | TiProxy Configuration File > Configure the `tiproxy.toml` file > log.log-file > `max-size` | TiProxy Configuration File > Configure the `tiproxy.toml` file > log.log-file > `max-days` | TiProxy Configuration File > Configure the `tiproxy.toml` file > log.log-file > `max-backups``
- Source Line Ranges: `5-148`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `pd`, `tidb`, `tiup`, `operator`
- Topic Tags: `configuration-file`, `hot-reload`, `sql-port`, `http-gateway`, `proxy-protocol`, `connection-draining`, `connection-limits`, `buffer-size`, `pd-addresses`, `logging`, `log-rotation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0391_9a95253e5e`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-configuration.md#tiproxy-configuration-file`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea18da974634adbcd2dced0b85b226f6579b6874acd0c5c1460c85110a0b613f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration#tiproxy-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiProxy tiproxy.toml settings for SQL proxy, HTTP API gateway, connection draining, PROXY protocol, PD addresses, hot-reload behavior, or log rotation options.
- Retrieval Keywords: tiproxy.toml, [proxy], [api], [log], addr, graceful-wait-before-shutdown, graceful-close-conn-timeout, max-connections, conn-buffer-size, pd-addrs, proxy-protocol, 0.0.0.0:6000, 0.0.0.0:3080, tiup cluster reload --skip-restart, log level, encoder, log.log-file, filename, max-size, max-days, max-backups, PROXY protocol version 2, pass the real client IP address to TiDB
- Follow-up Guidance: The content notes that configuration changes normally lead to a restart, but TiProxy supports hot-reloading and can be reloaded with `tiup cluster reload --skip-restart`.
- Classification Note: This is configuration content because it defines TiProxy `tiproxy.toml` parameters, defaults, hot-reload support, valid values, and behavior for proxy, API, and logging sections.

## Official Source Content

# TiProxy Configuration File

This document introduces the configuration parameters related to the deployment and use of TiProxy. The following is an example configuration:

```toml
[proxy]
addr = "0.0.0.0:6000"
max-connections = 100

[api]
addr = "0.0.0.0:3080"

[log]
level = "info"

[security]
[security.cluster-tls]
skip-ca = true

[security.sql-tls]
skip-ca = true
```
## Configure the `tiproxy.toml` file

This section introduces the configuration parameters of TiProxy.

> **Tip:**
>
> If you need to adjust the value of a configuration item, refer to [Modify the configuration](https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#modify-the-configuration). Normally the modification leads to a restart. Because TiProxy supports hot-reloading, you can skip restart by executing `tiup cluster reload --skip-restart`.
### proxy

Configuration for SQL port.
#### `addr`

+ Default value: `0.0.0.0:6000`
+ Support hot-reload: no
+ SQL gateway address. The format is `<ip>:<port>`.
#### `graceful-wait-before-shutdown`

+ Default value: `0`
+ Support hot-reload: yes
+ Unit: second
+ When TiProxy shuts down, the HTTP status returns unhealthy but the SQL port still accepts new connections for `graceful-wait-before-shutdown` seconds. After that, it rejects new connections and drains clients. It is recommended to set it to `0` when there are no other proxies (e.g. NLB) between the client and TiProxy.
#### `graceful-close-conn-timeout`

+ Default value: `15`
+ Support hot-reload: yes
+ Unit: second
+ When TiProxy shuts down, it closes connections when they have completed their current transactions (also known as draining clients) within `graceful-close-conn-timeout` seconds. After that, all the connections are closed at once. `graceful-close-conn-timeout` happens after `graceful-wait-before-shutdown`. It is recommended to set this timeout longer than the lifecycle of a transaction.
#### `max-connections`

+ Default value: `0`
+ Support hot-reload: yes
+ Each TiProxy instance can accept `max-connections` connections at most. `0` means no limitation.
#### `conn-buffer-size`

+ Default value: `32768`
+ Support hot-reload: yes, but only for new connections
+ Range: `[1024, 16777216]`
+ This configuration item lets you decide the connection buffer size. Each connection uses one read buffer and one write buffer. It is a tradeoff between memory and performance. A larger buffer might yield better performance results but consume more memory. When it is `0`, TiProxy uses the default buffer size.
#### `pd-addrs`

+ Default value: `127.0.0.1:2379`
+ Support hot-reload: no
+ The PD addresses TiProxy connects to. TiProxy discovers TiDB instances by fetching the TiDB list from the PD. It is set automatically when TiProxy is deployed by TiUP or TiDB Operator.
#### `proxy-protocol`

+ Default value: `""`
+ Support hot-reload: yes, but only for new connections
+ Possible values: `""`, `"v2"`
+ Enable the [PROXY protocol](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt) on the port. By enabling the PROXY protocol, TiProxy can pass the real client IP address to TiDB. `"v2"` indicates using the PROXY protocol version 2, and `""` indicates disabling the PROXY protocol. If the PROXY protocol is enabled on TiProxy, you need to also enable the [PROXY protocol](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#proxy-protocol) on the TiDB server.
### api

Configurations for HTTP gateway.
#### `addr`

+ Default value: `0.0.0.0:3080`
+ Support hot-reload: no
+ API gateway address. You can specify `ip:port`.
#### `proxy-protocol`

+ Default value: `""`
+ Support hot-reload: no
+ Possible values: `""`, `"v2"`
+ Enable the [PROXY protocol](https://www.haproxy.org/download/1.8/doc/proxy-protocol.txt) on the port. `"v2"` indicates using the PROXY protocol version 2, and `""` indicates disabling the PROXY protocol.
### log
#### `level`

+ Default value: `info`
+ Support hot-reload: yes
+ Possible values: `debug`, `info`, `warn`, `error`, `panic`
+ Specify the log level. With the `panic` level, TiProxy will panic on errors.
#### `encoder`

+ Default value: `tidb`
+ You can specify:

    + `tidb`: format used by TiDB. For details, refer to [Unified Log Format](https://github.com/tikv/rfcs/blob/master/text/0018-unified-log-format.md).
    + `json`: structured JSON format.
    + `console`: human-readable log format.
### log.log-file
#### `filename`

+ Default value: `""`
+ Support hot-reload: yes
+ Log file path. Non empty value will enable logging to file. When TiProxy is deployed with TiUP, the filename is set automatically.
#### `max-size`

+ Default value: `300`
+ Support hot-reload: yes
+ Unit: MB
+ Specifies the maximum size for log files. A log file will be rotated if its size exceeds this limit.
#### `max-days`

+ Default value: `3`
+ Support hot-reload: yes
+ Specifies the maximum number of days to keep old log files. Outdated log files are deleted after surpassing this period.
#### `max-backups`

+ Default value: `3`
+ Support hot-reload: yes
+ Specifies the maximum number of log files to be retained. Surplus log files will be automatically deleted when an excessive number is reached.
