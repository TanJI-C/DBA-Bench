# TRACE statement syntax, formats, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-trace.md`
- Source Title: `TRACE | TiDB SQL Statement Reference`
- Source Heading Path: `TRACE | TRACE > Synopsis | TRACE > Examples | TRACE > Examples > Row | TRACE > Examples > JSON | TRACE > Examples > Log | TRACE > MySQL compatibility | TRACE > See also`
- Source Line Ranges: `5-101`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `trace`, `sql-statement`, `syntax`, `formats`, `row-output`, `json-output`, `log-output`, `mysql-compatibility`, `status-port`, `trace-viewer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0695_6cafb5c920`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-trace.md#trace`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bcad1279d9c9081a7964be81440ae9865aab4a9cf1146dc3e928950d478864b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-trace#trace
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-trace.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TRACE statement syntax, supported FORMAT options, traceable statement types, or example outputs in row, json, or log format.
- Retrieval Keywords: TRACE, TraceStmt, TracableStmt, FORMAT='row', FORMAT='json', FORMAT='log', TRACE FORMAT='row' SELECT * FROM mysql.user;, TRACE FORMAT='json' SELECT * FROM mysql.user;, TRACE FORMAT='log' SELECT * FROM mysql.user;, row output in a tree format, structured output in JSON format, log based output, status port, trace viewer, session.Execute, executor.Compile, TableReaderExecutor.Open, distsql.Select, RPCClient.SendRequest, session.ExecuteStmt, regionRequest.SendReqCtx, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also points to EXPLAIN ANALYZE in the See also section.
- Classification Note: This is classified as reference content because it defines the TRACE statement syntax, lists supported formats and traceable statements, and shows official example outputs and compatibility notes.

## Official Source Content

# TRACE

The `TRACE` statement provides detailed information about query execution. It is intended to be viewed through a Graphical interface exposed by the TiDB server's status port.
## Synopsis

```ebnf+diagram
TraceStmt ::=
    "TRACE" ( "FORMAT" "=" stringLit )? TracableStmt

TracableStmt ::=
    ( SelectStmt | DeleteFromStmt | UpdateStmt | InsertIntoStmt | ReplaceIntoStmt | UnionStmt | LoadDataStmt | BeginTransactionStmt | CommitStmt | RollbackStmt | SetStmt )
```

| Format | Description                        |
|--------|------------------------------------|
| row    | Output in a tree format            |
| json   | Structured output in JSON format   |
| log    | Log based output                   |
## Examples
### Row

```sql
TRACE FORMAT='row' SELECT * FROM mysql.user;
```

```
+--------------------------------------------+-----------------+------------+
| operation                                  | startTS         | duration   |
+--------------------------------------------+-----------------+------------+
| trace                                      | 17:03:31.938237 | 886.086µs  |
|   ├─session.Execute                        | 17:03:31.938247 | 507.812µs  |
|   │ ├─session.ParseSQL                     | 17:03:31.938254 | 22.504µs   |
|   │ ├─executor.Compile                     | 17:03:31.938321 | 278.931µs  |
|   │ │ └─session.getTxnFuture               | 17:03:31.938337 | 1.515µs    |
|   │ └─session.runStmt                      | 17:03:31.938613 | 109.578µs  |
|   │   ├─TableReaderExecutor.Open           | 17:03:31.938645 | 50.657µs   |
|   │   │ └─distsql.Select                   | 17:03:31.938666 | 21.066µs   |
|   │   │   └─RPCClient.SendRequest          | 17:03:31.938799 | 158.411µs  |
|   │   └─session.CommitTxn                  | 17:03:31.938705 | 12.06µs    |
|   │     └─session.doCommitWitRetry         | 17:03:31.938709 | 2.437µs    |
|   ├─*executor.TableReaderExecutor.Next     | 17:03:31.938781 | 224.327µs  |
|   └─*executor.TableReaderExecutor.Next     | 17:03:31.939019 | 6.266µs    |
+--------------------------------------------+-----------------+------------+
13 rows in set (0.00 sec)
```
### JSON

```sql
TRACE FORMAT='json' SELECT * FROM mysql.user;
```

The JSON formatted trace can be pasted into the trace viewer, which is accessed via the TiDB status port:

![TiDB Trace Viewer-1](/media/trace-paste.png)

![TiDB Trace Viewer-2](/media/trace-view.png)
### Log

```sql
TRACE FORMAT='log' SELECT * FROM mysql.user;
```

```
+----------------------------+--------------------------------------------------------+------+------------------------------------+
| time                       | event                                                  | tags | spanName                           |
+----------------------------+--------------------------------------------------------+------+------------------------------------+
| 2024-04-08 08:41:47.358734 | --- start span trace ----                              |      | trace                              |
| 2024-04-08 08:41:47.358737 | --- start span session.ExecuteStmt ----                |      | session.ExecuteStmt                |
| 2024-04-08 08:41:47.358746 | --- start span executor.Compile ----                   |      | executor.Compile                   |
| 2024-04-08 08:41:47.358984 | --- start span session.runStmt ----                    |      | session.runStmt                    |
| 2024-04-08 08:41:47.359035 | --- start span TableReaderExecutor.Open ----           |      | TableReaderExecutor.Open           |
| 2024-04-08 08:41:47.359047 | --- start span distsql.Select ----                     |      | distsql.Select                     |
| 2024-04-08 08:41:47.359073 | --- start span *executor.TableReaderExecutor.Next ---- |      | *executor.TableReaderExecutor.Next |
| 2024-04-08 08:41:47.359077 | table scan table: user, range: [[-inf,+inf]]           |      | *executor.TableReaderExecutor.Next |
| 2024-04-08 08:41:47.359094 | --- start span regionRequest.SendReqCtx ----           |      | regionRequest.SendReqCtx           |
| 2024-04-08 08:41:47.359098 | send Cop request to region 16 at store1                |      | regionRequest.SendReqCtx           |
| 2024-04-08 08:41:47.359237 | --- start span *executor.TableReaderExecutor.Next ---- |      | *executor.TableReaderExecutor.Next |
| 2024-04-08 08:41:47.359240 | table scan table: user, range: [[-inf,+inf]]           |      | *executor.TableReaderExecutor.Next |
| 2024-04-08 08:41:47.359242 | execute done, ReturnRow: 1, ModifyRow: 0               |      | trace                              |
| 2024-04-08 08:41:47.359252 | execute done, modify row: 0                            |      | trace                              |
+----------------------------+--------------------------------------------------------+------+------------------------------------+
14 rows in set (0.0008 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [EXPLAIN ANALYZE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze)
