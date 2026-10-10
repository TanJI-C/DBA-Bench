# Using, monitoring, and terminating non-transactional DML

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements > Usage examples | Non-Transactional DML Statements > Usage examples > Use a non-transactional DML statement | Non-Transactional DML Statements > Usage examples > Check the execution progress | Non-Transactional DML Statements > Usage examples > Terminate a non-transactional DML statement`
- Source Line Ranges: `74-191`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `examples`, `delete`, `update-join`, `show-processlist`, `progress`, `kill-tidb`, `batch-execution`, `shard-column`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0173_73fb067b1d`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#usage-examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `534c92ac7e30a280670d5560f876b0aa80ea46aaeb2ad71422f76c580440542b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#usage-examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this content when you need examples of executing, monitoring, or terminating a TiDB non-transactional DML statement, including BATCH syntax, SHOW PROCESSLIST progress output, and KILL TIDB behavior.
- Retrieval Keywords: BATCH ON id LIMIT 2 DELETE FROM t WHERE v < 6, number of jobs, job status, all succeeded, BATCH ON test.t._tidb_rowid LIMIT 1 UPDATE t JOIN t2 ON t.id = t2.id SET t2.id = t2.id+1, SHOW PROCESSLIST, show full processlist, Time field, current batch execution, job 506/500000, KILL TIDB <processlist_id>, terminate a non-transactional DML statement
- Follow-up Guidance: The content says you can use SHOW PROCESSLIST to view progress during execution and KILL TIDB <processlist_id> to cancel all batches after the batch currently being executed, with execution results available in the log.
- Classification Note: This is classified as an operation topic because the official content provides concrete usage examples and operational checks for running, observing, and stopping non-transactional DML.

## Official Source Content

## Usage examples
### Use a non-transactional DML statement

The following sections describe the use of non-transactional DML statements with examples:

Create a table `t` with the following schema:

```sql
CREATE TABLE t (id INT, v INT, KEY(id));
```

```sql
Query OK, 0 rows affected
```

Insert some data into table `t`.

```sql
INSERT INTO t VALUES (1, 2), (2, 3), (3, 4), (4, 5), (5, 6);
```

```sql
Query OK, 5 rows affected
```

The following operation uses a non-transactional DML statement to delete rows with values less than the integer 6 on column `v` of table `t`. This statement is split into two SQL statements, with a batch size of 2, sharded by the `id` column and executed.

```sql
BATCH ON id LIMIT 2 DELETE FROM t WHERE v < 6;
```

```sql
+----------------+---------------+
| number of jobs | job status    |
+----------------+---------------+
| 2              | all succeeded |
+----------------+---------------+
1 row in set
```

Check the deletion results of the above non-transactional DML statement.

```sql
SELECT * FROM t;
```

```sql
+----+---+
| id | v |
+----+---+
| 5  | 6 |
+----+---+
1 row in set
```

The following example describes how to use multiple table joins. First, create table `t2` and insert data:

```sql
CREATE TABLE t2(id int, v int, key(id));
INSERT INTO t2 VALUES (1,1), (3,3), (5,5);
```

Then, update the data of table `t2` by joining table `t` and `t2`. Note that you need to specify the shard column along with the complete database name, table name, and column name (`test.t.id`):

```sql
BATCH ON test.t._tidb_rowid LIMIT 1 UPDATE t JOIN t2 ON t.id = t2.id SET t2.id = t2.id+1;
```

Query the results:

```sql
SELECT * FROM t2;
```

```sql
+----+---+
| id | v |
+----+---+
| 1  | 1 |
| 3  | 3 |
| 6  | 5 |
+----+---+
```
### Check the execution progress

During the execution of a non-transactional DML statement, you can view the progress using `SHOW PROCESSLIST`. The `Time` field in the returned result indicates the time consumption of the current batch execution. Logs and slow logs also record the progress of each split statement throughout the non-transactional DML execution. For example:

```sql
SHOW PROCESSLIST;
```

```sql
+------+------+--------------------+--------+---------+------+------------+----------------------------------------------------------------------------------------------------+
| Id   | User | Host               | db     | Command | Time | State      | Info                                                                                               |
+------+------+--------------------+--------+---------+------+------------+----------------------------------------------------------------------------------------------------+
| 1203 | root | 100.64.10.62:52711 | test   | Query   | 0    | autocommit | /* job 506/500000 */ DELETE FROM `test`.`t1` WHERE `test`.`t1`.`_tidb_rowid` BETWEEN 2271 AND 2273 |
| 1209 | root | 100.64.10.62:52735 | <null> | Query   | 0    | autocommit | show full processlist                                                                              |
+------+------+--------------------+--------+---------+------+------------+----------------------------------------------------------------------------------------------------+
```
### Terminate a non-transactional DML statement

To terminate a non-transactional DML statement, you can use `KILL TIDB <processlist_id>`. Then TiDB will cancel all batches after the batch that is currently being executed. You can get the execution result from the log.

For more information about `KILL TIDB`, see the reference [`KILL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill).
