# TiProxy server startup flag --config

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-command-line-flags.md`
- Source Title: `TiProxy Command-Line Flags`
- Source Heading Path: `TiProxy Command-Line Flags | TiProxy Command-Line Flags > TiProxy Server | TiProxy Command-Line Flags > TiProxy Server > `--config``
- Source Line Ranges: `5-20`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: `operator`, `tiup`
- Topic Tags: `command-line-flags`, `server-startup`, `configuration-file`, `config-reload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0959_da78c9430b`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-command-line-flags.md#tiproxy-command-line-flags`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f98a5e6dc2d8529e480bab6d86a19259602eeab59855362ad1109d7ec8a67ae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-command-line-flags#tiproxy-command-line-flags
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-command-line-flags.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about the TiProxy server startup flag for specifying the configuration file path or how configuration reload relates to the `--config` file.
- Retrieval Keywords: tiproxy --config, TiProxy configuration file path, server startup flag --config, TiProxy automatically reloads configuration, tiup cluster edit-config, kubectl edit tc, Configure TiProxy
- Follow-up Guidance: The source notes that TiProxy automatically reloads the configuration when the configuration file is modified and mentions `tiup cluster edit-config` and `kubectl edit tc` for modifying configuration.
- Classification Note: This is reference content because it defines the `tiproxy` server flag `--config`, including its type, default value, and related configuration behavior.

## Official Source Content

# TiProxy Command-Line Flags

This document introduces the command-line flags that you can use when you launch TiProxy. It also introduces flags of `tiproxyctl`.
## TiProxy Server

This section lists the flags of the server program `tiproxy`.
### `--config`

+ Specifies the path of the TiProxy configuration file.
+ Type: `string`
+ Default: `""`
+ You must specify the configuration file. For detailed configuration items, refer to [Configure TiProxy](https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-configuration). Note that TiProxy automatically reloads the configuration when the configuration file is modified. Therefore, do not directly modify the configuration file. It is recommended to modify the configuration by executing [`tiup cluster edit-config`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-edit-config) or [`kubectl edit tc`](https://docs.pingcap.com/tidb-in-kubernetes/stable/modify-tidb-configuration).
