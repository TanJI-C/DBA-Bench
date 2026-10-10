# DROP ROLE syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-role.md`
- Source Title: `DROP ROLE | TiDB SQL Statement Reference`
- Source Heading Path: `DROP ROLE | DROP ROLE > Synopsis | DROP ROLE > Examples | DROP ROLE > MySQL compatibility | DROP ROLE > See also`
- Source Line Ranges: `5-179`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `sql-statement`, `roles`, `access-control`, `rbac`, `privileges`, `drop-role`, `mysql-compatibility`, `examples`, `syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0578_bda2a6e9be`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-role.md#drop-role`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5edde7c684936e3f0e98d2b17b50deae9b00b0f02e45fd74024fa05c55ebd79f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role#drop-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-role.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL reference for removing a previously created role, including syntax, examples of role effects on user privileges, and MySQL compatibility for DROP ROLE.
- Retrieval Keywords: DROP ROLE, DropRoleStmt, RolenameList, DROP ROLE IF EXISTS, CREATE ROLE, GRANT analyticsteam TO jennifer, SET ROLE analyticsteam, SET DEFAULT ROLE analyticsteam TO jennifer, SHOW GRANTS, ERROR 1044 (42000): Access denied for user 'jennifer'@'%' to database 'test', ERROR 3530 (HY000): `analyticsteam`@`%` is is not granted to jennifer@%, MySQL 8.0 roles feature compatibility, Role-Based Access Control
- Follow-up Guidance: The source also points to related statements and concepts: CREATE ROLE, GRANT <role>, REVOKE <role>, SET ROLE, SET DEFAULT ROLE, and Role-Based Access Control.
- Classification Note: This is reference content because it defines the DROP ROLE statement syntax, demonstrates exact SQL examples and resulting privilege behavior, and states MySQL 8.0 compatibility.

## Official Source Content

# DROP ROLE

This statement removes a role, that was previously created with `CREATE ROLE`.
## Synopsis

```ebnf+diagram
DropRoleStmt ::=
    'DROP' 'ROLE' ( 'IF' 'EXISTS' )? RolenameList

RolenameList ::=
    Rolename ( ',' Rolename )*
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

Connect to TiDB as the `root` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u root
```

Drop the role for the `analyticsteam`:

```sql
DROP ROLE analyticsteam;
Query OK, 0 rows affected (0.02 sec)
```

`jennifer` no longer has the default role of `analyticsteam` associated, nor can set the role to `analyticsteam`.

Connect to TiDB as the `jennifer` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u jennifer
```

Show the privileges of `jennifer`:

```sql
SHOW GRANTS;
+--------------------------------------+
| Grants for User                      |
+--------------------------------------+
| GRANT USAGE ON *.* TO 'jennifer'@'%' |
+--------------------------------------+
1 row in set (0.00 sec)

SET ROLE analyticsteam;
ERROR 3530 (HY000): `analyticsteam`@`%` is is not granted to jennifer@%
```
## MySQL compatibility

The `DROP ROLE` statement in TiDB is fully compatible with the roles feature in MySQL 8.0. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role)
* [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role)
* [`REVOKE <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role)
* [`SET ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role)
* [`SET DEFAULT ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role)

* [Role-Based Access Control](https://docs.pingcap.com/tidb/stable/role-based-access-control)
