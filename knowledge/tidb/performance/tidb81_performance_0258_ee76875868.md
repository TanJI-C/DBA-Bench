# Compaction and broadcast join tuning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance > Tune TiDB parameters > Compact data using the `ALTER TABLE ... COMPACT` statement | Tune TiFlash Performance > Tune TiDB parameters > Replace Shuffled Hash Join with Broadcast Hash Join`
- Source Line Ranges: `218-249`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `compaction`, `alter-table`, `disk-usage`, `deleted-rows`, `join`, `broadcast-hash-join`, `shuffled-hash-join`, `system-variables`, `optimizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0258_ee76875868`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#compact-data-using-the-alter-table-compact-statement`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c4fb92cc1b47824afec7286be31a6d0a599c911ab9220e991237a22164975f4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#compact-data-using-the-alter-table-compact-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiFlash tuning content about compacting table data with ALTER TABLE ... COMPACT or switching join planning between Shuffled Hash Join and Broadcast Hash Join using broadcast join threshold variables.
- Retrieval Keywords: ALTER TABLE ... COMPACT, ALTER TABLE employees COMPACT TIFLASH REPLICA, ALTER TABLE employees COMPACT PARTITION pNorth, pEast TIFLASH REPLICA, Compact data using the ALTER TABLE ... COMPACT statement, cleaning up deleted rows, merging multiple versions of data caused by updates, reduce disk usage, Replace Shuffled Hash Join with Broadcast Hash Join, tidb_broadcast_join_threshold_size, tidb_broadcast_join_threshold_count, set @@tidb_broadcast_join_threshold_size = 2000000, set @@tidb_broadcast_join_threshold_count = 100000, ExchangeType, ExchangeSender_29, HashPartition, Broadcast
- Follow-up Guidance: The source also includes an example comparing the query result before and after re-configuring tidb_broadcast_join_threshold_size, where ExchangeSender_29 changes from HashPartition to Broadcast.
- Classification Note: This chunk is classified as TiFlash performance content because it covers data compaction for TiFlash replicas and optimizer-related join algorithm thresholds that affect TiFlash query computing performance.

## Official Source Content

### Compact data using the `ALTER TABLE ... COMPACT` statement

Executing the [`ALTER TABLE ... COMPACT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact) statement can initiate compaction for a specific table or partition on a TiFlash node. During the compaction, the physical data on the node is rewritten, including cleaning up deleted rows and merging multiple versions of data caused by updates. This helps enhance access performance and reduce disk usage. The following are examples:

```sql
ALTER TABLE employees COMPACT TIFLASH REPLICA;
```

```sql
ALTER TABLE employees COMPACT PARTITION pNorth, pEast TIFLASH REPLICA;
```
### Replace Shuffled Hash Join with Broadcast Hash Join

For `Join` operations with small tables, the Broadcast Hash Join algorithm can avoid transferring large tables, thereby improving the computing performance.

- The [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50) variable controls whether to use the Broadcast Hash Join algorithm. If the table size (unit: byte) is smaller than the value of this variable, the Broadcast Hash Join algorithm is used. Otherwise, the Shuffled Hash Join algorithm is used.

    ```sql
    set @@tidb_broadcast_join_threshold_size = 2000000;
    ```

- The [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50) variable also controls whether to use the Broadcast Hash Join algorithm. If the objects of the join operation belong to a subquery, the optimizer cannot estimate the size of the subquery result set. In this situation, the size is determined by the number of rows in the result set. If the estimated number of rows for the subquery is fewer than the value of this variable, the Broadcast Hash Join algorithm is used. Otherwise, the Shuffled Hash Join algorithm is used.

    ```sql
    set @@tidb_broadcast_join_threshold_count = 100000;
    ```

The following example shows the query result before and after `tidb_broadcast_join_threshold_size` is re-configured. Before the re-configuration, the `ExchangeType` of `ExchangeSender_29` is `HashPartition`. After the value of this variable changes to `10000000`, the `ExchangeType` of `ExchangeSender_29` changes to `Broadcast`.

Before `tidb_broadcast_join_threshold_size` is re-configured:
