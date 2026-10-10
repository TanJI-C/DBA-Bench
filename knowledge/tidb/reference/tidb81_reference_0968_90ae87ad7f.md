# TiSpark features, security, statistics, and FAQ

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tispark-overview.md`
- Source Title: `TiSpark User Guide`
- Source Heading Path: `TiSpark User Guide > Features | TiSpark User Guide > Features > Support for expression index | TiSpark User Guide > Features > Work with TiFlash | TiSpark User Guide > Features > Support for partitioned tables | TiSpark User Guide > Features > Security | TiSpark User Guide > Features > Other features | TiSpark User Guide > Statistics information | TiSpark User Guide > FAQ`
- Source Line Ranges: `380-484`
- Source Scope: `shared`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `tiflash`, `shared`
- Topic Tags: `feature-matrix`, `expression-index`, `tiflash`, `partitioned-tables`, `partition-pruning`, `security`, `authentication`, `authorization`, `statistics`, `analyze`, `faq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0968_90ae87ad7f`
- Source ID: `tidb-docs-8.1:tispark-overview.md#features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0488426af8c4cb917119e17072b11a5cec258b6bcea035df0b3aa9ec63b6cbe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tispark-overview#features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tispark-overview.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiSpark feature support, limits for expression index or partitioned tables, TiFlash reading, security settings, statistics usage, or the TiSpark FAQ.
- Retrieval Keywords: TiSpark features, feature support matrix, SQL select with tidb_catalog, DataFrame append, DataFrame reads, SQL show databases, SQL show tables, SQL auth, SQL delete, SQL insert, TLS, DataFrame auth, expression index, TiSpark planner will not use expression index, spark.tispark.isolation_read_engines, TiFlash, partitioned tables, partition pruning, range partitioning, hash partitioned tables, YEAR($argument), select col_name from table_name partition(partition_name), utf8mb4_bin collation, spark.sql.auth.enable, spark.sql.tidb.addr, spark.sql.tidb.port, spark.sql.tidb.user, spark.sql.tidb.password, authentication and authorization through TiDB, Statistics information, analyzed, Introduction to Statistics, small table broadcasting, broadcast join, TiSpark FAQ
- Follow-up Guidance: The source includes links to additional materials for authorization and authentication through TiDB server, push down, delete with TiSpark, stale read, multiple catalogs, TiSpark plan, statistics, and the TiSpark FAQ.
- Classification Note: This chunk is classified as reference because it summarizes supported features, documented limitations, related configuration names, and linked reference topics rather than a single procedure.

## Official Source Content

## Features

The major features of TiSpark are as follows:

| Feature support                 | TiSpark 2.4.x | TiSpark 2.5.x | TiSpark 3.0.x | TiSpark 3.1.x |
|---------------------------------| ------------- | ------------- | ----------- |---------------|
| SQL select without tidb_catalog | ✔           | ✔           |             |               |
| SQL select with tidb_catalog    |               | ✔           | ✔         | ✔             |
| DataFrame append                | ✔           | ✔           | ✔         | ✔             |
| DataFrame reads                 | ✔           | ✔           | ✔         | ✔             |
| SQL show databases              | ✔           | ✔           | ✔         | ✔             |
| SQL show tables                 | ✔           | ✔           | ✔         | ✔             |
| SQL auth                        |               | ✔           | ✔         | ✔             |
| SQL delete                      |               |               | ✔         | ✔             |
| SQL insert                      |               |               |           | ✔              |
| TLS                             |               |               | ✔         | ✔             |
| DataFrame auth                  |               |               |             | ✔             |
### Support for expression index

TiDB v5.0 supports [expression index](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index).

TiSpark currently supports retrieving data from tables with `expression index`, but the `expression index` will not be used by the planner of TiSpark.
### Work with TiFlash

TiSpark can read data from TiFlash via the configuration `spark.tispark.isolation_read_engines`.
### Support for partitioned tables

**Read partitioned tables from TiDB**

TiSpark can read the range and hash partitioned tables from TiDB.

Currently, TiSpark does not support a MySQL/TiDB partition table syntax `select col_name from table_name partition(partition_name)`. However, you can still use the `where` condition to filter the partitions.

TiSpark decides whether to apply partition pruning according to the partition type and the partition expression associated with the table.

TiSpark applies partition pruning on range partitioning only when the partition expression is one of the following:

+ column expression
+ `YEAR($argument)` where the argument is a column and its type is datetime or string literal that can be parsed as datetime.

If partition pruning is not applicable, TiSpark's reading is equivalent to doing a table scan over all partitions.

**Write into partitioned tables**

Currently, TiSpark only supports writing data into the range and hash partitioned tables under the following conditions:

+ The partition expression is a column expression.
+ The partition expression is `YEAR($argument)` where the argument is a column and its type is datetime or string literal that can be parsed as datetime.

There are two ways to write into partitioned tables:

- Use datasource API to write into partition table which supports replace and append semantics.
- Use delete statement with Spark SQL.

> **Note:**
>
> Currently, TiSpark only supports writing into partitioned tables with utf8mb4_bin collation enabled.
### Security

If you are using TiSpark v2.5.0 or a later version, you can authenticate and authorize TiSpark users by using TiDB.

The authentication and authorization feature is disabled by default. To enable it, add the following configurations to the Spark configuration file `spark-defaults.conf`.

```
// Enable authentication and authorization
spark.sql.auth.enable true

// Configure TiDB information
spark.sql.tidb.addr $your_tidb_server_address
spark.sql.tidb.port $your_tidb_server_port
spark.sql.tidb.user $your_tidb_server_user
spark.sql.tidb.password $your_tidb_server_password
```

For more information, see [Authorization and authentication through TiDB server](https://github.com/pingcap/tispark/blob/master/docs/features/authorization_userguide.md).
### Other features

- [Push down](https://github.com/pingcap/tispark/blob/master/docs/features/push_down.md)
- [Delete with TiSpark](https://github.com/pingcap/tispark/blob/master/docs/features/delete_userguide.md)
- [Stale read](https://github.com/pingcap/tispark/blob/master/docs/features/stale_read.md)
- [TiSpark with multiple catalogs](https://github.com/pingcap/tispark/wiki/TiSpark-with-multiple-catalogs)
- [TiSpark TLS](#tls-configurations)
- [TiSpark plan](https://github.com/pingcap/tispark/blob/master/docs/features/query_execution_plan_in_TiSpark.md)
## Statistics information

TiSpark uses the statistic information for:

+ Determining which index to use in your query plan with the minimum estimated cost.
+ Small table broadcasting, which enables efficient broadcast join.

To allow TiSpark to access statistic information, make sure that relevant tables have been analyzed.

See [Introduction to Statistics](https://docs.pingcap.com/tidb/stable/statistics) for more details about how to analyze tables.

Since TiSpark 2.0, statistics information is automatically loaded by default.
## FAQ

See [TiSpark FAQ](https://github.com/pingcap/tispark/wiki/TiSpark-FAQ).
