# EXPLAIN ANALYZE operator execution information

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain-analyze.md`
- Source Title: `EXPLAIN ANALYZE | TiDB SQL Statement Reference`
- Source Heading Path: `EXPLAIN ANALYZE > Execution information of operators | EXPLAIN ANALYZE > Execution information of operators > Point_Get | EXPLAIN ANALYZE > Execution information of operators > Batch_Point_Get | EXPLAIN ANALYZE > Execution information of operators > TableReader`
- Source Line Ranges: `99-132`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `execution info`, `operators`, `point get`, `batch point get`, `tablereader`, `rpc`, `backoff`, `cop task`, `coprocessor cache`, `lock resolution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0068_5f0eb3a95e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain-analyze.md#execution-information-of-operators`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `990593e5fde1c253d63dfffe09d087e1e50f6dc285699d87fe43bac3dad054f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze#execution-information-of-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain-analyze.md

## Retrieval Guidance

- Use When: Use this chunk when you need to interpret operator-specific execution info in EXPLAIN ANALYZE output for Point_Get, Batch_Point_Get, or TableReader operators.
- Retrieval Keywords: Execution information of operators, Point_Get, Batch_Point_Get, TableReader, Get:{num_rpc:1, total_time:697.051µs}, ResolveLock:{num_rpc:1, total_time:12.117495ms}, regionMiss_backoff, tikvRPC_backoff, BatchGet:{num_rpc:2, total_time:83.13µs}, cop_task, rpc_info, Cop:{num_rpc:6, total_time:5.313996ms}, copr_cache_hit_ratio, max_proc_keys, p95_proc_keys, backoff, read-write conflict
- Follow-up Guidance: If the difference between max_proc_keys and p95_proc_keys is large, the content says the data distribution might be imbalanced.
- Classification Note: This is diagnosis content because it explains how to read operator runtime details, RPC timing, backoff, lock resolution, and cop task statistics in EXPLAIN ANALYZE output.

## Official Source Content

## Execution information of operators

In addition to the basic `time` and `loop` execution information, `execution info` also contains operator-specific execution information, which mainly includes the time consumed for the operator to send RPC requests and the duration of other steps.
### Point_Get

The execution information from a `Point_Get` operator will typically contain the following information:

- `Get:{num_rpc:1, total_time:697.051µs}`: The number of the `Get` RPC requests (`num_rpc`) sent to TiKV and the total duration (`total_time`) of all RPC requests.
- `ResolveLock:{num_rpc:1, total_time:12.117495ms}`: If TiDB encounters a lock when reading data, it has to resolve the lock first, which generally occurs in the scenario of read-write conflict. This information indicates the duration of resolving locks.
- `regionMiss_backoff:{num:11, total_time:2010 ms},tikvRPC_backoff:{num:11, total_time:10691 ms}`: When an RPC request fails, TiDB will wait the backoff time before retrying the request. Backoff statistics include the type of backoff (such as `regionMiss` and `tikvRPC`), the total waiting time (`total_time`), and the total number of backoffs (`num`).
### Batch_Point_Get

The execution information of the `Batch_Point_Get` operator is similar to that of the `Point_Get` operator, but `Batch_Point_Get` generally sends `BatchGet` RPC requests to TiKV to read data.

`BatchGet:{num_rpc:2, total_time:83.13µs}`: The number of RPC requests (`num_rpc`) of the `BatchGet` type sent to TiKV and the total time consumed (`total_time`) for all RPC requests.
### TableReader

The execution information of a `TableReader` operator is typically as follows:

```
cop_task: {num: 6, max: 1.07587ms, min: 844.312µs, avg: 919.601µs, p95: 1.07587ms, max_proc_keys: 16, p95_proc_keys: 16, tot_proc: 1ms, tot_wait: 1ms, copr_cache_hit_ratio: 0.00}, rpc_info:{Cop:{num_rpc:6, total_time:5.313996ms}}
```

- `cop_task`: Contains the execution information of `cop` tasks. For example:
    - `num`: The number of cop tasks.
    - `max`, `min`, `avg`, `p95`: The maximum, minimum, average, and P95 values of the execution time consumed for executing cop tasks.
    - `max_proc_keys` and `p95_proc_keys`: The maximum and P95 key-values scanned by TiKV in all cop tasks. If the difference between the maximum value and the P95 value is large, the data distribution might be imbalanced.
    - `copr_cache_hit_ratio`: The hit rate of Coprocessor Cache for `cop` task requests.
- `rpc_info`: The total number and total time of RPC requests sent to TiKV aggregated by request type.
- `backoff`: Contains different types of backoff and the total waiting time of backoff.
