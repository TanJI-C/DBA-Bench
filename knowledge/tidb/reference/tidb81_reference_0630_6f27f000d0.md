# SELECT syntax and syntax element reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-select.md`
- Source Title: `SELECT | TiDB SQL Statement Reference`
- Source Heading Path: `SELECT | SELECT > Synopsis | SELECT > Description of the syntax elements`
- Source Line Ranges: `5-81`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `select`, `syntax`, `optimizer-hints`, `distinct`, `priority`, `sql-cache`, `straight-join`, `from`, `where`, `group-by`, `having`, `order-by`, `limit`, `fetch-first`, `window-functions`, `for-update`, `nowait`, `lock-in-share-mode`, `tablesample`, `resource-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0630_6f27f000d0`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-select.md#select`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c188b0b5233e58c214495b48c3bb0cc4bc16bc88eacc4870a63643b924ee96c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select#select
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-select.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB SELECT statement syntax, supported clauses, modifiers, and lock options such as LIMIT, FETCH FIRST/NEXT, FOR UPDATE NOWAIT, or TABLESAMPLE.
- Retrieval Keywords: SELECT syntax, SelectStmt, SelectStmtBasic, SelectStmtFromDualTable, SelectStmtFromTable, SelectStmtOpts, TableRefsClause, AsOfClause, OrderBy, LIMIT, OFFSET, FETCH FIRST, FETCH NEXT, FOR UPDATE, NOWAIT, LOCK IN SHARE MODE, TABLESAMPLE REGIONS, WindowClause, GROUP BY, HAVING, ORDER BY, STRAIGHT_JOIN, SQL_CACHE, SQL_NO_CACHE, SQL_CALC_FOUND_ROWS, HIGH_PRIORITY, TableOptimizerHints, AS OF TIMESTAMP
- Follow-up Guidance: The content points to related references for Optimizer Hints, Window Function, Optimistic Transaction Mode, Pessimistic Transaction Mode, Difference with MySQL InnoDB, and Resource Control.
- Classification Note: This is a SQL reference chunk because it defines the SELECT grammar and explains each syntax element and modifier.

## Official Source Content

# SELECT

The `SELECT` statement is used to read data from TiDB.
## Synopsis

```ebnf+diagram
SelectStmt ::=
    ( SelectStmtBasic | SelectStmtFromDualTable | SelectStmtFromTable )
    OrderBy? SelectStmtLimit? SelectLockOpt? SelectStmtIntoOption

SelectStmtBasic ::=
    "SELECT" SelectStmtOpts Field ("," Field)* ( "HAVING" Expression)?

SelectStmtFromDualTable ::=
    "SELECT" SelectStmtOpts Field ("," Field)* "FROM" "DUAL" WhereClause?

SelectStmtFromTable ::=
    "SELECT" SelectStmtOpts Field ("," Field)* "FROM" TableRefsClause
    WhereClause? GroupByClause? ( "HAVING" Expression)? WindowClause?

SelectStmtOpts ::=
    TableOptimizerHints DefaultFalseDistictOpt PriorityOpt SelectStmtSQLSmallResult
    SelectStmtSQLBigResult SelectStmtSQLBufferResult SelectStmtSQLCache SelectStmtCalcFoundRows
    SelectStmtStraightJoin

TableRefsClause ::=
    TableRef AsOfClause? ( ',' TableRef AsOfClause? )*

AsOfClause ::=
    'AS' 'OF' 'TIMESTAMP' Expression

SelectStmtLimit ::=
    ("LIMIT" LimitOption ( ("," | "OFFSET") LimitOption )?
| "FETCH" ("FIRST" | "NEXT") LimitOption? ("ROW" | "ROWS") "ONLY" )

SelectLockOpt ::= 
    ( 'FOR' 'UPDATE' ( 'OF' TableList )? 'NOWAIT'?
|   'LOCK' 'IN' 'SHARE' 'MODE' )

TableList ::=
    TableName ( ',' TableName )*

WindowClause ::=
    "WINDOW" WindowDefinition ("," WindowDefinition)*

TableSampleOpt ::=
    'TABLESAMPLE' 'REGIONS' '(' ')'
```
## Description of the syntax elements

|Syntax Element|Description|
|:--------------------- | :-------------------------------------------------- |
|`TableOptimizerHints`| This is the hint to control the behavior of TiDB's optimizer. For more information, refer to [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints). |
|`ALL`, `DISTINCT`, `DISTINCTROW` | The `ALL`, `DISTINCT`/`DISTINCTROW` modifiers specify whether duplicate rows should be returned. ALL (the default) specifies that all matching rows should be returned.|
|`HIGH_PRIORITY` | `HIGH_PRIORITY` gives the current statement higher priority than other statements. |
|`SQL_CALC_FOUND_ROWS`| TiDB does not support this feature, and will return an error unless [`tidb_enable_noop_functions=1`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_noop_functions-new-in-v40) is set. |
|`SQL_CACHE`, `SQL_NO_CACHE` | `SQL_CACHE` and `SQL_NO_CACHE` are used to control whether to cache the request results to the `BlockCache` of TiKV (RocksDB). For a one-time query on a large amount of data, such as the `count(*)` query, it is recommended to fill in `SQL_NO_CACHE` to avoid flushing the hot user data in `BlockCache`. |
|`STRAIGHT_JOIN`| `STRAIGHT_JOIN` forces the optimizer to do a union query in the order of the tables used in the `FROM` clause. When the optimizer chooses a join order that is not good, you can use this syntax to speed up the execution of the query. |
|`select_expr` | Each `select_expr` indicates a column to retrieve. including the column names and expressions. `\*` represents all the columns.|
|`FROM table_references` | The `FROM table_references` clause indicates the table (such as `select * from t;`), or tables (such as `select * from t1 join t2;`) or even 0 tables (such as `select 1+1 from dual;` which is equivalent to `select 1+1;`) from which to retrieve rows.|
|`WHERE where_condition` | The `WHERE` clause, if given, indicates the condition or conditions that rows must satisfy to be selected. The result contains only the data that meets the condition(s).|
|`GROUP BY` | The `GROUP BY` statement is used to group the result-set.|
|`HAVING where_condition` | The `HAVING` clause and the `WHERE` clause are both used to filter the results. The `HAVING` clause filters the results of `GROUP BY`, while the `WHERE` clause filter the results before aggregation. |
|`ORDER BY` | The `ORDER BY` clause is used to sort the data in ascending or descending order, based on columns, expressions or items in the `select_expr` list.|
|`LIMIT` | The `LIMIT` clause can be used to constrain the number of rows. `LIMIT` takes one or two numeric arguments. With one argument, the argument specifies the maximum number of rows to return, the first row to return is the first row of the table by default; with two arguments, the first argument specifies the offset of the first row to return, and the second specifies the maximum number of rows to return. TiDB also supports the `FETCH FIRST/NEXT n ROW/ROWS ONLY` syntax, which has the same effect as `LIMIT n`. You can omit `n` in this syntax and its effect is the same as `LIMIT 1`. |
|`Window window_definition`| This is the syntax for window function, which is usually used to do some analytical computation. For more information, refer to [Window Function](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions). |
| `FOR UPDATE`  | The `SELECT FOR UPDATE` clause locks all the data in the result sets to detect concurrent updates from other transactions. Data that match the query conditions but do not exist in the result sets are not read-locked, such as the row data written by other transactions after the current transaction is started. When TiDB uses the [Optimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/optimistic-transaction), the transaction conflicts are not detected in the statement execution phase. Therefore, the current transaction does not block other transactions from executing `UPDATE`, `DELETE` or `SELECT FOR UPDATE` like other databases such as PostgreSQL. In the committing phase, the rows read by `SELECT FOR UPDATE` are committed in two phases, which means they can also join the conflict detection. If write conflicts occur, the commit fails for all transactions that include the `SELECT FOR UPDATE` clause. If no conflict is detected, the commit succeeds. And a new version is generated for the locked rows, so that write conflicts can be detected when other uncommitted transactions are being committed later. When TiDB uses the [Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction), the behavior is basically the same as other databases. Refer to [Difference with MySQL InnoDB](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#difference-with-mysql-innodb) to see the details. TiDB supports the `NOWAIT` modifier for `FOR UPDATE`. See [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction#behaviors) for details. |
|`LOCK IN SHARE MODE` | To guarantee compatibility, TiDB parses these three modifiers, but will ignore them. |
| `TABLESAMPLE` | To get a sample of rows from the table. |

> **Note:**
>
> Starting from v6.6.0, TiDB supports [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control). You can use this feature to execute SQL statements with different priorities in different resource groups. By configuring proper quotas and priorities for these resource groups, you can gain better scheduling control for SQL statements with different priorities. When resource control is enabled, statement priority (`HIGH_PRIORITY`) will no longer take effect. It is recommended that you use [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) to manage resource usage for different SQL statements.
