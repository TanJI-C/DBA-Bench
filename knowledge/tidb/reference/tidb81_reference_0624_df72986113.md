# RENAME USER syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-rename-user.md`
- Source Title: `RENAME USER`
- Source Heading Path: `RENAME USER | RENAME USER > Synopsis | RENAME USER > Examples | RENAME USER > MySQL compatibility | RENAME USER > See also`
- Source Line Ranges: `5-81`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `rename-user`, `user-management`, `sql-syntax`, `examples`, `mysql-compatibility`, `grants`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0624_df72986113`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-rename-user.md#rename-user`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `80ccac41858cefaab98e2c27002ebc070876044c2a4271f6c86484b73bc5a2fc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-user#rename-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-rename-user.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SQL syntax, example behavior, or MySQL compatibility of renaming an existing user with RENAME USER.
- Retrieval Keywords: RENAME USER, RenameUserStmt, UserToUser, Username, CURRENT_USER, RENAME USER 'newuser' TO 'testuser', SHOW GRANTS, ERROR 1141 (42000), There is no such grant defined for user, MySQL compatibility, CREATE USER, DROP USER
- Follow-up Guidance: The source also points to related statements CREATE USER, SHOW GRANTS, and DROP USER.
- Classification Note: This is reference content because it provides the formal synopsis, concrete SQL examples and outputs, and a compatibility note for the RENAME USER statement.

## Official Source Content

# RENAME USER

`RENAME USER` is used to rename an existing user.
## Synopsis

```ebnf+diagram
RenameUserStmt ::=
    'RENAME' 'USER' UserToUser ( ',' UserToUser )*
UserToUser ::=
    Username 'TO' Username
Username ::=
    StringName ('@' StringName | singleAtIdentifier)? | 'CURRENT_USER' OptionalBraces
```
## Examples

```sql
CREATE USER 'newuser' IDENTIFIED BY 'mypassword';
```

```sql
Query OK, 1 row affected (0.02 sec)
```

```sql
SHOW GRANTS FOR 'newuser';
```

```sql
+-------------------------------------+
| Grants for newuser@%                |
+-------------------------------------+
| GRANT USAGE ON *.* TO 'newuser'@'%' |
+-------------------------------------+
1 row in set (0.00 sec)
```

```sql
RENAME USER 'newuser' TO 'testuser';
```

```sql
Query OK, 0 rows affected (0.08 sec)
```

```sql
SHOW GRANTS FOR 'testuser';
```

```sql
+--------------------------------------+
| Grants for testuser@%                |
+--------------------------------------+
| GRANT USAGE ON *.* TO 'testuser'@'%' |
+--------------------------------------+
1 row in set (0.00 sec)
```

```sql
SHOW GRANTS FOR 'newuser';
```

```sql
ERROR 1141 (42000): There is no such grant defined for user 'newuser' on host '%'
```
## MySQL compatibility

`RENAME USER` is expected to be fully compatible with MySQL. If you find any compatibility difference, you can [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user)
* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)
* [DROP USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-user)
