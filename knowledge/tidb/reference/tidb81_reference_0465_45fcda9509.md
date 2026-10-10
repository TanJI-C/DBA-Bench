# Range INTERVAL partitioning syntax, ALTER behavior, and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partitioning types > Range INTERVAL partitioning | Partitioning > Partitioning types > Range INTERVAL partitioning > ALTER INTERVAL partitioned tables | Partitioning > Partitioning types > Range INTERVAL partitioning > INTERVAL partitioning details and limitations`
- Source Line Ranges: `207-315`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partitioning`, `range-partitioning`, `interval-partitioning`, `range-columns`, `alter-table`, `null-partition`, `maxvalue-partition`, `limitations`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0465_45fcda9509`
- Source ID: `tidb-docs-8.1:partitioned-table.md#range-interval-partitioning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `341a635edb97b57e7c86580b98bdfce32048ec8896c709e17f6f9a8d2c64cc31`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#range-interval-partitioning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax, ALTER behavior, or limitations of RANGE INTERVAL partitioning or RANGE COLUMNS INTERVAL partitioning in TiDB.
- Retrieval Keywords: Range INTERVAL partitioning, PARTITION BY RANGE INTERVAL, PARTITION BY RANGE COLUMNS INTERVAL, FIRST PARTITION LESS THAN, LAST PARTITION LESS THAN, NULL PARTITION, MAXVALUE PARTITION, ALTER TABLE table_name FIRST PARTITION LESS THAN, ALTER TABLE table_name LAST PARTITION LESS THAN, SHOW CREATE TABLE, MySQL-compatible, single column INTEGER DATE DATETIME
- Follow-up Guidance: It also states that the ALTER syntax applies to existing tables conforming to INTERVAL, and that SHOW CREATE TABLE output does not change.
- Classification Note: This is reference content because it defines SQL syntax, optional clauses, ALTER statements, and documented limitations for INTERVAL partitioning.

## Official Source Content

### Range INTERVAL partitioning

Range INTERVAL partitioning is an extension of Range partitioning, which allows you to create partitions of a specified interval easily. Starting from v6.3.0, INTERVAL partitioning is introduced in TiDB as syntactic sugar.

The syntax is as follows:

```sql
PARTITION BY RANGE [COLUMNS] (<partitioning expression>)
INTERVAL (<interval expression>)
FIRST PARTITION LESS THAN (<expression>)
LAST PARTITION LESS THAN (<expression>)
[NULL PARTITION]
[MAXVALUE PARTITION]
```

For example:

```sql
CREATE TABLE employees (
    id int unsigned NOT NULL,
    fname varchar(30),
    lname varchar(30),
    hired date NOT NULL DEFAULT '1970-01-01',
    separated date DEFAULT '9999-12-31',
    job_code int,
    store_id int NOT NULL
) PARTITION BY RANGE (id)
INTERVAL (100) FIRST PARTITION LESS THAN (100) LAST PARTITION LESS THAN (10000) MAXVALUE PARTITION
```

It creates the following table:

```sql
CREATE TABLE `employees` (
  `id` int unsigned NOT NULL,
  `fname` varchar(30) DEFAULT NULL,
  `lname` varchar(30) DEFAULT NULL,
  `hired` date NOT NULL DEFAULT '1970-01-01',
  `separated` date DEFAULT '9999-12-31',
  `job_code` int DEFAULT NULL,
  `store_id` int NOT NULL
)
PARTITION BY RANGE (`id`)
(PARTITION `P_LT_100` VALUES LESS THAN (100),
 PARTITION `P_LT_200` VALUES LESS THAN (200),
...
 PARTITION `P_LT_9900` VALUES LESS THAN (9900),
 PARTITION `P_LT_10000` VALUES LESS THAN (10000),
 PARTITION `P_MAXVALUE` VALUES LESS THAN (MAXVALUE))
```

Range INTERVAL partitioning also works with [Range COLUMNS](#range-columns-partitioning) partitioning.

For example:

```sql
CREATE TABLE monthly_report_status (
    report_id int NOT NULL,
    report_status varchar(20) NOT NULL,
    report_date date NOT NULL
)
PARTITION BY RANGE COLUMNS (report_date)
INTERVAL (1 MONTH) FIRST PARTITION LESS THAN ('2000-01-01') LAST PARTITION LESS THAN ('2025-01-01')
```

It creates this table:

```
CREATE TABLE `monthly_report_status` (
  `report_id` int(11) NOT NULL,
  `report_status` varchar(20) NOT NULL,
  `report_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
PARTITION BY RANGE COLUMNS(`report_date`)
(PARTITION `P_LT_2000-01-01` VALUES LESS THAN ('2000-01-01'),
 PARTITION `P_LT_2000-02-01` VALUES LESS THAN ('2000-02-01'),
...
 PARTITION `P_LT_2024-11-01` VALUES LESS THAN ('2024-11-01'),
 PARTITION `P_LT_2024-12-01` VALUES LESS THAN ('2024-12-01'),
 PARTITION `P_LT_2025-01-01` VALUES LESS THAN ('2025-01-01'))
```

The optional parameter `NULL PARTITION` creates a partition with the definition as `PARTITION P_NULL VALUES LESS THAN (<minimum value of the column type>)`, only matching when the partitioning expression evaluates to `NULL`. See [Handling of NULL with Range partitioning](#handling-of-null-with-range-partitioning), which explains that `NULL` is considered to be less than any other value.

The optional parameter `MAXVALUE PARTITION` creates the last partition as `PARTITION P_MAXVALUE VALUES LESS THAN (MAXVALUE)`.
#### ALTER INTERVAL partitioned tables

INTERVAL partitioning also adds simpler syntaxes for adding and dropping partitions.

The following statement changes the first partition. It drops all partitions whose values are less than the given expression, and makes the matched partition the new first partition. It does not affect a NULL PARTITION.

```
ALTER TABLE table_name FIRST PARTITION LESS THAN (<expression>)
```

The following statement changes the last partition, meaning adding more partitions with higher ranges and room for new data. It will add new partitions with the current INTERVAL up to and including the given expression. It does not work if a `MAXVALUE PARTITION` exists, because it needs data reorganization.

```
ALTER TABLE table_name LAST PARTITION LESS THAN (<expression>)
```
#### INTERVAL partitioning details and limitations

- The INTERVAL partitioning feature only involves the `CREATE/ALTER TABLE` syntax. There is no change in metadata, so tables created or altered with the new syntax are still MySQL-compatible.
- There is no change in the output format of `SHOW CREATE TABLE` to keep MySQL compatibility.
- The new `ALTER` syntax applies to existing tables conforming to INTERVAL. You do not need to create these tables with the `INTERVAL` syntax.
- To use the `INTERVAL` syntax for `RANGE COLUMNS` partitioning, you can only specify a single column in the `INTEGER`, `DATE`, or `DATETIME` type as the partitioning key.
