# CREATE ROLE syntax, examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-role.md`
- Source Title: `CREATE ROLE | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE ROLE | CREATE ROLE > Synopsis | CREATE ROLE > Examples | CREATE ROLE > MySQL compatibility | CREATE ROLE > See also`
- Source Line Ranges: `5-146`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `create-role`, `rbac`, `roles`, `privileges`, `grant`, `set-role`, `set-default-role`, `mysql-compatibility`, `sql-syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0558_dc4bae0ae5`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-role.md#create-role`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff2a4b43739f96f3bf6e66c75a4cd3bf4ac59b2f53e87aa70cf8a9bd66c6b432`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role#create-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-role.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the CREATE ROLE syntax, an RBAC example that grants a role to a user, or the difference between SET ROLE and SET DEFAULT ROLE in TiDB.
- Retrieval Keywords: CREATE ROLE, CreateRoleStmt, IF NOT EXISTS, RoleSpec, Rolename, role-based access control, GRANT SELECT ON test.* TO analyticsteam, CREATE USER jennifer, GRANT analyticsteam TO jennifer, SET ROLE analyticsteam, SET DEFAULT ROLE analyticsteam TO jennifer, SHOW GRANTS, SHOW TABLES IN test, ERROR 1044 (42000): Access denied for user 'jennifer'@'%' to database 'test', MySQL 8.0 compatibility, DROP ROLE, GRANT <role>, REVOKE <role>, SET DEFAULT ROLE
- Follow-up Guidance: The source also points to related statements DROP ROLE, GRANT <role>, REVOKE <role>, SET ROLE, SET DEFAULT ROLE, and Role-Based Access Control.
- Classification Note: This is reference content because it defines CREATE ROLE syntax, shows concrete SQL examples and outputs, and states MySQL 8.0 compatibility and related statements.

## Official Source Content

# CREATE ROLE

This statement creates a new role, which can be assigned to users as part of role-based access control.
## Synopsis

```ebnf+diagram
CreateRoleStmt ::=
    'CREATE' 'ROLE' IfNotExists RoleSpec (',' RoleSpec)*

IfNotExists ::=
    ('IF' 'NOT' 'EXISTS')?

RoleSpec ::=
    Rolename
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
| GRANT SELECT ON test.* TO 'jennifer'@'%'    |
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
| GRANT SELECT ON test.* TO 'jennifer'@'%'    |
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
## MySQL compatibility

The `CREATE ROLE` statement in TiDB is fully compatible with the roles feature in MySQL 8.0. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [`DROP ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role)
* [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role)
* [`REVOKE <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role)
* [`SET ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role)
* [`SET DEFAULT ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role)

* [Role-Based Access Control](https://docs.pingcap.com/tidb/stable/role-based-access-control)
