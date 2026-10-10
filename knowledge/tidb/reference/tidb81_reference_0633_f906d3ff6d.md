# SET DEFAULT ROLE syntax, usage examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-default-role.md`
- Source Title: `SET DEFAULT ROLE | TiDB SQL Statement Reference`
- Source Heading Path: ``SET DEFAULT ROLE` | `SET DEFAULT ROLE` > Synopsis | `SET DEFAULT ROLE` > Examples | `SET DEFAULT ROLE` > MySQL compatibility | `SET DEFAULT ROLE` > See also`
- Source Line Ranges: `5-147`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `roles`, `privileges`, `access-control`, `default-role`, `sql-syntax`, `mysql-compatibility`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0633_f906d3ff6d`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-default-role.md#set-default-role`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a86a522aa0db3a123f03a42221fb4ac14f5af315521e671fc9a8cb0a4a59d064`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role#set-default-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-default-role.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL syntax, examples, or behavior of `SET DEFAULT ROLE` for assigning default roles to users in TiDB.
- Retrieval Keywords: SET DEFAULT ROLE, SetDefaultRoleStmt, SET DEFAULT ROLE NONE, SET DEFAULT ROLE ALL, Rolename TO Username, SET ROLE analyticsteam, SET ROLE ALL, GRANT analyticsteam TO jennifer, SHOW GRANTS, ERROR 1044 (42000): Access denied for user, ERROR 3530 (HY000), `analyticsteam`@`%` is is not granted to jennifer@%, MySQL 8.0 compatibility, roles feature, Role-Based Access Control
- Follow-up Guidance: Related statements listed are `CREATE ROLE`, `DROP ROLE`, `GRANT <role>`, `REVOKE <role>`, `SET ROLE`, and Role-Based Access Control.
- Classification Note: This is reference content because it defines the `SET DEFAULT ROLE` statement syntax, shows example SQL usage and errors, and notes MySQL 8.0 compatibility.

## Official Source Content

# `SET DEFAULT ROLE`

This statement sets a specific role to be applied to a user by default. Thus, they will automatically have the permissions associated with a role without having to execute `SET ROLE <rolename>` or `SET ROLE ALL`.
## Synopsis

```ebnf+diagram
SetDefaultRoleStmt ::=
    "SET" "DEFAULT" "ROLE" ( "NONE" | "ALL" | Rolename ("," Rolename)* ) "TO" Username ("," Username)*
```
## Examples

Connect to TiDB as the `root` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u root
```

Create a new role `analyticsteam` and a new user `jennifer`:

```sql
CREATE ROLE analyticsteam;
Query OK, 0 rows affected (0.02 sec)

GRANT SELECT ON test.* TO analyticsteam;
Query OK, 0 rows affected (0.02 sec)

CREATE USER jennifer;
Query OK, 0 rows affected (0.01 sec)

GRANT analyticsteam TO jennifer;
Query OK, 0 rows affected (0.01 sec)
```

Connect to TiDB as the `jennifer` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u jennifer
```

Note that by default `jennifer` needs to execute `SET ROLE analyticsteam` in order to be able to use the privileges associated with the `analyticsteam` role:

```sql
SHOW GRANTS;
+---------------------------------------------+
| Grants for User                             |
+---------------------------------------------+
| GRANT USAGE ON *.* TO 'jennifer'@'%'        |
| GRANT 'analyticsteam'@'%' TO 'jennifer'@'%' |
+---------------------------------------------+
2 rows in set (0.00 sec)

SHOW TABLES in test;
ERROR 1044 (42000): Access denied for user 'jennifer'@'%' to database 'test'
SET ROLE analyticsteam;
Query OK, 0 rows affected (0.00 sec)

SHOW GRANTS;
+---------------------------------------------+
| Grants for User                             |
+---------------------------------------------+
| GRANT USAGE ON *.* TO 'jennifer'@'%'        |
| GRANT Select ON test.* TO 'jennifer'@'%'    |
| GRANT 'analyticsteam'@'%' TO 'jennifer'@'%' |
+---------------------------------------------+
3 rows in set (0.00 sec)

SHOW TABLES IN test;
+----------------+
| Tables_in_test |
+----------------+
| t1             |
+----------------+
1 row in set (0.00 sec)
```

Connect to TiDB as the `root` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u root
```

The statement `SET DEFAULT ROLE` can be used to associate the role `analyticsteam` to `jennifer`:

```sql
SET DEFAULT ROLE analyticsteam TO jennifer;
Query OK, 0 rows affected (0.02 sec)
```

Connect to TiDB as the `jennifer` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u jennifer
```

After this, the user `jennifer` has the privileges associated with the role `analyticsteam` and `jennifer` does not have to execute the statement `SET ROLE`:

```sql
SHOW GRANTS;
+---------------------------------------------+
| Grants for User                             |
+---------------------------------------------+
| GRANT USAGE ON *.* TO 'jennifer'@'%'        |
| GRANT Select ON test.* TO 'jennifer'@'%'    |
| GRANT 'analyticsteam'@'%' TO 'jennifer'@'%' |
+---------------------------------------------+
3 rows in set (0.00 sec)

SHOW TABLES IN test;
+----------------+
| Tables_in_test |
+----------------+
| t1             |
+----------------+
1 row in set (0.00 sec)
```

`SET DEFAULT ROLE` will not automatically `GRANT` the associated role to the user. Attempting to `SET DEFAULT ROLE` for a role that `jennifer` does not have granted results in the following error:

```sql
SET DEFAULT ROLE analyticsteam TO jennifer;
ERROR 3530 (HY000): `analyticsteam`@`%` is is not granted to jennifer@%
```
## MySQL compatibility

The `SET DEFAULT ROLE` statement in TiDB is fully compatible with the roles feature in MySQL 8.0. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role)
* [`DROP ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role)
* [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role)
* [`REVOKE <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role)
* [`SET ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role)

* [Role-Based Access Control](https://docs.pingcap.com/tidb/stable/role-based-access-control)
