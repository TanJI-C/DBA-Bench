# JDBC parameter tuning for batch, performance, timeout, and connection strings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Batch-related parameters | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Integrate parameters | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Timeout-related parameters | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Typical JDBC connection string parameters`
- Source Line Ranges: `124-227`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `shared`, `sql`
- Topic Tags: `jdbc`, `batch-writes`, `prepared-statements`, `connection-string`, `timeouts`, `ssl`, `performance-tuning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0065_73cf7ae2b8`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#batch-related-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ff8b6580dd8438043239ffe81373d67aa2ba1104412f7ea434ad09ad91b36646`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#batch-related-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB Java JDBC parameter details for batch rewrite behavior, maxPerformance integration, timeout session variables, or a typical MySQL connection string.
- Retrieval Keywords: rewriteBatchedStatements=true, useServerPrepStmts=true, allowMultiQueries=true, useConfigs=maxPerformance, select @@session.transaction_read_only, wait_timeout, interactive_timeout, max_execution_time, sessionVariables=wait_timeout=3600, sessionVariables=max_execution_time=300000, characterEncoding=UTF-8, useSSL=false, cachePrepStmts=true, prepStmtCacheSqlLimit=10000, prepStmtCacheSize=1000, Typical JDBC connection string parameters, insert into t(a) values(10),(11),(12), on duplicate key update a = values(a)
- Follow-up Guidance: The source also notes that over a public network the connection string needs `useSSL=true` and links to enabling TLS between TiDB clients and servers.
- Classification Note: This is classified as configuration because the content centers on JDBC connection parameters, session variables, and connection string options for TiDB Java applications.

## Official Source Content

#### Batch-related parameters

While processing batch writes, it is recommended to configure `rewriteBatchedStatements=true`. After using `addBatch()` or `executeBatch()`, JDBC still sends SQL one by one by default, for example:

```java
pstmt = prepare("insert into t (a) values(?)");
pstmt.setInt(1, 10);
pstmt.addBatch();
pstmt.setInt(1, 11);
pstmt.addBatch();
pstmt.setInt(1, 12);
pstmt.executeBatch();
```

Although `Batch` methods are used, the SQL statements sent to TiDB are still individual `INSERT` statements:

```sql
insert into t(a) values(10);
insert into t(a) values(11);
insert into t(a) values(12);
```

But if you set `rewriteBatchedStatements=true`, the SQL statements sent to TiDB will be a single `INSERT` statement:

```sql
insert into t(a) values(10),(11),(12);
```

Note that the rewrite of the `INSERT` statements is to concatenate the values after multiple "values" keywords into a whole SQL statement. If the `INSERT` statements have other differences, they cannot be rewritten, for example:

```sql
insert into t (a) values (10) on duplicate key update a = 10;
insert into t (a) values (11) on duplicate key update a = 11;
insert into t (a) values (12) on duplicate key update a = 12;
```

The above `INSERT` statements cannot be rewritten into one statement. But if you change the three statements into the following ones:

```sql
insert into t (a) values (10) on duplicate key update a = values(a);
insert into t (a) values (11) on duplicate key update a = values(a);
insert into t (a) values (12) on duplicate key update a = values(a);
```

Then they meet the rewrite requirement. The above `INSERT` statements will be rewritten into the following one statement:

```sql
insert into t (a) values (10), (11), (12) on duplicate key update a = values(a);
```

If there are three or more updates during the batch update, the SQL statements will be rewritten and sent as multiple queries. This effectively reduces the client-to-server request overhead, but the side effect is that a larger SQL statement is generated. For example:

```sql
update t set a = 10 where id = 1; update t set a = 11 where id = 2; update t set a = 12 where id = 3;
```

In addition, because of a [client bug](https://bugs.mysql.com/bug.php?id=96623), if you want to configure `rewriteBatchedStatements=true` and `useServerPrepStmts=true` during batch update, it is recommended that you also configure the `allowMultiQueries=true` parameter to avoid this bug.
#### Integrate parameters

Through monitoring, you might notice that although the application only performs `INSERT` operations to the TiDB cluster, there are a lot of redundant `SELECT` statements. Usually this happens because JDBC sends some SQL statements to query the settings, for example, `select @@session.transaction_read_only`. These SQL statements are useless for TiDB, so it is recommended that you configure `useConfigs=maxPerformance` to avoid extra overhead.

`useConfigs=maxPerformance` includes a group of configurations. To get the detailed configurations in MySQL Connector/J 8.0 and those in MySQL Connector/J 5.1, see [mysql-connector-j 8.0](https://github.com/mysql/mysql-connector-j/blob/release/8.0/src/main/resources/com/mysql/cj/configurations/maxPerformance.properties) and [mysql-connector-j 5.1](https://github.com/mysql/mysql-connector-j/blob/release/5.1/src/com/mysql/jdbc/configs/maxPerformance.properties) respectively.

After it is configured, you can check the monitoring to see a decreased number of `SELECT` statements.

> **Note:**
>
> Enabling `useConfigs=maxPerformance` requires MySQL Connector/J version 8.0.33 or later. For more details, see [MySQL JDBC Bug](https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility#mysql-jdbc-bugs).
#### Timeout-related parameters

TiDB provides the following MySQL-compatible timeout control parameters.

- `wait_timeout`: controls the non-interactive idle timeout for the connection to Java applications. Starting from TiDB v5.4, the default value of `wait_timeout` is `28800` seconds, which is 8 hours. For TiDB versions earlier than v5.4, the default value is `0`, which means the timeout is unlimited.
- `interactive_timeout`: controls the interactive idle timeout for the connection to Java applications. The value is 8 hours by default.
- `max_execution_time`: controls the timeout for SQL execution in the connection, only effective for read-only SQL statements. The value is `0` by default, which allows the connection to be infinitely busy, that is, an SQL statement is executed for an infinitely long time.

However, in an actual production environment, idle connections and SQL statements with excessively long execution time negatively affect databases and applications. To avoid idle connections and SQL statements that are executed for too long, you can configure these two parameters in your application's connection string. For example, set `sessionVariables=wait_timeout=3600` (1 hour) and `sessionVariables=max_execution_time=300000` (5 minutes).
#### Typical JDBC connection string parameters

Combining the preceding parameter values, the JDBC connection string configuration is as follows:

```
jdbc:mysql://<IP_ADDRESS>:<PORT_NUMBER>/<DATABASE_NAME>?characterEncoding=UTF-8&useSSL=false&useServerPrepStmts=true&cachePrepStmts=true&prepStmtCacheSqlLimit=10000&prepStmtCacheSize=1000&useConfigs=maxPerformance&rewriteBatchedStatements=true
```

> **Note:**
>
> If you are connecting over a public network, you need to set `useSSL=true` and [enable TLS between TiDB clients and servers](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers).
