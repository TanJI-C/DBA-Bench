# REVOKE role syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-revoke-role.md`
- Source Title: `REVOKE <role> | TiDB SQL Statement Reference`
- Source Heading Path: ``REVOKE <role>` | `REVOKE <role>` > Synopsis | `REVOKE <role>` > Examples | `REVOKE <role>` > MySQL compatibility | `REVOKE <role>` > See also`
- Source Line Ranges: `5-177`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `roles`, `privileges`, `access-control`, `revoke`, `grant`, `set-role`, `default-role`, `mysql-compatibility`, `sql-syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0627_df00c6ec73`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-revoke-role.md#revoke-role`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7df52c8b350fa309649c2118b649aba94103b1e9e33c7768a63553e6b8cbd530`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-role#revoke-role
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-revoke-role.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL syntax, examples, or compatibility details for removing a previously assigned role from a user with REVOKE.
- Retrieval Keywords: REVOKE RolenameList FROM UsernameList, REVOKE analyticsteam FROM jennifer, REVOKE <role>, roles feature in MySQL 8.0, SET ROLE analyticsteam, SET DEFAULT ROLE analyticsteam TO jennifer, SHOW GRANTS, ERROR 1044 (42000): Access denied for user 'jennifer'@'%' to database 'test', GRANT analyticsteam TO jennifer
- Follow-up Guidance: The source also points to related statements and concepts including CREATE ROLE, DROP ROLE, GRANT <role>, SET ROLE, SET DEFAULT ROLE, and Role-Based Access Control.
- Classification Note: This is a SQL reference chunk because it defines the REVOKE role statement syntax, demonstrates usage examples, and states MySQL 8.0 compatibility.

## Official Source Content

# `REVOKE <role>`

This statement removes a previously assigned role from a specified user (or list of users).
## Synopsis

```ebnf+diagram
RevokeRoleStmt ::=
    'REVOKE' RolenameList 'FROM' UsernameList

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

Connect to TiDB as the `root` user:

```shell
mysql -h 127.0.0.1 -P 4000 -u root
```

Revoke the role of analyticsteam from `jennifer`:

```sql
REVOKE analyticsteam FROM jennifer;
Query OK, 0 rows affected (0.01 sec)
```

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
```
## MySQL compatibility

The `REVOKE <role>` statement in TiDB is fully compatible with the roles feature in MySQL 8.0. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [`CREATE ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-role)
* [`DROP ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-role)
* [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role)
* [`SET ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-role)
* [`SET DEFAULT ROLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-default-role)

* [Role-Based Access Control](https://docs.pingcap.com/tidb/stable/role-based-access-control)
