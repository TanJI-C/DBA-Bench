# SHUTDOWN statement syntax, usage, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-shutdown.md`
- Source Title: `SHUTDOWN`
- Source Heading Path: `SHUTDOWN | SHUTDOWN > Synopsis | SHUTDOWN > Examples | SHUTDOWN > MySQL compatibility`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `shutdown`, `privileges`, `syntax`, `examples`, `mysql-compatibility`, `distributed-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0689_effd61c715`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-shutdown.md#shutdown`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e2c25e7b673f2276523b9f16e7c70ee5104c6f089e05fd62faceced2f648da04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-shutdown#shutdown
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-shutdown.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the SQL SHUTDOWN statement syntax, required SHUTDOWN privilege, example execution, or its TiDB distributed behavior versus MySQL.
- Retrieval Keywords: SHUTDOWN, ShutdownStmt, SHUTDOWN privilege, SHUTDOWN;, Query OK, 0 rows affected, MySQL compatibility, distributed database, stops the client-connected TiDB instance, not the entire TiDB cluster, TiDB Self-Managed, not available on TiDB Cloud
- Follow-up Guidance: The content notes that in TiDB the shutdown operation stops the client-connected TiDB instance rather than the entire TiDB cluster.
- Classification Note: This is reference content because it defines the SHUTDOWN statement syntax, privilege requirement, example output, and compatibility note for SQL in TiDB.

## Official Source Content

# SHUTDOWN

The `SHUTDOWN` statement is used to perform a shutdown operation in TiDB. Execution of the `SHUTDOWN` statement requires the user to have `SHUTDOWN privilege`.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).
## Synopsis

```ebnf+diagram
ShutdownStmt ::=
    "SHUTDOWN"
```
## Examples

```sql
SHUTDOWN;
```

```
Query OK, 0 rows affected (0.00 sec)
```
## MySQL compatibility

> **Note:**
>
> Because TiDB is a distributed database, the shutdown operation in TiDB stops the client-connected TiDB instance, not the entire TiDB cluster.

The `SHUTDOWN` statement is partly compatible with MySQL. If you encounter any compatibility issues, you can [report a bug](https://docs.pingcap.com/tidb/stable/support).
