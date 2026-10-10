# Reorganize range and list partitions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partition management > Manage Range, Range COLUMNS, List, and List COLUMNS partitions > Reorganize partitions`
- Source Line Ranges: `992-1077`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partition-management`, `reorganize-partition`, `split-partition`, `merge-partition`, `range-partition`, `list-partition`, `analyze-table`, `statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0176_912f234e69`
- Source ID: `tidb-docs-8.1:partitioned-table.md#reorganize-partitions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `39f1939c0edd708e7c3d586c6ee87bbcfcc9040f9cf8d0e79a0b2ca5d3cd644a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#reorganize-partitions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to split, merge, or redefine Range or List partitions with ALTER TABLE ... REORGANIZE PARTITION, including related errors and statistics warnings.
- Retrieval Keywords: REORGANIZE PARTITION, ALTER TABLE members REORGANIZE PARTITION, ALTER TABLE member_level REORGANIZE PARTITION, split a partition, merge partitions, change the partitioning scheme definition, Range partition adjacent partitions, Unsupported REORGANIZE PARTITION of RANGE; not adjacent partitions, ERROR 8200 (HY000), Table has no partition for value 2022, Table has no partition for value 6, ERROR 1526 (HY000), VALUES LESS THAN, VALUES IN, ANALYZE TABLE, The statistics of related partitions will be outdated after reorganizing partitions
- Follow-up Guidance: After partitions are reorganized, the source says the related partition statistics are outdated and can be updated with ANALYZE TABLE.
- Classification Note: This is classified as an operation chunk because it shows SQL procedures and constraints for reorganizing Range and List partitions.

## Official Source Content

#### Reorganize partitions

Split a partition:

```sql
ALTER TABLE members REORGANIZE PARTITION `p1990to2010` INTO
(PARTITION p1990 VALUES LESS THAN (2000),
 PARTITION p2000 VALUES LESS THAN (2010),
 PARTITION p2010 VALUES LESS THAN (2020),
 PARTITION p2020 VALUES LESS THAN (2030),
 PARTITION pMax VALUES LESS THAN (MAXVALUE));

ALTER TABLE member_level REORGANIZE PARTITION l5_6 INTO
(PARTITION l5 VALUES IN (5),
 PARTITION l6 VALUES IN (6));
```

Merge partitions:

```sql
ALTER TABLE members REORGANIZE PARTITION pBefore1950,p1950 INTO (PARTITION pBefore1960 VALUES LESS THAN (1960));

ALTER TABLE member_level REORGANIZE PARTITION l1,l2 INTO (PARTITION l1_2 VALUES IN (1,2));
```

Change the partitioning scheme definition:

```sql
ALTER TABLE members REORGANIZE PARTITION pBefore1960,p1960,p1970,p1980,p1990,p2000,p2010,p2020,pMax INTO
(PARTITION p1800 VALUES LESS THAN (1900),
 PARTITION p1900 VALUES LESS THAN (2000),
 PARTITION p2000 VALUES LESS THAN (2100));

ALTER TABLE member_level REORGANIZE PARTITION l1_2,l3,l4,l5,l6 INTO
(PARTITION lOdd VALUES IN (1,3,5),
 PARTITION lEven VALUES IN (2,4,6));
```

When reorganizing partitions, you need to note the following key points:

- Reorganizing partitions (including merging or splitting partitions) can change the listed partitions into a new set of partition definitions but cannot change the type of partitioning (for example, change the List type to the Range type, or change the Range COLUMNS type to the Range type).

- For a Range partition table, you can reorganize only adjacent partitions in it.

    ```sql
    ALTER TABLE members REORGANIZE PARTITION p1800,p2000 INTO (PARTITION p2000 VALUES LESS THAN (2100));
    ```

    ```
    ERROR 8200 (HY000): Unsupported REORGANIZE PARTITION of RANGE; not adjacent partitions
    ```

- For a Range partitioned table, to modify the end of the range, the new end defined in `VALUES LESS THAN` must cover the existing rows in the last partition. Otherwise, existing rows no longer fit and an error is reported:

    ```sql
    INSERT INTO members VALUES (313, "John", "Doe", "2022-11-22", NULL);
    ALTER TABLE members REORGANIZE PARTITION p2000 INTO (PARTITION p2000 VALUES LESS THAN (2050)); -- This statement will work as expected, because 2050 covers the existing rows.
    ALTER TABLE members REORGANIZE PARTITION p2000 INTO (PARTITION p2000 VALUES LESS THAN (2020)); -- This statement will fail with an error, because 2022 does not fit in the new range.
    ```

    ```
    ERROR 1526 (HY000): Table has no partition for value 2022
    ```

- For a List partitioned table, to modify the set of values defined for a partition, the new definition must cover the existing values in that partition. Otherwise, an error is reported:

    ```sql
    INSERT INTO member_level (id, level) values (313, 6);
    ALTER TABLE member_level REORGANIZE PARTITION lEven INTO (PARTITION lEven VALUES IN (2,4));
    ```

    ```
    ERROR 1526 (HY000): Table has no partition for value 6
    ```

- After partitions are reorganized, the statistics of the corresponding partitions are outdated, so you will get the following warning. In this case, you can use the [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement to update the statistics.

    ```sql
    +---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Level   | Code | Message                                                                                                                                                |
    +---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
    | Warning | 1105 | The statistics of related partitions will be outdated after reorganizing partitions. Please use 'ANALYZE TABLE' statement if you want to update it now |
    +---------+------+--------------------------------------------------------------------------------------------------------------------------------------------------------+
    1 row in set (0.00 sec)
    ```
