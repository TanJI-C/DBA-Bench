# SHOW PLUGINS syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-plugins.md`
- Source Title: `SHOW PLUGINS`
- Source Heading Path: `SHOW PLUGINS | SHOW PLUGINS > Synopsis | SHOW PLUGINS > Examples | SHOW PLUGINS > MySQL compatibility | SHOW PLUGINS > See also`
- Source Line Ranges: `5-55`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `show plugins`, `plugin metadata`, `sql syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0668_9635476f1b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-plugins.md#show-plugins`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `477154f693ff27878fa3eedb65316f04078bd03fdf068e9b498c353e1cb6ea37`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-plugins#show-plugins
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-plugins.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about the SQL statement that lists installed TiDB plugins, including plugin status and version information, or its syntax and examples.
- Retrieval Keywords: SHOW PLUGINS, ShowPluginsStmt, SHOW PLUGINS LIKE 'a%', show all plugins installed in TiDB, plugin status, version information, Name Status Type Library License Version, MySQL compatibility, ADMIN PLUGINS
- Follow-up Guidance: The page also points to the related `ADMIN PLUGINS` statement and notes that `SHOW PLUGINS` is fully compatible with MySQL.
- Classification Note: This is reference content because it defines the `SHOW PLUGINS` statement, shows its synopsis and example output, and states a compatibility note and availability note.

## Official Source Content

# SHOW PLUGINS

`SHOW PLUGINS` shows all plugins installed in TiDB, including each plugin's status and version information.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
ShowPluginsStmt ::=
    "SHOW" "PLUGINS" ShowLikeOrWhere?
```
## Examples

```sql
SHOW PLUGINS;
```

```
+-------+--------------+-------+-----------------------------+---------+---------+
| Name  | Status       | Type  | Library                     | License | Version |
+-------+--------------+-------+-----------------------------+---------+---------+
| audit | Ready-enable | Audit | /tmp/tidb/plugin/audit-1.so |         | 1       |
+-------+--------------+-------+-----------------------------+---------+---------+
1 row in set (0.000 sec)
```

```sql
SHOW PLUGINS LIKE 'a%';
```

```
+-------+--------------+-------+-----------------------------+---------+---------+
| Name  | Status       | Type  | Library                     | License | Version |
+-------+--------------+-------+-----------------------------+---------+---------+
| audit | Ready-enable | Audit | /tmp/tidb/plugin/audit-1.so |         | 1       |
+-------+--------------+-------+-----------------------------+---------+---------+
1 row in set (0.000 sec)
```
## MySQL compatibility

The `SHOW PLUGINS` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

- [`ADMIN PLUGINS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#admin-plugins-related-statement)
