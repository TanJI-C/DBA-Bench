# List partitioning and default list partition behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partitioning types > List partitioning | Partitioning > Partitioning types > List partitioning > Default List partition`
- Source Line Ranges: `316-465`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partitioning`, `list-partitioning`, `default-partition`, `system-variables`, `truncate-partition`, `drop-partition`, `insert-ignore`, `mysql-compatibility`, `replication-limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0466_6c201b509e`
- Source ID: `tidb-docs-8.1:partitioned-table.md#list-partitioning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2632e05b877c99667c862caab8146981db8ccda549547cba9035c9c5bb3dd3ee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#list-partitioning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when you need the behavior and syntax of LIST partitioning, including default list partitions, INSERT error handling, or TRUNCATE and DROP PARTITION examples.
- Retrieval Keywords: List partitioning, PARTITION BY LIST, PARTITION ... VALUES IN (...), Default List partition, PARTITION pDef DEFAULT, PARTITION pDef VALUES IN (DEFAULT), tidb_enable_list_partition, tidb_enable_table_partition, ALTER TABLE employees TRUNCATE PARTITION pEast, ALTER TABLE employees DROP PARTITION pEast, ALTER TABLE ... ADD PARTITION, INSERT INTO t VALUES (7, 7), ERROR 1525 (HY000): Table has no partition for value 7, INSERT IGNORE, List COLUMNS partitioned table, cannot be directly replicated to MySQL
- Follow-up Guidance: It explains that without a default partition, unmatched INSERT values return ERROR 1525, while INSERT IGNORE inserts only matched rows and skips unmatched rows without returning an error.
- Classification Note: This is reference content because it describes LIST partition syntax, related system variables, default partition behavior, and exact SQL statements and errors.

## Official Source Content

### List partitioning

Before creating a List partitioned table, make sure the following system variables are set to their default values of `ON`:

- [`tidb_enable_list_partition`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_list_partition-new-in-v50)
- [`tidb_enable_table_partition`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_table_partition)

List partitioning is similar to Range partitioning. Unlike Range partitioning, in List partitioning, the partitioning expression values for all rows in each partition are in a given value set. This value set defined for each partition can have any number of values but cannot have duplicate values. You can use the `PARTITION ... VALUES IN (...)` clause to define a value set.

Suppose that you want to create a personnel record table. You can create a table as follows:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    hired DATE NOT NULL DEFAULT '1970-01-01',
    store_id INT
);
```

Suppose that there are 20 stores distributed in 4 districts, as shown in the table below:

```
| Region  | Store ID Numbers     |
| ------- | -------------------- |
| North   | 1, 2, 3, 4, 5        |
| East    | 6, 7, 8, 9, 10       |
| West    | 11, 12, 13, 14, 15   |
| Central | 16, 17, 18, 19, 20   |
```

If you want to store the personnel data of employees of the same region in the same partition, you can create a List partitioned table based on `store_id`:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    hired DATE NOT NULL DEFAULT '1970-01-01',
    store_id INT
)
PARTITION BY LIST (store_id) (
    PARTITION pNorth VALUES IN (1, 2, 3, 4, 5),
    PARTITION pEast VALUES IN (6, 7, 8, 9, 10),
    PARTITION pWest VALUES IN (11, 12, 13, 14, 15),
    PARTITION pCentral VALUES IN (16, 17, 18, 19, 20)
);
```

After creating the partitions as above, you can easily add or delete records related to a specific region in the table. For example, suppose that all stores in the East region (East) are sold to another company. Then all the row data related to the store employees of this region can be deleted by executing `ALTER TABLE employees TRUNCATE PARTITION pEast`, which is much more efficient than the equivalent statement `DELETE FROM employees WHERE store_id IN (6, 7, 8, 9, 10)`.

You can also execute `ALTER TABLE employees DROP PARTITION pEast` to delete all related rows, but this statement also deletes the `pEast` partition from the table definition. In this situation, you must execute the `ALTER TABLE ... ADD PARTITION` statement to recover the original partitioning scheme of the table.
#### Default List partition

Starting from v7.3.0, you can add a default partition to a List or List COLUMNS partitioned table. The default partition acts as a fallback partition, where rows that do not match value sets of any partitions can be placed.

> **Note:**
>
> This feature is a TiDB extension to MySQL syntax. For a List or List COLUMNS partitioned table with a default partition, the data in the table cannot be directly replicated to MySQL.

Take the following List partitioned table as an example:

```sql
CREATE TABLE t (
  a INT,
  b INT
)
PARTITION BY LIST (a) (
  PARTITION p0 VALUES IN (1, 2, 3),
  PARTITION p1 VALUES IN (4, 5, 6)
);
Query OK, 0 rows affected (0.11 sec)
```

You can add a default list partition named `pDef` to the table as follows:

```sql
ALTER TABLE t ADD PARTITION (PARTITION pDef DEFAULT);
```

or

```sql
ALTER TABLE t ADD PARTITION (PARTITION pDef VALUES IN (DEFAULT));
```

In this way, newly inserted values that do not match value sets of any partitions can automatically go into the default partition.

```sql
INSERT INTO t VALUES (7, 7);
Query OK, 1 row affected (0.01 sec)
```

You can also add a default partition when creating a List or List COLUMNS partitioned table. For example:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    hired DATE NOT NULL DEFAULT '1970-01-01',
    store_id INT
)
PARTITION BY LIST (store_id) (
    PARTITION pNorth VALUES IN (1, 2, 3, 4, 5),
    PARTITION pEast VALUES IN (6, 7, 8, 9, 10),
    PARTITION pWest VALUES IN (11, 12, 13, 14, 15),
    PARTITION pCentral VALUES IN (16, 17, 18, 19, 20),
    PARTITION pDefault DEFAULT
);
```

For a List or List COLUMNS partitioned table without a default partition, the values to be inserted using an `INSERT` statement must match value sets defined in the `PARTITION ... VALUES IN (...)` clauses of the table. If the values to be inserted do not match value sets of any partitions, the statement will fail and an error is returned, as shown in the following example:

```sql
CREATE TABLE t (
  a INT,
  b INT
)
PARTITION BY LIST (a) (
  PARTITION p0 VALUES IN (1, 2, 3),
  PARTITION p1 VALUES IN (4, 5, 6)
);
Query OK, 0 rows affected (0.11 sec)

INSERT INTO t VALUES (7, 7);
ERROR 1525 (HY000): Table has no partition for value 7
```

To ignore the preceding error, you can add the `IGNORE` keyword to the `INSERT` statement. After this keyword is added, the `INSERT` statement will only insert rows that match the partition value sets and will not insert unmatched rows, without returning an error:

```sql
test> TRUNCATE t;
Query OK, 1 row affected (0.00 sec)

test> INSERT IGNORE INTO t VALUES (1, 1), (7, 7), (8, 8), (3, 3), (5, 5);
Query OK, 3 rows affected, 2 warnings (0.01 sec)
Records: 5  Duplicates: 2  Warnings: 2

test> select * from t;
+------+------+
| a    | b    |
+------+------+
|    5 |    5 |
|    1 |    1 |
|    3 |    3 |
+------+------+
3 rows in set (0.01 sec)
```
