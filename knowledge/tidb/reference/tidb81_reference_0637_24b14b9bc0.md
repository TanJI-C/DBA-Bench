# SET ROLE syntax, examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-role.md`
- Source Title: `SET ROLE | TiDB SQL Statement Reference`
- Source Heading Path: `SET ROLE | SET ROLE > Synopsis | SET ROLE > Examples | SET ROLE > MySQL compatibility | SET ROLE > See also`
- Source Line Ranges: `5-108`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `roles`, `privileges`, `session`, `syntax`, `examples`, `mysql-compatibility`, `rbac`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0637_24b14b9bc0`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-role.md#set-role`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47e151ec6d711daec7cb787ec58220e758aedb1e1889c9490a49b983a492dcb5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role#set-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-role.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the SQL syntax or behavior of `SET ROLE` for enabling roles in the current session, including `DEFAULT`, `ALL`, `ALL EXCEPT`, `NONE`, or specific role names.
- Retrieval Keywords: SET ROLE, SetRoleStmt, SET ROLE DEFAULT, SET ROLE ALL, SET ROLE ALL EXCEPT, SET ROLE NONE, Rolename, CURRENT_ROLE(), enable roles in the current session, privileges of the role(s), MySQL 8.0 compatibility, SET DEFAULT ROLE, CREATE ROLE, GRANT 'r1', 'r2', 'r3' TO 'u1'@'%'
- Follow-up Guidance: The source also points to related statements `CREATE ROLE`, `DROP ROLE`, `GRANT <role>`, `REVOKE <role>`, `SET DEFAULT ROLE`, and Role-Based Access Control.
- Classification Note: This is reference content because it provides the formal `SET ROLE` syntax, concrete SQL examples with `CURRENT_ROLE()`, a MySQL compatibility note, and links to related SQL statements.

## Official Source Content

# SET ROLE

The `SET ROLE` statement is used to enable roles in the current session. After enabling roles, users can use the privileges of the role(s).
## Synopsis

```ebnf+diagram
SetRoleStmt ::=
    "SET" "ROLE" ( "DEFAULT" | "ALL" ( "EXCEPT" Rolename ("," Rolename)* )? | "NONE" | Rolename ("," Rolename)* )?
```
## Examples

Create a user `'u1'@'%'` and three roles: `'r1'@'%'`, `'r2'@'%'` and `'r3'@'%'`. Grant these roles to `'u1'@'%'` and set `'r1'@'%'` as the default role of `'u1'@'%'`.

```sql
CREATE USER 'u1'@'%';
CREATE ROLE 'r1', 'r2', 'r3';
GRANT 'r1', 'r2', 'r3' TO 'u1'@'%';
SET DEFAULT ROLE 'r1' TO 'u1'@'%';
```

Log in as `'u1'@'%'` and execute the following `SET ROLE` statement to enable all roles.

```sql
SET ROLE ALL;
SELECT CURRENT_ROLE();
```

```
+----------------------------+
| CURRENT_ROLE()             |
+----------------------------+
| `r1`@`%`,`r2`@`%`,`r3`@`%` |
+----------------------------+
1 row in set (0.000 sec)
```

Execute the following `SET ROLE` statement to enable `'r2'` and `'r3'`.

```sql
SET ROLE 'r2', 'r3';
SELECT CURRENT_ROLE();
```

```
+-------------------+
| CURRENT_ROLE()    |
+-------------------+
| `r2`@`%`,`r3`@`%` |
+-------------------+
1 row in set (0.000 sec)
```

Execute the following `SET ROLE` statement to enable the default role(s).

```sql
SET ROLE DEFAULT;
SELECT CURRENT_ROLE();
```

```
+----------------+
| CURRENT_ROLE() |
+----------------+
| `r1`@`%`       |
+----------------+
1 row in set (0.000 sec)
```

Execute the following `SET ROLE` statement to cancel all enabled role(s).

```sql
SET ROLE NONE;
SELECT CURRENT_ROLE();
```

```
+----------------+
| CURRENT_ROLE() |
+----------------+
|                |
+----------------+
1 row in set (0.000 sec)
```
## MySQL compatibility

The `SET ROLE` statement in TiDB is fully compatible with the roles feature in MySQL 8.0. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE ROLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role)
* [DROP ROLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role)
* [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role)
* [`REVOKE <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role)
* [SET DEFAULT ROLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role)

* [Role-Based Access Control](https://docs.pingcap.com/tidb/stable/role-based-access-control)
