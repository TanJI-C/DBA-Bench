# CREATE USER syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-user.md`
- Source Title: `CREATE USER | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE USER | CREATE USER > Synopsis | CREATE USER > Examples | CREATE USER > MySQL compatibility | CREATE USER > See also`
- Source Line Ranges: `5-171`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `create-user`, `user-management`, `authentication`, `passwords`, `host-based-access`, `tls`, `x509`, `account-lock`, `user-attributes`, `password-policy`, `resource-groups`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0564_5441ae05c3`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-user.md#create-user`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0649b9c39ce6029f96d1b9148d02428aee514bcce63ed021ba3f4a528b9b17f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user#create-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-user.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the CREATE USER statement syntax, examples of authentication and host-based accounts, or TiDB-specific MySQL compatibility notes for user creation.
- Retrieval Keywords: CREATE USER, CreateUserStmt, UserSpec, IDENTIFIED BY, IDENTIFIED WITH, 'newuser2'@'192.168.1.1', REQUIRE SSL, REQUIRE X509, ISSUER, SUBJECT, CIPHER, SAN, TOKEN_ISSUER, ACCOUNT LOCK, ACCOUNT UNLOCK, COMMENT, ATTRIBUTE, information_schema.user_attributes, PASSWORD EXPIRE, PASSWORD HISTORY, PASSWORD REUSE INTERVAL, FAILED_LOGIN_ATTEMPTS, PASSWORD_LOCK_TIME, RESOURCE GROUP, MYSQL.USER, SHOW CREATE USER, ALTER USER, DROP USER, DEFAULT ROLE, WITH MAX_QUERIES_PER_HOUR, WITH MAX_UPDATES_PER_HOUR, WITH MAX_USER_CONNECTIONS
- Follow-up Guidance: The source also points to related statements and references including SHOW CREATE USER, ALTER USER, DROP USER, Security Compatibility with MySQL, and Privilege Management.
- Classification Note: This is a SQL reference chunk because it defines CREATE USER syntax, shows executable examples, and states TiDB MySQL compatibility for unsupported options that are parsed but ignored.

## Official Source Content

# CREATE USER

This statement creates a new user, specified with a password. In the MySQL privilege system, a user is the combination of a username and the host from which they are connecting from. Thus, it is possible to create a user `'newuser2'@'192.168.1.1'` who is only able to connect from the IP address `192.168.1.1`. It is also possible to have two users have the same user-portion, and different permissions as they login from different hosts.
## Synopsis

```ebnf+diagram
CreateUserStmt ::=
    'CREATE' 'USER' IfNotExists UserSpecList RequireClauseOpt ConnectionOptions PasswordOption LockOption AttributeOption ResourceGroupNameOption

IfNotExists ::=
    ('IF' 'NOT' 'EXISTS')?

UserSpecList ::=
    UserSpec ( ',' UserSpec )*

UserSpec ::=
    Username AuthOption

AuthOption ::=
    ( 'IDENTIFIED' ( 'BY' ( AuthString | 'PASSWORD' HashString ) | 'WITH' StringName ( 'BY' AuthString | 'AS' HashString )? ) )?

StringName ::=
    stringLit
|   Identifier

PasswordOption ::= ( 'PASSWORD' 'EXPIRE' ( 'DEFAULT' | 'NEVER' | 'INTERVAL' N 'DAY' )? | 'PASSWORD' 'HISTORY' ( 'DEFAULT' | N ) | 'PASSWORD' 'REUSE' 'INTERVAL' ( 'DEFAULT' | N 'DAY' ) | 'FAILED_LOGIN_ATTEMPTS' N | 'PASSWORD_LOCK_TIME' ( N | 'UNBOUNDED' ) )*

LockOption ::= ( 'ACCOUNT' 'LOCK' | 'ACCOUNT' 'UNLOCK' )?

AttributeOption ::= ( 'COMMENT' CommentString | 'ATTRIBUTE' AttributeString )?

ResourceGroupNameOption::= ( 'RESOURCE' 'GROUP' Identifier)?

RequireClauseOpt ::= ('REQUIRE' ('NONE' | 'SSL' | 'X509' | RequireListElement ('AND'? RequireListElement)*))?

RequireListElement ::= 'ISSUER' Issuer | 'SUBJECT' Subject | 'CIPHER' Cipher | 'SAN' SAN | 'TOKEN_ISSUER' TokenIssuer
```
## Examples

Create a user with the `newuserpassword` password.

```sql
mysql> CREATE USER 'newuser' IDENTIFIED BY 'newuserpassword';
Query OK, 1 row affected (0.04 sec)
```

Create a user who can only log in to `192.168.1.1`.

```sql
mysql> CREATE USER 'newuser2'@'192.168.1.1' IDENTIFIED BY 'newuserpassword';
Query OK, 1 row affected (0.02 sec)
```

Create a user who is enforced to log in using TLS connection.

```sql
CREATE USER 'newuser3'@'%' IDENTIFIED BY 'newuserpassword' REQUIRE SSL;
Query OK, 1 row affected (0.02 sec)
```

Create a user who is required to use X.509 certificate at login.

```sql
CREATE USER 'newuser4'@'%' IDENTIFIED BY 'newuserpassword' REQUIRE ISSUER '/C=US/ST=California/L=San Francisco/O=PingCAP';
Query OK, 1 row affected (0.02 sec)
```

Create a user who is locked upon creation.

```sql
CREATE USER 'newuser5'@'%' ACCOUNT LOCK;
```

```
Query OK, 1 row affected (0.02 sec)
```

Create a user with a comment.

```sql
CREATE USER 'newuser6'@'%' COMMENT 'This user is created only for test';
SELECT * FROM information_schema.user_attributes;
```

```
+-----------+------+---------------------------------------------------+
| USER      | HOST | ATTRIBUTE                                         |
+-----------+------+---------------------------------------------------+
| newuser6  | %    | {"comment": "This user is created only for test"} |
+-----------+------+---------------------------------------------------+
1 rows in set (0.00 sec)
```

Create a user with an `email` attribute.

```sql
CREATE USER 'newuser7'@'%' ATTRIBUTE '{"email": "user@pingcap.com"}';
SELECT * FROM information_schema.user_attributes;
```

```sql
+-----------+------+---------------------------------------------------+
| USER      | HOST | ATTRIBUTE                                         |
+-----------+------+---------------------------------------------------+
| newuser7  | %    | {"email": "user@pingcap.com"} |
+-----------+------+---------------------------------------------------+
1 rows in set (0.00 sec)
```

Create a user who is not allowed to reuse the last 5 passwords:

```sql
CREATE USER 'newuser8'@'%' PASSWORD HISTORY 5;
```

```
Query OK, 1 row affected (0.02 sec)
```

Create a user whose password is manually expired:

```sql
CREATE USER 'newuser9'@'%' PASSWORD EXPIRE;
```

```
Query OK, 1 row affected (0.02 sec)
```

Create a user that uses the resource group `rg1`.

```sql
CREATE USER 'newuser7'@'%' RESOURCE GROUP rg1;
SELECT USER, HOST, USER_ATTRIBUTES FROM MYSQL.USER WHERE USER='newuser7';
```

```sql
+----------+------+---------------------------+
| USER     | HOST | USER_ATTRIBUTES           |
+----------+------+---------------------------+
| newuser7 | %    | {"resource_group": "rg1"} |
+----------+------+---------------------------+
1 rows in set (0.00 sec)
```
## MySQL compatibility

The following `CREATE USER` options are not yet supported by TiDB, and will be parsed but ignored:

* TiDB does not support `WITH MAX_QUERIES_PER_HOUR`, `WITH MAX_UPDATES_PER_HOUR`, and `WITH MAX_USER_CONNECTIONS` options.
* TiDB does not support the `DEFAULT ROLE` option.
## See also

* [Security Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql)
* [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management)

* [DROP USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-user)
* [SHOW CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-user)
* [ALTER USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user)
