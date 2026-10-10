# Manage hash and key partitions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partition management > Manage Hash and Key partitions | Partitioning > Partition management > Manage Hash and Key partitions > Increase the number of partitions | Partitioning > Partition management > Manage Hash and Key partitions > Decrease the number of partitions | Partitioning > Partition management > Manage Hash and Key partitions > Truncate partitions`
- Source Line Ranges: `1078-1163`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partition-management`, `hash-partition`, `key-partition`, `add-partition`, `coalesce-partition`, `truncate-partition`, `show-create-table`, `analyze-table`, `statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0177_18670aeec8`
- Source ID: `tidb-docs-8.1:partitioned-table.md#manage-hash-and-key-partitions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b13e24bbcb410e742ccc1e84537f21e24df36564ee539d941c0a793eb85ed4ce`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#manage-hash-and-key-partitions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for SQL to manage Hash or Key partitions by adding partitions, decreasing partitions with COALESCE PARTITION, truncating partitions, or checking the resulting definition with SHOW CREATE TABLE.
- Retrieval Keywords: Manage Hash and Key partitions, PARTITION BY HASH(id), ADD PARTITION PARTITIONS 1, ALTER TABLE example ADD PARTITION, COALESCE PARTITION, ALTER TABLE example COALESCE PARTITION 1, DROP PARTITION is not supported for Hash and Key partitioning, TRUNCATE PARTITION, ALTER TABLE example TRUNCATE PARTITION p0, SHOW CREATE TABLE, pExample4, pExample5, ANALYZE TABLE, The statistics of related partitions will be outdated after reorganizing partitions
- Follow-up Guidance: The source notes that changing the number of Hash or Key partitions reorganizes partitions by copying all data, and then SHOW CREATE TABLE can be used to inspect the resulting table definition.
- Classification Note: This is classified as an operation chunk because it provides partition management statements for Hash and Key partitioned tables.

## Official Source Content

### Manage Hash and Key partitions

This section uses the partitioned table created by the following SQL statement as examples to show you how to manage Hash partitions. For Key partitions, you can use the same management statements as well.

```sql
CREATE TABLE example (
  id INT PRIMARY KEY,
  data VARCHAR(1024)
)
PARTITION BY HASH(id)
PARTITIONS 2;
```
#### Increase the number of partitions

Increase the number of partitions for the `example` table by 1 (from 2 to 3):

```sql
ALTER TABLE example ADD PARTITION PARTITIONS 1;
```

You can also specify partition options by adding partition definitions. For example, you can use the following statement to increase the number of partitions from 3 to 5 and specify the names of the newly added partitions as `pExample4` and `pExample5`:

```sql
ALTER TABLE example ADD PARTITION
(PARTITION pExample4 COMMENT = 'not p3, but pExample4 instead',
 PARTITION pExample5 COMMENT = 'not p4, but pExample5 instead');
```
#### Decrease the number of partitions

Unlike Range and List partitioning, `DROP PARTITION` is not supported for Hash and Key partitioning, but you can decrease the number of partitions with `COALESCE PARTITION` or delete all data from specific partitions with `TRUNCATE PARTITION`.

Decrease the number of partitions for the `example` table by 1 (from 5 to 4):

```sql
ALTER TABLE example COALESCE PARTITION 1;
```

> **Note:**
>
> The process of changing the number of partitions for Hash or Key partitioned tables reorganizes the partitions by copying all data to the new number of partitions. Therefore, after changing the number of partitions for a Hash or Key partitioned table, you will get the following warning about the outdated statistics. In this case, you can use the [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement to update the statistics.
>
> ```sql
> +---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
> | Level   | Code | Message                                                                                                                                                |
> +---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
> | Warning | 1105 | The statistics of related partitions will be outdated after reorganizing partitions. Please use 'ANALYZE TABLE' statement if you want to update it now |
> +---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
> 1 row in set (0.00 sec)
> ```

To better understand how the `example` table is organized now, you can show the SQL statement that is used to recreate the `example` table as follows:

```sql
SHOW CREATE TABLE\G
```

```
*************************** 1. row ***************************
       Table: example
Create Table: CREATE TABLE `example` (
  `id` int(11) NOT NULL,
  `data` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`id`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
PARTITION BY HASH (`id`)
(PARTITION `p0`,
 PARTITION `p1`,
 PARTITION `p2`,
 PARTITION `pExample4` COMMENT 'not p3, but pExample4 instead')
1 row in set (0.01 sec)
```
#### Truncate partitions

Delete all data from a partition:

```sql
ALTER TABLE example TRUNCATE PARTITION p0;
```

```
Query OK, 0 rows affected (0.03 sec)
```
