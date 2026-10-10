# Linear partition syntax behavior and NULL handling in partitioning

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partitioning types > Key partitioning > How TiDB handles Linear Hash partitions | Partitioning > Partitioning types > How TiDB handles Linear Key partitions | Partitioning > Partitioning types > How TiDB partitioning handles NULL | Partitioning > Partitioning types > How TiDB partitioning handles NULL > Handling of NULL with Range partitioning | Partitioning > Partitioning types > How TiDB partitioning handles NULL > Handling of NULL with Hash partitioning | Partitioning > Partitioning types > How TiDB partitioning handles NULL > Handling of NULL with Key partitioning`
- Source Line Ranges: `715-886`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partitioning`, `linear-hash`, `linear-key`, `null-handling`, `range-partitioning`, `hash-partitioning`, `key-partitioning`, `version-behavior`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0469_66815edafe`
- Source ID: `tidb-docs-8.1:partitioned-table.md#how-tidb-handles-linear-hash-partitions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6eaa5d1ed13c005f508933863051defc316f82f8e700d8875835776a08486ebd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#how-tidb-handles-linear-hash-partitions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB partitioning behavior for `PARTITION BY LINEAR HASH`, `PARTITION BY LINEAR KEY`, or how `NULL` values are assigned in Range, Hash, and Key partitioned tables.
- Retrieval Keywords: PARTITION BY LINEAR HASH, PARTITION BY LINEAR KEY, Linear Hash partitions, Linear Key partitions, ignores the LINEAR keyword, non-linear Hash partitioned table, non-linear hash algorithm, number of partitions is a power of 2, partition selection, TRUNCATE PARTITION, EXCHANGE PARTITION, NULL handling, Range partitioning, Hash partitioning, Key partitioning, NULL is treated as 0, lowest partition, VALUES LESS THAN, select * from t1 partition(p0), select * from th partition (p0)
- Follow-up Guidance: It also shows example SQL and results for `ALTER TABLE t1 DROP PARTITION p0`, `PARTITION BY HASH(c1) PARTITIONS 2`, and partition queries that demonstrate where `NULL` rows are stored.
- Classification Note: This is reference content because it explains syntax and behavior differences, including version-specific parsing behavior and `NULL` handling semantics, rather than a procedural workflow.

## Official Source Content

#### How TiDB handles Linear Hash partitions

Before v6.4.0, if you execute DDL statements of [MySQL Linear Hash](https://dev.mysql.com/doc/refman/8.0/en/partitioning-linear-hash.html) partitions in TiDB, TiDB can only create non-partitioned tables. In this case, if you still want to use partitioned tables in TiDB, you need to modify the DDL statements.

Since v6.4.0, TiDB supports parsing the MySQL `PARTITION BY LINEAR HASH` syntax but ignores the `LINEAR` keyword in it. If you have some existing DDL and DML statements of MySQL Linear Hash partitions, you can execute them in TiDB without modification:

- For a `CREATE` statement of MySQL Linear Hash partitions, TiDB will create a non-linear Hash partitioned table (note that there is no Linear Hash partitioned table in TiDB). If the number of partitions is a power of 2, the rows in the TiDB Hash partitioned table are distributed the same as that in the MySQL Linear Hash partitioned table. Otherwise, the distribution of these rows in TiDB is different from MySQL. This is because non-linear partitioned tables use a simple "modulus number of partition", while linear partitioned tables use "modulus next power of 2 and fold the values between the number of partitions and the next power of 2". For details, see [#38450](https://github.com/pingcap/tidb/issues/38450).

- For all other statements of MySQL Linear Hash partitions, they work in TiDB the same as that in MySQL, except that the rows are distributed differently if the number of partitions is not a power of 2, which will give different results for [partition selection](#partition-selection), `TRUNCATE PARTITION`, and `EXCHANGE PARTITION`.
### How TiDB handles Linear Key partitions

Starting from v7.0.0, TiDB supports parsing the MySQL `PARTITION BY LINEAR KEY` syntax for Key partitioning. However, TiDB ignores the `LINEAR` keyword and uses a non-linear hash algorithm instead.

Before v7.0.0, if you try creating a Key partitioned table, TiDB creates it as a non-partitioned table and returns a warning.
### How TiDB partitioning handles NULL

It is allowed in TiDB to use `NULL` as the calculation result of a partitioning expression.

> **Note:**
>
> `NULL` is not an integer. TiDB's partitioning implementation treats `NULL` as being less than any other integer values, just as `ORDER BY` does.
#### Handling of NULL with Range partitioning

When you insert a row into a table partitioned by Range, and the column value used to determine the partition is `NULL`, then this row is inserted into the lowest partition.

```sql
CREATE TABLE t1 (
    c1 INT,
    c2 VARCHAR(20)
)

PARTITION BY RANGE(c1) (
    PARTITION p0 VALUES LESS THAN (0),
    PARTITION p1 VALUES LESS THAN (10),
    PARTITION p2 VALUES LESS THAN MAXVALUE
);
```

```
Query OK, 0 rows affected (0.09 sec)
```

```sql
select * from t1 partition(p0);
```

```
+------|--------+
| c1   | c2     |
+------|--------+
| NULL | mothra |
+------|--------+
1 row in set (0.00 sec)
```

```sql
select * from t1 partition(p1);
```

```
Empty set (0.00 sec)
```

```sql
select * from t1 partition(p2);
```

```
Empty set (0.00 sec)
```

Drop the `p0` partition and verify the result:

```sql
alter table t1 drop partition p0;
```

```
Query OK, 0 rows affected (0.08 sec)
```

```sql
select * from t1;
```

```
Empty set (0.00 sec)
```
#### Handling of NULL with Hash partitioning

When partitioning tables by Hash, there is a different way of handling `NULL` value - if the calculation result of the partitioning expression is `NULL`, it is considered as `0`.

```sql
CREATE TABLE th (
    c1 INT,
    c2 VARCHAR(20)
)

PARTITION BY HASH(c1)
PARTITIONS 2;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
INSERT INTO th VALUES (NULL, 'mothra'), (0, 'gigan');
```

```
Query OK, 2 rows affected (0.04 sec)
```

```sql
select * from th partition (p0);
```

```
+------|--------+
| c1   | c2     |
+------|--------+
| NULL | mothra |
|    0 | gigan  |
+------|--------+
2 rows in set (0.00 sec)
```

```sql
select * from th partition (p1);
```

```
Empty set (0.00 sec)
```

You can see that the inserted record `(NULL, 'mothra')` falls into the same partition as `(0, 'gigan')`.

> **Note:**
>
> `NULL` values by Hash partitions in TiDB are handled in the same way as described in [How MySQL Partitioning Handles NULL](https://dev.mysql.com/doc/refman/8.0/en/partitioning-handling-nulls.html), which, however, is not consistent with the actual behavior of MySQL. In other words, MySQL's implementation in this case is not consistent with its documentation.
>
> In this case, the actual behavior of TiDB is in line with the description of this document.
#### Handling of NULL with Key partitioning

For Key partitioning, the way of handling `NULL` value is consistent with that of Hash partitioning. If the value of a partitioning field is `NULL`, it is treated as `0`.
