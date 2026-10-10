# Performance resource and transaction limit settings

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > performance | TiDB Configuration File > performance > `max-procs` | TiDB Configuration File > performance > `server-memory-quota` <span class="version-mark">New in v4.0.9</span> | TiDB Configuration File > performance > `max-txn-ttl` | TiDB Configuration File > performance > `stmt-count-limit``
- Source Line Ranges: `488-520`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `cpu`, `memory`, `transactions`, `locks`, `ttl`, `statement-limit`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0235_5bce90643c`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1de7cfd6c8fa223d7d98678049c9de20d1471b7b906378ef56c05ad953501545`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB performance configuration for CPU usage, server memory quota, maximum transaction lock TTL, or the statement count limit in a single transaction.
- Retrieval Keywords: performance, max-procs, server-memory-quota, tidb_server_memory_limit, max-txn-ttl, stmt-count-limit, statement count 5001 exceeds the transaction limitation, autocommit = false, retryable optimistic transaction, pessimistic transaction, transaction retry, bulk DML mode, tidb_dml_type
- Follow-up Guidance: The content states that `server-memory-quota` is deprecated in favor of `tidb_server_memory_limit`, and that `stmt-count-limit` applies only to retryable optimistic transactions.
- Classification Note: This is classified as performance content because it defines TiDB resource and transaction limit configuration items affecting CPU usage, memory limits, lock holding time, and statement count per transaction.

## Official Source Content

## performance

Configuration items related to performance.
### `max-procs`

- The number of CPUs used by TiDB.
- Default value: `0`
- The default `0` indicates using all the CPUs on the machine. You can also set it to n, and then TiDB uses n CPUs.
### `server-memory-quota` New in v4.0.9

> **Warning:**
>
> Since v6.5.0, the `server-memory-quota` configuration item is deprecated and replaced by the system variable [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640).

+ The memory usage limit of tidb-server instances.
+ Default value: `0` (in bytes), which means no memory limit.
### `max-txn-ttl`

- The longest time that a single transaction can hold locks. If this time is exceeded, the locks of a transaction might be cleared by other transactions so that this transaction cannot be successfully committed.
- Default value: `3600000`
- Unit: Millisecond
- The transaction that holds locks longer than this time can only be committed or rolled back. The commit might not be successful.
- For transactions executed using the [`"bulk"` DML mode](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800), the maximum TTL can exceed the limit of this configuration item. The maximum value is the greater value between this configuration item and 24 hours.
### `stmt-count-limit`

- The maximum number of statements allowed in a single TiDB transaction.
- Default value: `5000`
- If a transaction does not roll back or commit after the number of statements exceeds `stmt-count-limit`, TiDB returns the `statement count 5001 exceeds the transaction limitation, autocommit = false` error. This configuration takes effect **only** in the retryable optimistic transaction. If you use the pessimistic transaction or have disabled the transaction retry, the number of statements in a transaction is not limited by this configuration.
