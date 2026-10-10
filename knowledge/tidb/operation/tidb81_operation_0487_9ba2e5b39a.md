# TiSpark getting started in spark-shell for read, write, delete, and catalog access

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tispark-overview.md`
- Source Title: `TiSpark User Guide`
- Source Heading Path: `TiSpark User Guide > Getting started | TiSpark User Guide > Getting started > Start spark-shell | TiSpark User Guide > Getting started > Get TiSpark version | TiSpark User Guide > Getting started > Read data using TiSpark | TiSpark User Guide > Getting started > Write data using TiSpark | TiSpark User Guide > Getting started > Write data using JDBC DataSource | TiSpark User Guide > Getting started > Delete data using TiSpark | TiSpark User Guide > Getting started > Work with other data sources`
- Source Line Ranges: `145-264`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `tikv`, `pd`, `sql`
- Topic Tags: `spark-shell`, `configuration`, `pd-addresses`, `catalog`, `version-check`, `read`, `write`, `jdbc`, `delete`, `datasource`, `sql`, `acid`, `multi-catalog`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0487_9ba2e5b39a`
- Source ID: `tidb-docs-8.1:tispark-overview.md#getting-started`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `acf86d908c0e992edd16b44cf5578c8e87d6d5bfc643cd8b1db68770f5c1fdf2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tispark-overview#getting-started
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tispark-overview.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs spark-shell startup settings for TiSpark, example read or write commands, delete syntax, TiSpark version checking, or multi-catalog access examples.
- Retrieval Keywords: Getting started, Start spark-shell, spark-defaults.conf, spark.sql.extensions org.apache.spark.sql.TiExtensions, spark.tispark.pd.addresses, spark.sql.catalog.tidb_catalog, org.apache.spark.sql.catalyst.catalog.TiCatalog, spark-shell --jars tispark-assembly-{version}.jar, select ti_version(), use tidb_catalog, select count(*) from ${database}.${table}, format("tidb"), tidb.addr, tidb.port, tidb.user, tidb.password, ACID is guaranteed, Starting from TiSpark 3.1, Spark JDBC, com.mysql.jdbc.Driver, rewriteBatchedStatements=true, JDBCOptions.JDBC_BATCH_INSERT_SIZE, isolationLevel NONE, ISOLATION LEVEL does not support, REPEATABLE-READ, delete from ${database}.${table} where xxx, spark_catalog.default.t, tidb_catalog.test.t
- Follow-up Guidance: The source links to separate user guides for the Data Source API, insert SQL, and delete feature for more details.
- Classification Note: This is classified as operation because the content provides concrete runtime configuration and command examples for starting spark-shell and performing read, write, delete, and catalog operations.

## Official Source Content

## Getting started

This document describes how to use TiSpark in spark-shell.
### Start spark-shell

To use TiSpark in spark-shell:

Add the following configuration in `spark-defaults.conf`:

```
spark.sql.extensions  org.apache.spark.sql.TiExtensions
spark.tispark.pd.addresses  ${your_pd_address}
spark.sql.catalog.tidb_catalog  org.apache.spark.sql.catalyst.catalog.TiCatalog
spark.sql.catalog.tidb_catalog.pd.addresses  ${your_pd_address}
```

Start spark-shell with the `--jars` option.

```
spark-shell --jars tispark-assembly-{version}.jar
```
### Get TiSpark version

You can get TiSpark version information by running the following command in spark-shell:

```scala
spark.sql("select ti_version()").collect
```
### Read data using TiSpark

You can use Spark SQL to read data from TiKV.

```scala
spark.sql("use tidb_catalog")
spark.sql("select count(*) from ${database}.${table}").show
```
### Write data using TiSpark

You can use the Spark DataSource API to write data to TiKV, for which ACID is guaranteed.

```scala
val tidbOptions: Map[String, String] = Map(
  "tidb.addr" -> "127.0.0.1",
  "tidb.password" -> "",
  "tidb.port" -> "4000",
  "tidb.user" -> "root"
)

val customerDF = spark.sql("select * from customer limit 100000")

customerDF.write
.format("tidb")
.option("database", "tpch_test")
.option("table", "cust_test_select")
.options(tidbOptions)
.mode("append")
.save()
```

See [Data Source API User Guide](https://github.com/pingcap/tispark/blob/master/docs/features/datasource_api_userguide.md) for more details.

Starting from TiSpark 3.1, you can write data to TiKV using Spark SQL. For more information, see [insert SQL](https://github.com/pingcap/tispark/blob/master/docs/features/insert_sql_userguide.md).
### Write data using JDBC DataSource

You can also use Spark JDBC to write to TiDB without the use of TiSpark.

This is beyond the scope of TiSpark. This document only provides an example here. For detailed information, see [JDBC To Other Databases](https://spark.apache.org/docs/latest/sql-data-sources-jdbc.html).

```scala
import org.apache.spark.sql.execution.datasources.jdbc.JDBCOptions

val customer = spark.sql("select * from customer limit 100000")
// you might need to repartition the source to make it balanced across nodes
// and increase concurrency
val df = customer.repartition(32)
df.write
.mode(saveMode = "append")
.format("jdbc")
.option("driver", "com.mysql.jdbc.Driver")
 // replace the host and port with yours and be sure to use rewrite batch
.option("url", "jdbc:mysql://127.0.0.1:4000/test?rewriteBatchedStatements=true")
.option("useSSL", "false")
// as tested, setting to `150` is a good practice
.option(JDBCOptions.JDBC_BATCH_INSERT_SIZE, 150)
.option("dbtable", s"cust_test_select") // database name and table name here
.option("isolationLevel", "NONE") // set isolationLevel to NONE
.option("user", "root") // TiDB user here
.save()
```

Set `isolationLevel` to `NONE` to avoid large single transactions which might lead to TiDB OOM and also avoid the `ISOLATION LEVEL does not support` error (TiDB currently only supports `REPEATABLE-READ`).
### Delete data using TiSpark

You can use Spark SQL to delete data from TiKV.

```
spark.sql("use tidb_catalog")
spark.sql("delete from ${database}.${table} where xxx")
```

See [delete feature](https://github.com/pingcap/tispark/blob/master/docs/features/delete_userguide.md) for more details.
### Work with other data sources

You can use multiple catalogs to read data from different data sources as follows:

```
// Read from Hive
spark.sql("select * from spark_catalog.default.t").show

// Join Hive tables and TiDB tables
spark.sql("select t1.id,t2.id from spark_catalog.default.t t1 left join tidb_catalog.test.t t2").show
```
