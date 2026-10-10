# REVOKE privileges syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-revoke-privileges.md`
- Source Title: `REVOKE <privileges> | TiDB SQL Statement Reference`
- Source Heading Path: ``REVOKE <privileges>` | `REVOKE <privileges>` > Synopsis | `REVOKE <privileges>` > Examples | `REVOKE <privileges>` > MySQL compatibility | `REVOKE <privileges>` > See also`
- Source Line Ranges: `5-108`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `privileges`, `revoke`, `grant-option`, `sql-syntax`, `examples`, `mysql-compatibility`, `show-grants`, `user-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0626_1fe725bb5e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-revoke-privileges.md#revoke-privileges`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a77245db7b65b4fe70b8292848720c72b0e24cc12c053eb48d9e76a0c771f5d6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-privileges#revoke-privileges
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-revoke-privileges.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the REVOKE statement syntax, supported privilege names, examples of removing privileges from a user, or TiDB behavior after REVOKE compared with MySQL.
- Retrieval Keywords: REVOKE privileges, RevokeStmt, PrivElemList, GRANT OPTION, REVOKE ALL ON test.* FROM 'newuser', SHOW GRANTS FOR 'newuser', ERROR 1141 (42000), There is no such grant defined for user, MySQL compatibility, takes effect immediately on the current connection, ALL PRIVILEGES, ALTER ROUTINE, CREATE USER, CREATE ROLE, TRIGGER, DELETE, DROP ROLE, PROCESS, EXECUTE, INDEX, INSERT, SELECT, SUPER, SHOW DATABASES, SHOW VIEW, UPDATE, GRANT OPTION, REFERENCES, REPLICATION SLAVE, REPLICATION CLIENT, USAGE, RELOAD, FILE, CONFIG, LOCK TABLES, EVENT, SHUTDOWN
- Follow-up Guidance: Related official topics listed here are `GRANT <privileges>`, SHOW GRANTS, and Privilege Management.
- Classification Note: This is reference content because it defines the `REVOKE` SQL syntax in EBNF, enumerates supported privilege types, shows example SQL and output, and notes a TiDB versus MySQL compatibility detail.

## Official Source Content

# `REVOKE <privileges>`

This statement removes privileges from an existing user. Executing this statement requires the `GRANT OPTION` privilege and all privileges you revoke.
## Synopsis

```ebnf+diagram
RevokeStmt ::=
    'REVOKE' PrivElemList 'ON' ObjectType PrivLevel 'FROM' UserSpecList

PrivElemList ::=
    PrivElem ( ',' PrivElem )*

PrivElem ::=
    PrivType ( '(' ColumnNameList ')' )?

PrivType ::=
    'ALL' 'PRIVILEGES'?
|   'ALTER' 'ROUTINE'?
|   'CREATE' ( 'USER' | 'TEMPORARY' 'TABLES' | 'VIEW' | 'ROLE' | 'ROUTINE' )?
|    'TRIGGER'
|   'DELETE'
|    'DROP' 'ROLE'?
|    'PROCESS'
|    'EXECUTE'
|   'INDEX'
|   'INSERT'
|   'SELECT'
|   'SUPER'
|    'SHOW' ( 'DATABASES' | 'VIEW' )
|   'UPDATE'
|   'GRANT' 'OPTION'
|   'REFERENCES'
|   'REPLICATION' ( 'SLAVE' | 'CLIENT' )
|   'USAGE'
|    'RELOAD'
|   'FILE'
|   'CONFIG'
|   'LOCK' 'TABLES'
|    'EVENT'
|   'SHUTDOWN'

ObjectType ::=
    'TABLE'?

PrivLevel ::=
    '*' ( '.' '*' )?
|    Identifier ( '.' ( '*' | Identifier ) )?

UserSpecList ::=
    UserSpec ( ',' UserSpec )*
```
## Examples

```sql
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

* In TiDB, after the `REVOKE <privileges>` statement is executed successfully, the execution result takes effect immediately on the current connection. Whereas [in MySQL, for some privileges, the execution results take effect only on subsequent connections](https://dev.mysql.com/doc/refman/8.0/en/privilege-changes.html). See [TiDB #39356](https://github.com/pingcap/tidb/issues/39356) for details.
## See also

* [`GRANT <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges)
* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)

* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
