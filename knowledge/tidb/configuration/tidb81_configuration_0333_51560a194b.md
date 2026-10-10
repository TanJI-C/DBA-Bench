# TiDB Lightning configuration file types and global sample

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-configuration.md`
- Source Title: `TiDB Lightning Configuration`
- Source Heading Path: `TiDB Lightning Configuration | TiDB Lightning Configuration > Configuration files | TiDB Lightning Configuration > Configuration files > TiDB Lightning (Global) | TiDB Lightning Configuration > Configuration files > TiDB Lightning (Task)`
- Source Line Ranges: `5-44`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `shared`
- Topic Tags: `configuration-files`, `global-configuration`, `task-configuration`, `server-mode`, `status-address`, `logging`, `diagnostic-logs`, `web-interface`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0333_51560a194b`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-configuration.md#tidb-lightning-configuration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1715be625050df6ba8742df74245405ffa5ee1d21a0ddc15c8fed8fb236542e9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Lightning global versus task configuration structure, or for the [lightning] settings that control server mode, status HTTP endpoint, logging, and diagnostic logs.
- Retrieval Keywords: TiDB Lightning Configuration, Configuration files, TiDB Lightning (Global), TiDB Lightning (Task), [lightning], status-addr, :8289, server-mode, web interface, Prometheus metrics, debug data, submit import tasks, level, file, max-size, max-days, max-backups, enable-diagnose-logs, diagnostic logs, GRPC debugging
- Follow-up Guidance: The source states that when server mode is disabled by default, TiDB Lightning executes only one task and the same configuration file is used for both global and task configurations.
- Classification Note: This is classified as configuration for the lightning component because the content is a TiDB Lightning configuration reference covering global and task configuration file types and [lightning] parameters.

## Official Source Content

# TiDB Lightning Configuration

This document provides samples for global configuration and task configuration, and describes the usage of command-line parameters.
## Configuration files

TiDB Lightning has two configuration classes: "global" and "task", and they have compatible structures. Their distinction arises only when the [server mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface) is enabled. When server mode is disabled (the default), TiDB Lightning will only execute one task, and the same configuration file is used for both global and task configurations.
### TiDB Lightning (Global)

```toml
### tidb-lightning global configuration

[lightning]
# The HTTP port for displaying the web interface, pulling Prometheus metrics, exposing debug data,
# and submitting import tasks (in server mode). Setting it to 0 disables the port.
status-addr = ':8289'

# Server mode. Defaults to false, which means an import task starts immediately after you execute the command.
# If this value is set to true, after you execute the command,
# TiDB Lightning waits until you submit an import task in the web interface.
# See the "TiDB Lightning Web Interface" section for details.
server-mode = false

# Logging
level = "info"
file = "tidb-lightning.log"
max-size = 128 # MB
max-days = 28
max-backups = 14

# Controls whether to enable the diagnostic logs. The default value is false, that is, only the logs related to the import are output, and the logs of other dependent components are not output.
# When you set it to true, logs from both the import process and other dependent components are output, and GRPC debugging is enabled, which can be used for diagnosis.
# This parameter is introduced in v7.3.0.
enable-diagnose-logs = false
```
### TiDB Lightning (Task)
