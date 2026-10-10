# Transaction size limits and version-dependent behavior

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > performance > `txn-entry-size-limit` <span class="version-mark">New in v4.0.10 and v5.0.0</span> | TiDB Configuration File > performance > `txn-total-size-limit``
- Source Line Ranges: `521-540`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `transaction-size`, `row-size`, `memory-quota`, `binlog`, `kafka`, `upgrade-behavior`, `dynamic-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0320_9058ce9d54`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#txn-entry-size-limit-span-class-version-mark-new-in-v4-0-10-and-v5-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e67d23977418afd625cdb4d9067e3c1051ed16f8dc09b23d77f679c68dfa8c8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-span-class-version-mark-new-in-v4-0-10-and-v5-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB transaction or row size limits, including the `entry too large` error, `txn-entry-size-limit`, `txn-total-size-limit`, or upgrade behavior after v6.5.0.
- Retrieval Keywords: txn-entry-size-limit, txn-total-size-limit, entry too large, tidb_txn_entry_size_limit, raft-entry-max-size, max_allowed_packet, tidb_mem_quota_query, tidb_dml_type, bulk mode, single row size limit, single transaction size limit, Kafka 1 GB message size, binlog downstream consumer Kafka
- Follow-up Guidance: It also points to related limits and controls including `raft-entry-max-size`, `max_allowed_packet`, `tidb_mem_quota_query`, and `tidb_dml_type` `"bulk"` mode.
- Classification Note: This is classified as configuration content because it defines TiDB performance configuration items, their defaults, limits, related errors, and version-dependent behavior.

## Official Source Content

### `txn-entry-size-limit` New in v4.0.10 and v5.0.0

- The size limit of a single row of data in TiDB.
- Default value: `6291456` (in bytes)
- The size limit of a single key-value record in a transaction. If the size limit is exceeded, TiDB returns the `entry too large` error. The maximum value of this configuration item does not exceed `125829120` (120 MB).
- Starting from v7.6.0, you can use the system variable [`tidb_txn_entry_size_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_entry_size_limit-new-in-v760) to dynamically modify the value of this configuration item.
- Note that TiKV has a similar limit. If the data size of a single write request exceeds [`raft-entry-max-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-entry-max-size), which is 8 MB by default, TiKV refuses to process this request. When a table has a row of large size, you need to modify both configurations at the same time.
- The default value of [`max_allowed_packet`](https://docs.pingcap.com/tidb/stable/system-variables#max_allowed_packet-new-in-v610) (the maximum size of a packet for the MySQL protocol) is 67108864 (64 MiB). If a row is larger than `max_allowed_packet`, the row gets truncated.
- The default value of [`txn-total-size-limit`](#txn-total-size-limit) (the size limit of a single transaction in TiDB) is 100 MiB. If you increase the `txn-entry-size-limit` value to be over 100 MiB, you need to increase the `txn-total-size-limit` value accordingly.
### `txn-total-size-limit`

- The size limit of a single transaction in TiDB.
- Default value: `104857600` (in bytes)
- In a single transaction, the total size of key-value records cannot exceed this value. The maximum value of this parameter is `1099511627776` (1 TB). Note that if you have used the binlog to serve the downstream consumer Kafka, the value of this parameter must be no more than `1073741824` (1 GB). This is because 1 GB is the upper limit of a single message size that Kafka can process. Otherwise, an error is returned if this limit is exceeded.
- In TiDB v6.5.0 and later versions, this configuration is no longer recommended. The memory size of a transaction will be accumulated into the memory usage of the session, and the [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) variable will take effect when the session memory threshold is exceeded. To be compatible with previous versions, this configuration works as follows when you upgrade from an earlier version to TiDB v6.5.0 or later:
    - If this configuration is not set or is set to the default value (`104857600`), after an upgrade, the memory size of a transaction will be accumulated into the memory usage of the session, and the `tidb_mem_quota_query` variable will take effect.
    - If this configuration is not defaulted (`104857600`), it still takes effect and its behavior on controlling the size of a single transaction remains unchanged before and after the upgrade. This means that the memory size of the transaction is not controlled by the `tidb_mem_quota_query` variable.
- When TiDB executes transactions in the [`tidb_dml_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) `"bulk"` mode, transaction size is not limited by the TiDB configuration item [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit).
