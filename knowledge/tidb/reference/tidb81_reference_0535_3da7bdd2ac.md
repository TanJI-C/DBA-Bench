# ALTER USER syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-user.md`
- Source Title: `ALTER USER | TiDB SQL Statement Reference`
- Source Heading Path: `ALTER USER | ALTER USER > Synopsis | ALTER USER > Examples | ALTER USER > Examples > Modify basic user information | ALTER USER > Examples > Modify the resource group bound to the user | ALTER USER > See also`
- Source Line Ranges: `5-204`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `alter user`, `user management`, `authentication`, `password policy`, `account lock`, `user attributes`, `resource groups`, `sql syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0535_3da7bdd2ac`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-user.md#alter-user`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66974696de45fa80c3cd2bb7caa1be8ebe39d5e6c145caead88a460eb6313c6c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user#alter-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-user.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the ALTER USER SQL syntax or examples for changing authentication, password policy, account lock state, user attributes, comments, TLS REQUIRE options, or RESOURCE GROUP binding for an existing user.
- Retrieval Keywords: ALTER USER, AlterUserStmt, UserSpecList, IDENTIFIED BY, IDENTIFIED WITH, PASSWORD EXPIRE NEVER, PASSWORD HISTORY, PASSWORD REUSE INTERVAL 90 DAY, FAILED_LOGIN_ATTEMPTS, PASSWORD_LOCK_TIME, ACCOUNT LOCK, ACCOUNT UNLOCK, ATTRIBUTE, COMMENT, RESOURCE GROUP, REQUIRE SSL, REQUIRE X509, ISSUER, SUBJECT, CIPHER, SAN, TOKEN_ISSUER, SHOW CREATE USER, information_schema.user_attributes, mysql.user, JSON_EXTRACT(User_attributes, "$.resource_group"), ALTER USER 'newuser' IDENTIFIED BY 'newnewpassword', ALTER USER 'newuser' ACCOUNT LOCK, ALTER USER 'newuser' RESOURCE GROUP rg1
- Follow-up Guidance: The source also points to related statements and references including CREATE USER, DROP USER, SHOW CREATE USER, and Security Compatibility with MySQL.
- Classification Note: This is reference content because it provides the formal ALTER USER synopsis and concrete SQL examples for modifying existing users in the TiDB privilege system.

## Official Source Content

# ALTER USER

This statement changes an existing user inside the TiDB privilege system. In the MySQL privilege system, a user is the combination of a username and the host from which they are connecting from. Thus, it is possible to create a user `'newuser2'@'192.168.1.1'` who is only able to connect from the IP address `192.168.1.1`. It is also possible to have two users have the same user-portion, and different permissions as they login from different hosts.
## Synopsis

```ebnf+diagram
AlterUserStmt ::=
    'ALTER' 'USER' IfExists (UserSpecList RequireClauseOpt ConnectionOptions PasswordOption LockOption AttributeOption | 'USER' '(' ')' 'IDENTIFIED' 'BY' AuthString) ResourceGroupNameOption

UserSpecList ::=
    UserSpec ( ',' UserSpec )*

UserSpec ::=
    Username AuthOption

Username ::=
    StringName ('@' StringName | singleAtIdentifier)? | 'CURRENT_USER' OptionalBraces

AuthOption ::=
    ( 'IDENTIFIED' ( 'BY' ( AuthString | 'PASSWORD' HashString ) | 'WITH' StringName ( 'BY' AuthString | 'AS' HashString )? ) )?

PasswordOption ::= ( 'PASSWORD' 'EXPIRE' ( 'DEFAULT' | 'NEVER' | 'INTERVAL' N 'DAY' )? | 'PASSWORD' 'HISTORY' ( 'DEFAULT' | N ) | 'PASSWORD' 'REUSE' 'INTERVAL' ( 'DEFAULT' | N 'DAY' ) | 'FAILED_LOGIN_ATTEMPTS' N | 'PASSWORD_LOCK_TIME' ( N | 'UNBOUNDED' ) )*

LockOption ::= ( 'ACCOUNT' 'LOCK' | 'ACCOUNT' 'UNLOCK' )?

AttributeOption ::= ( 'COMMENT' CommentString | 'ATTRIBUTE' AttributeString )?

ResourceGroupNameOption::= ( 'RESOURCE' 'GROUP' Identifier)?

RequireClauseOpt ::= ('REQUIRE' ('NONE' | 'SSL' | 'X509' | RequireListElement ('AND'? RequireListElement)*))?

RequireListElement ::= 'ISSUER' Issuer | 'SUBJECT' Subject | 'CIPHER' Cipher | 'SAN' SAN | 'TOKEN_ISSUER' TokenIssuer
```
## Examples

```sql
mysql> CREATE USER 'newuser' IDENTIFIED BY 'newuserpassword';
Query OK, 1 row affected (0.01 sec)

mysql> SHOW CREATE USER 'newuser';
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER for newuser@%                                                                                                                                            |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER 'newuser'@'%' IDENTIFIED WITH 'mysql_native_password' AS '*5806E04BBEE79E1899964C6A04D68BCA69B1A879' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```
### Modify basic user information

Change the password for user `newuser`:

```
mysql> ALTER USER 'newuser' IDENTIFIED BY 'newnewpassword';
Query OK, 0 rows affected (0.02 sec)

mysql> SHOW CREATE USER 'newuser';
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER for newuser@%                                                                                                                                            |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| CREATE USER 'newuser'@'%' IDENTIFIED WITH 'mysql_native_password' AS '*FB8A1EA1353E8775CA836233E367FBDFCB37BE73' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Lock the user `newuser`:

```sql
ALTER USER 'newuser' ACCOUNT LOCK;
```

```
Query OK, 0 rows affected (0.02 sec)
```

Modify the attributes of `newuser`:

```sql
ALTER USER 'newuser' ATTRIBUTE '{"newAttr": "value", "deprecatedAttr": null}';
SELECT * FROM information_schema.user_attributes;
```

```sql
+-----------+------+--------------------------+
| USER      | HOST | ATTRIBUTE                |
+-----------+------+--------------------------+
| newuser   | %    | {"newAttr": "value"}     |
+-----------+------+--------------------------+
1 rows in set (0.00 sec)
```

Modify the comment of `newuser` using `ALTER USER ... COMMENT`:

```sql
ALTER USER 'newuser' COMMENT 'Here is the comment';
SELECT * FROM information_schema.user_attributes;
```

```sql
+-----------+------+--------------------------------------------------------+
| USER      | HOST | ATTRIBUTE                                              |
+-----------+------+--------------------------------------------------------+
| newuser   | %    | {"comment": "Here is the comment", "newAttr": "value"} |
+-----------+------+--------------------------------------------------------+
1 rows in set (0.00 sec)
```

Remove the comment of `newuser` using `ALTER USER ... ATTRIBUTE`:

```sql
ALTER USER 'newuser' ATTRIBUTE '{"comment": null}';
SELECT * FROM information_schema.user_attributes;
```

```sql
+-----------+------+---------------------------+
| USER      | HOST | ATTRIBUTE                 |
+-----------+------+---------------------------+
| newuser   | %    | {"newAttr": "value"}      |
+-----------+------+---------------------------+
1 rows in set (0.00 sec)
```

Change the automatic password expiration policy for `newuser` to never expire via `ALTER USER ... PASSWORD EXPIRE NEVER`:

```sql
ALTER USER 'newuser' PASSWORD EXPIRE NEVER;
```

```
Query OK, 0 rows affected (0.02 sec)
```

Modify the password reuse policy for `newuser` to disallow the reuse of any password used within the last 90 days using `ALTER USER ... PASSWORD REUSE INTERVAL ... DAY`:

```sql
ALTER USER 'newuser' PASSWORD REUSE INTERVAL 90 DAY;
```

```
Query OK, 0 rows affected (0.02 sec)
```
### Modify the resource group bound to the user

Use `ALTER USER ... RESOURCE GROUP` to modify the resource group of the user `newuser` to `rg1`.

```sql
ALTER USER 'newuser' RESOURCE GROUP rg1;
```

```
Query OK, 0 rows affected (0.02 sec)
```

View the resource group bound to the current user:

```sql
SELECT USER, JSON_EXTRACT(User_attributes, "$.resource_group") FROM mysql.user WHERE user = "newuser";
```

```
+---------+---------------------------------------------------+
| USER    | JSON_EXTRACT(User_attributes, "$.resource_group") |
+---------+---------------------------------------------------+
| newuser | "rg1"                                             |
+---------+---------------------------------------------------+
1 row in set (0.02 sec)
```

Unbind the user to a resource group, that is, bind the user to the `default` resource group.

```sql
ALTER USER 'newuser' RESOURCE GROUP `default`;
SELECT USER, JSON_EXTRACT(User_attributes, "$.resource_group") FROM mysql.user WHERE user = "newuser";
```

```
+---------+---------------------------------------------------+
| USER    | JSON_EXTRACT(User_attributes, "$.resource_group") |
+---------+---------------------------------------------------+
| newuser | "default"                                         |
+---------+---------------------------------------------------+
1 row in set (0.02 sec)
```
## See also

* [Security Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql)

* [CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user)
* [DROP USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-user)
* [SHOW CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-user)
