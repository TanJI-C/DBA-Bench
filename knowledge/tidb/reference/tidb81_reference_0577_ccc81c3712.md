# DROP RESOURCE GROUP syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-resource-group.md`
- Source Title: `DROP RESOURCE GROUP`
- Source Heading Path: `DROP RESOURCE GROUP | DROP RESOURCE GROUP > Synopsis | DROP RESOURCE GROUP > Examples | DROP RESOURCE GROUP > MySQL compatibility | DROP RESOURCE GROUP > See also`
- Source Line Ranges: `5-90`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `resource groups`, `ddl`, `syntax`, `examples`, `mysql compatibility`, `resource control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0577_ccc81c3712`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-resource-group.md#drop-resource-group`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `447e4dea72505d5ef16fefc275ee8efa2da8c89f3c334907dba08070e8c294ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group#drop-resource-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-resource-group.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL reference for dropping a resource group, including syntax, IF EXISTS usage, examples, and MySQL compatibility notes.
- Retrieval Keywords: DROP RESOURCE GROUP, DropResourceGroupStmt, IF EXISTS, ResourceGroupName, DEFAULT, tidb_enable_resource_control, information_schema.resource_groups, CREATE RESOURCE GROUP IF NOT EXISTS rg1 RU_PER_SEC = 500 BURSTABLE, DROP RESOURCE GROUP IF EXISTS rg1, MySQL compatibility, FORCE parameter
- Follow-up Guidance: See also ALTER RESOURCE GROUP, CREATE RESOURCE GROUP, and Request Unit (RU).
- Classification Note: This is a SQL reference chunk because the official content provides statement syntax, execution prerequisites, example SQL, and a MySQL compatibility note for DROP RESOURCE GROUP.

## Official Source Content

# DROP RESOURCE GROUP

You can use the `DROP RESOURCE GROUP` statement to drop a resource group.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
DropResourceGroupStmt ::=
    "DROP" "RESOURCE" "GROUP" IfExists ResourceGroupName

IfExists ::=
    ('IF' 'EXISTS')?

ResourceGroupName ::=
    Identifier
|   "DEFAULT"
```

> **Note:**
>
> - The `DROP RESOURCE GROUP` statement can only be executed when the global variable [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660) is set to `ON`.
> - The `default` resource group is reserved and cannot be dropped.
## Examples

Drop a resource group named `rg1`.

```sql
DROP RESOURCE GROUP IF EXISTS rg1;
```

```sql
Query OK, 0 rows affected (0.22 sec)
```

```sql
CREATE RESOURCE GROUP IF NOT EXISTS rg1 RU_PER_SEC = 500 BURSTABLE;
```

```sql
Query OK, 0 rows affected (0.08 sec)
```

```sql
SELECT * FROM information_schema.resource_groups WHERE NAME ='rg1';
```

```sql
+------+------------+----------+-----------+-------------+
| NAME | RU_PER_SEC | PRIORITY | BURSTABLE | QUERY_LIMIT |
+------+------------+----------+-----------+-------------+
| rg1  | 500        | MEDIUM   | YES       | NULL        |
+------+------------+----------+-----------+-------------+
1 row in set (0.01 sec)
```

```sql
DROP RESOURCE GROUP IF EXISTS rg1;
```

```sql
Query OK, 1 rows affected (0.09 sec)
```

```
SELECT * FROM information_schema.resource_groups WHERE NAME ='rg1';
```

```sql
Empty set (0.00 sec)
```
## MySQL compatibility

MySQL also supports [DROP RESOURCE GROUP](https://dev.mysql.com/doc/refman/8.0/en/drop-resource-group.html), but TiDB does not support the `FORCE` parameter.
## See also

* [ALTER RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group)
* [CREATE RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group)
* [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru)
