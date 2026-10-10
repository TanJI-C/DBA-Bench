# Observe ALTER TABLE COMPACT progress with TIFLASH_TABLES

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-table-compact.md`
- Source Title: `ALTER TABLE ... COMPACT`
- Source Heading Path: `ALTER TABLE ... COMPACT > Observe data compaction progress`
- Source Line Ranges: `92-199`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `sql`, `tidb`
- Topic Tags: `compaction-progress`, `information-schema`, `total-delta-rows`, `total-stable-rows`, `partitioned-table`, `non-partitioned-table`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0078_0c7429d6e9`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-table-compact.md#observe-data-compaction-progress`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4d64e45f9721aa7e021bee8a2bf7b8e8e9636aaac9cb84b6fffcc1e572cc083b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact#observe-data-compaction-progress
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-table-compact.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants to observe TiFlash table compaction progress or judge whether `ALTER TABLE ... COMPACT` is needed by querying system tables.
- Retrieval Keywords: INFORMATION_SCHEMA.TIFLASH_TABLES, TOTAL_DELTA_ROWS, TOTAL_STABLE_ROWS, IS_TOMBSTONE, INFORMATION_SCHEMA.PARTITIONS, TABLE_ID = p.TIDB_PARTITION_ID, PARTITION_NAME, observe data compaction progress, determine whether to initiate compaction
- Follow-up Guidance: If `TOTAL_DELTA_ROWS` remains non-zero after compaction because data was updated during compaction, the content states that executing `ALTER TABLE ... COMPACT` again compacts these updates.
- Classification Note: This is observability content because it explains how to inspect compaction state and progress through `INFORMATION_SCHEMA.TIFLASH_TABLES` and related queries.

## Official Source Content

## Observe data compaction progress

You can observe the progress of data compaction or determine whether to initiate compaction for a table by checking the `TOTAL_DELTA_ROWS` column in the `INFORMATION_SCHEMA.TIFLASH_TABLES` table. The larger the value of `TOTAL_DELTA_ROWS`, the more data that can be compacted. If `TOTAL_DELTA_ROWS` is `0`, all data in the table is in the best state and does not need to be compacted.

<details>
  <summary>Example: Check the compaction state of a non-partitioned table</summary>

```sql
USE test;

CREATE TABLE foo(id INT);

ALTER TABLE foo SET TIFLASH REPLICA 1;

SELECT TOTAL_DELTA_ROWS, TOTAL_STABLE_ROWS FROM INFORMATION_SCHEMA.TIFLASH_TABLES
    WHERE IS_TOMBSTONE = 0 AND
    `TIDB_DATABASE` = "test" AND `TIDB_TABLE` = "foo";
+------------------+-------------------+
| TOTAL_DELTA_ROWS | TOTAL_STABLE_ROWS |
+------------------+-------------------+
|                0 |                 0 |
+------------------+-------------------+

INSERT INTO foo VALUES (1), (3), (7);

SELECT TOTAL_DELTA_ROWS, TOTAL_STABLE_ROWS FROM INFORMATION_SCHEMA.TIFLASH_TABLES
    WHERE IS_TOMBSTONE = 0 AND
    `TIDB_DATABASE` = "test" AND `TIDB_TABLE` = "foo";
+------------------+-------------------+
| TOTAL_DELTA_ROWS | TOTAL_STABLE_ROWS |
+------------------+-------------------+
|                3 |                 0 |
+------------------+-------------------+
-- Newly written data can be compacted

ALTER TABLE foo COMPACT TIFLASH REPLICA;

SELECT TOTAL_DELTA_ROWS, TOTAL_STABLE_ROWS FROM INFORMATION_SCHEMA.TIFLASH_TABLES
    WHERE IS_TOMBSTONE = 0 AND
    `TIDB_DATABASE` = "test" AND `TIDB_TABLE` = "foo";
+------------------+-------------------+
| TOTAL_DELTA_ROWS | TOTAL_STABLE_ROWS |
+------------------+-------------------+
|                0 |                 3 |
+------------------+-------------------+
-- All data is in the best state and no compaction is needed
```

</details>

<details>
  <summary>Example: Check the compaction state of a partitioned table</summary>

```sql
USE test;

CREATE TABLE employees
    (id INT NOT NULL, store_id INT)
    PARTITION BY LIST (store_id) (
        PARTITION pNorth VALUES IN (1, 2, 3, 4, 5),
        PARTITION pEast VALUES IN (6, 7, 8, 9, 10),
        PARTITION pWest VALUES IN (11, 12, 13, 14, 15),
        PARTITION pCentral VALUES IN (16, 17, 18, 19, 20)
    );

ALTER TABLE employees SET TIFLASH REPLICA 1;

INSERT INTO employees VALUES (1, 1), (6, 6), (10, 10);

SELECT PARTITION_NAME, TOTAL_DELTA_ROWS, TOTAL_STABLE_ROWS
    FROM INFORMATION_SCHEMA.TIFLASH_TABLES t, INFORMATION_SCHEMA.PARTITIONS p
    WHERE t.IS_TOMBSTONE = 0 AND t.TABLE_ID = p.TIDB_PARTITION_ID AND
    p.TABLE_SCHEMA = "test" AND p.TABLE_NAME = "employees";
+----------------+------------------+-------------------+
| PARTITION_NAME | TOTAL_DELTA_ROWS | TOTAL_STABLE_ROWS |
+----------------+------------------+-------------------+
| pNorth         |                1 |                 0 |
| pEast          |                2 |                 0 |
| pWest          |                0 |                 0 |
| pCentral       |                0 |                 0 |
+----------------+------------------+-------------------+
-- Some partitions can be compacted

ALTER TABLE employees COMPACT TIFLASH REPLICA;

SELECT PARTITION_NAME, TOTAL_DELTA_ROWS, TOTAL_STABLE_ROWS
    FROM INFORMATION_SCHEMA.TIFLASH_TABLES t, INFORMATION_SCHEMA.PARTITIONS p
    WHERE t.IS_TOMBSTONE = 0 AND t.TABLE_ID = p.TIDB_PARTITION_ID AND
    p.TABLE_SCHEMA = "test" AND p.TABLE_NAME = "employees";
+----------------+------------------+-------------------+
| PARTITION_NAME | TOTAL_DELTA_ROWS | TOTAL_STABLE_ROWS |
+----------------+------------------+-------------------+
| pNorth         |                0 |                 1 |
| pEast          |                0 |                 2 |
| pWest          |                0 |                 0 |
| pCentral       |                0 |                 0 |
+----------------+------------------+-------------------+
-- Data in all partitions is in the best state and no compaction is needed
```

</details>

> **Note:**
>
> - If data is updated during compaction, `TOTAL_DELTA_ROWS` might still be a non-zero value after compaction is done. This is normal and indicates that these updates have not been compacted. To compact these updates, execute the `ALTER TABLE ... COMPACT` statement again.
>
> - `TOTAL_DELTA_ROWS` indicates the data version, not the number of rows. For example, if you insert a row and then delete it, `TOTAL_DELTA_ROWS` will increase by 2.
