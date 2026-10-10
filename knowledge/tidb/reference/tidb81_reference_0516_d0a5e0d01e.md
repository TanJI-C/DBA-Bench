# ADMIN reload plugins and bindings statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-admin.md`
- Source Title: `ADMIN | TiDB SQL Statement Reference`
- Source Heading Path: `ADMIN > `ADMIN RELOAD` statement | ADMIN > `ADMIN PLUGINS` related statement | ADMIN > `ADMIN BINDINGS` related statement`
- Source Line Ranges: `43-100`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `admin`, `reload`, `plugins`, `sql-plan-binding`, `blacklist`, `statement-reference`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0516_d0a5e0d01e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-admin.md#admin-reload-statement`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17477a765858ecc746d25b96701be83a7ca04a6636f6f3f09844ee0787adefe3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin#admin-reload-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-admin.md

## Retrieval Guidance

- Use When: Use this chunk when looking for ADMIN statements for reloading blacklists or bindings, enabling or disabling plugins, or managing SQL Plan bindings.
- Retrieval Keywords: ADMIN RELOAD expr_pushdown_blacklist, expr_pushdown_blacklist, ADMIN RELOAD opt_rule_blacklist, opt_rule_blacklist, ADMIN PLUGINS ENABLE, ADMIN PLUGINS DISABLE, plugin_name, ADMIN FLUSH BINDINGS, ADMIN CAPTURE BINDINGS, ADMIN EVOLVE BINDINGS, ADMIN RELOAD BINDINGS, SQL Plan binding, bind-info-leave
- Follow-up Guidance: The source notes that ADMIN PLUGINS and ADMIN SHOW SLOW features are not available on Starter and Essential clusters, and it explains that ADMIN EVOLVE BINDINGS proactively triggers binding evolution that otherwise runs every bind-info-leave by default.
- Classification Note: This is reference content because it lists exact ADMIN statement forms and states what each reload, plugin, and binding statement is used for.

## Official Source Content

## `ADMIN RELOAD` statement

```sql
ADMIN RELOAD expr_pushdown_blacklist;
```

The above statement is used to reload the blocklist pushed down by the expression.

```sql
ADMIN RELOAD opt_rule_blacklist;
```

The above statement is used to reload the blocklist of logic optimization rules.
## `ADMIN PLUGINS` related statement

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
ADMIN PLUGINS ENABLE plugin_name [, plugin_name] ...;
```

The above statement is used to enable the `plugin_name` plugin.

```sql
ADMIN PLUGINS DISABLE plugin_name [, plugin_name] ...;
```

The above statement is used to disable the `plugin_name` plugin.
## `ADMIN BINDINGS` related statement

```sql
ADMIN FLUSH BINDINGS;
```

The above statement is used to persist SQL Plan binding information.

```sql
ADMIN CAPTURE BINDINGS;
```

The above statement can generate the binding of SQL Plan from the `SELECT` statement that occurs more than once.

```sql
ADMIN EVOLVE BINDINGS;
```

After the automatic binding feature is enabled, the evolution of SQL Plan binding information is triggered every `bind-info-leave` (the default value is `3s`). The above statement is used to proactively trigger this evolution.

```sql
ADMIN RELOAD BINDINGS;
```

The above statement is used to reload SQL Plan binding information.
