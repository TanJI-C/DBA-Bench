# SET PASSWORD syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-password.md`
- Source Title: `SET PASSWORD | TiDB SQL Statement Reference`
- Source Heading Path: `SET PASSWORD | SET PASSWORD > Synopsis | SET PASSWORD > Examples | SET PASSWORD > MySQL compatibility | SET PASSWORD > See also`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `password`, `user-account`, `authentication`, `sql-syntax`, `examples`, `mysql-compatibility`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0635_371fcdc4ff`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-password.md#set-password`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `487cf67224c15b2dcc700e1b3fa385ba77ee3d2aac5d0d4ee722b48e52ef1c50`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-password#set-password
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-password.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL syntax and examples for changing a user account password with `SET PASSWORD`, including changing your own password or using `FOR Username`.
- Retrieval Keywords: SET PASSWORD, SetPasswordStmt, SET PASSWORD FOR Username, SET PASSWORD = 'test', SET PASSWORD FOR newuser = 'test', PASSWORD('test'), deprecated syntax from earlier MySQL releases, SHOW CREATE USER, CREATE USER, mysql_native_password, TiDB system database, MySQL compatibility, Privilege Management
- Follow-up Guidance: See also `CREATE USER` and `Privilege Management` for related user-account and privilege statements.
- Classification Note: This is reference content because it defines the `SET PASSWORD` statement syntax, provides example SQL statements and outputs, and states MySQL compatibility.

## Official Source Content

# SET PASSWORD

This statement changes the user password for a user account in the TiDB system database.
## Synopsis

```ebnf+diagram
SetPasswordStmt ::=
    "SET" "PASSWORD" ( "FOR" Username )? "=" ( stringLit | "PASSWORD" "(" stringLit ")" )
```
## Examples

```sql
mysql> SET PASSWORD='test'; -- change my password
Query OK, 0 rows affected (0.01 sec)

mysql> CREATE USER 'newuser' IDENTIFIED BY 'test';
Query OK, 1 row affected (0.00 sec)

mysql> SHOW CREATE USER 'newuser';
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER for newuser@%                                                                                                                                            |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER 'newuser'@'%' IDENTIFIED WITH 'mysql_native_password' AS '*94BDCEBE19083CE2A1F959FD02F964C7AF4CFC29' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SET PASSWORD FOR newuser = 'test';
Query OK, 0 rows affected (0.01 sec)

mysql> SHOW CREATE USER 'newuser';
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER for newuser@%                                                                                                                                            |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER 'newuser'@'%' IDENTIFIED WITH 'mysql_native_password' AS '*94BDCEBE19083CE2A1F959FD02F964C7AF4CFC29' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SET PASSWORD FOR newuser = PASSWORD('test'); -- deprecated syntax from earlier MySQL releases
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW CREATE USER 'newuser';
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER for newuser@%                                                                                                                                            |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER 'newuser'@'%' IDENTIFIED WITH 'mysql_native_password' AS '*94BDCEBE19083CE2A1F959FD02F964C7AF4CFC29' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

The `SET PASSWORD` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user)

* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
