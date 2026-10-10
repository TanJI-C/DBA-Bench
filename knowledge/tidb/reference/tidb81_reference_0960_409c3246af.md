# tiproxyctl syntax and global options

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-command-line-flags.md`
- Source Title: `TiProxy Command-Line Flags`
- Source Heading Path: `TiProxy Command-Line Flags > TiProxy Control | TiProxy Command-Line Flags > TiProxy Control > Syntax | TiProxy Command-Line Flags > TiProxy Control > Options | TiProxy Command-Line Flags > TiProxy Control > Options > `--log_encoder` | TiProxy Command-Line Flags > TiProxy Control > Options > `--log_level` | TiProxy Command-Line Flags > TiProxy Control > Options > `--curls` | TiProxy Command-Line Flags > TiProxy Control > Options > `-k, --insecure` | TiProxy Command-Line Flags > TiProxy Control > Options > `--ca` | TiProxy Command-Line Flags > TiProxy Control > Options > `--cert``
- Source Line Ranges: `21-85`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: none
- Topic Tags: `tiproxyctl`, `syntax`, `logging`, `server-addresses`, `tls`, `certificate`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0960_409c3246af`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-command-line-flags.md#tiproxy-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `789ab71431fa52536fd0245298233519974646bf192063e13495885fd8b73804`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-command-line-flags#tiproxy-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-command-line-flags.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for `tiproxyctl` command syntax or its global flags for logging, server addresses, and TLS-related connection options.
- Retrieval Keywords: tiproxyctl [flags] [command], tiproxyctl syntax, --log_encoder, --log_level, --curls, -k --insecure, --ca, --cert, localhost:3080, Server API gateway addresses
- Follow-up Guidance: The source includes the example `tiproxyctl --curls 127.0.0.1:3080 config get` and states that TiProxy Control is designed for debugging purposes.
- Classification Note: This is reference content because it lists `tiproxyctl` syntax and option definitions, including defaults, types, and supported values.

## Official Source Content

## TiProxy Control

This section introduces the syntax, options, and commands of the client program `tiproxyctl`.

> **Note:**
>
> TiProxy Control is specifically designed for debugging purposes and might not be fully compatible with future capabilities introduced in TiProxy. It's not recommended to include this tool in application or utility development to get information.
### Syntax

```
tiproxyctl [flags] [command]
```

For example:

```
tiproxyctl --curls 127.0.0.1:3080 config get
```
### Options
#### `--log_encoder`

+ Specifies the log format of `tiproxyctl`.
+ Type: `string`
+ Default: `"tidb"`
+ It defaults to the same log format of TiDB. However, you can also specify it as one of the following:

    - `console`: a more human-readable format
    - `json`: a structured log format
#### `--log_level`

+ Specifies the log level of tiproxyctl.
+ Type: `string`
+ Default: `"warn"`
+ You can specify `debug`, `info`, `warn`, `error`, `panic`.
#### `--curls`

+ Specifies the server addresses. You can add multiple listening addresses.
+ Type: `comma separated lists of ip:port`
+ Default: `localhost:3080`
+ Server API gateway addresses.
#### `-k, --insecure`

+ Specifies whether to skip TLS CA verification when dialing to the server.
+ Type: `boolean`
+ Default: `false`
+ Used for testing.
#### `--ca`

+ Specifies the CA when dialing to the server.
+ Type: `string`
+ Default: `""`
#### `--cert`

+ Specifies the certificate when dialing to the server.
+ Type: `string`
+ Default: `""`
