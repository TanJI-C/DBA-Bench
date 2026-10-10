# Irrelevant-column workload test plan, results, and summary

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/online-workloads-and-add-index-operations.md`
- Source Title: `Interaction Test on Online Workloads and `ADD INDEX` Operations`
- Source Heading Path: `Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads > Test results | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads > Test result of `oltp_read_write` without `ADD INDEX` operations | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads > Test result of `oltp_read_write` without `ADD INDEX` operations > `tidb_ddl_reorg_batch_size = 32` | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads > Test result of `oltp_read_write` without `ADD INDEX` operations > `tidb_ddl_reorg_batch_size = 1024` | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads > Test result of `oltp_read_write` without `ADD INDEX` operations > `tidb_ddl_reorg_batch_size = 4096` | Interaction Test on Online Workloads and `ADD INDEX` Operations > Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads > Test conclusion | Interaction Test on Online Workloads and `ADD INDEX` Operations > Summary`
- Source Line Ranges: `283-348`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `add-index`, `ddl`, `sysbench`, `read-write`, `reorg-batch-size`, `worker-count`, `throughput`, `benchmark-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0037_eafd990080`
- Source ID: `tidb-docs-8.1:benchmark/online-workloads-and-add-index-operations.md#test-plan-3-the-target-column-of-the-add-index-statement-is-irrelevant-to-online-workloads`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d8efd1b15f8ab9b62f2f0d1d7445f0e59a14fffa75fa05bdbb81609307678fa0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/online-workloads-and-add-index-operations#test-plan-3-the-target-column-of-the-add-index-statement-is-irrelevant-to-online-workloads
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/online-workloads-and-add-index-operations.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the test plan, benchmark tables, and summary for `ADD INDEX` while the target column is irrelevant to online workloads in `oltp_read_write` tests.
- Retrieval Keywords: Test plan 3, target column of the ADD INDEX statement is irrelevant to online workloads, oltp_read_write, alter table test add index pad_idx(pad), tidb_ddl_reorg_worker_cnt, tidb_ddl_reorg_batch_size, tidb_ddl_reorg_batch_size = 32, tidb_ddl_reorg_batch_size = 1024, tidb_ddl_reorg_batch_size = 4096, add_index_durations(s), sysbench TPS, sysbench QPS, Summary, frequent write operations, INSERT, DELETE, UPDATE, write conflicts, continuous retry attempts, 1/32 of the default value, tidb_ddl_reorg_worker_cnt = 4, tidb_ddl_reorg_batch_size = 256, default ADD INDEX configuration
- Follow-up Guidance: The summary says that when frequent write operations hit the target column, reducing the product of `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size` to 1/32 of the default value, such as `4` and `256`, gives better performance, while query-only or irrelevant-column workloads can use the default `ADD INDEX` configuration.
- Classification Note: This is classified as performance content because it provides benchmark procedures, result tables, and workload impact conclusions for `ADD INDEX` under different DDL reorganization parameter settings in TiDB.

## Official Source Content

## Test plan 3: The target column of the `ADD INDEX` statement is irrelevant to online workloads

1. Start the `oltp_read_write` test.
2. Perform at the same time with step 1: use `alter table test add index pad_idx(pad)` to add an index.
3. Perform at the end of step 2: when the index is added successfully, stop the `oltp_read_only` test.
4. Get the duration of `alter table ... add index` and the average TPS and QPS of Sysbench in this period.
5. Gradually increase the value of two parameters `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size`, and then repeat step 1-4.
### Test results
### Test result of `oltp_read_write` without `ADD INDEX` operations

| sysbench TPS | sysbench QPS    |
| :------- | :-------- |
| 350.31   | 6806 |
#### `tidb_ddl_reorg_batch_size = 32`

| tidb_ddl_reorg_worker_cnt |  add_index_durations(s) | sysbench TPS   | sysbench QPS |
| :------------------------ | :---------------------- | :------------- | :----------- |
| 1     | 372 |  350.4 |           6892 |
| 2     | 207 |  344.2 |           6700 |
| 4     | 140 |  343.1 |           6672 |
| 8     | 121 |  339.1 |           6579 |
| 16    | 76 |   340   |           6607 |
| 32    | 42 |   343.1 |           6695 |
| 48    | 42 |   333.4 |           6454 |

![add-index-load-3-b32](/media/add-index-load-3-b32.png)
#### `tidb_ddl_reorg_batch_size = 1024`

| tidb_ddl_reorg_worker_cnt |  add_index_durations(s) | sysbench TPS   | sysbench QPS |
| :------------------------ | :---------------------- | :------------- | :----------- |
| 1     | 94 |  352.4 |           6794 |
| 2     | 50 |  332 |           6493 |
| 4     | 45 |  330 |           6456 |
| 8     | 36 |  325.5 |           6324 |
| 16    | 32 |   312.5   |           6294 |
| 32    | 32 |   300.6 |           6017 |
| 48    | 31 |   279.5 |           5612 |

![add-index-load-3-b1024](/media/add-index-load-3-b1024.png)
#### `tidb_ddl_reorg_batch_size = 4096`

| tidb_ddl_reorg_worker_cnt |  add_index_durations(s) | sysbench TPS   | sysbench QPS |
| :------------------------ | :---------------------- | :------------- | :----------- |
| 1     | 116 |  325.5 |           6324 |
| 2     | 65 |  312.5 |           6290 |
| 4     | 50 |  300.6 |           6017 |
| 8     | 37 |  279.5 |           5612 |
| 16    | 34 |   250.4   |           5365 |
| 32    | 32 |   220.2 |           4924 |
| 48    | 33 |   214.8 |           4544 |

![add-index-load-3-b4096](/media/add-index-load-3-b4096.png)
### Test conclusion

When the target column of the `ADD INDEX` statement is irrelevant to online workloads, the effect of `ADD INDEX` operations on the workload is not obvious.
## Summary

- When you perform frequent write operations (including `INSERT`, `DELETE` and `UPDATE` operations) to the target column of the `ADD INDEX` statement, the default `ADD INDEX` configuration causes relatively frequent write conflicts, which has a great impact on online workloads. At the same time, the `ADD INDEX` operation takes a long time to complete due to continuous retry attempts. In this test, you can modify the product of `tidb_ddl_reorg_worker_cnt` and `tidb_ddl_reorg_batch_size` to 1/32 of the default value. For example, you can set `tidb_ddl_reorg_worker_cnt` to `4` and `tidb_ddl_reorg_batch_size` to `256` for better performance.
- When only performing query operations to the target column of the `ADD INDEX` statement or the target column is not directly related to online workloads, you can use the default `ADD INDEX` configuration.
