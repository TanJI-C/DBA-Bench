# KILL statement syntax, examples, compatibility, and behavior changes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-kill.md`
- Source Title: `KILL`
- Source Heading Path: `KILL | KILL > Synopsis | KILL > Examples | KILL > MySQL compatibility | KILL > Behavior change descriptions | KILL > See also`
- Source Line Ranges: `5-90`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `kill`, `connection-termination`, `query-termination`, `ddl-jobs`, `global-kill`, `connection-id`, `mysql-compatibility`, `processlist`, `proxy-routing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0605_542200b37e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-kill.md#kill`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3f9f159ba8334a1723450da1a630d51eec9400809fee36bcdfae4d4cc4c37d2c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill#kill
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-kill.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB `KILL` statement syntax, examples for terminating a connection or query from `INFORMATION_SCHEMA.CLUSTER_PROCESSLIST`, MySQL compatibility differences, Global Kill behavior, `KILL TIDB`, or `Control+C` behavior changes.
- Retrieval Keywords: KILL, KillStmt ::= 'KILL' 'TIDB'? ( 'CONNECTION' | 'QUERY' )? CONNECTION_ID, KILL TIDB, CONNECTION_ID, INFORMATION_SCHEMA.CLUSTER_PROCESSLIST, SELECT ID, USER, INSTANCE, INFO FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST, Global Kill, enable-global-kill, enable-32bits-connection-id, compatible-kill-query, Control+C, 32-bit connection IDs, 64-bit connection IDs, terminate ongoing DDL jobs, proxy between the client and the TiDB cluster, MySQL compatibility, SHOW PROCESSLIST, CLUSTER_PROCESSLIST
- Follow-up Guidance: See also `SHOW [FULL] PROCESSLIST` and `CLUSTER_PROCESSLIST` for finding active queries and connection IDs.
- Classification Note: This is reference content because it defines the `KILL` statement syntax, shows exact SQL examples, and documents compatibility and behavior conditions such as Global Kill, `KILL TIDB`, and connection ID changes.

## Official Source Content

# KILL

The `KILL` statement is used to terminate a connection in any TiDB instance in the current TiDB cluster. Starting from TiDB v6.2.0, you can also use the `KILL` statement to terminate ongoing DDL jobs. 
## Synopsis

```ebnf+diagram
KillStmt ::= 'KILL' 'TIDB'? ( 'CONNECTION' | 'QUERY' )? CONNECTION_ID
```
## Examples

The following example shows how to get all active queries in the current cluster and terminate any one of them.

```sql
SELECT ID, USER, INSTANCE, INFO FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST;
```

```
+---------------------+------+-----------------+-----------------------------------------------------------------------------+
| ID                  | USER | INSTANCE        | INFO                                                                        |
+---------------------+------+-----------------+-----------------------------------------------------------------------------+
| 8306449708033769879 | root | 127.0.0.1:10082 | select sleep(30), 'foo'                                                     |
| 5857102839209263511 | root | 127.0.0.1:10080 | select sleep(50)                                                            |
| 5857102839209263513 | root | 127.0.0.1:10080 | SELECT ID, USER, INSTANCE, INFO FROM INFORMATION_SCHEMA.CLUSTER_PROCESSLIST |
+---------------------+------+-----------------+-----------------------------------------------------------------------------+
```

```sql
KILL 5857102839209263511;
```

```
Query OK, 0 rows affected (0.00 sec)
```
## MySQL compatibility

- The `KILL` statement of MySQL can only terminate a connection in the currently connected MySQL instance, while the `KILL` statement of TiDB can terminate a connection in any TiDB instance in the entire cluster.
- In v7.2.0 and earlier versions, using the MySQL command line <kbd>Control+C</kbd> to terminate a query or connection in TiDB is not supported.
## Behavior change descriptions

Starting from v7.3.0, TiDB supports generating 32-bit connection IDs, which is enabled by default and controlled by the [`enable-32bits-connection-id`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-32bits-connection-id-new-in-v730) configuration item. When both the Global Kill feature and 32-bit connection ID are enabled, TiDB generates a 32-bit connection ID and you can terminate queries or connections in the MySQL command-line using <kbd>Control+C</kbd>.

> **Warning:**
>
> When the number of TiDB instances in the cluster exceeds 2048 or the concurrent connection count of a single TiDB instance exceeds 1048576, the 32-bit connection ID space becomes insufficient and is automatically upgraded to 64-bit connection IDs. During the upgrade process, existing business and established connections are unaffected. However, subsequent new connections cannot be terminated using <kbd>Control+C</kbd> in the MySQL command-line.

Starting from v6.1.0, TiDB supports the Global Kill feature, which is enabled by default and controlled by the [`enable-global-kill`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610) configuration.

Starting from v7.3.0, TiDB supports generating 32-bit connection IDs, which is enabled by default. When both the Global Kill feature and 32-bit connection ID are enabled, You can terminate queries or connections in the MySQL command-line using <kbd>Control+C</kbd>.

Starting from v6.1.0, TiDB supports the Global Kill feature, which is enabled by default.

When the Global Kill feature is enabled, both `KILL` and `KILL TIDB` statements can terminate queries or connections across instances so you do not need to worry about erroneously terminating queries or connections. When you use a client to connect to any TiDB instance and execute the `KILL` or `KILL TIDB` statement, the statement will be forwarded to the target TiDB instance. If there is a proxy between the client and the TiDB cluster, the `KILL` and `KILL TIDB` statements will also be forwarded to the target TiDB instance for execution.

If the Global Kill feature is not enabled or you are using a TiDB version earlier than v6.1.0, note the following:

- By default, `KILL` is not compatible with MySQL. This helps prevent against a case of a connection being terminated by a wrong TiDB server, because it is common to place multiple TiDB servers behind a load balancer. To terminate other connections on the currently connected TiDB instance, you need to add the `TIDB` suffix explicitly by executing the `KILL TIDB` statement.

- It is **STRONGLY NOT RECOMMENDED** to set [`compatible-kill-query = true`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#compatible-kill-query) in your configuration file UNLESS you are certain that clients will be always connected to the same TiDB instance. This is because pressing <kbd>Control+C</kbd> in the default MySQL client opens a new connection in which `KILL` is executed. If there is a proxy between the client and the TiDB cluster, the new connection might be routed to a different TiDB instance, which possibly kills a different session by mistake.

- The `KILL TIDB` statement is a TiDB extension. The feature of this statement is similar to the MySQL `KILL [CONNECTION|QUERY]` command and the MySQL command line <kbd>Control+C</kbd>. It is safe to use `KILL TIDB` on the same TiDB instance.
## See also

* [SHOW \[FULL\] PROCESSLIST](/sql-statements/sql-statement-show-processlist.md)
* [CLUSTER_PROCESSLIST](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-processlist#cluster_processlist)
