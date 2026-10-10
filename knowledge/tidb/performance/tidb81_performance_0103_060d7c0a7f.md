# JDBC API usage patterns for prepare batch and streaming

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > JDBC | Best Practices for Developing Java Applications with TiDB > JDBC > JDBC API | Best Practices for Developing Java Applications with TiDB > JDBC > JDBC API > Use Prepare API | Best Practices for Developing Java Applications with TiDB > JDBC > JDBC API > Use Batch API | Best Practices for Developing Java Applications with TiDB > JDBC > JDBC API > Use `StreamingResult` to get the execution result`
- Source Line Ranges: `31-75`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `jdbc`, `prepared-statements`, `batch`, `streaming-result`, `fetchsize`, `cursor-fetch`, `connector-j`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0103_060d7c0a7f`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#jdbc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b007a93adb5770d00280f92a7d9ab230a44098026e8129cfc62ebf8796c0fd2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#jdbc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for JDBC API patterns in TiDB-focused Java applications for Prepared Statements, batch execution, and streaming large result sets.
- Retrieval Keywords: Prepared Statements, useServerPrepStmts=true, addBatch, executeBatch, rewriteBatchedStatements=true, StreamingResult, FetchSize Integer.MIN_VALUE, useCursorFetch=true, clobberStreamingResults=true, No statements may be issued when any streaming result sets are open and in use on a given connection
- Follow-up Guidance: It also states that TiDB supports both streaming methods and prefers setting FetchSize to Integer.MIN_VALUE because it is simpler and has better execution efficiency.
- Classification Note: This is classified as performance because it describes JDBC usage choices and parameters that affect SQL parsing overhead, network transfer behavior, and large result handling efficiency.

## Official Source Content

## JDBC

Java applications can be encapsulated with various frameworks. In most of the frameworks, JDBC API is called on the bottommost level to interact with the database server. For JDBC, it is recommended that you focus on the following things:

- JDBC API usage choice
- API Implementer's parameter configuration
### JDBC API

For JDBC API usage, see [JDBC official tutorial](https://docs.oracle.com/javase/tutorial/jdbc/). This section covers the usage of several important APIs.
#### Use Prepare API

For OLTP (Online Transactional Processing) scenarios, the SQL statements sent by the program to the database are several types that can be exhausted after removing parameter changes. Therefore, it is recommended to use [Prepared Statements](https://docs.oracle.com/javase/tutorial/jdbc/basics/prepared.html) instead of regular [execution from a text file](https://docs.oracle.com/javase/tutorial/jdbc/basics/processingsqlstatements.html#executing_queries) and reuse Prepared Statements to execute directly. This avoids the overhead of repeatedly parsing and generating SQL execution plans in TiDB.

At present, most upper-level frameworks call the Prepare API for SQL execution. If you use the JDBC API directly for development, pay attention to choosing the Prepare API.

In addition, with the default implementation of MySQL Connector/J, only client-side statements are preprocessed, and the statements are sent to the server in a text file after `?` is replaced on the client. Therefore, in addition to using the Prepare API, you also need to configure `useServerPrepStmts = true` in JDBC connection parameters before you perform statement preprocessing on the TiDB server. For detailed parameter configuration, see [MySQL JDBC parameters](#mysql-jdbc-parameters).
#### Use Batch API

For batch inserts, you can use the [`addBatch`/`executeBatch` API](https://www.tutorialspoint.com/jdbc/jdbc-batch-processing). The `addBatch()` method is used to cache multiple SQL statements first on the client, and then send them to the database server together when calling the `executeBatch` method.

> **Note:**
>
> In the default MySQL Connector/J implementation, the sending time of the SQL statements that are added to batch with `addBatch()` is delayed to the time when `executeBatch()` is called, but the statements will still be sent one by one during the actual network transfer. Therefore, this method usually does not reduce the amount of communication overhead.
>
> If you want to batch network transfer, you need to configure `rewriteBatchedStatements = true` in the JDBC connection parameters. For the detailed parameter configuration, see [Batch-related parameters](#batch-related-parameters).
#### Use `StreamingResult` to get the execution result

In most scenarios, to improve execution efficiency, JDBC obtains query results in advance and save them in client memory by default. But when the query returns a super large result set, the client often wants the database server to reduce the number of records returned at a time, and waits until the client's memory is ready and it requests for the next batch.

Usually, there are two kinds of processing methods in JDBC:

- [Set `FetchSize` to `Integer.MIN_VALUE`](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-implementation-notes.html#ResultSet) to ensure that the client does not cache. The client will read the execution result from the network connection through `StreamingResult`.

    When the client uses the streaming read method, it needs to finish reading or close `resultset` before continuing to use the statement to make a query. Otherwise, the error `No statements may be issued when any streaming result sets are open and in use on a given connection. Ensure that you have called .close() on any active streaming result sets before attempting more queries.` is returned.

    To avoid such an error in queries before the client finishes reading or closes `resultset`, you can add the `clobberStreamingResults=true` parameter in the URL. Then, `resultset` is automatically closed but the result set to be read in the previous streaming query is lost.

- To use Cursor Fetch, first [set `FetchSize`](http://makejavafaster.blogspot.com/2015/06/jdbc-fetch-size-performance.html) as a positive integer and configure `useCursorFetch=true` in the JDBC URL.

TiDB supports both methods, but it is preferred that you use the first method, because it is a simpler implementation and has a better execution efficiency.
