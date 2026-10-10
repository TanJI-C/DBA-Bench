# Repair, bootstrap collation, and connection limit settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > `repair-mode` | TiDB Configuration File > `repair-table-list` | TiDB Configuration File > `new_collations_enabled_on_first_bootstrap` | TiDB Configuration File > `max-server-connections``
- Source Line Ranges: `130-154`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `repair-mode`, `table-repair`, `bootstrap`, `collation`, `connection-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0316_46d2247a0a`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#repair-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4f7ab5e876494a214a2fd64b534eb0187ad458491333f5e9ade68561db58e82d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#repair-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB configuration file information about untrusted repair mode, the `repair-table-list`, bootstrap-only collation initialization, or the maximum number of concurrent client connections.
- Retrieval Keywords: repair-mode, repair-table-list, untrusted repair mode, bad tables cannot be loaded, new_collations_enabled_on_first_bootstrap, new collation support, first initialized, max-server-connections, maximum number of concurrent client connections, instance.max_connections, max_connections
- Follow-up Guidance: The source notes that `repair-table-list` is valid only when `repair-mode` is `true`, and that `instance.max_connections` or the `max_connections` system variable takes precedence when both are set with `max-server-connections`.
- Classification Note: This is classified as TiDB self-managed configuration because the content defines `config.toml` options for repair behavior, initial collation bootstrap, and connection limits, including defaults and precedence rules.

## Official Source Content

### `repair-mode`

- Determines whether to enable the untrusted repair mode. When the `repair-mode` is set to `true`, bad tables in the `repair-table-list` cannot be loaded.
- Default value: `false`
- The `repair` syntax is not supported by default. This means that all tables are loaded when TiDB is started.
### `repair-table-list`

- `repair-table-list` is only valid when [`repair-mode`](#repair-mode) is set to `true`. `repair-table-list` is a list of bad tables that need to be repaired in an instance. An example of the list is: ["db.table1","db.table2"...].
- Default value: []
- The list is empty by default. This means that there are no bad tables that need to be repaired.
### `new_collations_enabled_on_first_bootstrap`

- Enables or disables the new collation support.
- Default value: `true`
- Note: This configuration takes effect only for the TiDB cluster that is first initialized. After the initialization, you cannot use this configuration item to enable or disable the new collation support.
### `max-server-connections`

- The maximum number of concurrent client connections allowed in TiDB. It is used to control resources.
- Default value: `0`
- By default, TiDB does not set limit on the number of concurrent client connections. When the value of this configuration item is greater than `0` and the number of actual client connections reaches this value, the TiDB server rejects new client connections.
- Since v6.2.0, the TiDB configuration item [`instance.max_connections`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#max_connections) or the system variable [`max_connections`](https://docs.pingcap.com/tidb/stable/system-variables#max_connections) is used to set the maximum number of concurrent client connections allowed in TiDB. `max-server-connections` still takes effect. But if `max-server-connections` and `instance.max_connections` are set at the same time, the latter takes effect.
