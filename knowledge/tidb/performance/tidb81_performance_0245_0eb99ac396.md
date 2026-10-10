# Workload tuning for transaction mode, pushdown, statistics, and thread pools

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-performance-tuning-config.md`
- Source Title: `Configure TiDB for Optimal Performance`
- Source Heading Path: `Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize transaction mode and DML type for different workloads | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize transaction mode and DML type for different workloads > Transaction modes | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize transaction mode and DML type for different workloads > DML types | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize `GROUP BY` and `DISTINCT` operations with TiKV pushdown | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize `GROUP BY` and `DISTINCT` operations with TiKV pushdown > Usage scenarios | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize `GROUP BY` and `DISTINCT` operations with TiKV pushdown > Configuration | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize statistics collection during batch operations | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize statistics collection during batch operations > When to disable auto analyze | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize statistics collection during batch operations > Best practices | Configure TiDB for Optimal Performance > Edge cases and optimizations > Optimize thread pool settings for different instance types`
- Source Line Ranges: `316-434`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `transaction-mode`, `pessimistic`, `optimistic`, `bulk-dml`, `group-by`, `distinct`, `pushdown`, `statistics`, `auto-analyze`, `batch-operations`, `thread-pool`, `instance-sizing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0245_0eb99ac396`
- Source ID: `tidb-docs-8.1:tidb-performance-tuning-config.md#optimize-transaction-mode-and-dml-type-for-different-workloads`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9243bbb56474dba36d02c50f3a0848b15af8deb019db7a912d638d7f41af5d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-performance-tuning-config#optimize-transaction-mode-and-dml-type-for-different-workloads
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-performance-tuning-config.md

## Retrieval Guidance

- Use When: Use this chunk when you need workload-specific performance tuning for transaction mode, bulk DML, GROUP BY or DISTINCT pushdown, statistics collection during batch operations, or TiKV thread pool sizing.
- Retrieval Keywords: tidb_txn_mode, pessimistic transaction mode, optimistic transaction mode, SET SESSION tidb_txn_mode = "pessimistic", SET SESSION tidb_txn_mode = "optimistic", tidb_dml_type, bulk DML, SET SESSION tidb_dml_type = "bulk", autocommit, pessimistic-auto-commit, GROUP BY pushdown, DISTINCT pushdown, TiKV pushdown, tidb_opt_agg_push_down, tidb_opt_distinct_agg_push_down, SET GLOBAL tidb_opt_agg_push_down = ON, SET GLOBAL tidb_opt_distinct_agg_push_down = ON, low NDV, high NDV, tidb_enable_auto_analyze, SET GLOBAL tidb_enable_auto_analyze = OFF, ANALYZE TABLE your_table, SET GLOBAL tidb_enable_auto_analyze = ON, batch operations, large data imports, bulk update operations, thread pool settings, grpc-concurrency = 10, apply-pool-size = 4, store-pool-size = 4, store-io-pool-size = 2, 8 to 16 cores, 32 or more cores
- Follow-up Guidance: The source provides before-and-after batch operation steps: disable auto analyze before the batch work, then run ANALYZE TABLE and re-enable auto analyze afterward.
- Classification Note: This is classified as performance for TiDB with related TiKV components because the content focuses on workload-dependent transaction and DML behavior, pushdown execution, statistics collection overhead, and TiKV thread pool resource utilization.

## Official Source Content

### Optimize transaction mode and DML type for different workloads

TiDB provides different transaction modes and DML execution types to optimize performance for various workload patterns.
#### Transaction modes

You can set the transaction mode using the [`tidb_txn_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_mode) system variable.

- [Pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) (default):

    - Suitable for general workloads with potential write conflicts.
    - Provides stronger consistency guarantees.

  ```sql
  SET SESSION tidb_txn_mode = "pessimistic";
  ```

- [Optimistic transaction mode](https://docs.pingcap.com/tidb/stable/optimistic-transaction):

    - Suitable for workloads with minimal write conflicts.
    - Better performance for multi-statement transactions.
    - Example: `BEGIN; INSERT...; INSERT...; COMMIT;`.

  ```sql
  SET SESSION tidb_txn_mode = "optimistic";
  ```
#### DML types

You can control the execution mode of DML statements using the [`tidb_dml_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) system variable, which is introduced in v8.0.0.

To use the bulk DML execution mode, set `tidb_dml_type` to `"bulk"`. This mode optimizes bulk data loading without conflicts and reduces memory usage during large write operations. Before using this mode, ensure that:

- [`autocommit`](https://docs.pingcap.com/tidb/stable/system-variables#autocommit) is enabled.
- The [`pessimistic-auto-commit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pessimistic-auto-commit-new-in-v600) configuration item is set to `false`.

```sql
SET SESSION tidb_dml_type = "bulk";
```
### Optimize `GROUP BY` and `DISTINCT` operations with TiKV pushdown

TiDB pushes down aggregation operations to TiKV to reduce data transfer and processing overhead. The performance improvement varies based on your data characteristics.
#### Usage scenarios

- **Ideal scenarios** (high performance gain):
    - Columns containing few distinct values (low NDV).
    - Data containing frequent duplicate values.
    - Example: status columns, category codes, date parts.

- **Non-ideal scenarios** (potential performance loss):
    - Columns containing mostly unique values (high NDV).
    - Unique identifiers or timestamps.
    - Example: User IDs, transaction IDs.
#### Configuration

Enable pushdown optimizations at the session or global level:

```sql
-- Enable regular aggregation pushdown
SET GLOBAL tidb_opt_agg_push_down = ON;

-- Enable distinct aggregation pushdown
SET GLOBAL tidb_opt_distinct_agg_push_down = ON;
```
### Optimize statistics collection during batch operations

You can optimize performance during batch operations while maintaining query optimization by managing statistics collection. This section describes how to manage this process effectively.
#### When to disable auto analyze

You can disable auto analyze by setting the [`tidb_enable_auto_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze-new-in-v610) system variable to `OFF` in the following scenarios:

- During large data imports.
- During bulk update operations.
- For time-sensitive batch processing.
- When you need full control over the timing of statistics collection.
#### Best practices

- Before the batch operation:

   ```sql
   -- Disable auto analyze
   SET GLOBAL tidb_enable_auto_analyze = OFF;
   ```

- After the batch operation:

   ```sql
   -- Manually collect statistics
   ANALYZE TABLE your_table;
   
   -- Re-enable auto analyze
   SET GLOBAL tidb_enable_auto_analyze = ON;
   ```
### Optimize thread pool settings for different instance types

To improve TiKV performance, configure the thread pools based on your instance's CPU resources. The following guidelines help you optimize these settings:

- For instances with 8 to 16 cores, the default settings are typically sufficient.

- For instances with 32 or more cores, increase the pool sizes for better resource utilization. Adjust the settings as follows:

    ```toml
    [server]
    # Increase gRPC thread pool 
    grpc-concurrency = 10
    
    [raftstore]
    # Optimize for write-intensive workloads
    apply-pool-size = 4
    store-pool-size = 4
    store-io-pool-size = 2
    ```
