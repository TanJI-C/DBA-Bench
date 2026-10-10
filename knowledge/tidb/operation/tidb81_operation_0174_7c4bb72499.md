# Query split statements and apply best practices for non-transactional DML

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements > Usage examples > Query the batch-dividing statement | Non-Transactional DML Statements > Usage examples > Query the statements corresponding to the first and the last batches | Non-Transactional DML Statements > Usage examples > Use the optimizer hint | Non-Transactional DML Statements > Best practices`
- Source Line Ranges: `192-257`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `non-transactional dml`, `dry run`, `dry run query`, `optimizer hint`, `batch splitting`, `best practices`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0174_7c4bb72499`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#query-the-batch-dividing-statement`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d2aca620bc2ac91960b4fac6541ddebb33dd3a4377d54ef9032bbadf53f2529`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#query-the-batch-dividing-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this content when you need to inspect how a non-transactional DML statement is split, see the batch-dividing query or first and last split statements with DRY RUN QUERY or DRY RUN, check optimizer hint placement for non-transactional DELETE, or review the documented best-practice workflow.
- Retrieval Keywords: DRY RUN QUERY, DRY RUN, BATCH ON id LIMIT 2 DELETE FROM t WHERE v < 6, BATCH ON id LIMIT 2 DRY RUN QUERY DELETE FROM t WHERE v < 6, BATCH ON id LIMIT 2 DRY RUN DELETE FROM t WHERE v < 6, query the batch-dividing statement, query the statements corresponding to the first and the last batches, split statement examples, optimizer hint, DELETE /*+ USE_INDEX(t)*/, non-transactional DELETE statement, best practices, execute the query manually, check the split statements and the execution plans, failed data range from the error message or log
- Follow-up Guidance: The documented follow-up is to confirm the affected data range with DRY RUN QUERY, check split statements and execution plans with DRY RUN, then execute the non-transactional DML statement and use the failed data range from the error message or log for retry or manual handling if an error occurs.
- Classification Note: This chunk is classified as operation content because it shows usage examples and a step-by-step best-practice workflow for querying and validating non-transactional DML batch splitting.

## Official Source Content

### Query the batch-dividing statement

During the execution of a non-transactional DML statement, a statement is internally used to divide the DML statement into multiple batches. To query this batch-dividing statement, you can add `DRY RUN QUERY` to this non-transactional DML statement. Then TiDB will not execute this query and the subsequent DML operations.

The following statement queries the batch-dividing statement during the execution of `BATCH ON id LIMIT 2 DELETE FROM t WHERE v < 6`:

```sql
BATCH ON id LIMIT 2 DRY RUN QUERY DELETE FROM t WHERE v < 6;
```

```sql
+--------------------------------------------------------------------------------+
| query statement                                                                |
+--------------------------------------------------------------------------------+
| SELECT `id` FROM `test`.`t` WHERE (`v` < 6) ORDER BY IF(ISNULL(`id`),0,1),`id` |
+--------------------------------------------------------------------------------+
1 row in set
```
### Query the statements corresponding to the first and the last batches

To query the actual DML statements corresponding to the first and the last batches in a non-transactional DML statement, you can add `DRY RUN` to this non-transactional DML statement. Then, TiDB only divides batches and does not execute these SQL statements. Because there might be many batches, not all batches are displayed, and only the first one and the last one are displayed.

```sql
BATCH ON id LIMIT 2 DRY RUN DELETE FROM t WHERE v < 6;
```

```sql
+-------------------------------------------------------------------+
| split statement examples                                          |
+-------------------------------------------------------------------+
| DELETE FROM `test`.`t` WHERE (`id` BETWEEN 1 AND 2 AND (`v` < 6)) |
| DELETE FROM `test`.`t` WHERE (`id` BETWEEN 3 AND 4 AND (`v` < 6)) |
+-------------------------------------------------------------------+
2 rows in set
```
### Use the optimizer hint

If an optimizer hint is originally supported in the `DELETE` statement, the optimizer hint is also supported in the non-transactional `DELETE` statement. The position of the hint is the same as that in the ordinary `DELETE` statement:

```sql
BATCH ON id LIMIT 2 DELETE /*+ USE_INDEX(t)*/ FROM t WHERE v < 6;
```
## Best practices

To use a non-transactional DML statement, the following steps are recommended:

1. Select an appropriate [shard column](#parameter-description). Integer or string types are recommended.
2. Add `DRY RUN QUERY` to the non-transactional DML statement, execute the query manually, and confirm whether the data range affected by the DML statement is roughly correct.
3. Add `DRY RUN` to the non-transactional DML statement, execute the query manually, and check the split statements and the execution plans. You need to pay attention to the following points:

    - Whether the split statement can read the result written by the previous statement, which might cause an anomaly.
    - The index selectivity.
    - Whether the shard column automatically selected by TiDB will be modified.

4. Execute the non-transactional DML statement.
5. If an error is reported, get the specific failed data range from the error message or log, and retry or handle it manually.
