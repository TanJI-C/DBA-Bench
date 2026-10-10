# Query-only test results and conclusion for batch size 4096

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/online-workloads-and-add-index-operations.md`
- Source Title: `Interaction Test on Online Workloads and `ADD INDEX` Operations`
- Source Heading Path: `Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 2: Do not perform write operations to the target column of the `ADD INDEX` statement (query-only) > Test results > `tidb_ddl_reorg_batch_size = 4096` | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 2: Do not perform write operations to the target column of the `ADD INDEX` statement (query-only) > Test conclusion`
- Source Line Ranges: `265-282`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `add-index`, `ddl`, `sysbench`, `query-only`, `reorg-batch-size`, `worker-count`, `throughput`, `latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0036_c5f1ecd5df`
- Source ID: `tidb-docs-8.1:benchmark/online-workloads-and-add-index-operations.md#tidb-ddl-reorg-batch-size-4096`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e495c4aa4bc4e928dfa915f5c3fb57e121ecc1de778053ef6482181ae006d44`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/online-workloads-and-add-index-operations#tidb-ddl-reorg-batch-size-4096
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/online-workloads-and-add-index-operations.md

## Retrieval Guidance

- Use When: Use this chunk when comparing query-only online workload behavior during `ADD INDEX` with `tidb_ddl_reorg_batch_size = 4096` across different `tidb_ddl_reorg_worker_cnt` values.
- Retrieval Keywords: ADD INDEX, query-only, tidb_ddl_reorg_batch_size = 4096, tidb_ddl_reorg_worker_cnt, add_index_durations(s), sysbench TPS, sysbench QPS, target column of the ADD INDEX statement, effect of ADD INDEX operations on online workloads is not obvious
- Follow-up Guidance: The test conclusion states that when you only perform query operations to the target column of the `ADD INDEX` statement, the effect of `ADD INDEX` operations on online workloads is not obvious.
- Classification Note: This is classified as performance content because it reports benchmark results for `ADD INDEX` using Sysbench throughput, latency-related duration, and DDL reorganization settings in TiDB.

## Official Source Content

#### `tidb_ddl_reorg_batch_size = 4096`

| tidb_ddl_reorg_worker_cnt |  add_index_durations(s) | sysbench TPS   | sysbench QPS |
| :------------------------ | :---------------------- | :------------- | :----------- |
| 1     | 103 |  502.2 |           7823 |
| 2     | 63 |  486.5 |           7672 |
| 4     | 52 |  467.4 |            7516 |
| 8     | 39 |  452.5 |           7302 |
| 16    | 35 |   447.2 |           7206 |
| 32    | 30 |   441.9 |           7057 |
| 48    | 30 |   440.1 |           7004 |

![add-index-load-2-b4096](/media/add-index-load-2-b4096.png)
### Test conclusion

When you only perform query operations to the target column of the `ADD INDEX` statement, the effect of `ADD INDEX` operations on online workloads is not obvious.
