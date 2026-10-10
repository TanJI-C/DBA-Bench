# Common issues with non-transactional DML execution

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements > Common issues | Non-Transactional DML Statements > Common issues > Executing a multiple table joins statement results in the `Unknown column xxx in 'where clause'` error | Non-Transactional DML Statements > Common issues > The `Unknown column '<alias>.<column>' in 'where clause'` error occurs when using table aliases in non-transactional DML statements | Non-Transactional DML Statements > Common issues > The actual batch size is not the same as the specified batch size | Non-Transactional DML Statements > Common issues > The `Failed to restore the delete statement, probably because of unsupported type of the shard column` error occurs during execution | Non-Transactional DML Statements > Common issues > Non-transactional `DELETE` has "exceptional" behavior that is not equivalent to ordinary `DELETE``
- Source Line Ranges: `329-422`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `troubleshooting`, `joins`, `aliases`, `dry-run`, `batch-size`, `shard-column`, `delete`, `concurrent-writes`, `unsupported-types`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0056_9ab69366cb`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#common-issues`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f0106f1d52394c17a884557af466d7963c1bf2117abee7b3ff46fab599723e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#common-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting non-transactional DML errors, rewritten statement behavior, batch size differences, unsupported shard column types, or exceptional DELETE results.
- Retrieval Keywords: Unknown column xxx in 'where clause', Unknown column '<alias>.<column>' in 'where clause', multiple table joins, table aliases, DRY RUN QUERY, DRY RUN, actual batch size is not the same as the specified batch size, Failed to restore the delete statement, probably because of unsupported type of the shard column, unsupported type of the shard column, ENUM, BIT, SET, JSON, non-transactional DELETE exceptional behavior, concurrent writes, non-deterministic operations, shard column
- Follow-up Guidance: This content points to DRY RUN QUERY and DRY RUN for previewing rewritten statements and notes support links when the unsupported shard column type error occurs unexpectedly.
- Classification Note: This is diagnosis content because it lists common issues, specific error messages, causes, and troubleshooting guidance for non-transactional DML execution.

## Official Source Content

## Common issues
### Executing a multiple table joins statement results in the `Unknown column xxx in 'where clause'` error

This error occurs when the `WHERE` clause concatenated in a query involves tables other than the table in which the [shard column](#parameter-description) is defined. For example, in the following SQL statement, the shard column is `t2.id` and it is defined in table `t2`, but the `WHERE` clause involves table `t2` and `t3`.

```sql
BATCH ON test.t2.id LIMIT 1 
INSERT INTO t 
SELECT t2.id, t2.v, t3.id FROM t2, t3 WHERE t2.id = t3.id
```

```sql
(1054, "Unknown column 't3.id' in 'where clause'")
```

If the error occurs, you can print the query statement for confirmation by using `DRY RUN QUERY`. For example:

```sql
BATCH ON test.t2.id LIMIT 1 
DRY RUN QUERY INSERT INTO t 
SELECT t2.id, t2.v, t3.id FROM t2, t3 WHERE t2.id = t3.id
```

To avoid the error, you can move the condition related to other tables in the `WHERE` clause to the `ON` condition in the `JOIN` clause. For example:

```sql
BATCH ON test.t2.id LIMIT 1 
INSERT INTO t 
SELECT t2.id, t2.v, t3.id FROM t2 JOIN t3 ON t2.id = t3.id
```

```
+----------------+---------------+
| number of jobs | job status    |
+----------------+---------------+
| 0              | all succeeded |
+----------------+---------------+
```
### The `Unknown column '<alias>.<column>' in 'where clause'` error occurs when using table aliases in non-transactional DML statements

When you execute a non-transactional DML statement, TiDB internally constructs a query for dividing batches and then generates the actual split execution statements. You can use [`DRY RUN QUERY`](https://docs.pingcap.com/tidb/stable/non-transactional-dml#query-the-batch-dividing-statement) and [`DRY RUN`](https://docs.pingcap.com/tidb/stable/non-transactional-dml#query-the-statements-corresponding-to-the-first-and-the-last-batches) to view these two types of statements, respectively.

In the current version, the rewritten statements might not preserve the table aliases from the original DML statement. Therefore, if you use the `<alias>.<column>` format to reference columns in a `WHERE` clause or other expressions, an `Unknown column` error might occur.

For example, the following statement might return an error in some cases:

```sql
BATCH ON t_old.id LIMIT 5000
INSERT INTO t_new
SELECT * FROM t_old AS t
WHERE t.c1 IS NULL;
```

To avoid this error, follow these recommendations:

- Avoid using table aliases in non-transactional DML statements. For example, rewrite `t.c1` as `c1` or `t_old.c1`.
- When specifying the [shard column](#parameter-description), do not use table aliases. For example, rewrite `BATCH ON t.id` as `BATCH ON db.t_old.id` or `BATCH ON t_old.id`.
- Before execution, use `DRY RUN QUERY` or `DRY RUN` to preview the rewritten statements and verify that they meet your expectations.
### The actual batch size is not the same as the specified batch size

During the execution of a non-transactional DML statement, the size of data to be processed in the last batch might be smaller than the specified batch size.

When **duplicated values exist in the shard column**, each batch will contain all the duplicated values of the last element of the shard column in this batch. Therefore, the number of rows in this batch might be greater than the specified batch size.

In addition, when other concurrent writes occur, the number of rows processed in each batch might be different from the specified batch size.
### The `Failed to restore the delete statement, probably because of unsupported type of the shard column` error occurs during execution

The shard column does not support `ENUM`, `BIT`, `SET`, `JSON` types. Try to specify a new shard column. It is recommended to use an integer or string type column.

If the error occurs when the selected shard column is not one of these unsupported types, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

If the error occurs when the selected shard column is not one of these unsupported types, [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### Non-transactional `DELETE` has "exceptional" behavior that is not equivalent to ordinary `DELETE`

A non-transactional DML statement is not equivalent to the original form of this DML statement, which might have the following reasons:

- There are other concurrent writes.
- The non-transactional DML statement modifies a value that the statement itself will read.
- The SQL statement executed in each batch might cause a different execution plan and expression calculation order because the `WHERE` condition is changed. Therefore, the execution result might be different from the original statement.
- The DML statements contain non-deterministic operations.
