# SHOW CONFIG syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-config.md`
- Source Title: `SHOW CONFIG`
- Source Heading Path: `SHOW CONFIG | SHOW CONFIG > Synopsis | SHOW CONFIG > Examples | SHOW CONFIG > MySQL compatibility | SHOW CONFIG > See also`
- Source Line Ranges: `5-82`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show config`, `sql syntax`, `configuration inspection`, `like clause`, `where clause`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0649_70366161db`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-config.md#show-config`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ad7912645e940b2b6bcaebb0e2873cc68d8e13247d7537163694e532fc1f72f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-config#show-config
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL syntax, filtering options, or examples for inspecting current configuration values of TiDB components with SHOW CONFIG.
- Retrieval Keywords: SHOW CONFIG, ShowConfigStmt, SHOW CONFIG LIKE, SHOW CONFIG WHERE, SHOW CONFIG WHERE type = 'tidb' AND name = 'advertise-address', SHOW CONFIG LIKE 'tidb', Type Instance Name Value, SHOW VARIABLES, TiDB extension to MySQL syntax
- Follow-up Guidance: If the goal is to obtain system variable information instead of component configuration, the source points to SHOW VARIABLES.
- Classification Note: This is reference content because it defines the SHOW CONFIG syntax, documents LIKE and WHERE forms, provides example queries and result columns, and notes MySQL compatibility and scope.

## Official Source Content

# SHOW CONFIG

The `SHOW CONFIG` statement is used to show the current configuration of various components of TiDB. Note that the configuration and system variables act on different dimensions and should not be mixed up. If you want to obtain the system variable information, use the [SHOW VARIABLES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-variables) syntax.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/). 
## Synopsis

```ebnf+diagram
ShowConfigStmt ::=
    "SHOW" "CONFIG" ShowLikeOrWhere?

ShowLikeOrWhere ::=
    "LIKE" SimpleExpr
|   "WHERE" Expression
```
## Examples

Show all configurations:

```sql
SHOW CONFIG;
```

```
+------+----------------+-------------------------------------------------+---------------------------------------------------------------------+
| Type | Instance       | Name                                            | Value                                                               |
+------+----------------+-------------------------------------------------+---------------------------------------------------------------------+
| tidb | 127.0.0.1:4000 | advertise-address                               | 127.0.0.1                                                           |
| tidb | 127.0.0.1:4000 | binlog.binlog-socket                            |                                                                     |
| tidb | 127.0.0.1:4000 | binlog.enable                                   | false                                                               |
...
120 rows in set (0.01 sec)
```

Show the configuration where the `type` is `tidb`:

```sql
SHOW CONFIG WHERE type = 'tidb' AND name = 'advertise-address';
```

```
+------+----------------+-------------------+-----------+
| Type | Instance       | Name              | Value     |
+------+----------------+-------------------+-----------+
| tidb | 127.0.0.1:4000 | advertise-address | 127.0.0.1 |
+------+----------------+-------------------+-----------+
1 row in set (0.05 sec)
```

You can also use the `LIKE` clause to show the configuration where the `type` is `tidb`:

```sql
SHOW CONFIG LIKE 'tidb';
```

```
+------+----------------+-------------------------------------------------+---------------------------------------------------------------------+
| Type | Instance       | Name                                            | Value                                                               |
+------+----------------+-------------------------------------------------+---------------------------------------------------------------------+
| tidb | 127.0.0.1:4000 | advertise-address                               | 127.0.0.1                                                           |
| tidb | 127.0.0.1:4000 | binlog.binlog-socket                            |                                                                     |
| tidb | 127.0.0.1:4000 | binlog.enable                                   | false                                                               |
...
40 rows in set (0.01 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [SHOW VARIABLES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-variables)
