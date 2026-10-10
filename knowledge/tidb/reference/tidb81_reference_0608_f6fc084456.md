# LOAD STATS syntax and usage

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-load-stats.md`
- Source Title: `LOAD STATS`
- Source Heading Path: `LOAD STATS | LOAD STATS > Synopsis | LOAD STATS > Examples | LOAD STATS > MySQL compatibility | LOAD STATS > See also`
- Source Line Ranges: `5-45`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `statistics`, `sql-syntax`, `load-stats`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0608_f6fc084456`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-load-stats.md#load-stats`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d13ad101ea7c0640a0a458163321a9354c415140fecad7a20cf0a6d3db242764`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-stats#load-stats
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-load-stats.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for the SQL syntax, example usage, or compatibility note for loading statistics into TiDB with the LOAD STATS statement.
- Retrieval Keywords: LOAD STATS, LoadStatsStmt ::= 'LOAD' 'STATS' stringLit, load the statistics into TiDB, LOAD STATS '/tmp/stats.json';, stats/dump/${db_name}/${table_name}, tidb-server-status-port, absolute path or relative path, MySQL compatibility, TiDB extension to MySQL syntax
- Follow-up Guidance: The content also points to downloading statistics from http://${tidb-server-ip}:${tidb-server-status-port}/stats/dump/${db_name}/${table_name} and notes that a relative stats path is resolved from where tidb-server is started.
- Classification Note: This is reference content because it defines the LOAD STATS statement syntax, gives a concrete SQL example, and states its MySQL compatibility status.

## Official Source Content

# LOAD STATS

The `LOAD STATS` statement is used to load the statistics into TiDB.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
LoadStatsStmt ::=
    'LOAD' 'STATS' stringLit
```
## Examples

You can access the address `http://${tidb-server-ip}:${tidb-server-status-port}/stats/dump/${db_name}/${table_name}` to download the TiDB instance's statistics.

You can also use `LOAD STATS ${stats_path}` to load the specific statistics file.

The `${stats_path}` can be an absolute path or a relative path. If you use a relative path, the corresponding file is found starting from the path where `tidb-server` is started. Here is an example:

```sql
LOAD STATS '/tmp/stats.json';
```

```
Query OK, 0 rows affected (0.00 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [Statistics](https://docs.pingcap.com/tidb/stable/statistics)
