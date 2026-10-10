# JDBC API choices for prepared and batch execution

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-connection-parameters.md`
- Source Title: `Connection Pools and Connection Parameters`
- Source Heading Path: `Connection Pools and Connection Parameters > Connection parameters | Connection Pools and Connection Parameters > Connection parameters > JDBC API | Connection Pools and Connection Parameters > Connection parameters > JDBC API > Use Prepare API | Connection Pools and Connection Parameters > Connection parameters > JDBC API > Use Batch API`
- Source Line Ranges: `113-141`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `shared`
- Topic Tags: `jdbc`, `prepared-statements`, `server-side-prepare`, `batch-execution`, `mysql-connector-j`, `connection-parameters`, `oltp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0038_d0fbcbe657`
- Source ID: `tidb-docs-8.1:develop/dev-guide-connection-parameters.md#connection-parameters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `edee941144e4c0e385d97232d4248a7806670f4c3f5ae1418b462218503bfd16`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-connection-parameters#connection-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-connection-parameters.md

## Retrieval Guidance

- Use When: Use this chunk when you need JDBC connection parameter guidance for choosing Prepared Statements or Batch API behavior with MySQL Connector/J against TiDB.
- Retrieval Keywords: Prepared Statements, Prepare API, useServerPrepStmts = true, MySQL Connector/J, client-side statements are preprocessed, server-side prepare, addBatch, executeBatch, rewriteBatchedStatements = true, batch inserts, JDBC API, OLTP, batch network transfer, MySQL JDBC parameters, Batch-related parameters
- Follow-up Guidance: The source explicitly refers readers to the MySQL JDBC parameters and Batch-related parameters sections for detailed parameter configuration.
- Classification Note: This is classified as configuration content because the official text centers on JDBC API choices together with specific JDBC connection parameters that control prepared statement and batch execution behavior.

## Official Source Content

## Connection parameters

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
