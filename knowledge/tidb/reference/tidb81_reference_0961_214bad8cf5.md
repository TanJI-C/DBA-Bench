# tiproxyctl commands for config and health

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-command-line-flags.md`
- Source Title: `TiProxy Command-Line Flags`
- Source Heading Path: `TiProxy Command-Line Flags > TiProxy Control > Commands | TiProxy Command-Line Flags > TiProxy Control > Commands > `config set` | TiProxy Command-Line Flags > TiProxy Control > Commands > `config get` | TiProxy Command-Line Flags > TiProxy Control > Commands > `health``
- Source Line Ranges: `86-116`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: none
- Topic Tags: `tiproxyctl`, `config-set`, `config-get`, `health-check`, `toml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0961_214bad8cf5`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-command-line-flags.md#commands`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `21f71e835148f1e8897674a3936d1e39829c2efc2d6448913f8b05f23f38a797`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-command-line-flags#commands
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-command-line-flags.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to use `tiproxyctl` commands to read or update TiProxy configuration in TOML format or to check health and configuration checksum.
- Retrieval Keywords: tiproxyctl config set, tiproxyctl config get, tiproxyctl health, TOML-formatted configuration file from standard input, log.level='warning', config_checksum, health status of TiProxy
- Follow-up Guidance: The source shows that `config set` reads TOML from standard input, `config get` returns the current configuration in TOML format, and `health` can return a JSON object such as `{"config_checksum":3006078629}` or an error when TiProxy is shutting down or offline.
- Classification Note: This is reference content because it documents the `tiproxyctl` commands `config set`, `config get`, and `health`, along with their exact behavior and example output.

## Official Source Content

### Commands
#### `config set`

The `tiproxyctl config set` command reads a TOML-formatted configuration file from standard input and sets these configuration items to TiProxy. Unspecified configuration items will remain unchanged, so you only need to specify the items that you want to modify.

The following example sets `log.level` as `'warning'`, while leaving other configuration items unchanged.

```bash
$ cat test.toml
[log]
level='warning'
$ cat test.toml | tiproxyctl config set
""
$ tiproxyctl config get | grep level
level = 'warning'
```
#### `config get`

The `tiproxyctl config get` command is used to get the current TiProxy configuration in TOML format.
#### `health`

The `tiproxyctl health` command is used to get the health status of TiProxy and the checksum of the configuration. When TiProxy is running normally, it returns the checksum of the configuration. When TiProxy is shutting down or offline, it returns an error.

Example output:

```json
{"config_checksum":3006078629}
```
