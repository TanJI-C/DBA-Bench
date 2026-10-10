# Flow control and disk spill behaviors for tidb-server memory pressure

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-memory-usage.md`
- Source Title: `TiDB Memory Control`
- Source Heading Path: `TiDB Memory Control > Other memory control behaviors of tidb-server > Flow control | TiDB Memory Control > Other memory control behaviors of tidb-server > Disk spill`
- Source Line Ranges: `138-208`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `memory-control`, `flow-control`, `disk-spill`, `oom`, `query-memory-quota`, `temporary-storage`, `hashagg`, `hashjoin`, `sort`, `mergejoin`, `logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0024_48c6043c87`
- Source ID: `tidb-docs-8.1:configure-memory-usage.md#flow-control`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `107f7ef94bfade5082663ae82dbd0d66e82dcffea8b474568c216def0dc766d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-memory-usage#flow-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-memory-usage.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB memory pressure behavior involving flow control, disk spill, OOM quota messages, or the controlling variables and logs for Sort, MergeJoin, HashJoin, and HashAgg.
- Retrieval Keywords: tidb_enable_rate_limit_action, tidb_distsql_scan_concurrency, tidb_mem_quota_query, tidb_enable_tmp_storage_on_oom, tmp-storage-path, tmp-storage-quota, memory exceeds quota, destroy one token now, memory exceeds quota, spill to disk now, memory exceeds quota, set aggregate mode to spill-mode, Out Of Memory Quota, disk spill, flow control, HashAgg, HashJoin, MergeJoin, Sort, DISTINCT aggregate function, explain analyze select /*+ HASH_AGG() */ count(*) from t t1 join t t2 join t t3 group by t1.a, t2.a, t3.a
- Follow-up Guidance: The content includes an example that sets `tidb_mem_quota_query`, runs `explain analyze` with `/*+ HASH_AGG() */`, shows an initial `ERROR 1105 (HY000): Out Of Memory Quota!`, and then shows a later execution plan with disk usage for `HashAgg`.
- Classification Note: This is classified as TiDB configuration content because it describes memory-control behaviors and the exact system variables, configuration parameters, operators, and log messages that govern flow control and disk spill in tidb-server.

## Official Source Content

### Flow control

- TiDB supports dynamic memory control for the operator that reads data. By default, this operator uses the maximum number of threads that [`tidb_distsql_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_distsql_scan_concurrency) allows to read data. When the memory usage of a single SQL execution exceeds [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) each time, the operator that reads data stops one thread.

- This flow control behavior is controlled by the system variable [`tidb_enable_rate_limit_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_rate_limit_action).
- When the flow control behavior is triggered, TiDB outputs a log containing the keywords `memory exceeds quota, destroy one token now`.
### Disk spill

TiDB supports disk spill for execution operators. When the memory usage of a SQL execution exceeds the memory quota, tidb-server can spill the intermediate data of execution operators to the disk to relieve memory pressure. Operators supporting disk spill include Sort, MergeJoin, HashJoin, and HashAgg.

- The disk spill behavior is jointly controlled by the following parameters: [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), [`tidb_enable_tmp_storage_on_oom`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tmp_storage_on_oom), [`tmp-storage-path`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tmp-storage-path), and [`tmp-storage-quota`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tmp-storage-quota).
- When the disk spill is triggered, TiDB outputs a log containing the keywords `memory exceeds quota, spill to disk now` or `memory exceeds quota, set aggregate mode to spill-mode`.
- Disk spill for the Sort, MergeJoin, and HashJoin operators is introduced in v4.0.0; disk spill for the non-parallel algorithm of the HashAgg operator is introduced in v5.2.0; disk spill for the parallel algorithm of the HashAgg operator is introduced in v8.0.0.
- When the SQL executions containing Sort, MergeJoin, HashJoin, or HashAgg cause OOM, TiDB triggers disk spill by default. 

> **Note:**
>
> The disk spill for HashAgg does not support SQL executions containing the `DISTINCT` aggregate function. When a SQL execution containing a `DISTINCT` aggregate function uses too much memory, the disk spill does not apply.

The following example uses a memory-consuming SQL statement to demonstrate the disk spill feature for HashAgg:

1. Configure the memory quota of a SQL statement to 1GB (1 GB by default):

    ```sql
    SET tidb_mem_quota_query = 1 << 30;
    ```

2. Create a single table `CREATE TABLE t(a int);` and insert 256 rows of different data.

3. Execute the following SQL statement:

    ```sql
    [tidb]> explain analyze select /*+ HASH_AGG() */ count(*) from t t1 join t t2 join t t3 group by t1.a, t2.a, t3.a;
    ```

    Because executing this SQL statement occupies too much memory, the following "Out of Memory Quota" error message is returned:

    ```sql
    ERROR 1105 (HY000): Out Of Memory Quota![conn_id=3]
    ```

4. Execute the same SQL statement. You can find that this time, the statement is successfully executed and no error message is returned. From the following detailed execution plan, you can see that HashAgg has used 600 MB of hard disk space.

    ```sql
    [tidb]> explain analyze select /*+ HASH_AGG() */ count(*) from t t1 join t t2 join t t3 group by t1.a, t2.a, t3.a;
    ```

    ```sql
    +---------------------------------+-------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+-----------+----------+
    | id                              | estRows     | actRows  | task      | access object | execution info                                                                                                                                                      | operator info                                                   | memory    | disk     |
    +---------------------------------+-------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+-----------+----------+
    | HashAgg_11                      | 204.80      | 16777216 | root      |               | time:1m37.4s, loops:16385                                                                                                                                           | group by:test.t.a, test.t.a, test.t.a, funcs:count(1)->Column#7 | 1.13 GB   | 600.0 MB |
    | └─HashJoin_12                   | 16777216.00 | 16777216 | root      |               | time:21.5s, loops:16385, build_hash_table:{total:267.2µs, fetch:228.9µs, build:38.2µs}, probe:{concurrency:1, total:35s, max:35s, probe:35s, fetch:962.2µs}         | CARTESIAN inner join                                            | 8.23 KB   | 4 KB     |
    |   ├─TableReader_21(Build)       | 256.00      | 256      | root      |               | time:87.2µs, loops:2, cop_task: {num: 1, max: 150µs, proc_keys: 0, rpc_num: 1, rpc_time: 145.1µs, copr_cache_hit_ratio: 0.00}                                       | data:TableFullScan_20                                           | 885 Bytes | N/A      |
    |   │ └─TableFullScan_20          | 256.00      | 256      | cop[tikv] | table:t3      | tikv_task:{time:23.2µs, loops:256}                                                                                                                                  | keep order:false, stats:pseudo                                  | N/A       | N/A      |
    |   └─HashJoin_14(Probe)          | 65536.00    | 65536    | root      |               | time:728.1µs, loops:65, build_hash_table:{total:307.5µs, fetch:277.6µs, build:29.9µs}, probe:{concurrency:1, total:34.3s, max:34.3s, probe:34.3s, fetch:278µs}      | CARTESIAN inner join                                            | 8.23 KB   | 4 KB     |
    |     ├─TableReader_19(Build)     | 256.00      | 256      | root      |               | time:126.2µs, loops:2, cop_task: {num: 1, max: 308.4µs, proc_keys: 0, rpc_num: 1, rpc_time: 295.3µs, copr_cache_hit_ratio: 0.00}                                    | data:TableFullScan_18                                           | 885 Bytes | N/A      |
    |     │ └─TableFullScan_18        | 256.00      | 256      | cop[tikv] | table:t2      | tikv_task:{time:79.2µs, loops:256}                                                                                                                                  | keep order:false, stats:pseudo                                  | N/A       | N/A      |
    |     └─TableReader_17(Probe)     | 256.00      | 256      | root      |               | time:211.1µs, loops:2, cop_task: {num: 1, max: 295.5µs, proc_keys: 0, rpc_num: 1, rpc_time: 279.7µs, copr_cache_hit_ratio: 0.00}                                    | data:TableFullScan_16                                           | 885 Bytes | N/A      |
    |       └─TableFullScan_16        | 256.00      | 256      | cop[tikv] | table:t1      | tikv_task:{time:71.4µs, loops:256}                                                                                                                                  | keep order:false, stats:pseudo                                  | N/A       | N/A      |
    +---------------------------------+-------------+----------+-----------+---------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------+-----------------------------------------------------------------+-----------+----------+
    9 rows in set (1 min 37.428 sec)
    ```
