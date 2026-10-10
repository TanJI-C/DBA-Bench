# Identify hotspots and mitigate write hotspots

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-hot-spot-issues.md`
- Source Title: `Troubleshoot Hotspot Issues`
- Source Heading Path: `Troubleshoot Hotspot Issues > Identify hotspot issues | Troubleshoot Hotspot Issues > Identify hotspot issues > Use TiDB Dashboard to locate hotspot tables | Troubleshoot Hotspot Issues > Use `SHARD_ROW_ID_BITS` to process hotspots | Troubleshoot Hotspot Issues > Handle auto-increment primary key hotspot tables using `AUTO_RANDOM``
- Source Line Ranges: `62-172`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tikv`, `sql`
- Topic Tags: `hotspot-detection`, `monitoring`, `key-visualizer`, `hot-write`, `thread-cpu`, `shard-row-id-bits`, `auto-random`, `auto-increment`, `clustered-index`, `nonclustered-primary-key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0278_1e4527ce4b`
- Source ID: `tidb-docs-8.1:troubleshoot-hot-spot-issues.md#identify-hotspot-issues`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d86a31240188ed37914182f979a2d5dbaa7fd45353f07daee03404e5a9256ea2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#identify-hotspot-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-hot-spot-issues.md

## Retrieval Guidance

- Use When: Use this chunk when you need to identify hotspot symptoms or mitigate write hotspots with `SHARD_ROW_ID_BITS` or `AUTO_RANDOM`.
- Retrieval Keywords: Identify hotspot issues, Hot Write, TiKV-Trouble-Shooting, Raftstore CPU, Thread_CPU, TiKV-Details, Key Visualizer, TiDB Dashboard, SHARD_ROW_ID_BITS, CREATE TABLE t (c int) SHARD_ROW_ID_BITS = 4, ALTER TABLE t SHARD_ROW_ID_BITS = 4, AUTO_RANDOM, AUTO_INCREMENT, LAST_INSERT_ID(), CLUSTERED, NONCLUSTERED
- Follow-up Guidance: Use the mitigation method that matches the table type or primary key definition described in the chunk.
- Classification Note: This chunk covers hotspot identification with TiDB Dashboard and specific write-hotspot handling options for row IDs and auto-increment primary keys.

## Official Source Content

## Identify hotspot issues

Performance problems are not necessarily caused by hotspots and might be caused by multiple factors. Before troubleshooting issues, confirm whether it is related to hotspots.

- To judge write hotspots, open **Hot Write** in the **TiKV-Trouble-Shooting** monitoring panel to check whether the Raftstore CPU metric value of any TiKV node is significantly higher than that of other nodes.

- To judge read hotspots, open **Thread_CPU** in the **TiKV-Details** monitoring panel to check whether the coprocessor CPU metric value of any TiKV node is particularly high.
### Use TiDB Dashboard to locate hotspot tables

The **Key Visualizer** feature in [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) helps users narrow down hotspot troubleshooting scope to the table level. The following is an example of the thermal diagram shown by **Key Visualizer**. The horizontal axis of the graph is time, and the vertical axis are various tables and indexes. The brighter the color, the greater the load. You can switch the read or write flow in the toolbar.

![Dashboard Example 1](/media/troubleshoot-hot-spot-issues-1.png)

The following bright diagonal lines (oblique upward or downward) can appear in the write flow graph. Because the write only appears at the end, as the number of table Regions becomes larger, it appears as a ladder. This indicates that a write hotspot shows in this table:

![Dashboard Example 2](/media/troubleshoot-hot-spot-issues-2.png)

For read hotspots, a bright horizontal line is generally shown in the thermal diagram. Usually these are caused by small tables with a large number of accesses, shown as follows:

![Dashboard Example 3](/media/troubleshoot-hot-spot-issues-3.png)

Hover over the bright block, you can see what table or index has a heavy load. For example:

![Dashboard Example 4](/media/troubleshoot-hot-spot-issues-4.png)
## Use `SHARD_ROW_ID_BITS` to process hotspots

For a non-clustered primary key or a table without a primary key, TiDB uses an implicit auto-increment RowID. When a large number of `INSERT` operations exist, the data is written into a single Region, resulting in a write hotspot.

By setting [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits), row IDs are scattered and written into multiple Regions, which can alleviate the write hotspot issue.

```
SHARD_ROW_ID_BITS = 4 # Represents 16 shards.
SHARD_ROW_ID_BITS = 6 # Represents 64 shards.
SHARD_ROW_ID_BITS = 0 # Represents the default 1 shard.
```

Statement example:

```sql
CREATE TABLE: CREATE TABLE t (c int) SHARD_ROW_ID_BITS = 4;
ALTER TABLE: ALTER TABLE t SHARD_ROW_ID_BITS = 4;
```

The value of `SHARD_ROW_ID_BITS` can be dynamically modified. The modified value only takes effect for newly written data.

For the table with a primary key of the `CLUSTERED` type, TiDB uses the primary key of the table as the RowID. At this time, the `SHARD_ROW_ID_BITS` option cannot be used because it changes the RowID generation rules. For the table with the primary key of the `NONCLUSTERED` type, TiDB uses an automatically allocated 64-bit integer as the RowID. In this case, you can use the `SHARD_ROW_ID_BITS` feature. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).

The following two load diagrams shows the case where two tables without primary keys use `SHARD_ROW_ID_BITS` to scatter hotspots. The first diagram shows the situation before scattering hotspots, while the second one shows the situation after scattering hotspots.

![Dashboard Example 5](/media/troubleshoot-hot-spot-issues-5.png)

![Dashboard Example 6](/media/troubleshoot-hot-spot-issues-6.png)

As shown in the load diagrams above, before setting `SHARD_ROW_ID_BITS`, load hotspots are concentrated on a single Region. After setting `SHARD_ROW_ID_BITS`, load hotspots become scattered.
## Handle auto-increment primary key hotspot tables using `AUTO_RANDOM`

To resolve the write hotspots brought by auto-increment primary keys, use `AUTO_RANDOM` to handle hotspot tables that have auto-increment primary keys.

If this feature is enabled, TiDB generates randomly distributed and non-repeated (before the space is used up) primary keys to achieve the purpose of scattering write hotspots.

Note that the primary keys generated by TiDB are no longer auto-increment primary keys and you can use `LAST_INSERT_ID()` to obtain the primary key value assigned last time.

To use this feature, modify `AUTO_INCREMENT` to `AUTO_RANDOM` in the `CREATE TABLE` statement. This feature is suitable for non-application scenarios where the primary keys only need to guarantee uniqueness.

For example:

```sql
CREATE TABLE t (a BIGINT PRIMARY KEY AUTO_RANDOM, b varchar(255));
INSERT INTO t (b) VALUES ("foo");
SELECT * FROM t;
```

```sql
+------------+---+
| a          | b |
+------------+---+
| 1073741825 | b |
+------------+---+
```

```sql
SELECT LAST_INSERT_ID();
```

```sql
+------------------+
| LAST_INSERT_ID() |
+------------------+
| 1073741825       |
+------------------+
```

The following two load diagrams shows the situations both before and after modifying `AUTO_INCREMENT` to `AUTO_RANDOM` to scatter hotspots. The first one uses `AUTO_INCREMENT`, while the second one uses `AUTO_RANDOM`.

![Dashboard Example 7](/media/troubleshoot-hot-spot-issues-7.png)

![Dashboard Example 8](/media/troubleshoot-hot-spot-issues-8.png)

As shown in the load diagrams above, using `AUTO_RANDOM` to replace `AUTO_INCREMENT` can well scatter hotspots.

For more details, see [AUTO_RANDOM](https://docs.pingcap.com/tidb/stable/auto-random).
