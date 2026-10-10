# SHOW PROFILES behavior, syntax, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-profiles.md`
- Source Title: `SHOW PROFILES`
- Source Heading Path: `SHOW PROFILES | SHOW PROFILES > Synopsis | SHOW PROFILES > Examples | SHOW PROFILES > MySQL compatibility`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show profiles`, `sql syntax`, `mysql compatibility`, `empty result`, `statement summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0671_bfe5ce1614`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-profiles.md#show-profiles`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5f6debbaf2a80a08131b13772b15c05f3c96158013ae594830c4fa781857a5a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-profiles#show-profiles
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-profiles.md

## Retrieval Guidance

- Use When: Use this chunk when someone asks about the behavior, syntax, or MySQL compatibility of the `SHOW PROFILES` statement in TiDB.
- Retrieval Keywords: SHOW PROFILES, ShowProfilesStmt, SHOW PROFILES LIKE, SHOW PROFILES WHERE, empty result, Empty set (0.00 sec), MySQL compatibility, statement summary tables, SQL performance issues
- Follow-up Guidance: The source also points to statement summary tables as an alternative to help understand SQL performance issues.
- Classification Note: This is a SQL reference chunk because the official content defines the `SHOW PROFILES` syntax, shows an example result, and states its compatibility behavior in TiDB.

## Official Source Content

# SHOW PROFILES

The `SHOW PROFILES` statement currently only returns an empty result.
## Synopsis

```ebnf+diagram
ShowProfilesStmt ::=
    "SHOW" "PROFILES" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

```sql
SHOW PROFILES;
```

```
Empty set (0.00 sec)
```
## MySQL compatibility

This statement is included only for compatibility with MySQL. Executing `SHOW PROFILES` always returns an empty result.

As an alternative, TiDB provides [statement summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables) to help understand SQL performance issues.
