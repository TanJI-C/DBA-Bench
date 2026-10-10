# DROP USER syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-user.md`
- Source Title: `DROP USER | TiDB SQL Statement Reference`
- Source Heading Path: `DROP USER | DROP USER > Synopsis | DROP USER > Examples | DROP USER > MySQL compatibility | DROP USER > See also`
- Source Line Ranges: `5-76`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `drop user`, `user management`, `privileges`, `syntax`, `examples`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0582_4f5a728acd`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-user.md#drop-user`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `efae3ef2bd150d7ca3541288ca45cfc940d60de59865c2a35b90b721e416415c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-user#drop-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-user.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB DROP USER syntax, the IF EXISTS behavior, required privilege, examples of removing a user, or MySQL compatibility for missing users.
- Retrieval Keywords: DROP USER, DROP USER IF EXISTS, DropUserStmt, UsernameList, CURRENT_USER, CREATE USER privilege, Operation DROP USER failed, ERROR 1396 (HY000), SHOW GRANTS, REVOKE ALL, There is no such grant defined for user, ERROR 1141 (42000), Dropping a user that does not exist with IF EXISTS will not create a warning in TiDB, MySQL compatibility, Issue #10196
- Follow-up Guidance: The source also points to CREATE USER, ALTER USER, SHOW CREATE USER, and Privilege Management.
- Classification Note: This is reference content because it defines the DROP USER statement syntax, privilege requirement, examples, and a specific MySQL compatibility note from the official documentation.

## Official Source Content

# DROP USER

This statement removes a user from the TiDB system database. The optional keyword `IF EXISTS` can be used to silence an error if the user does not exist. This statement requires the `CREATE USER` privilege.
## Synopsis

```ebnf+diagram
DropUserStmt ::=
    'DROP' 'USER' ( 'IF' 'EXISTS' )? UsernameList

Username ::=
    StringName ('@' StringName | singleAtIdentifier)? | 'CURRENT_USER' OptionalBraces
```
## Examples

```sql
mysql> DROP USER idontexist;
ERROR 1396 (HY000): Operation DROP USER failed for idontexist@%

mysql> DROP USER IF EXISTS 'idontexist';
Query OK, 0 rows affected (0.01 sec)

mysql> CREATE USER 'newuser' IDENTIFIED BY 'mypassword';
Query OK, 1 row affected (0.02 sec)

mysql> GRANT ALL ON test.* TO 'newuser';
Query OK, 0 rows affected (0.03 sec)

mysql> SHOW GRANTS FOR 'newuser';
+-------------------------------------------------+
| Grants for newuser@%                            |
+-------------------------------------------------+
| GRANT USAGE ON *.* TO 'newuser'@'%'             |
| GRANT ALL PRIVILEGES ON test.* TO 'newuser'@'%' |
+-------------------------------------------------+
2 rows in set (0.00 sec)

mysql> REVOKE ALL ON test.* FROM 'newuser';
Query OK, 0 rows affected (0.03 sec)

mysql> SHOW GRANTS FOR 'newuser';
+-------------------------------------+
| Grants for newuser@%                |
+-------------------------------------+
| GRANT USAGE ON *.* TO 'newuser'@'%' |
+-------------------------------------+
1 row in set (0.00 sec)

mysql> DROP USER 'newuser';
Query OK, 0 rows affected (0.14 sec)

mysql> SHOW GRANTS FOR 'newuser';
ERROR 1141 (42000): There is no such grant defined for user 'newuser' on host '%'
```
## MySQL compatibility

* Dropping a user that does not exist with `IF EXISTS` will not create a warning in TiDB. [Issue #10196](https://github.com/pingcap/tidb/issues/10196).
## See also

* [CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user)
* [ALTER USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user)
* [SHOW CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-user)

* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
