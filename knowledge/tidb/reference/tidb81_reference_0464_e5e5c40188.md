# Range COLUMNS partitioning

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partitioning types > Range COLUMNS partitioning`
- Source Line Ranges: `167-206`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partitioning`, `range-columns-partitioning`, `partition-keys`, `strictly-increasing-ranges`, `partition-pruning`, `drop-partition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0464_e5e5c40188`
- Source ID: `tidb-docs-8.1:partitioned-table.md#range-columns-partitioning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e4a72812434ed1fb05bcdaaf3cfef662bf957d135777a0fd514d4d9e5bc96bd5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#range-columns-partitioning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the rules and examples for Range COLUMNS partitioning, especially supported partition key data types, unsupported expressions, strictly increasing VALUES LESS THAN requirements, and pruning or drop-data use cases.
- Retrieval Keywords: Range COLUMNS partitioning, PARTITION BY RANGE COLUMNS, strictly increasing, VALUES LESS THAN value must be strictly increasing for each partition, Error 1493 (HY000), partitioning keys, integer, CHAR, VARCHAR, DATE, DATETIME, expressions are not supported, partition pruning, drop invalid data, valid_until, name, p2022-g, p2023-g, p2022-m, p2023-m, p2022-s, p2023-s
- Follow-up Guidance: The chunk includes a supported example partitioned by RANGE COLUMNS(name, valid_until) and an unsupported definition that triggers Error 1493 (HY000).
- Classification Note: This chunk is classified as a SQL reference because it defines the syntax constraints and behavior of Range COLUMNS partitioning with exact SQL and error text.

## Official Source Content

### Range COLUMNS partitioning

Range COLUMNS partitioning is a variant of Range partitioning. You can use one or more columns as partitioning keys. The data types of partition columns can be integer, string (`CHAR` or `VARCHAR`), `DATE`, and `DATETIME`. Any expressions, such as non-COLUMNS partitioning, are not supported.

Like Range partitioning, Range COLUMNS partitioning also requires the partition ranges to be strictly increasing. The partition definition in the following example is not supported:

```sql
CREATE TABLE t(
    a int,
    b datetime,
    c varchar(8)
) PARTITION BY RANGE COLUMNS(`c`,`b`)
(PARTITION `p20240520A` VALUES LESS THAN ('A','2024-05-20 00:00:00'),
 PARTITION `p20240520Z` VALUES LESS THAN ('Z','2024-05-20 00:00:00'),
 PARTITION `p20240521A` VALUES LESS THAN ('A','2024-05-21 00:00:00'));
```

```
Error 1493 (HY000): VALUES LESS THAN value must be strictly increasing for each partition
```

Suppose that you want to partition by name, and drop old and invalid data, then you can create a table as follows:

```sql
CREATE TABLE t (
  valid_until datetime,
  name varchar(255) CHARACTER SET ascii,
  notes text
)
PARTITION BY RANGE COLUMNS(name, valid_until)
(PARTITION `p2022-g` VALUES LESS THAN ('G','2023-01-01 00:00:00'),
 PARTITION `p2023-g` VALUES LESS THAN ('G','2024-01-01 00:00:00'),
 PARTITION `p2022-m` VALUES LESS THAN ('M','2023-01-01 00:00:00'),
 PARTITION `p2023-m` VALUES LESS THAN ('M','2024-01-01 00:00:00'),
 PARTITION `p2022-s` VALUES LESS THAN ('S','2023-01-01 00:00:00'),
 PARTITION `p2023-s` VALUES LESS THAN ('S','2024-01-01 00:00:00'))
```

The preceding SQL statement will partition the data by year and by name in the ranges `[ ('', ''), ('G', '2023-01-01 00:00:00') )`, `[ ('G', '2023-01-01 00:00:00'), ('G', '2024-01-01 00:00:00') )`, `[ ('G', '2024-01-01 00:00:00'), ('M', '2023-01-01 00:00:00') )`, `[ ('M', '2023-01-01 00:00:00'), ('M', '2024-01-01 00:00:00') )`, `[ ('M', '2024-01-01 00:00:00'), ('S', '2023-01-01 00:00:00') )`, and `[ ('S', '2023-01-01 00:00:00'), ('S', '2024-01-01 00:00:00') )`. It allows you to easily drop invalid data while still benefit from partition pruning on both `name` and `valid_until` columns. In this example, `[,)` indicates a left-closed, right-open range. For example, `[ ('G', '2023-01-01 00:00:00'), ('G', '2024-01-01 00:00:00') )` indicates a range of data whose name is `'G'`, the year contains `2023-01-01 00:00:00` and is greater than `2023-01-01 00:00:00` but less than `2024-01-01 00:00:00`. It does not include `(G, 2024-01-01 00:00:00)`.
