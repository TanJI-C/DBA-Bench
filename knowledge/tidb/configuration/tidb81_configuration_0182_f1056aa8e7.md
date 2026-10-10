# TiCDC server configuration file parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-server-config.md`
- Source Title: `TiCDC Server Configurations`
- Source Heading Path: `TiCDC Server Configurations > `cdc server` configuration file parameters`
- Source Line Ranges: `29-90`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `configuration-file`, `toml`, `security`, `tls`, `mtls`, `authentication`, `memory`, `gogc`, `session`, `flush-interval`, `logging`, `sorter`, `kv-client`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0182_f1056aa8e7`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-server-config.md#cdc-server-configuration-file-parameters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2e15e1c2f9d5f3ae706fbc65d60144f0bb7df3924328f4b1844631ef148b327a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-server-config#cdc-server-configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-server-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the TiCDC `cdc server` configuration file parameters in TOML, including security, memory tuning, session TTL, flush intervals, sorter, logging, and kv-client settings.
- Retrieval Keywords: cdc server configuration file parameters, config option, TOML, addr, advertise-addr, log-file, log-level, data-dir, gc-ttl, tz, cluster-id, gc-tuner-memory-threshold, security, ca-path, cert-path, key-path, mtls, client-user-required, client-allowed-user, capture-session-ttl, owner-flush-interval, processor-flush-interval, log.error-output, log.file.max-size, log.file.max-days, log.file.max-backups, sorter, cache-size-in-mb, sorter-dir, kv-client, worker-concurrent, worker-pool-size, region-retry-duration
- Follow-up Guidance: This chunk states that the configuration method of several file parameters is the same as the CLI parameters, but the CLI parameters have higher priorities.
- Classification Note: This is configuration content because it defines TiCDC server configuration file fields, default values, and parameter groups such as `[security]`, `[sorter]`, and `[kv-client]`.

## Official Source Content

## `cdc server` configuration file parameters

The following describes the configuration file specified by the `config` option in the `cdc server` command:

```toml
# The configuration method of the following parameters is the same as that of CLI parameters, but the CLI parameters have higher priorities.
addr = "127.0.0.1:8300"
advertise-addr = ""
log-file = ""
log-level = "info"
data-dir = ""
gc-ttl = 86400 # 24 h
tz = "System"
cluster-id = "default"
# This parameter specifies the maximum memory threshold (in bytes) for tuning GOGC: Setting a smaller threshold increases the GC frequency. Setting a larger threshold reduces GC frequency and consumes more memory resources for the TiCDC process. Once the memory usage exceeds this threshold, GOGC Tuner stops working. The default value is 0, indicating that GOGC Tuner is disabled.
gc-tuner-memory-threshold = 0

[security]
  ca-path = ""
  cert-path = ""
  key-path = ""
  # This parameter controls whether to enable the TLS client authentication. The default value is false.
  mtls = false
  # This parameter controls whether to use username and password for client authentication. The default value is false.
  client-user-required = false
  # This parameter lists the usernames that are allowed for client authentication. Authentication requests with usernames not in this list will be rejected. The default value is null.
  client-allowed-user = ["username_1", "username_2"]

# The session duration between TiCDC and etcd services, measured in seconds. This parameter is optional and its default value is 10.
capture-session-ttl = 10 # 10s

# The interval at which the Owner module in the TiCDC cluster attempts to push the replication progress. This parameter is optional and its default value is `50000000` nanoseconds (that is, 50 milliseconds). You can configure this parameter in two ways: specifying only the number (for example, configuring it as `40000000` represents 40000000 nanoseconds, which is 40 milliseconds), or specifying both the number and unit (for example, directly configuring it as `40ms`).
owner-flush-interval = 50000000 # 50 ms

# The interval at which the Processor module in the TiCDC cluster attempts to push the replication progress. This parameter is optional and its default value is `50000000` nanoseconds (that is, 50 milliseconds). The configuration method of this parameter is the same as that of `owner-flush-interval`.
processor-flush-interval = 50000000 # 50 ms

# [log]
# # The output location for internal error logs of the zap log module. This parameter is optional and its default value is "stderr".
#   error-output = "stderr"
#   [log.file]
#     # The maximum size of a single log file, measured in MiB. This parameter is optional and its default value is 300.
#     max-size = 300 # 300 MiB
#     # The maximum number of days to retain log files. This parameter is optional and its default value is `0`, indicating never to delete.
#     max-days = 0
#     # The number of log files to retain. This parameter is optional and its default value is `0`, indicating to keep all log files.
#     max-backups = 0

#[sorter]
# The size of the shared pebble block cache in the Sorter module for the 8 pebble DBs started by default, measured in MiB. The default value is 128.
# cache-size-in-mb = 128
# The directory where sorter files are stored relative to the data directory (`data-dir`). This parameter is optional and its default value is "/tmp/sorter".
# sorter-dir = "/tmp/sorter"

# [kv-client]
#   The number of threads that can be used in a single Region worker. This parameter is optional and its default value is 8.
#   worker-concurrent = 8
#   The number of threads in the shared thread pool of TiCDC, mainly used for processing KV events. This parameter is optional and its default value is 0, indicating that the default pool size is twice the number of CPU cores.
#   worker-pool-size = 0
#   The retry duration of Region connections. This parameter is optional and its default value is `60000000000` nanoseconds (that is, 1 minute). You can configure this parameter in two ways: specifying only the number (for example, configuring it as `50000000` represents 50000000 nanoseconds, which is 50 milliseconds), or specifying both the number and unit (for example, directly configuring it as `50ms`).
#   region-retry-duration = 60000000000
```
