# SHOW CREATE USER syntax, example, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-create-user.md`
- Source Title: `SHOW CREATE USER | TiDB SQL Statement Reference`
- Source Heading Path: `SHOW CREATE USER | SHOW CREATE USER > Synopsis | SHOW CREATE USER > Examples | SHOW CREATE USER > MySQL compatibility | SHOW CREATE USER > See also`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `show create user`, `create user syntax`, `user accounts`, `mysql compatibility`, `show grants`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0655_4257d4d8b9`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-create-user.md#show-create-user`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9ac75caeeed65788deb77464ea9ff09f30f6a5c9c6dea6901bddece50942b29`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-user#show-create-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-create-user.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, example output, or MySQL compatibility notes of `SHOW CREATE USER` for a user account or `CURRENT_USER()` in TiDB SQL.
- Retrieval Keywords: SHOW CREATE USER, ShowCreateUserStmt, SHOW CREATE USER 'root', CURRENT_USER(), CREATE USER syntax, CREATE USER for root@%, IDENTIFIED WITH 'mysql_native_password' AS '', REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK, SHOW GRANTS FOR 'root', MySQL compatibility, not yet supported options will be parsed but ignored, Security compatibility
- Follow-up Guidance: The source also points to `CREATE USER`, `SHOW GRANTS`, and `DROP USER` as related statements.
- Classification Note: This is reference content because it defines the `SHOW CREATE USER` statement syntax, shows example SQL and output, and notes compatibility behavior with MySQL.

## Official Source Content

# SHOW CREATE USER

This statement shows how to re-create a user using the `CREATE USER` syntax.
## Synopsis

```ebnf+diagram
ShowCreateUserStmt ::=
    "SHOW" "CREATE" "USER" (Username ("@" Hostname)? | "CURRENT_USER" ( "(" ")" )? )
```
## Examples

```sql
mysql> SHOW CREATE USER 'root';
+--------------------------------------------------------------------------------------------------------------------------+
| CREATE USER for root@%                                                                                                   |
+--------------------------------------------------------------------------------------------------------------------------+
| CREATE USER 'root'@'%' IDENTIFIED WITH 'mysql_native_password' AS '' REQUIRE NONE PASSWORD EXPIRE DEFAULT ACCOUNT UNLOCK |
+--------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SHOW GRANTS FOR 'root';
+-------------------------------------------+
| Grants for root@%                         |
+-------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' |
+-------------------------------------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

* The output of `SHOW CREATE USER` is designed to match MySQL, but several of the `CREATE` options are not yet supported by TiDB. Not yet supported options will be parsed but ignored. See [Security compatibility](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql) for more details.

* The output of `SHOW CREATE USER` is designed to match MySQL, but several of the `CREATE` options are not yet supported by TiDB. Not yet supported options will be parsed but ignored. See [Security compatibility](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql/) for more details.
## See also

* [CREATE USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user)
* [SHOW GRANTS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-grants)
* [DROP USER](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-user)
