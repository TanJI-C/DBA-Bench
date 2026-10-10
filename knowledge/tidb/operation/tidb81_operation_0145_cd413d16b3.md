# TiDB server management FAQs for DDL, metadata, connections, and table sizing

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > TiDB server management | TiDB Cluster Management FAQs > TiDB server management > How to set the `lease` parameter in TiDB? | TiDB Cluster Management FAQs > TiDB server management > What is the processing time of a DDL operation? | TiDB Cluster Management FAQs > TiDB server management > Why it is very slow to run DDL statements sometimes? | TiDB Cluster Management FAQs > TiDB server management > Can I use S3 as the backend storage engine in TiDB? | TiDB Cluster Management FAQs > TiDB server management > Can the `Information_schema` support more real information? | TiDB Cluster Management FAQs > TiDB server management > What's the explanation of the TiDB Backoff type scenario? | TiDB Cluster Management FAQs > TiDB server management > What is the main reason of TiDB TiClient type? | TiDB Cluster Management FAQs > TiDB server management > What's the maximum number of concurrent connections that TiDB supports? | TiDB Cluster Management FAQs > TiDB server management > How to view the creation time of a table? | TiDB Cluster Management FAQs > TiDB server management > What is the meaning of `EXPENSIVE_QUERY` in the TiDB log? | TiDB Cluster Management FAQs > TiDB server management > How do I estimate the size of a table in TiDB?`
- Source Line Ranges: `188-298`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `shared`
- Topic Tags: `ddl`, `lease`, `schema-changes`, `backoff`, `ticlient`, `connections`, `information-schema`, `expensive-query`, `table-size`, `metrics-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0145_cd413d16b3`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#tidb-server-management`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `142b23f1f69639c2c9a4bc9ebeafa936541a203597025c1ac7a175f7b1e54253`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#tidb-server-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiDB server management topics such as the lease parameter, DDL timing and slowness, INFORMATION_SCHEMA details, TiDB Backoff or TiClient errors, connection limits, EXPENSIVE_QUERY, table creation time, or estimating table size with SQL.
- Retrieval Keywords: --lease=60, lease parameter, DDL owner, Add Index, DDL statements are executed serially, 2 * lease, kill -9, S3 as the backend storage engine, INFORMATION_SCHEMA, TiDB Backoff, Server is busy, backoff.maxsleep 20000ms, TiClient Region Error, not_leader, stale_epoch, instance.max_connections, config.toml, max_connections, create_time, EXPENSIVE_QUERY, 10,000 rows, information_schema.TIKV_REGION_STATUS, METRICS_SCHEMA.store_size_amplification, Size amplification, Grafana Monitoring PD - statistics balance
- Follow-up Guidance: The content includes the exact SQL for estimating table size and says to replace @dbname and @table_name as appropriate, while also pointing to METRICS_SCHEMA.store_size_amplification and the Grafana Size amplification metric.
- Classification Note: This is classified as TiDB operation content because it covers TiDB server startup parameters, DDL behavior, TiDB log and client error meanings, connection configuration, metadata queries, and table size estimation.

## Official Source Content

## TiDB server management

This section describes common problems you may encounter during TiDB server management, their causes, and solutions.
### How to set the `lease` parameter in TiDB?

The lease parameter (`--lease=60`) is set from the command line when starting a TiDB server. The value of the lease parameter impacts the Database Schema Changes (DDL) speed of the current session. In the testing environments, you can set the value to 1s for to speed up the testing cycle. But in the production environments, it is recommended to set the value to minutes (for example, 60) to ensure the DDL safety.
### What is the processing time of a DDL operation?

The processing time is different for different scenarios. Generally, you can consider the following three scenarios:

1. The `Add Index` operation with a relatively small number of rows in the corresponding data table: about 3s
2. The `Add Index` operation with a relatively large number of rows in the corresponding data table: the processing time depends on the specific number of rows and the QPS at that time (the `Add Index` operation has a lower priority than ordinary SQL operations)
3. Other DDL operations: about 1s

If the TiDB server instance that receives the DDL request is the same TiDB server instance that the DDL owner is in, the first and third scenarios above may cost only dozens to hundreds of milliseconds.
### Why it is very slow to run DDL statements sometimes?

Possible reasons:

- If you run multiple DDL statements together, the last few DDL statements might run slowly. This is because the DDL statements are executed serially in the TiDB cluster.
- After you start the cluster successfully, the first DDL operation may take a longer time to run, usually around 30s. This is because the TiDB cluster is electing the leader that processes DDL statements.
- The processing time of DDL statements in the first ten minutes after starting TiDB would be much longer than the normal case if you meet the following conditions: 1) TiDB cannot communicate with PD as usual when you are stopping TiDB (including the case of power failure); 2) TiDB fails to clean up the registration data from PD in time because TiDB is stopped by the `kill -9` command. If you run DDL statements during this period, for the state change of each DDL, you need to wait for 2 * lease (lease = 45s).
- If a communication issue occurs between a TiDB server and a PD server in the cluster, the TiDB server cannot get or update the version information from the PD server in time. In this case, you need to wait for 2 * lease for the state processing of each DDL.
### Can I use S3 as the backend storage engine in TiDB?

No. Currently, TiDB only supports the distributed storage engine and the Goleveldb/RocksDB/BoltDB engine.
### Can the `Information_schema` support more real information?

As part of MySQL compatibility, TiDB supports a number of `INFORMATION_SCHEMA` tables. Many of these tables also have a corresponding SHOW command. For more information, see [Information Schema](https://docs.pingcap.com/tidb/stable/information-schema/information-schema).
### What's the explanation of the TiDB Backoff type scenario?

In the communication process between the TiDB server and the TiKV server, the `Server is busy` or `backoff.maxsleep 20000ms` log message is displayed when processing a large volume of data. This is because the system is busy while the TiKV server processes data. At this time, usually you can view that the TiKV host resources usage rate is high. If this occurs, you can increase the server capacity according to the resources usage.
### What is the main reason of TiDB TiClient type?

The TiClient Region Error indicator describes the error types and metrics that appear when the TiDB server as a client accesses the TiKV server through the KV interface to perform data operations. The error types include `not_leader` and `stale_epoch`. These errors occur when the TiDB server manipulates the Region leader data according to its own cache information, the Region leader has migrated, or the current TiKV Region information and the routing information of the TiDB cache are inconsistent. Generally, in this case, the TiDB server will automatically retrieve the latest routing data from PD and redo the previous operation.
### What's the maximum number of concurrent connections that TiDB supports?

By default, there is no limit on the maximum number of connections per TiDB server. If needed, you can limit the maximum number of connections by setting `instance.max_connections` in the `config.toml` file, or changing the value of the system variable [`max_connections`](https://docs.pingcap.com/tidb/stable/system-variables#max_connections). If too large concurrency leads to an increase of response time, it is recommended to increase the capacity by adding TiDB nodes.
### How to view the creation time of a table?

The `create_time` of tables in the `information_schema` is the creation time.
### What is the meaning of `EXPENSIVE_QUERY` in the TiDB log?

When TiDB is executing a SQL statement, the query will be `EXPENSIVE_QUERY` if each operator is estimated to process over 10,000 rows. You can modify the `tidb-server` configuration parameter to adjust the threshold and then restart the `tidb-server`.
### How do I estimate the size of a table in TiDB?

To estimate the size of a table in TiDB, you can use the following query statement.

```sql
SELECT
  db_name,
  table_name,
  ROUND(SUM(total_size / cnt), 2) Approximate_Size,
  ROUND(
    SUM(
      total_size / cnt / (
        SELECT
          ROUND(AVG(value), 2)
        FROM
          METRICS_SCHEMA.store_size_amplification
        WHERE
          value > 0
      )
    ),
    2
  ) Disk_Size
FROM
  (
    SELECT
      db_name,
      table_name,
      region_id,
      SUM(Approximate_Size) total_size,
      COUNT(*) cnt
    FROM
      information_schema.TIKV_REGION_STATUS
    WHERE
      db_name = @dbname
      AND table_name IN (@table_name)
    GROUP BY
      db_name,
      table_name,
      region_id
  ) tabinfo
GROUP BY
  db_name,
  table_name;
```

When using the above statement, you need to fill in and replace the following fields in the statement as appropriate.

- `@dbname`: the name of the database.
- `@table_name`: the name of the target table.

In addition, in the above statement:

- `store_size_amplification` indicates the average of the cluster compression ratio. In addition to using `SELECT * FROM METRICS_SCHEMA.store_size_amplification;` to query this information, you can also check the **Size amplification** metric for each node on the **Grafana Monitoring PD - statistics balance** panel. The average of the cluster compression ratio is the average of the Size amplification for all nodes.
- `Approximate_Size` indicates the size of the table in a replica before compression. Note that this is an approximate value, not an accurate one.
- `Disk_Size` indicates the size of the table after compression. This is an approximate value and can be calculated according to `Approximate_Size` and `store_size_amplification`.
