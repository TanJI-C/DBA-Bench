# SET GLOBAL or SESSION variables syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-variable.md`
- Source Title: `SET [GLOBAL|SESSION] <variable> | TiDB SQL Statement Reference`
- Source Heading Path: ``SET [GLOBAL|SESSION] <variable>` | `SET [GLOBAL|SESSION] <variable>` > Synopsis | `SET [GLOBAL|SESSION] <variable>` > Examples | `SET [GLOBAL|SESSION] <variable>` > MySQL compatibility | `SET [GLOBAL|SESSION] <variable>` > See also`
- Source Line Ranges: `5-115`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `set statement`, `system variables`, `user variables`, `global scope`, `session scope`, `sql_mode`, `mysql compatibility`, `syntax`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0639_5cd4f43c6b`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-variable.md#set-global-session-variable`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9500ffecc39a196291f98948a65c8dbe4d48703d68dd89131d4f0407e81b149c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable#set-global-session-variable
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-variable.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the syntax, scope behavior, examples, or MySQL compatibility of `SET GLOBAL` or `SET SESSION` for system variables or `@` user variables in TiDB.
- Retrieval Keywords: SET GLOBAL, SET SESSION, SET [GLOBAL|SESSION] <variable>, SetVariableStmt, SystemVariable, UserVariable, sql_mode, SHOW GLOBAL VARIABLES LIKE 'sql_mode', SHOW SESSION VARIABLES LIKE 'sql_mode', SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER', SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER', SET @myvar := 5, user-defined variables, GLOBAL scope, SESSION scope, SET PERSIST, SET PERSIST_ONLY, MySQL compatibility
- Follow-up Guidance: The source also points to `SHOW [GLOBAL|SESSION] VARIABLES` for checking variable values.
- Classification Note: This is reference content because it defines the `SET [GLOBAL|SESSION]` statement syntax, demonstrates exact SQL examples, and lists explicit MySQL compatibility differences from the official documentation.

## Official Source Content

# `SET [GLOBAL|SESSION] <variable>`

The statement `SET [GLOBAL|SESSION]` modifies one of TiDB's built in variables. These variables can be [system variables](https://docs.pingcap.com/tidb/stable/system-variables) of either `SESSION` or `GLOBAL` scope or [user variables](https://docs.pingcap.com/tidb/stable/user-defined-variables).

> **Warning:**
>
> User-defined variables are still an experimental feature. It is **NOT** recommended that you use them in the production environment.

> **Note:**
>
> Similar to MySQL, changes to `GLOBAL` variables do not apply to either existing connections, or the local connection. Only new sessions reflect the changes to the value.
## Synopsis

```ebnf+diagram
SetVariableStmt ::=
    "SET" Variable "=" Expression ("," Variable "=" Expression )*

Variable ::=
    ("GLOBAL" | "SESSION") SystemVariable
|   UserVariable 
```
## Examples

Get the value of `sql_mode`.

```sql
mysql> SHOW GLOBAL VARIABLES LIKE 'sql_mode';
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| Variable_name | Value                                                                                                                                     |
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| sql_mode      | ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SHOW SESSION VARIABLES LIKE 'sql_mode';
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| Variable_name | Value                                                                                                                                     |
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| sql_mode      | ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Update the value of `sql_mode` globally. If you check the value of `SQL_mode` after the update, you can see that the value of `SESSION` level has not been updated:

```sql
mysql> SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER';
Query OK, 0 rows affected (0.03 sec)

mysql> SHOW GLOBAL VARIABLES LIKE 'sql_mode';
+---------------+-----------------------------------------+
| Variable_name | Value                                   |
+---------------+-----------------------------------------+
| sql_mode      | STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER |
+---------------+-----------------------------------------+
1 row in set (0.00 sec)

mysql> SHOW SESSION VARIABLES LIKE 'sql_mode';
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| Variable_name | Value                                                                                                                                     |
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
| sql_mode      | ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
+---------------+-------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

Using `SET SESSION` takes effect immediately:

```sql
mysql> SET SESSION sql_mode = 'STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER';
Query OK, 0 rows affected (0.01 sec)

mysql> SHOW SESSION VARIABLES LIKE 'sql_mode';
+---------------+-----------------------------------------+
| Variable_name | Value                                   |
+---------------+-----------------------------------------+
| sql_mode      | STRICT_TRANS_TABLES,NO_AUTO_CREATE_USER |
+---------------+-----------------------------------------+
1 row in set (0.00 sec)
```

User variables start with a `@`.

```sql
SET @myvar := 5;
Query OK, 0 rows affected (0.00 sec)

SELECT @myvar, @myvar + 1;
+--------+------------+
| @myvar | @myvar + 1 |
+--------+------------+
|      5 |          6 |
+--------+------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

The following behavior differences apply:

* Changes made with `SET GLOBAL` will be propagated to all TiDB instances in the cluster. This differs from MySQL, where changes do not propagate to replicas.
* TiDB presents several variables as both readable and settable. This is required for MySQL compatibility, because it is common for both applications and connectors to read MySQL variables. For example: JDBC connectors both read and set query cache settings, despite not relying on the behavior.
* Changes made with `SET GLOBAL` will persist through TiDB server restarts. This means that `SET GLOBAL` in TiDB behaves more similar to `SET PERSIST` as available in MySQL 8.0 and above.
* TiDB does not support `SET PERSIST` and `SET PERSIST_ONLY`, because TiDB persists global variables.
## See also

* [SHOW \[GLOBAL|SESSION\] VARIABLES](/sql-statements/sql-statement-show-variables.md)
