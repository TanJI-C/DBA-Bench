# MySQL Connector/J prepare-related parameter tuning

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Prepare-related parameters | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Prepare-related parameters > `useServerPrepStmts` | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Prepare-related parameters > `cachePrepStmts` | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Prepare-related parameters > `prepStmtCacheSqlLimit` | Best Practices for Developing Java Applications with TiDB > JDBC > MySQL JDBC parameters > Prepare-related parameters > `prepStmtCacheSize``
- Source Line Ranges: `76-123`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `dashboard`
- Topic Tags: `jdbc-url`, `connector-j`, `prepare`, `prepared-statement-cache`, `server-prepare`, `query-summary`, `cps`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0064_8468f83661`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#mysql-jdbc-parameters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c88fe31fb419419e594d8d4f5bad5af3830edf9edf6cc6119ec8060eb930c667`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#mysql-jdbc-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when tuning MySQL Connector/J Prepared Statement behavior for TiDB and verifying it through Query Summary command types.
- Retrieval Keywords: useServerPrepStmts, cachePrepStmts, prepStmtCacheSqlLimit, prepStmtCacheSize, useConfigs=maxPerformance, Query Summary, CPS By Instance, COM_QUERY, COM_STMT_EXECUTE, COM_STMT_PREPARE, COM_STMT_CLOSE
- Follow-up Guidance: The chunk explains how to verify each setting in TiDB monitoring dashboard by comparing COM_QUERY, COM_STMT_EXECUTE, COM_STMT_PREPARE, and COM_STMT_CLOSE in Query Summary > CPS By Instance.
- Classification Note: This is classified as configuration because it focuses on JDBC URL parameter settings in MySQL Connector/J and their observable effects.

## Official Source Content

### MySQL JDBC parameters

JDBC usually provides implementation-related configurations in the form of JDBC URL parameters. This section introduces [MySQL Connector/J's parameter configurations](https://dev.mysql.com/doc/connector-j/en/connector-j-reference-configuration-properties.html) (If you use MariaDB, see [MariaDB's parameter configurations](https://mariadb.com/docs/connectors/mariadb-connector-j/about-mariadb-connector-j#optional-url-parameters)). Because this document cannot cover all configuration items, it mainly focuses on several parameters that might affect performance.
#### Prepare-related parameters

This section introduces parameters related to `Prepare`.
##### `useServerPrepStmts`

`useServerPrepStmts` is set to `false` by default, that is, even if you use the Prepare API, the "prepare" operation will be done only on the client. To avoid the parsing overhead of the server, if the same SQL statement uses the Prepare API multiple times, it is recommended to set this configuration to `true`.

To verify that this setting already takes effect, you can do:

- Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
- If `COM_QUERY` is replaced by `COM_STMT_EXECUTE` or `COM_STMT_PREPARE` in the request, it means this setting already takes effect.
##### `cachePrepStmts`

Although `useServerPrepStmts=true` allows the server to execute Prepared Statements, by default, the client closes the Prepared Statements after each execution and does not reuse them. This means that the "prepare" operation is not even as efficient as text file execution. To solve this, it is recommended that after setting `useServerPrepStmts=true`, you should also configure `cachePrepStmts=true`. This allows the client to cache Prepared Statements.

To verify that this setting already takes effect, you can do:

- Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
- If the number of `COM_STMT_EXECUTE` in the request is far more than the number of `COM_STMT_PREPARE`, it means this setting already takes effect.

In addition, configuring `useConfigs=maxPerformance` will configure multiple parameters at the same time, including `cachePrepStmts=true`.
##### `prepStmtCacheSqlLimit`

After configuring `cachePrepStmts`, also pay attention to the `prepStmtCacheSqlLimit` configuration (the default value is `256`). This configuration controls the maximum length of the Prepared Statements cached on the client.

The Prepared Statements that exceed this maximum length will not be cached, so they cannot be reused. In this case, you may consider increasing the value of this configuration depending on the actual SQL length of the application.

You need to check whether this setting is too small if you:

- Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
- And find that `cachePrepStmts=true` has been configured, but `COM_STMT_PREPARE` is still mostly equal to `COM_STMT_EXECUTE` and `COM_STMT_CLOSE` exists.
##### `prepStmtCacheSize`

`prepStmtCacheSize` controls the number of cached Prepared Statements (the default value is `25`). If your application requires "preparing" many types of SQL statements and wants to reuse Prepared Statements, you can increase this value.

To verify that this setting already takes effect, you can do:

- Go to TiDB monitoring dashboard and view the request command type through **Query Summary** > **CPS By Instance**.
- If the number of `COM_STMT_EXECUTE` in the request is far more than the number of `COM_STMT_PREPARE`, it means this setting already takes effect.
