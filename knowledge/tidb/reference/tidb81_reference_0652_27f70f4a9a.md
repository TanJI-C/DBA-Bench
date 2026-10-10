# SHOW CREATE RESOURCE GROUP syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-create-resource-group.md`
- Source Title: `SHOW CREATE RESOURCE GROUP`
- Source Heading Path: `SHOW CREATE RESOURCE GROUP | SHOW CREATE RESOURCE GROUP > Synopsis | SHOW CREATE RESOURCE GROUP > Examples | SHOW CREATE RESOURCE GROUP > MySQL compatibility | SHOW CREATE RESOURCE GROUP > See also`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `resource-groups`, `show-create`, `sql-syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0652_27f70f4a9a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-create-resource-group.md#show-create-resource-group`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13cca055c0475a4a93f8dda6c0d289c9ef02de6e1e67803690cb9096f4792271`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-resource-group#show-create-resource-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-create-resource-group.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, example output, or MySQL compatibility note for `SHOW CREATE RESOURCE GROUP` to view the current definition of a resource group.
- Retrieval Keywords: SHOW CREATE RESOURCE GROUP, ShowCreateResourceGroupStmt, ResourceGroupName, Identifier, DEFAULT, view the current definition of a resource group, CREATE RESOURCE GROUP rg1 RU_PER_SEC=100, SHOW CREATE RESOURCE GROUP rg1, CREATE RESOURCE GROUP `rg1` RU_PER_SEC=100 PRIORITY=MEDIUM, TiDB extension for MySQL, resource groups
- Follow-up Guidance: The source also points to `TiDB RESOURCE CONTROL`, `CREATE RESOURCE GROUP`, `ALTER RESOURCE GROUP`, and `DROP RESOURCE GROUP` in the See also section.
- Classification Note: This is reference content because it defines the statement purpose, EBNF synopsis, example SQL and output, and a MySQL compatibility note for the SQL statement.

## Official Source Content

# SHOW CREATE RESOURCE GROUP

You can use the `SHOW CREATE RESOURCE GROUP` statement to view the current definition of a resource group.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
ShowCreateResourceGroupStmt ::=
    "SHOW" "CREATE" "RESOURCE" "GROUP" ResourceGroupName

ResourceGroupName ::=
    Identifier
|   "DEFAULT"
```
## Examples

Create a resource group `rg1`.

```sql
CREATE RESOURCE GROUP rg1 RU_PER_SEC=100;
Query OK, 0 rows affected (0.10 sec)
```

View the definition of `rg1`.

```sql
SHOW CREATE RESOURCE GROUP rg1;
***************************[ 1. row ]***************************
+----------------+------------------------------------------------------------+
| Resource_Group | Create Resource Group                                      |
+----------------+------------------------------------------------------------+
| rg1            | CREATE RESOURCE GROUP `rg1` RU_PER_SEC=100 PRIORITY=MEDIUM |
+----------------+------------------------------------------------------------+
1 row in set (0.01 sec)
```
## MySQL compatibility

This statement is a TiDB extension for MySQL.
## See also

* [TiDB RESOURCE CONTROL](https://docs.pingcap.com/tidb/stable/tidb-resource-control)
* [CREATE RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group)
* [ALTER RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group)
* [DROP RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group)
