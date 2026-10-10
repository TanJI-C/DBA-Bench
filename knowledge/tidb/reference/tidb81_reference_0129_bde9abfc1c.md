# Prepared statements syntax and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-prepared-statement.md`
- Source Title: `Prepared Statements`
- Source Heading Path: `Prepared Statements | Prepared Statements > SQL syntax | Prepared Statements > SQL syntax > Create a prepared statement | Prepared Statements > SQL syntax > Use the prepared statement | Prepared Statements > SQL syntax > Delete the prepared statement | Prepared Statements > Examples | Prepared Statements > Examples > `SELECT` example | Prepared Statements > Examples > `INSERT` example | Prepared Statements > Need help?`
- Source Line Ranges: `5-240`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `ecosystem`, `shared`
- Topic Tags: `prepared-statements`, `sql-syntax`, `prepare`, `execute`, `deallocate`, `user-variables`, `select`, `insert`, `jdbc`, `server-side-prepared-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0129_bde9abfc1c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-prepared-statement.md#prepared-statements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `02bc7ca3fdec556eb3c66c5faa74c7a265951f7c95279cd59fcbd9936b47acd2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-prepared-statement#prepared-statements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-prepared-statement.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB prepared statement SQL syntax, examples for PREPARE and EXECUTE with user variables, or JDBC server-side prepared statement configuration details.
- Retrieval Keywords: prepared statements, PREPARE {prepared_statement_name} FROM, EXECUTE {prepared_statement_name} USING, DEALLOCATE PREPARE, user variables, SET @{parameter_name}, SELECT * FROM `books` WHERE `id` = ?, INSERT INTO `books`, books_query, books_insert, JDBC, PreparedStatement, useServerPrepStmts, cachePrepStmts, prepStmtCacheSqlLimit, prepStmtCacheSize, server-side prepared statements, client-side prepared statement
- Follow-up Guidance: The chunk also points to the PREPARE, EXECUTE, DEALLOCATE, and SET statement references plus Java examples and JDBC connection string parameters for server-side prepared statements.
- Classification Note: This is reference content because it defines prepared statement syntax, parameter rules, concrete SQL and Java examples, and named JDBC configuration parameters from the official documentation.

## Official Source Content

# Prepared Statements

A [prepared statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare) templatizes multiple SQL statements in which only parameters are different. It separates the SQL statements from the parameters. You can use it to improve the following aspects of SQL statements:

- **Security**: Because parameters and statements are separated, the risk of [SQL injection](https://en.wikipedia.org/wiki/SQL_injection) attacks is avoided.
- **Performance**: Because the statement is parsed in advance on the TiDB server, only parameters are passed for subsequent executions, saving the cost of parsing the entire SQL statements, splicing SQL statement strings, and network transmission.

In most applications, SQL statements can be enumerated. You can use a limited number of SQL statements to complete data queries for the entire application. So using a prepared statement is a best practice.
## SQL syntax

This section describes the SQL syntax for creating, running and deleting a prepared statement.
### Create a prepared statement

```sql
PREPARE {prepared_statement_name} FROM '{prepared_statement_sql}';
```

| Parameter Name | Description |
| :-------------------------: | :------------------------------------: |
| `{prepared_statement_name}` | name of the prepared statement|
| `{prepared_statement_sql}`  | the prepared statement SQL with a question mark as a placeholder |

See [PREPARE statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare) for more information.
### Use the prepared statement

A prepared statement can only use **user variables** as parameters, so use the [`SET` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) to set the variables before the [`EXECUTE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-execute) can call the prepared statement.

```sql
SET @{parameter_name} = {parameter_value};
EXECUTE {prepared_statement_name} USING @{parameter_name};
```

| Parameter Name | Description |
| :-------------------------: | :-------------------------------------------------------------------: |
|     `{parameter_name}`      |                              user variable name                               |
|     `{parameter_value}`     |                              user variable value                               |
| `{prepared_statement_name}` | The name of the preprocessing statement, which must be the same as the name defined in the [Create a prepared statement](#create-a-prepared-statement) |

See the [`EXECUTE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-execute) for more information.
### Delete the prepared statement

```sql
DEALLOCATE PREPARE {prepared_statement_name};
```

| Parameter Name | Description |
| :-------------------------: | :-------------------------------------------------------------------: |
| `{prepared_statement_name}` | The name of the preprocessing statement, which must be the same as the name defined in the [Create a prepared statement](#create-a-prepared-statement) |

See the [`DEALLOCATE` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-deallocate) for more information.
## Examples

This section describes two examples of prepared statements: `SELECT` data and `INSERT` data.
### `SELECT` example

For example, you need to query a book with `id = 1` in the [`bookshop` application](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#books-table).

<div label="SQL" value="sql">

```sql
PREPARE `books_query` FROM 'SELECT * FROM `books` WHERE `id` = ?';
```

Running result:

```
Query OK, 0 rows affected (0.01 sec)
```

```sql
SET @id = 1;
```

Running result:

```
Query OK, 0 rows affected (0.04 sec)
```

```sql
EXECUTE `books_query` USING @id;
```

Running result:

```
+---------+---------------------------------+--------+---------------------+-------+--------+
| id      | title                           | type   | published_at        | stock | price  |
+---------+---------------------------------+--------+---------------------+-------+--------+
| 1       | The Adventures of Pierce Wehner | Comics | 1904-06-06 20:46:25 |   586 | 411.66 |
+---------+---------------------------------+--------+---------------------+-------+--------+
1 row in set (0.05 sec)
```

</div>

<div label="Java" value="java">

```java
// ds is an entity of com.mysql.cj.jdbc.MysqlDataSource
try (Connection connection = ds.getConnection()) {
    PreparedStatement preparedStatement = connection.prepareStatement("SELECT * FROM `books` WHERE `id` = ?");
    preparedStatement.setLong(1, 1);

    ResultSet res = preparedStatement.executeQuery();
    if(!res.next()) {
        System.out.println("No books in the table with id 1");
    } else {
        // got book's info, which id is 1
        System.out.println(res.getLong("id"));
        System.out.println(res.getString("title"));
        System.out.println(res.getString("type"));
    }
} catch (SQLException e) {
    e.printStackTrace();
}
```

</div>
### `INSERT` example

Using the [`books` table](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#books-table) as an example, you need to insert a book with `title = TiDB Developer Guide`, `type = Science & Technology`, `stock = 100`, `price = 0.0`, and `published_at = NOW()` (current time of insertion). Note that you don't need to specify the `AUTO_RANDOM` attribute in the **primary key** of the `books` table. For more information about inserting data, see [Insert Data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).

<div label="SQL" value="sql">

```sql
PREPARE `books_insert` FROM 'INSERT INTO `books` (`title`, `type`, `stock`, `price`, `published_at`) VALUES (?, ?, ?, ?, ?);';
```

Running result:

```
Query OK, 0 rows affected (0.03 sec)
```

```sql
SET @title = 'TiDB Developer Guide';
SET @type = 'Science & Technology';
SET @stock = 100;
SET @price = 0.0;
SET @published_at = NOW();
```

Running result:

```
Query OK, 0 rows affected (0.04 sec)
```

```sql
EXECUTE `books_insert` USING @title, @type, @stock, @price, @published_at;
```

Running result:

```
Query OK, 1 row affected (0.03 sec)
```

</div>

<div label="Java" value="java">

```java
try (Connection connection = ds.getConnection()) {
    String sql = "INSERT INTO `books` (`title`, `type`, `stock`, `price`, `published_at`) VALUES (?, ?, ?, ?, ?);";
    PreparedStatement preparedStatement = connection.prepareStatement(sql);

    preparedStatement.setString(1, "TiDB Developer Guide");
    preparedStatement.setString(2, "Science & Technology");
    preparedStatement.setInt(3, 100);
    preparedStatement.setBigDecimal(4, new BigDecimal("0.0"));
    preparedStatement.setTimestamp(5, new Timestamp(Calendar.getInstance().getTimeInMillis()));

    preparedStatement.executeUpdate();
} catch (SQLException e) {
    e.printStackTrace();
}
```

As you can see, JDBC helps you control the life cycle of prepared statements and you don't need to manually create, use, or delete prepared statements in your application. However, note that because TiDB is compatible with MySQL, the default configuration for using MySQL JDBC Driver on the client-side is not to enable the **_server-side_** prepared statement option, but to use the client-side prepared statement.

The following configurations help you use the TiDB server-side prepared statements under JDBC:

|            Parameter            |                 Means                  |   Recommended Scenario   | Recommended Configuration|
| :------------------------: | :-----------------------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------: | :----------------------: |
|    `useServerPrepStmts`    |    Whether to use the server side to enable prepared statements    |  When you need to use a prepared statement more than once                                                             |          `true`          |
|      `cachePrepStmts`      |       Whether the client caches prepared statements        |                                                           `useServerPrepStmts=true`                                                             |          `true`          |
|  `prepStmtCacheSqlLimit`   |  Maximum size of a prepared statement (256 characters by default)  | When the prepared statement is greater than 256 characters | Configured according to the actual size of the prepared statement |
|    `prepStmtCacheSize`     | Maximum number of prepared statements (25 by default) | When the number of prepared statements is greater than 25  | Configured according to the actual number of prepared statements |

The following is a typical scenario of JDBC connection string configurations. Host: `127.0.0.1`, Port: `4000`, User name: `root`, Password: null, Default database: `test`:

```
jdbc:mysql://127.0.0.1:4000/test?user=root&useConfigs=maxPerformance&useServerPrepStmts=true&prepStmtCacheSqlLimit=2048&prepStmtCacheSize=256&rewriteBatchedStatements=true&allowMultiQueries=true
```

You can also see the [insert rows](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data#insert-rows) chapter if you need to change other JDBC parameters when inserting data.

For a complete example in Java, see:

- [Connect to TiDB with JDBC](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-jdbc)
- [Connect to TiDB with Hibernate](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-hibernate)
- [Connect to TiDB with Spring Boot](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-java-spring-boot)

</div>
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
