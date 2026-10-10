# Performance and stability features with transition to data migration

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > New features > Performance | TiDB 6.0.0 Release Notes > New features > Stability | TiDB 6.0.0 Release Notes > New features > Data migration`
- Source Line Ranges: `87-182`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `new-features`, `performance`, `stability`, `cached-tables`, `pessimistic-locking`, `read-committed`, `plan-cache`, `pushdown`, `hotspot-index`, `mpp`, `quota-limiter`, `compression`, `checksum`, `thread-utilization`, `data-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0286_5da5ce8c63`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a09e948bba4bd3f3f9ad5e219c02929155236b5c059970dcc40551d96d7484e8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.0.0 release-note content about new performance, stability, and data migration related features across TiDB, TiKV, and TiFlash.
- Retrieval Keywords: TiDB 6.0.0 Release Notes, cached tables, cache hotspot small tables, in-memory pessimistic locking, tidb_rc_read_check_ts, Read Committed isolation level, tidb_ignore_prepared_cache_close_stmt, COM_STMT_CLOSE, prepared plan cache, expressions pushed down, BIT data type, tidb_shard, hotspot index, unique secondary index, dynamic pruning mode, partitioned tables, TiFlash MPP, MPP engine, IS, IS NOT, REGEXP(), NOT REGEXP(), GREATEST, LEAST, DAYNAME, DAYOFMONTH, DAYOFWEEK, DAYOFYEAR, LAST_DAY, MONTHNAME, Anti Left Outer Semi Join, Left Outer Semi Join, elastic thread pool, baseline capturing, sql plan management, bindings, quota limiter, quota, profiles.default.dt_compression_method, profiles.default.dt_compression_level, zstd compression, Checksum, dttool migrate, asynchronous gRPC, Min-TSO scheduling
- Follow-up Guidance: The source points to user documents for cached tables, pessimistic transactions, Read Committed isolation, prepared plan cache, expression pushdown, tidb_shard, TiFlash MPP, TiFlash supported pushdown calculations, TiFlash configuration, SQL plan management baseline capturing, TiKV quota, TiFlash data validation, and TiFlash monitoring.
- Classification Note: The official content is classified as a release-note summary because it lists TiDB 6.0.0 new features under Performance and Stability, with a Data migration heading present but no further content in this chunk.

## Official Source Content

### Performance

- Cache hotspot small tables

    For user applications in scenarios where hotspot small tables are accessed, TiDB supports explicitly caching the hotspot tables in memory, which greatly improves the access performance, improves the throughput, and reduces access latency. This solution can effectively avoid introducing a third-party cache middleware, reduce the complexity of the architecture, and cut the cost of operation and maintenance. The solution is suitable for scenarios where small tables are frequently accessed but rarely updated, such as the configuration tables or exchange rate tables.

    [User document](https://docs.pingcap.com/tidb/stable/cached-tables), [#25293](https://github.com/pingcap/tidb/issues/25293)

- In-memory pessimistic locking

    Since TiDB v6.0.0, in-memory pessimistic locking is enabled by default. After enabling this feature, pessimistic transaction locks are managed in memory. This avoids persisting pessimistic locks and the Raft replication of the lock information, and greatly reduces the overhead of managing pessimistic transaction locks. Under the performance bottleneck caused by pessimistic locks, memory optimization for pessimistic locks can effectively reduce latency by 10% and increase QPS by 10%.

    [User document](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#in-memory-pessimistic-lock), [#11452](https://github.com/tikv/tikv/issues/11452)

- Optimization to get TSO at the Read Committed isolation level

    To reduce query latency, when read-write conflicts are rare, TiDB adds the `tidb_rc_read_check_ts` system variable at the [Read Committed isolation level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#read-committed-isolation-level) to get less unnecessary TSO. This variable is disabled by default. When the variable is enabled, this optimization avoids getting duplicated TSO to reduce latency in scenarios where there is no read-write conflict. However, in scenarios with frequent read-write conflicts, enabling this variable might cause a performance regression.

    [User document](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#read-committed-isolation-level), [#33159](https://github.com/pingcap/tidb/issues/33159)

- Enhance prepared statements to share execution plans

    Reusing SQL execution plans can effectively reduce the time for parsing SQL statements, lessen CPU resource consumption, and improve SQL execution efficiency. One of the important methods of SQL tuning is to reuse SQL execution plans effectively. TiDB has supported sharing execution plans with prepared statements. However, when the prepared statements are closed, TiDB automatically clears the corresponding plan cache. After that, TiDB might unnecessarily parse the repeated SQL statements, affecting the execution efficiency. Since v6.0.0, TiDB supports controlling whether to ignore the `COM_STMT_CLOSE` command through the `tidb_ignore_prepared_cache_close_stmt` parameter (disabled by default). When the parameter is enabled, TiDB ignores the command of closing prepared statements and keeps the execution plan in the cache, improving the reuse rate of the execution plan.

    [User document](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache#ignore-the-com_stmt_close-command-and-the-deallocate-prepare-statement), [#31056](https://github.com/pingcap/tidb/issues/31056)

- Improve query pushdown

    With its native architecture of separating computing from storage, TiDB supports filtering out invalid data by pushing down operators, which greatly reduces the data transmission between TiDB and TiKV and thereby improves the query efficiency. In v6.0.0, TiDB supports pushing down more expressions and the `BIT` data type to TiKV, improving the query efficiency when computing the expressions and data type.

    [User document](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down), [#30738](https://github.com/pingcap/tidb/issues/30738)

- Optimization of hotspot index

    Writing monotonically increasing data in batches to the secondary index causes an index hotspot and affects the overall write throughput. Since v6.0.0, TiDB supports scattering the index hotspot using the `tidb_shard` function to improve the write performance. Currently, `tidb_shard` only takes effect on the unique secondary index. This application-friendly solution does not require modifying the original query conditions. You can use this solution in the scenarios of high write throughput, point queries, and batch point queries. Note that using the data that has been scattered by range queries in the application might cause a performance regression. Therefore, do not use this function in such cases without verification.

    [User document](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_shard), [#31040](https://github.com/pingcap/tidb/issues/31040)

- Support dynamic pruning mode for partitioned tables in TiFlash MPP engine (experimental)

    In this mode, TiDB can read and compute the data on partitioned tables using the MPP engine of TiFlash, which greatly improves the query performance of partitioned tables.

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#access-partitioned-tables-in-the-mpp-mode)

- Improve the computing performance of the MPP engine

    - Support pushing down more functions and operators to the MPP engine

        - Logical functions: `IS`, `IS NOT`
        - String functions: `REGEXP()`, `NOT REGEXP()`
        - Mathematical functions: `GREATEST(int/real)`, `LEAST(int/real)`
        - Date functions: `DAYNAME()`, `DAYOFMONTH()`, `DAYOFWEEK()`, `DAYOFYEAR()`, `LAST_DAY()`, `MONTHNAME()`
        - Operators: Anti Left Outer Semi Join, Left Outer Semi Join

        [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations)

    - The elastic thread pool (enabled by default) becomes GA. This feature aims to improve CPU utilization.

        [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file)
### Stability

- Enhance baseline capturing of execution plans

    Enhance the usability of baseline capturing of execution plans by adding a blocklist with such dimensions as table name, frequency, and user name. Introduce a new algorithm to optimize memory management for caching bindings. After baseline capturing is enabled, the system automatically creates bindings for most OLTP queries. Execution plans of bound statements are fixed, avoiding performance problems due to any change in the execution plans. Baseline capturing is applicable to scenarios such as major version upgrades and cluster migration, and helps reduce performance problems caused by regression of execution plans.

    [User document](https://docs.pingcap.com/tidb/stable/sql-plan-management#baseline-capturing), [#32466](https://github.com/pingcap/tidb/issues/32466)

- Support TiKV quota limiter (experimental)

    If your machine deployed with TiKV has limited resources and the foreground is burdened by an excessively large amount of requests, background CPU resources are occupied by the foreground, causing TiKV performance unstable. In TiDB v6.0.0, you can use the quota-related configuration items to limit the resources used by the foreground, including CPU and read/write bandwidth. This greatly improves stability of clusters under long-term heavy workloads.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#quota), [#12131](https://github.com/tikv/tikv/issues/12131)

- Support the zstd compression algorithm in TiFlash

    TiFlash introduces two parameters, `profiles.default.dt_compression_method` and `profiles.default.dt_compression_level`, which allow users to select the optimal compression algorithm based on performance and capacity balance.

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file)

- Enable all I/O checks (Checksum) by default

    This feature was introduced in v5.4.0 as experimental. It enhances data accuracy and security without imposing an obvious impact on users' businesses.

    Warning: Newer version of data format cannot be downgraded in place to versions earlier than v5.4.0. During such a downgrade, you need to delete TiFlash replicas and replicate data after the downgrade. Alternatively, you can perform a downgrade by referring to [dttool migrate](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-command-line-flags#dttool-migrate).

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-data-validation)

- Improve thread utilization

    TiFlash introduces asynchronous gRPC and Min-TSO scheduling mechanisms. Such mechanisms ensure more efficient use of threads and avoid system crashes caused by excessive threads.

    [User document](https://docs.pingcap.com/tidb/stable/tiflash/monitor-tiflash#coprocessor)
### Data migration
