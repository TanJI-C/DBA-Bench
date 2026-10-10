# GRANT role syntax, usage examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-grant-role.md`
- Source Title: `GRANT <role> | TiDB SQL Statement Reference`
- Source Heading Path: ``GRANT <role>` | `GRANT <role>` > Synopsis | `GRANT <role>` > Examples | `GRANT <role>` > MySQL compatibility | `GRANT <role>` > See also`
- Source Line Ranges: `5-147`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `grant-role`, `roles`, `rbac`, `privileges`, `set-role`, `default-role`, `mysql-compatibility`, `sql-syntax`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0599_c0382fd1e6`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-grant-role.md#grant-role`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c4b979efad09f8f3155607da2d0f6dddb88bff0a047d024260d9ea4c5c8abb3d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role#grant-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-grant-role.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB SQL syntax or examples for assigning a previously created role to an existing user with `GRANT <role>`, including how `SET ROLE` and `SET DEFAULT ROLE` affect the granted role.
- Retrieval Keywords: GRANT <role>, GrantRoleStmt, GRANT RolenameList TO UsernameList, RolenameList, UsernameList, GRANT analyticsteam TO jennifer, SET ROLE analyticsteam, SET ROLE ALL, SET DEFAULT ROLE analyticsteam TO jennifer, SHOW GRANTS, ERROR 1044 (42000): Access denied for user 'jennifer'@'%' to database 'test', MySQL 8.0 roles compatibility, Role-Based Access Control
- Follow-up Guidance: The source also points to related statements `GRANT <privileges>`, `CREATE ROLE`, `DROP ROLE`, `REVOKE <role>`, `SET ROLE`, and `SET DEFAULT ROLE`.
- Classification Note: This is reference content because it provides the formal `GRANT <role>` syntax, concrete SQL examples, and a MySQL compatibility note for role-based access control behavior.

## Official Source Content

# `GRANT <role>`

Assigns a previously created role to an existing user. The user can use then use the statement `SET ROLE <rolename>` to assume the privileges of the role, or `SET ROLE ALL` to assume all roles that have been assigned.
## Synopsis

```ebnf+diagram
GrantRoleStmt ::=
    'GRANT' RolenameList 'TO' UsernameList

RolenameList ::=
    Rolename ( ',' Rolename )*

UsernameList ::=
    Username ( ',' Username )*
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

The `GRANT <role>` statement in TiDB is fully compatible with the roles feature in MySQL 8.0. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [`GRANT <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges)
* [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role)
* [`DROP ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role)
* [`REVOKE <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role)
* [`SET ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role)
* [`SET DEFAULT ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role)

* [Role-Based Access Control](https://docs.pingcap.com/tidb/stable/role-based-access-control)
