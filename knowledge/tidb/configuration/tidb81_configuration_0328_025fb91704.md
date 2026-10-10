# Proxy protocol fallback and experimental expression index settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > proxy-protocol > `fallbackable` <span class="version-mark">New in v6.5.1</span> | TiDB Configuration File > experimental | TiDB Configuration File > experimental > `allow-expression-index` <span class="version-mark">New in v4.0.0</span>`
- Source Line Ranges: `1054-1066`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `proxy protocol`, `client connections`, `fallback mode`, `experimental features`, `expression index`, `version dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0328_025fb91704`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#fallbackable-span-class-version-mark-new-in-v6-5-1-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `82eec9f7639e91e7805a0cc2f5e01192ff621b2f8a86f739d2d4fb5cb333dc69`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#fallbackable-span-class-version-mark-new-in-v6-5-1-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the `proxy-protocol.fallbackable` setting or the `experimental.allow-expression-index` setting, including default behavior, fallback mode, and safe-function limits for expression indexes.
- Retrieval Keywords: proxy-protocol.fallbackable, PROXY protocol fallback mode, proxy-protocol.networks, PROXY protocol header, experimental.allow-expression-index, allow-expression-index, expression index, tidb_allow_function_for_expression_index, safe function, New in v6.5.1, New in v4.0.0
- Follow-up Guidance: The content also states that querying the `tidb_allow_function_for_expression_index` variable shows which functions are safe to be directly used for creating an expression.
- Classification Note: This chunk is classified as TiDB configuration because it defines configuration items in the TiDB configuration file for PROXY protocol fallback behavior and an experimental expression index feature.

## Official Source Content

### `fallbackable` New in v6.5.1

+ Controls whether to enable the PROXY protocol fallback mode. If this configuration item is set to `true`, TiDB can accept clients that belong to `proxy-protocol.networks` to connect to TiDB without using the PROXY protocol specification or without sending the PROXY protocol header. By default, TiDB only accepts client connections that belong to `proxy-protocol.networks` and send a PROXY protocol header.
+ Default value: `false`
## experimental

The `experimental` section, introduced in v3.1.0, describes the configurations related to the experimental features of TiDB.
### `allow-expression-index` New in v4.0.0

+ Controls whether an expression index can be created. Since TiDB v5.2.0, if the function in an expression is safe, you can create an expression index directly based on this function without enabling this configuration. If you want to create an expression index based on other functions, you can enable this configuration, but correctness issues might exist. By querying the `tidb_allow_function_for_expression_index` variable, you can get the functions that are safe to be directly used for creating an expression.
+ Default value: `false`
