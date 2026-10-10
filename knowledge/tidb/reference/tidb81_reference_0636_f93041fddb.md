# SET RESOURCE GROUP syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-resource-group.md`
- Source Title: `SET RESOURCE GROUP`
- Source Heading Path: `SET RESOURCE GROUP | SET RESOURCE GROUP > Synopsis | SET RESOURCE GROUP > Examples | SET RESOURCE GROUP > MySQL compatibility | SET RESOURCE GROUP > See also`
- Source Line Ranges: `5-93`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `cloud`
- Topic Tags: `resource-group`, `session`, `syntax`, `examples`, `mysql-compatibility`, `resource-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0636_f93041fddb`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-resource-group.md#set-resource-group`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8bb43f0944933cc260cdb3b5759924050570a417cdd21c950da321d5760a0551`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group#set-resource-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-resource-group.md

## Retrieval Guidance

- Use When: Use this when asking how to set the resource group for the current session, what the SET RESOURCE GROUP syntax looks like, or how to verify the current session resource group with SQL examples.
- Retrieval Keywords: SET RESOURCE GROUP, SetResourceGroupStmt, SET RESOURCE GROUP ResourceGroupName, ResourceGroupName, Identifier, DEFAULT, CURRENT_RESOURCE_GROUP(), SET RESOURCE GROUP `rg2`, SET RESOURCE GROUP `default`, ALTER USER 'user1' RESOURCE GROUP `rg1`, CREATE RESOURCE GROUP 'rg1' RU_PER_SEC = 1000, MySQL compatibility, accepted parameters are different, not compatible
- Follow-up Guidance: The same source also points to CREATE RESOURCE GROUP, DROP RESOURCE GROUP, ALTER RESOURCE GROUP, and Resource Control in the See also section.
- Classification Note: This is reference content because it defines the SET RESOURCE GROUP statement syntax, shows example SQL and outputs, and states a MySQL compatibility note and availability note for Starter and Essential clusters.

## Official Source Content

# SET RESOURCE GROUP

`SET RESOURCE GROUP` is used to set the resource group for the current session.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

**SetResourceGroupStmt:**

```ebnf+diagram
SetResourceGroupStmt ::=
    "SET" "RESOURCE" "GROUP" ResourceGroupName

ResourceGroupName ::=
    Identifier
|   "DEFAULT"
```
## Examples

Create a user `user1`, create two resource groups `rg1` and `rg2`, and bind the user `user1` to the resource group `rg1`.

```sql
CREATE USER 'user1';
CREATE RESOURCE GROUP 'rg1' RU_PER_SEC = 1000;
ALTER USER 'user1' RESOURCE GROUP `rg1`;
```

Use `user1` to log in and view the resource group bound to the current user.

```sql
SELECT CURRENT_RESOURCE_GROUP();
```

```
+--------------------------+
| CURRENT_RESOURCE_GROUP() |
+--------------------------+
| rg1                      |
+--------------------------+
1 row in set (0.00 sec)
```

Execute `SET RESOURCE GROUP` to set the resource group for the current session to `rg2`.

```sql
SET RESOURCE GROUP `rg2`;
SELECT CURRENT_RESOURCE_GROUP();
```

```
+--------------------------+
| CURRENT_RESOURCE_GROUP() |
+--------------------------+
| rg2                      |
+--------------------------+
1 row in set (0.00 sec)
```

Execute `SET RESOURCE GROUP` to specify the current session to use the default resource group.

```sql
SET RESOURCE GROUP `default`;
SELECT CURRENT_RESOURCE_GROUP();
```

```sql
+--------------------------+
| CURRENT_RESOURCE_GROUP() |
+--------------------------+
| default                  |
+--------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

MySQL also supports [SET RESOURCE GROUP](https://dev.mysql.com/doc/refman/8.0/en/set-resource-group.html). But the accepted parameters are different from that of TiDB. They are not compatible.
## See also

* [CREATE RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-resource-group)
* [DROP RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-resource-group)
* [ALTER RESOURCE GROUP](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group)
* [Resource Control](https://docs.pingcap.com/tidb/stable/tidb-resource-control)
