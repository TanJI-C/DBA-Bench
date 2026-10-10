# JDBC streaming results and prepare-related Connector/J parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-connection-parameters.md`
- Source Title: `Connection Pools and Connection Parameters`
- Source Heading Path: `Connection Pools and Connection Parameters > Connection parameters > JDBC API > Use `StreamingResult` to get the execution result | Connection Pools and Connection Parameters > Connection parameters > MySQL JDBC parameters | Connection Pools and Connection Parameters > Connection parameters > MySQL JDBC parameters > Prepare-related parameters`
- Source Line Ranges: `142-205`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `dashboard`
- Topic Tags: `jdbc`, `streamingresult`, `fetchsize`, `cursor-fetch`, `prepare`, `prepared-statements`, `connector-j`, `monitoring`, `query-summary`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0039_7b4d0da50f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-connection-parameters.md#use-streamingresult-to-get-the-execution-result`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc5935d2ddf18f178f0adca5025117fedb6541389571e2c844e38cb41ce1ae17`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-connection-parameters#use-streamingresult-to-get-the-execution-result
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-connection-parameters.md

## Retrieval Guidance

- Use When: Use this chunk when searching for MySQL Connector/J parameters for JDBC streaming result handling, Cursor Fetch, or prepared statement behavior and how to verify them in TiDB monitoring.
- Retrieval Keywords: StreamingResult, FetchSize, Integer.MIN_VALUE, useCursorFetch=true, clobberStreamingResults=true, No statements may be issued when any streaming result sets are open and in use on a given connection, useServerPrepStmts, cachePrepStmts, prepStmtCacheSqlLimit, prepStmtCacheSize, useConfigs=maxPerformance, Query Summary, CPS By Instance, COM_QUERY, COM_STMT_EXECUTE, COM_STMT_PREPARE, COM_STMT_CLOSE, Prepared Statements
- Follow-up Guidance: The content also describes checking TiDB monitoring dashboard through Query Summary > CPS By Instance to compare COM_QUERY, COM_STMT_EXECUTE, COM_STMT_PREPARE, and COM_STMT_CLOSE for verification.
- Classification Note: This chunk is classified as configuration because it introduces JDBC URL parameters and FetchSize settings that affect streaming reads and prepared statement execution behavior.

## Official Source Content

#### Use `StreamingResult` to get the execution result

In most scenarios, to improve execution efficiency, JDBC obtains query results in advance and saves them in client memory by default. But when the query returns a super large result set, the client often wants the database server to reduce the number of records returned at a time and waits until the client's memory is ready and it requests for the next batch.

Usually, there are two kinds of processing methods in JDBC:

- [Set **FetchSize** to `Integer.MIN_VALUE`](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-implementation-notes.html#ResultSet) to ensure that the client does not cache. The client will read the execution result from the network connection through `StreamingResult`.

    When the client uses the streaming read method, it needs to finish reading or close `resultset` before continuing to use the statement to make a query. Otherwise, the error `No statements may be issued when any streaming result sets are open and in use on a given connection. Ensure that you have called .close() on any active streaming result sets before attempting more queries.` is returned.

    To avoid such an error in queries before the client finishes reading or closes `resultset`, you can add the `clobberStreamingResults=true` parameter in the URL. Then, `resultset` is automatically closed but the result set to be read in the previous streaming query is lost.

- To use Cursor Fetch, first [set `FetchSize`](http://makejavafaster.blogspot.com/2015/06/jdbc-fetch-size-performance.html) as a positive integer and configure `useCursorFetch=true` in the JDBC URL.

TiDB supports both methods, but it is preferred that you use the first method, because it is a simpler implementation and has a better execution efficiency.
### MySQL JDBC parameters

JDBC usually provides implementation-related configurations in the form of JDBC URL parameters. This section introduces [MySQL Connector/J's parameter configurations](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-configuration-properties.html) (If you use MariaDB, see [MariaDB's parameter configurations](https://mariadb.com/docs/connectors/mariadb-connector-j/about-mariadb-connector-j#optional-url-parameters)). Because this document cannot cover all configuration items, it mainly focuses on several parameters that might affect performance.
#### Prepare-related parameters

This section introduces parameters related to `Prepare`.

- **useServerPrepStmts**

    **useServerPrepStmts** is set to `false` by default, that is, even if you use the Prepare API, the "prepare" operation will be done only on the client. To avoid the parsing overhead of the server, if the same SQL statement uses the Prepare API multiple times, it is recommended to set this configuration to `true`.

    To verify that this setting already takes effect, you can do:

    - Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
    - If `COM_QUERY` is replaced by `COM_STMT_EXECUTE` or `COM_STMT_PREPARE` in the request, it means this setting already takes effect.

- **cachePrepStmts**

    Although `useServerPrepStmts=true` allows the server to execute Prepared Statements, by default, the client closes the Prepared Statements after each execution and does not reuse them. This means that the "prepare" operation is not even as efficient as text file execution. To solve this, it is recommended that after setting `useServerPrepStmts=true`, you should also configure `cachePrepStmts=true`. This allows the client to cache Prepared Statements.

    To verify that this setting already takes effect, you can do:

    - Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
    - If the number of `COM_STMT_EXECUTE` in the request is far more than the number of `COM_STMT_PREPARE`, it means this setting already takes effect.

    In addition, configuring `useConfigs=maxPerformance` will configure multiple parameters at the same time, including `cachePrepStmts=true`.

- **prepStmtCacheSqlLimit**

    After configuring `cachePrepStmts`, also pay attention to the `prepStmtCacheSqlLimit` configuration (the default value is `256`). This configuration controls the maximum length of the Prepared Statements cached on the client.

    The Prepared Statements that exceed this maximum length will not be cached, so they cannot be reused. In this case, you may consider increasing the value of this configuration depending on the actual SQL length of the application.

    You need to check whether this setting is too small if you:

    - Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
    - And find that `cachePrepStmts=true` has been configured, but `COM_STMT_PREPARE` is still mostly equal to `COM_STMT_EXECUTE` and `COM_STMT_CLOSE` exists.

- **prepStmtCacheSize**

    **prepStmtCacheSize** controls the number of cached Prepared Statements (the default value is `25`). If your application requires "preparing" many types of SQL statements and wants to reuse Prepared Statements, you can increase this value.

    To verify that this setting already takes effect, you can do:

    - Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
    - If the number of `COM_STMT_EXECUTE` in the request is far more than the number of `COM_STMT_PREPARE`, it means this setting already takes effect.
