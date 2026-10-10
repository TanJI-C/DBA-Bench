# tidb-lightning command line flags and config precedence

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-command-line-full.md`
- Source Title: `TiDB Lightning Command Line Flags`
- Source Heading Path: `TiDB Lightning Command Line Flags | TiDB Lightning Command Line Flags > Command line flags | TiDB Lightning Command Line Flags > Command line flags > `tidb-lightning``
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tidb`, `tikv`, `shared`
- Topic Tags: `command-line-flags`, `configuration`, `import-mode`, `tls`, `checkpoint`, `analyze`, `checksum`, `logging`, `pd-addresses`, `server-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0935_b8974cc9ee`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-command-line-full.md#tidb-lightning-command-line-flags`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6abc3bab890479e3ce481f71cad7efab91d7208ccd904ea70ef824c8488bcc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-command-line-full#tidb-lightning-command-line-flags
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-command-line-full.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB Lightning command line flags, their corresponding configuration items, or the rule that command line parameters override configuration file settings.
- Retrieval Keywords: tidb-lightning, --config <file>, configuration file precedence, command line parameter takes precedence, -d <directory>, mydumper.data-source-dir, -L <level>, lightning.level, -f <rule>, mydumper.filter, --backend <backend>, physical import mode, logical import mode, tikv-importer.backend, --log-file <file>, --status-addr <ip:port>, --pd-urls <host1:port1,host2:port2,...,hostn:portn>, tidb.pd-addr, multiple PD addresses, --tidb-host <host>, --tidb-port <port>, --tidb-status <port>, --tidb-user <user>, --tidb-password <password>, Base64 encoded, --enable-checkpoint <bool>, checkpoint.enable, --analyze <level>, post-restore.analyze, --checksum <level>, post-restore.checksum, --check-requirements <bool>, lightning.check-requirements, --ca <file>, --cert <file>, --key <file>, TLS connection, security.ca-path, security.cert-path, security.key-path, --server-mode, lightning.server-mode, tiup tidb-lightning -L debug --config cfg.toml
- Follow-up Guidance: The source also states that if both a command line parameter and the corresponding setting in the configuration file are specified, the command line parameter takes precedence.
- Classification Note: This is reference content because it enumerates `tidb-lightning` flags, their meanings, and the exact corresponding configuration items.

## Official Source Content

# TiDB Lightning Command Line Flags

You can configure TiDB Lightning either using the configuration file or in command line. This document describes the command line flags of TiDB Lightning.
## Command line flags
### `tidb-lightning`

You can configure the following parameters using `tidb-lightning`:

| Parameter | Description | Corresponding configuration item |
| :---- | :---- | :---- |
| `--config <file>` | Read the global configuration from the file. If this parameter is not specified, TiDB Lightning uses the default configuration. | |
| `-V` | Print the program version. | |
| `-d <directory>` | Local directory or [external storage URI](https://docs.pingcap.com/tidb/stable/external-storage-uri) of data files. | `mydumper.data-source-dir` |
| `-L <level>` | Log level: `debug`, `info`, `warn`, `error`, or `fatal`. `info` by default.| `lightning.level` |
| `-f <rule>` | [Table filter rules](https://docs.pingcap.com/tidb/stable/table-filter). Can be specified multiple times. | `mydumper.filter` |
| `--backend <backend>` | Select an import mode. `local` refers to [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode); `tidb` refers to [logical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode). | `tikv-importer.backend` |
| `--log-file <file>` | Log file path. By default, it is `/tmp/lightning.log.{timestamp}`. If set to '-', it means that the log files will be output to stdout. | `lightning.log-file` |
| `--status-addr <ip:port>` | Listening address of the TiDB Lightning server | `lightning.status-port` |
| `--pd-urls <host1:port1,host2:port2,...,hostn:portn>` | PD endpoint address. Starting from v7.6.0, TiDB supports setting multiple PD addresses. | `tidb.pd-addr` |
| `--tidb-host <host>` | TiDB server host | `tidb.host` |
| `--tidb-port <port>` | TiDB server port (default = 4000) | `tidb.port` |
| `--tidb-status <port>` | TiDB status port (default = 10080) | `tidb.status-port` |
| `--tidb-user <user>` | User name to connect to TiDB | `tidb.user` |
| `--tidb-password <password>` | Password to connect to TiDB. The password can either be plaintext or Base64 encoded. | `tidb.password` |
| `--enable-checkpoint <bool>` | Whether to enable checkpoints (default = true) | `checkpoint.enable` |
| `--analyze <level>` | Analyze tables after importing. Available values are "required", "optional" (default value), and "off". | `post-restore.analyze` |
| `--checksum <level>` | Compare checksum after importing. Available values are "required" (default value), "optional", and "off". | `post-restore.checksum` |
| `--check-requirements <bool>` | Check cluster version compatibility before starting the task, and check whether TiKV has more than 10% free space left during running time. (default = true) | `lightning.check-requirements` |
| `--ca <file>` | CA certificate path for TLS connection | `security.ca-path` |
| `--cert <file>` | Certificate path for TLS connection | `security.cert-path` |
| `--key <file>` | Private key path for TLS connection | `security.key-path` |
| `--server-mode` | Start TiDB Lightning in server mode | `lightning.server-mode` |

If you specify both a command line parameter and the corresponding setting in the configuration file, the command line parameter takes precedence. For example, running `tiup tidb-lightning -L debug --config cfg.toml` would always set the log level to "debug" regardless of the content of `cfg.toml`.
