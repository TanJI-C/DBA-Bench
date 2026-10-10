# GRANT privileges syntax, examples, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-grant-privileges.md`
- Source Title: `GRANT <privileges> | TiDB SQL Statement Reference`
- Source Heading Path: ``GRANT <privileges>` | `GRANT <privileges>` > Synopsis | `GRANT <privileges>` > Examples | `GRANT <privileges>` > MySQL compatibility | `GRANT <privileges>` > See also`
- Source Line Ranges: `5-99`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `grant`, `privileges`, `users`, `syntax`, `examples`, `mysql-compatibility`, `security`, `show-grants`, `access-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0598_1d61edabe3`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-grant-privileges.md#grant-privileges`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc4e3f370e168a994e19b40983d4250e373dc6e2102bec1d15d9d37dea6d50e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges#grant-privileges
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-grant-privileges.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the `GRANT <privileges>` statement syntax, supported privilege types, examples with `SHOW GRANTS`, or TiDB MySQL compatibility notes for privilege allocation to a pre-existing user.
- Retrieval Keywords: GRANT <privileges>, GrantStmt, PrivElemList, PrivType, GRANT OPTION, SHOW GRANTS, USAGE privilege, NO_AUTO_CREATE_USER, column level privileges are not currently supported, execution result takes effect immediately on the current connection, REQUIRE SSL, REQUIRE X509, TOKEN_ISSUER, CREATE USER, REVOKE <privileges>, Privilege Management
- Follow-up Guidance: The source also points to related statements and topics: `GRANT <role>`, `REVOKE <privileges>`, `SHOW GRANTS`, and `Privilege Management`.
- Classification Note: This is reference content because it provides formal `GRANT <privileges>` syntax, privilege identifiers, examples, compatibility notes, and related statement links for the SQL component.

## Official Source Content

# `GRANT <privileges>`

This statement allocates privileges to a pre-existing user in TiDB. The privilege system in TiDB follows MySQL, where credentials are assigned based on a database/table pattern. Executing this statement requires the `GRANT OPTION` privilege and all privileges you allocate.
## Synopsis

```ebnf+diagram
GrantStmt ::=
    'GRANT' PrivElemList 'ON' ObjectType PrivLevel 'TO' UserSpecList RequireClauseOpt WithGrantOptionOpt

PrivElemList ::=
    PrivElem ( ',' PrivElem )*

PrivElem ::=
    PrivType ( '(' ColumnNameList ')' )?

PrivType ::=
    'ALL' 'PRIVILEGES'?
|    'ALTER' 'ROUTINE'?
|   'CREATE' ( 'USER' | 'TEMPORARY' 'TABLES' | 'VIEW' | 'ROLE' | 'ROUTINE' )?
|   'TRIGGER'
|   'DELETE'
|   'DROP' 'ROLE'?
|    'PROCESS'
|   'EXECUTE'
|   'INDEX'
|   'INSERT'
|   'SELECT'
|   'SUPER'
|   'SHOW' ( 'DATABASES' | 'VIEW' )
|   'UPDATE'
|    'GRANT' 'OPTION'
|    'REFERENCES'
|    'REPLICATION' ( 'SLAVE' | 'CLIENT' )
|    'USAGE'
|   'RELOAD'
|   'FILE'
|   'CONFIG'
|   'LOCK' 'TABLES'
|   'EVENT'
|   'SHUTDOWN'

ObjectType ::=
    'TABLE'?

PrivLevel ::=
    '*' ( '.' '*' )?
|    Identifier ( '.' ( '*' | Identifier ) )?

UserSpecList ::=
    UserSpec ( ',' UserSpec )*

RequireClauseOpt ::= ('REQUIRE' ('NONE' | 'SSL' | 'X509' | RequireListElement ('AND'? RequireListElement)*))?

RequireListElement ::= 'ISSUER' Issuer | 'SUBJECT' Subject | 'CIPHER' Cipher | 'SAN' SAN | 'TOKEN_ISSUER' TokenIssuer
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
```
## MySQL compatibility

* Similar to MySQL, the `USAGE` privilege denotes the ability to log into a TiDB server.
* Column level privileges are not currently supported.
* Similar to MySQL, when the `NO_AUTO_CREATE_USER` sql mode is not present, the `GRANT` statement will automatically create a new user with an empty password when a user does not exist. Removing this sql-mode (it is enabled by default) presents a security risk.
* In TiDB, after the `GRANT <privileges>` statement is executed successfully, the execution result takes effect immediately on the current connection. Whereas [in MySQL, for some privileges, the execution results take effect only on subsequent connections](https://dev.mysql.com/doc/refman/8.0/en/privilege-changes.html). See [TiDB #39356](https://github.com/pingcap/tidb/issues/39356) for details.
## See also

* [`GRANT <role>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-role)
* [`REVOKE <privileges>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-revoke-privileges)
* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)

* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)
