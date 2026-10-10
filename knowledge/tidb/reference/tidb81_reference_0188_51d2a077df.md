# MySQL Connector/J compatibility issues and bugs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-third-party-tools-compatibility.md`
- Source Title: `Known Incompatibility Issues with Third-Party Tools`
- Source Heading Path: `Known Incompatibility Issues with Third-Party Tools > Compatibility with MySQL JDBC | Known Incompatibility Issues with Third-Party Tools > Compatibility with MySQL JDBC > The default collation is inconsistent | Known Incompatibility Issues with Third-Party Tools > Compatibility with MySQL JDBC > The `NO_BACKSLASH_ESCAPES` parameter does not take effect | Known Incompatibility Issues with Third-Party Tools > Compatibility with MySQL JDBC > The `INDEX_USED` related parameters are not supported | Known Incompatibility Issues with Third-Party Tools > Compatibility with MySQL JDBC > The `enablePacketDebug` parameter is not supported | Known Incompatibility Issues with Third-Party Tools > Compatibility with MySQL JDBC > The UpdatableResultSet is not supported | Known Incompatibility Issues with Third-Party Tools > MySQL JDBC bugs | Known Incompatibility Issues with Third-Party Tools > MySQL JDBC bugs > `useLocalTransactionState` and `rewriteBatchedStatements` are true at the same time will cause the transaction to fail to commit or roll back | Known Incompatibility Issues with Third-Party Tools > MySQL JDBC bugs > Connector is incompatible with the server version earlier than 5.7.5`
- Source Line Ranges: `85-180`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `jdbc`, `connector-j`, `collation`, `escaping`, `protocol`, `debugging`, `resultset`, `transactions`, `version-compatibility`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0188_51d2a077df`
- Source ID: `tidb-docs-8.1:develop/dev-guide-third-party-tools-compatibility.md#compatibility-with-mysql-jdbc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `281674a393961e5f9b7ab33eff9100d463c02c632413f23b031ec347625d04b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility#compatibility-with-mysql-jdbc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-third-party-tools-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when investigating MySQL Connector/J compatibility issues with TiDB, including collation defaults, NO_BACKSLASH_ESCAPES behavior, unsupported protocol index flags, enablePacketDebug, UpdatableResultSet, or documented Connector/J bugs tied to specific versions.
- Retrieval Keywords: MySQL Connector/J 8.0.29, default collation, ascii_general_ci, ascii_bin, latin1_swedish_ci, latin1_bin, utf8mb4_0900_ai_ci, utf8mb4_bin, NO_BACKSLASH_ESCAPES, \\, SERVER_QUERY_NO_GOOD_INDEX_USED, SERVER_QUERY_NO_INDEX_USED, com.mysql.cj.protocol.ServerSession.noIndexUsed(), com.mysql.cj.protocol.ServerSession.noGoodIndexUsed(), enablePacketDebug, UpdatableResultSet, ResultSet.CONCUR_UPDATABLE, useLocalTransactionState, rewriteBatchedStatements, useConfigs=maxPerformance, useLocalTransactionState=false, MySQL Connector/J 8.0.33, MySQL Connector/J 8.0.32, server version earlier than 5.7.5, pingcap/mysql-connector-j, TiDB v6.3.0
- Follow-up Guidance: The content includes version-specific follow-up for Connector/J bugs, including fixes in MySQL Connector/J 8.0.32 or 8.0.33, pingcap/mysql-connector-j, and a server-side fix since TiDB v6.3.0 for the earlier protocol compatibility issue.
- Classification Note: This is reference content because it catalogs exact Connector/J parameters, APIs, bug conditions, and versioned compatibility notes rather than describing a general workflow.

## Official Source Content

## Compatibility with MySQL JDBC

The test version is MySQL Connector/J 8.0.29.
### The default collation is inconsistent

**Description**

The collations of MySQL Connector/J are stored on the client side and distinguished by the server version.

The following table lists known client-side and server-side collation inconsistencies in character sets:

| Character | Client-side default collation | Server-side default collation |
| --------- | -------------------- | ------------- |
| `ascii`   | `ascii_general_ci`   | `ascii_bin`   |
| `latin1`  | `latin1_swedish_ci`  | `latin1_bin`  |
| `utf8mb4` | `utf8mb4_0900_ai_ci` | `utf8mb4_bin` |

**Way to avoid**

Set the collation manually, and do not rely on the client-side default collation. The client-side default collation is stored by the MySQL Connector/J configuration file.
### The `NO_BACKSLASH_ESCAPES` parameter does not take effect

**Description**

In TiDB, you cannot use the `NO_BACKSLASH_ESCAPES` parameter without escaping the `\` character. For more details, track this [issue](https://github.com/pingcap/tidb/issues/35302).

**Way to avoid**

Do not use `NO_BACKSLASH_ESCAPES` with `\` in TiDB, but use `\\` in SQL statements.
### The `INDEX_USED` related parameters are not supported

**Description**

TiDB does not set the `SERVER_QUERY_NO_GOOD_INDEX_USED` and `SERVER_QUERY_NO_INDEX_USED` parameters in the protocol. This will cause the following parameters to be returned inconsistently with the actual situation:

- `com.mysql.cj.protocol.ServerSession.noIndexUsed()`
- `com.mysql.cj.protocol.ServerSession.noGoodIndexUsed()`

**Way to avoid**

Do not use the `noIndexUsed()` and `noGoodIndexUsed()` functions in TiDB.
### The `enablePacketDebug` parameter is not supported

**Description**

TiDB does not support the [enablePacketDebug](https://dev.mysql.com/doc/connector-j/en/connector-j-connp-props-debugging-profiling.html) parameter. It is a MySQL Connector/J parameter used for debugging that will keep the buffer of the data packet. This might cause the connection to close unexpectedly. **DO NOT** turn it on.

**Way to avoid**

Do not set the `enablePacketDebug` parameter in TiDB.
### The UpdatableResultSet is not supported

**Description**

TiDB does not support `UpdatableResultSet`. **DO NOT** specify the `ResultSet.CONCUR_UPDATABLE` parameter and **DO NOT** update data inside the `ResultSet`.

**Way to avoid**

To ensure data consistency by transaction, you can use `UPDATE` statements to update data.
## MySQL JDBC bugs
### `useLocalTransactionState` and `rewriteBatchedStatements` are true at the same time will cause the transaction to fail to commit or roll back

**Description**

When using MySQL Connector/J 8.0.32 or an earlier version, if the `useLocalTransactionState` and `rewriteBatchedStatements` parameters are set to `true` at the same time, the transaction might fail to commit. You can reproduce with [this code](https://github.com/Icemap/tidb-java-gitpod/tree/reproduction-local-transaction-state-txn-error).

**Way to avoid**

> **Note:**
>
> `useConfigs=maxPerformance` includes a group of configurations. For detailed configurations in MySQL Connector/J 8.0 and MySQL Connector/J 5.1, see [mysql-connector-j 8.0](https://github.com/mysql/mysql-connector-j/blob/release/8.0/src/main/resources/com/mysql/cj/configurations/maxPerformance.properties) and [mysql-connector-j 5.1](https://github.com/mysql/mysql-connector-j/blob/release/5.1/src/com/mysql/jdbc/configs/maxPerformance.properties) respectively. You need to disable `useLocalTransactionState` when using `maxPerformance`. That is, use `useConfigs=maxPerformance&useLocalTransactionState=false`.

This bug has been fixed in MySQL Connector/J 8.0.33. Considering updates for the 8.0.x series have ceased, it is strongly recommended to upgrade your MySQL Connector/J to [the latest General Availability (GA) version](https://dev.mysql.com/downloads/connector/j/) for improved stability and performance.
### Connector is incompatible with the server version earlier than 5.7.5

**Description**

The database connection might hang under certain conditions when using MySQL Connector/J 8.0.31 or an earlier version with a MySQL server < 5.7.5 or a database using the MySQL server < 5.7.5 protocol (such as TiDB earlier than v6.3.0). For more details, see the [Bug Report](https://bugs.mysql.com/bug.php?id=106252).

**Way to avoid**

This bug has been fixed in MySQL Connector/J 8.0.32. Considering updates for the 8.0.x series have ceased, it is strongly recommended to upgrade your MySQL Connector/J to [the latest General Availability (GA) version](https://dev.mysql.com/downloads/connector/j/) for improved stability and performance.

TiDB also fixes it in the following ways:

- Client side: This bug has been fixed in **pingcap/mysql-connector-j** and you can use the [pingcap/mysql-connector-j](https://github.com/pingcap/mysql-connector-j) instead of the official MySQL Connector/J.
- Server side: This compatibility issue has been fixed since TiDB v6.3.0 and you can upgrade the server to v6.3.0 or later versions.
