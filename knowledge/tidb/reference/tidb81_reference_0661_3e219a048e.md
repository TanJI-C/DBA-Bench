# SHOW GRANTS syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-grants.md`
- Source Title: `SHOW GRANTS | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW GRANTS | SHOW GRANTS > Synopsis | SHOW GRANTS > Examples | SHOW GRANTS > MySQL compatibility | SHOW GRANTS > See also`
- Source Line Ranges: `5-60`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `privileges`, `users`, `roles`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0661_3e219a048e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-grants.md#show-grants`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9eedd077fbb1642952bd0fafbef9317534fbd527790109d4cd82b4e174d8059`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants#show-grants
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-grants.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the SHOW GRANTS syntax, examples of listing privileges for the current user or a specified user, or MySQL compatibility details for SHOW GRANTS in TiDB.
- Retrieval Keywords: SHOW GRANTS, SHOW GRANTS FOR, SHOW GRANTS USING RolenameList, ShowGrantsStmt, CURRENT_USER(), Username @ Hostname, RolenameList, USAGE privilege, GRANT USAGE ON *.*, GRANT SELECT ON test.*, ERROR 1141 (42000), There is no such grant defined for user, MySQL compatibility, SHOW CREATE USER, GRANT
- Follow-up Guidance: The source also points to related statements SHOW CREATE USER and GRANT.
- Classification Note: This is reference content because it defines the SHOW GRANTS statement syntax, shows exact example output and error text, and states its MySQL compatibility.

## Official Source Content

# SHOW GRANTS

This statement shows a list of privileges associated with a user. As in MySQL, the `USAGE` privileges denotes the ability to login to TiDB.
## Synopsis

```ebnf+diagram
ShowGrantsStmt ::=
    "SHOW" "GRANTS" ("FOR" Username ("USING" RolenameList)?)?

Username ::=
    "CURRENT_USER" ( "(" ")" )?
| Username ("@" Hostname)?

RolenameList ::=
    Rolename ("@" Hostname)? ("," Rolename ("@" Hostname)? )*
```
## Examples

```sql
mysql> SHOW GRANTS;
+-------------------------------------------+
| Grants for User                           |
+-------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' |
+-------------------------------------------+
1 row in set (0.00 sec)

mysql> SHOW GRANTS FOR 'u1';
ERROR 1141 (42000): There is no such grant defined for user 'u1' on host '%'
mysql> CREATE USER u1;
Query OK, 1 row affected (0.04 sec)

mysql> GRANT SELECT ON test.* TO u1;
Query OK, 0 rows affected (0.04 sec)

mysql> SHOW GRANTS FOR u1;
+------------------------------------+
| Grants for u1@%                    |
+------------------------------------+
| GRANT USAGE ON *.* TO 'u1'@'%'     |
| GRANT Select ON test.* TO 'u1'@'%' |
+------------------------------------+
2 rows in set (0.00 sec)
```
## MySQL compatibility

The `SHOW GRANTS` statement in TiDB is fully compatible with MySQL. If you find any compatibility differences, [report a bug](https://docs.pingcap.com/tidb/stable/support).
## See also

* [SHOW CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-user)
* [GRANT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-grant-privileges)
