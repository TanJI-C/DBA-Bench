# TiDB startup, bootstrap, config, and logging flags

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/command-line-flags-for-tidb-configuration.md`
- Source Title: `Configuration Options`
- Source Heading Path: `Configuration Options | Configuration Options > `--advertise-address` | Configuration Options > `--config` | Configuration Options > `--config-check` | Configuration Options > `--config-strict` | Configuration Options > `--cors` | Configuration Options > `--enable-binlog` | Configuration Options > `--host` | Configuration Options > `--initialize-insecure` | Configuration Options > `--initialize-secure` | Configuration Options > `--initialize-sql-file` | Configuration Options > `-L` | Configuration Options > `--lease` | Configuration Options > `--log-file` | Configuration Options > `--log-general` | Configuration Options > `--log-slow-query``
- Source Line Ranges: `5-92`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `command-line-flags`, `startup`, `bootstrap`, `configuration-file`, `network-binding`, `cors`, `binlog`, `logging`, `schema-lease`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0059_e5e6e27e6f`
- Source ID: `tidb-docs-8.1:command-line-flags-for-tidb-configuration.md#configuration-options`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd507cf0d55a7c800740c60aca1b92543429060dc473d9ca4ca06467564c037b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/command-line-flags-for-tidb-configuration#configuration-options
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/command-line-flags-for-tidb-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB command-line flags for startup, bootstrap mode, configuration file validation, network binding, CORS, binlog generation, schema lease, or log output settings.
- Retrieval Keywords: --advertise-address, --config, --config-check, --config-strict, --cors, --enable-binlog, --host, --initialize-insecure, --initialize-secure, --initialize-sql-file, -L, --lease, --log-file, --log-general, --log-slow-query, default TiDB ports 4000 10080, Access-Control-Allow-Origin, General Log, schema lease
- Follow-up Guidance: The content states that command-line options overwrite corresponding settings in the configuration file when both are specified.
- Classification Note: This is reference content because it enumerates TiDB startup and logging command-line options with their defaults and exact meanings.

## Official Source Content

# Configuration Options

When you start the TiDB cluster, you can use command-line options or environment variables to configure it. This document introduces TiDB's command options. The default TiDB ports are `4000` for client requests and `10080` for status report.
## `--advertise-address`

- The IP address through which to log into the TiDB server
- Default: `""`
- This address must be accessible by the rest of the TiDB cluster and the user.
## `--config`

- The configuration file
- Default: `""`
- If you have specified the configuration file, TiDB reads the configuration file. If the corresponding configuration also exists in the command line options, TiDB uses the configuration in the command line options to overwrite that in the configuration file. For detailed configuration information, see [TiDB Configuration File Description](https://docs.pingcap.com/tidb/stable/tidb-configuration-file).
## `--config-check`

- Checks the validity of the configuration file and exits
- Default: `false`
## `--config-strict`

- Enforces the validity of the configuration file
- Default: `false`
## `--cors`

- Specifies the `Access-Control-Allow-Origin` value for Cross-Origin Request Sharing (CORS) request of the TiDB HTTP status service
- Default: `""`
## `--enable-binlog`

+ Enables or disables TiDB binlog generation
+ Default: `false`
## `--host`

- The host address that the TiDB server monitors
- Default: `"0.0.0.0"`
- The TiDB server monitors this address.
- The `"0.0.0.0"` address monitors all network cards by default. If you have multiple network cards, specify the network card that provides service, such as `192.168.100.113`.
## `--initialize-insecure`

- Bootstraps tidb-server in insecure mode
- Default: `true`
## `--initialize-secure`

- Bootstraps tidb-server in secure mode
- Default: `false`
## `--initialize-sql-file`

- The SQL script to be executed when the TiDB cluster is started for the first time. For details, see [configuration item `initialize-sql-file`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#initialize-sql-file-new-in-v660)
- Default: `""`
## `-L`

- The log level
- Default: `"info"`
- Optional values: `"debug"`, `"info"`, `"warn"`, `"error"`, `"fatal"`
## `--lease`

- The duration of the schema lease. It is **dangerous** to change the value unless you know what you do.
- Default: `45s`
## `--log-file`

- The log file
- Default: `""`
- If this option is not set, logs are output to "stderr". If this option is set, logs are output to the corresponding file.
## `--log-general`

+ The filename of the [General Log](https://docs.pingcap.com/tidb/stable/system-variables#tidb_general_log)
+ Default: `""`
+ If this option is not set, the general log is written to the file specified by [`--log-file`](#--log-file) by default.
## `--log-slow-query`

- The directory for the slow query log
- Default: `""`
- If this option is not set, logs are output to the file specified by `--log-file` by default.
