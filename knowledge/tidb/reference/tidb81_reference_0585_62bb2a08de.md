# EXPLAIN ANALYZE syntax, output, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain-analyze.md`
- Source Title: `EXPLAIN ANALYZE | TiDB SQL Statement Reference`
- Source Heading Path: `EXPLAIN ANALYZE | EXPLAIN ANALYZE > Synopsis | EXPLAIN ANALYZE > EXPLAIN ANALYZE output format | EXPLAIN ANALYZE > Examples`
- Source Line Ranges: `5-98`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain analyze`, `sql syntax`, `output format`, `execution plan`, `actrows`, `execution info`, `memory`, `disk`, `examples`, `analyze table`, `dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0585_62bb2a08de`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain-analyze.md#explain-analyze`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `128c3efc05bebf7bf78894881738ac1f8ac2788d58ebcfad43dc964cadfed7d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze#explain-analyze
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain-analyze.md

## Retrieval Guidance

- Use When: Use this chunk when you need the EXPLAIN ANALYZE syntax, the meaning of output columns such as actRows, execution info, memory, and disk, or example output for SELECT statements.
- Retrieval Keywords: EXPLAIN ANALYZE, DESCRIBE, DESC, ExplainStmt, ExplainableStmt, SelectStmt, DeleteFromStmt, UpdateStmt, InsertIntoStmt, ReplaceIntoStmt, UnionStmt, actRows, execution info, memory, disk, Point_Get_1, TableReader_5, TableFullScan_4, cop[tikv], ANALYZE TABLE, DML statements cannot be shown yet, EXPLAIN ANALYZE SELECT * FROM t1 WHERE id = 1, EXPLAIN ANALYZE SELECT * FROM t1
- Follow-up Guidance: If the estimates differ significantly from the actual values, the content says you should consider running ANALYZE TABLE on the affected tables.
- Classification Note: This is reference content because it defines EXPLAIN ANALYZE syntax, explains output fields, and shows example execution plan output.

## Official Source Content

# EXPLAIN ANALYZE

The `EXPLAIN ANALYZE` statement works similar to `EXPLAIN`, with the major difference being that it will actually execute the statement. This allows you to compare the estimates used as part of query planning to actual values encountered during execution. If the estimates differ significantly from the actual values, you should consider running `ANALYZE TABLE` on the affected tables.

> **Note:**
>
> When you use `EXPLAIN ANALYZE` to execute DML statements, modification to data is normally executed. Currently, the execution plan for DML statements **cannot** be shown yet.
## Synopsis

```ebnf+diagram
ExplainSym ::=
    'EXPLAIN'
|   'DESCRIBE'
|    'DESC'

ExplainStmt ::=
    ExplainSym ( TableName ColumnName? | 'ANALYZE'? ExplainableStmt | 'FOR' 'CONNECTION' NUM | 'FORMAT' '=' ( stringLit | ExplainFormatType ) ( 'FOR' 'CONNECTION' NUM | ExplainableStmt ) )

ExplainableStmt ::=
    SelectStmt
|   DeleteFromStmt
|   UpdateStmt
|   InsertIntoStmt
|   ReplaceIntoStmt
|   UnionStmt
```
## EXPLAIN ANALYZE output format

Different from `EXPLAIN`, `EXPLAIN ANALYZE` executes the corresponding SQL statement, records its runtime information, and returns the information together with the execution plan. Therefore, you can regard `EXPLAIN ANALYZE` as an extension of the `EXPLAIN` statement. Compared to `EXPLAIN` (for debugging query execution), the return results of `EXPLAIN ANALYZE` also include columns of information such as `actRows`, `execution info`, `memory`, and `disk`. The details of these columns are shown as follows:

| attribute name          | description |
|:----------------|:---------------------------------|
| actRows       | Number of rows output by the operator. |
| execution info  | Execution information of the operator. `time` represents the total `wall time` from entering the operator to leaving the operator, including the total execution time of all sub-operators. If the operator is called many times by the parent operator (in loops), then the time refers to the accumulated time. `loops` is the number of times the current operator is called by the parent operator. |
| memory  | Memory space occupied by the operator. |
| disk  | Disk space occupied by the operator. |
## Examples

```sql
CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, c1 INT NOT NULL);
```

```sql
Query OK, 0 rows affected (0.12 sec)
```

```sql
INSERT INTO t1 (c1) VALUES (1), (2), (3);
```

```sql
Query OK, 3 rows affected (0.02 sec)
Records: 3  Duplicates: 0  Warnings: 0
```

```sql
EXPLAIN ANALYZE SELECT * FROM t1 WHERE id = 1;
```

```sql
+-------------+---------+---------+------+---------------+----------------------------------------------------------------+---------------+--------+------+
| id          | estRows | actRows | task | access object | execution info                                                 | operator info | memory | disk |
+-------------+---------+---------+------+---------------+----------------------------------------------------------------+---------------+--------+------+
| Point_Get_1 | 1.00    | 1       | root | table:t1      | time:757.205µs, loops:2, Get:{num_rpc:1, total_time:697.051µs} | handle:1      | N/A    | N/A  |
+-------------+---------+---------+------+---------------+----------------------------------------------------------------+---------------+--------+------+
1 row in set (0.01 sec)
```

```sql
EXPLAIN ANALYZE SELECT * FROM t1;
```

```sql
+-------------------+----------+---------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+-----------+------+
| id                | estRows  | actRows | task      | access object | execution info                                                                                                                                                                                                                            | operator info                  | memory    | disk |
+-------------------+----------+---------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+-----------+------+
| TableReader_5     | 10000.00 | 3       | root      |               | time:278.2µs, loops:2, cop_task: {num: 1, max: 437.6µs, proc_keys: 3, copr_cache_hit_ratio: 0.00}, rpc_info:{Cop:{num_rpc:1, total_time:423.9µs}}                                                                                         | data:TableFullScan_4           | 251 Bytes | N/A  |
| └─TableFullScan_4 | 10000.00 | 3       | cop[tikv] | table:t1      | tikv_task:{time:0s, loops:1}, scan_detail: {total_process_keys: 3, total_process_keys_size: 111, total_keys: 4, rocksdb: {delete_skipped_count: 0, key_skipped_count: 3, block: {cache_hit_count: 0, read_count: 0, read_byte: 0 Bytes}}} | keep order:false, stats:pseudo | N/A       | N/A  |
+-------------------+----------+---------+-----------+---------------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------------------------------+-----------+------+
2 rows in set (0.00 sec)
```
