# Batch rewrite, maxPerformance, and timeout Connector/J parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-connection-parameters.md`
- Source Title: `Connection Pools and Connection Parameters`
- Source Heading Path: `Connection Pools and Connection Parameters > Connection parameters > MySQL JDBC parameters > Batch-related parameters | Connection Pools and Connection Parameters > Connection parameters > MySQL JDBC parameters > Integrate parameters | Connection Pools and Connection Parameters > Connection parameters > MySQL JDBC parameters > Timeout-related parameters`
- Source Line Ranges: `206-279`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `jdbc`, `batch`, `rewritebatchedstatements`, `allowmultiqueries`, `maxperformance`, `timeouts`, `wait-timeout`, `max-execution-time`, `idle-transaction-timeout`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0040_3f94b91abb`
- Source ID: `tidb-docs-8.1:develop/dev-guide-connection-parameters.md#batch-related-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9490602977b1435bf8ffdb74f0beed04556c348c8bd6a65e07e8fb79567f4b4f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-connection-parameters#batch-related-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-connection-parameters.md

## Retrieval Guidance

- Use When: Use this chunk when searching for Connector/J batch rewrite, maxPerformance, allowMultiQueries, or timeout-related connection string parameters for TiDB.
- Retrieval Keywords: rewriteBatchedStatements=true, addBatch(), executeBatch(), allowMultiQueries=true, useServerPrepStmts=true, useConfigs=maxPerformance, select @@session.transaction_read_only, wait_timeout, max_execution_time, tidb_idle_transaction_timeout, sessionVariables=wait_timeout=3600, sessionVariables=max_execution_time=300000, batch update, multiple queries, ON DUPLICATE KEY UPDATE, VALUES(`a`)
- Follow-up Guidance: The content also notes monitoring can show a decreased number of SELECT statements after configuring useConfigs=maxPerformance.
- Classification Note: This chunk is classified as configuration because it focuses on JDBC URL and session parameters that control batch SQL rewriting, integrated performance presets, and timeout behavior.

## Official Source Content

#### Batch-related parameters

While processing batch writes, it is recommended to configure `rewriteBatchedStatements=true`. After using `addBatch()` or `executeBatch()`, JDBC still sends SQL one by one by default, for example:

```java
pstmt = prepare("INSERT INTO `t` (a) values(?)");
pstmt.setInt(1, 10);
pstmt.addBatch();
pstmt.setInt(1, 11);
pstmt.addBatch();
pstmt.setInt(1, 12);
pstmt.executeBatch();
```

Although `Batch` methods are used, the SQL statements sent to TiDB are still individual `INSERT` statements:

```sql
INSERT INTO `t` (`a`) VALUES(10);
INSERT INTO `t` (`a`) VALUES(11);
INSERT INTO `t` (`a`) VALUES(12);
```

But if you set `rewriteBatchedStatements=true`, the SQL statements sent to TiDB will be a single `INSERT` statement:

```sql
INSERT INTO `t` (`a`) values(10),(11),(12);
```

Note that the rewrite of the `INSERT` statements is to concatenate the values after multiple "values" keywords into a whole SQL statement. If the `INSERT` statements have other differences, they cannot be rewritten, for example:

```sql
INSERT INTO `t` (`a`) VALUES (10) ON DUPLICATE KEY UPDATE `a` = 10;
INSERT INTO `t` (`a`) VALUES (11) ON DUPLICATE KEY UPDATE `a` = 11;
INSERT INTO `t` (`a`) VALUES (12) ON DUPLICATE KEY UPDATE `a` = 12;
```

The above `INSERT` statements cannot be rewritten into one statement. But if you change the three statements into the following ones:

```sql
INSERT INTO `t` (`a`) VALUES (10) ON DUPLICATE KEY UPDATE `a` = VALUES(`a`);
INSERT INTO `t` (`a`) VALUES (11) ON DUPLICATE KEY UPDATE `a` = VALUES(`a`);
INSERT INTO `t` (`a`) VALUES (12) ON DUPLICATE KEY UPDATE `a` = VALUES(`a`);
```

Then they meet the rewrite requirement. The above `INSERT` statements will be rewritten into the following one statement:

```sql
INSERT INTO `t` (`a`) VALUES (10), (11), (12) ON DUPLICATE KEY UPDATE a = VALUES(`a`);
```

If there are three or more updates during the batch update, the SQL statements will be rewritten and sent as multiple queries. This effectively reduces the client-to-server request overhead, but the side effect is that a larger SQL statement is generated. For example:

```sql
UPDATE `t` SET `a` = 10 WHERE `id` = 1; UPDATE `t` SET `a` = 11 WHERE `id` = 2; UPDATE `t` SET `a` = 12 WHERE `id` = 3;
```

In addition, because of a [client bug](https://bugs.mysql.com/bug.php?id=96623), if you want to configure `rewriteBatchedStatements=true` and `useServerPrepStmts=true` during batch update, it is recommended that you also configure the `allowMultiQueries=true` parameter to avoid this bug.
#### Integrate parameters

Through monitoring, you might notice that although the application only performs `INSERT` operations to the TiDB cluster, there are a lot of redundant `SELECT` statements. Usually this happens because JDBC sends some SQL statements to query the settings, for example, `select @@session.transaction_read_only`. These SQL statements are useless for TiDB, so it is recommended that you configure `useConfigs=maxPerformance` to avoid extra overhead.

`useConfigs=maxPerformance` includes a group of configurations. To get the detailed configurations in MySQL Connector/J 8.0 and those in MySQL Connector/J 5.1, see [mysql-connector-j 8.0](https://github.com/mysql/mysql-connector-j/blob/release/8.0/src/main/resources/com/mysql/cj/configurations/maxPerformance.properties) and [mysql-connector-j 5.1](https://github.com/mysql/mysql-connector-j/blob/release/5.1/src/com/mysql/jdbc/configs/maxPerformance.properties) respectively.

After it is configured, you can check the monitoring to see a decreased number of `SELECT` statements.
#### Timeout-related parameters

TiDB provides two MySQL-compatible parameters to control the timeout: [`wait_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#wait_timeout) and [`max_execution_time`](https://docs.pingcap.com/tidb/stable/system-variables#max_execution_time). These two parameters respectively control the connection idle timeout with the Java application and the timeout of the SQL execution in the connection; that is to say, these parameters control the longest idle time and the longest busy time for the connection between TiDB and the Java application. Since TiDB v5.4, the default value of `wait_timeout` is `28800` seconds, which is 8 hours. For TiDB versions earlier than v5.4, the default value is `0`, which means the timeout is unlimited. The default value of `max_execution_time` is `0`, which means the maximum execution time of a SQL statement is unlimited.

The default value of [`wait_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#wait_timeout) is relatively large. In scenarios where a transaction starts but is neither committed nor rolled back, you might need a finer-grained control and a shorter timeout to prevent prolonged lock holding. In this case, you can use [`tidb_idle_transaction_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760) (introduced in TiDB v7.6.0) to control the idle timeout for transactions in a user session.

However, in an actual production environment, idle connections and SQL statements with excessively long execution time negatively affect databases and applications. To avoid idle connections and SQL statements that are executed for too long, you can configure these two parameters in your application's connection string. For example, set `sessionVariables=wait_timeout=3600` (1 hour) and `sessionVariables=max_execution_time=300000` (5 minutes).
