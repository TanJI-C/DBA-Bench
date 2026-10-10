# SHOW ENGINES syntax, example output, and compatibility note

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-engines.md`
- Source Title: `SHOW ENGINES | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW ENGINES | SHOW ENGINES > Synopsis | SHOW ENGINES > Examples | SHOW ENGINES > MySQL compatibility`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `show engines`, `sql syntax`, `mysql compatibility`, `storage engines`, `example output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0658_356f9dee7b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-engines.md#show-engines`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d6994dd0f0d16827c7345b8bc7ad581b4ef6d383cdc4e2dcdf51c39550eec215`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-engines#show-engines
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-engines.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about the SHOW ENGINES statement syntax, example output, or what engine TiDB reports for MySQL compatibility.
- Retrieval Keywords: SHOW ENGINES, ShowEnginesStmt, SHOW ENGINES LIKE, SHOW ENGINES WHERE, storage engines, MySQL compatibility, InnoDB, TiKV, This statement will always only return InnoDB as the supported engine
- Follow-up Guidance: The content also notes that internally TiDB will typically use TiKV as the storage engine.
- Classification Note: This is reference content because it defines the SHOW ENGINES syntax, shows example SQL output, and states the MySQL compatibility behavior described in the official documentation.

## Official Source Content

# SHOW ENGINES

This statement is used to list all supported storage engines. The syntax is included only for compatibility with MySQL.
## Synopsis

```ebnf+diagram
ShowEnginesStmt ::=
    "SHOW" "ENGINES" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
mysql> SHOW ENGINES;
+--------+---------+------------------------------------------------------------+--------------+------+------------+
| Engine | Support | Comment                                                    | Transactions | XA   | Savepoints |
+--------+---------+------------------------------------------------------------+--------------+------+------------+
| InnoDB | DEFAULT | Supports transactions, row-level locking, and foreign keys | YES          | YES  | YES        |
+--------+---------+------------------------------------------------------------+--------------+------+------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

* This statement will always only return InnoDB as the supported engine. Internally, TiDB will typically use [TiKV](https://docs.pingcap.com/tidb/stable/tikv-overview) as the storage engine.
