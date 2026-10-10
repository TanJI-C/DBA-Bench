# Tune export concurrency consistency snapshots and GC

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dumpling-overview.md`
- Source Title: `Dumpling Overview`
- Source Heading Path: `Use Dumpling to Export Data > Export data from TiDB or MySQL > Improve export efficiency through concurrency | Use Dumpling to Export Data > Export data from TiDB or MySQL > Adjust Dumpling's data consistency options | Use Dumpling to Export Data > Export data from TiDB or MySQL > Export historical data snapshots of TiDB | Use Dumpling to Export Data > Export data from TiDB or MySQL > Control the memory usage of exporting large tables | Use Dumpling to Export Data > Export data from TiDB or MySQL > Manually set the TiDB GC time | Use Dumpling to Export Data > Option list of Dumpling`
- Source Line Ranges: `283-373`
- Source Scope: `shared`
- Primary Component: `dumpling`
- Related Components: `tidb`, `pd`, `sql`
- Topic Tags: `concurrency`, `compression`, `consistency`, `snapshot`, `memory-usage`, `gc-lifetime`, `large-tables`, `options`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0134_6e357c5e6e`
- Source ID: `tidb-docs-8.1:dumpling-overview.md#improve-export-efficiency-through-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `34fbffb7d7414d7b4cbf99e1652c2ee6410c3d939c9e2d28a95130f2316c8910`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dumpling-overview#improve-export-efficiency-through-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dumpling-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs official Dumpling options for concurrency, consistency levels, snapshots, memory control for large-table export, or manual TiDB GC lifetime handling.
- Retrieval Keywords: -t, -r, --compress, gzip, snappy, zstd, --consistency, flush, snapshot, lock, none, auto, --snapshot, SHOW MASTER STATUS, tidb_snapshot, --tidb-mem-quota-query, --params "tidb_distsql_scan_concurrency=5", tidb_distsql_scan_concurrency, Out of Memory (OOM), SET GLOBAL tidb_gc_life_time = '720h';, SET GLOBAL tidb_gc_life_time = '10m';, INFORMATION_SCHEMA.CLUSTER_INFO, PD address
- Follow-up Guidance: The source explains that auto is the default consistency level, gives example --snapshot values as either a TSO or a datetime, and states that manual GC lifetime extension is needed when Dumpling cannot automatically adjust the GC safe point.
- Classification Note: This is classified as operation because the content covers runtime export behavior, performance tuning, consistency control, snapshot export, memory-related parameters, and GC handling during Dumpling operations.

## Official Source Content

### Improve export efficiency through concurrency

The exported file is stored in the `./export-<current local time>` directory by default. Commonly used options are as follows:

- The `-t` option specifies the number of threads for the export. Increasing the number of threads improves the concurrency of Dumpling and the export speed, and also increases the database's memory consumption. Therefore, it is not recommended to set the number too large.
- The `-r` option enables the in-table concurrency to speed up the export. The default value is `0`, which means disabled. A value greater than 0 means it is enabled, and the value is of `INT` type. When the source database is TiDB, a `-r` value greater than 0 indicates that the TiDB region information is used for splitting, and reduces the memory usage. The specific `-r` value does not affect the split algorithm. When the source database is MySQL and the primary key or the first column of the composite primary key is of the `INT` type, specifying `-r` can also enable the in-table concurrency.
- The `--compress <format>` option specifies the compression format of the dump. It supports the following compression algorithms: `gzip`, `snappy`, and `zstd`. This option can speed up dumping of data if storage is the bottleneck or if storage capacity is a concern. The drawback is an increase in CPU usage. Each file is compressed individually.

With the above options specified, Dumpling can have a quicker speed of data export.
### Adjust Dumpling's data consistency options

> **Note:**
>
> The default value is `auto` for the data consistency option. In most scenarios, you do not need to adjust the default data consistency options of Dumpling.

Dumpling uses the `--consistency <consistency level>` option to control the way in which data is exported for "consistency assurance". When using snapshot for consistency, you can use the `--snapshot` option to specify the timestamp to be backed up. You can also use the following levels of consistency:

- `flush`: Use [`FLUSH TABLES WITH READ LOCK`](https://dev.mysql.com/doc/refman/8.0/en/flush.html#flush-tables-with-read-lock) to temporarily interrupt the DML and DDL operations of the replica database, to ensure the global consistency of the backup connection, and to record the binlog position (POS) information. The lock is released after all backup connections start transactions. It is recommended to perform full backups during off-peak hours or on the MySQL replica database.
- `snapshot`: Get a consistent snapshot of the specified timestamp and export it.
- `lock`: Add read locks on all tables to be exported.
- `none`: No guarantee for consistency.
- `auto`: Use `flush` for MySQL and `snapshot` for TiDB.

After everything is done, you can see the exported file in `/tmp/test`:

```shell
ls -lh /tmp/test | awk '{print $5 "\t" $9}'
```

```
140B  metadata
66B   test-schema-create.sql
300B  test.sbtest1-schema.sql
190K  test.sbtest1.0.sql
300B  test.sbtest2-schema.sql
190K  test.sbtest2.0.sql
300B  test.sbtest3-schema.sql
190K  test.sbtest3.0.sql
```
### Export historical data snapshots of TiDB

Dumpling can export the data of a certain [tidb_snapshot](https://docs.pingcap.com/tidb/stable/read-historical-data#how-tidb-reads-data-from-history-versions) with the `--snapshot` option specified.

The `--snapshot` option can be set to a TSO (the `Position` field output by the `SHOW MASTER STATUS` command) or a valid time of the `datetime` data type (in the form of `YYYY-MM-DD hh:mm:ss`), for example:

```shell
tiup dumpling --snapshot 417773951312461825
tiup dumpling --snapshot "2020-07-02 17:12:45"
```

The TiDB historical data snapshots when the TSO is `417773951312461825` and the time is `2020-07-02 17:12:45` are exported.
### Control the memory usage of exporting large tables

When Dumpling is exporting a large single table from TiDB, Out of Memory (OOM) might occur because the exported data size is too large, which causes connection abort and export failure. You can use the following parameters to reduce the memory usage of TiDB:

+ Setting `-r` to split the data to be exported into chunks. This reduces the memory overhead of TiDB's data scan and enables concurrent table data dump to improve export efficiency. When the upstream database is TiDB v3.0 or later versions, a `-r` value greater than 0 indicates that the TiDB region information is used for splitting and the specific `-r` value does not affect the split algorithm.
+ Reduce the value of `--tidb-mem-quota-query` to `8589934592` (8 GB) or lower. `--tidb-mem-quota-query` controls the memory usage of a single query statement in TiDB.
+ Adjust the `--params "tidb_distsql_scan_concurrency=5"` parameter. [`tidb_distsql_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_distsql_scan_concurrency) is a session variable which controls the concurrency of the scan operations in TiDB.
### Manually set the TiDB GC time

When exporting data from TiDB (less than 1 TB), if the TiDB version is v4.0.0 or later and Dumpling can access the PD address and the [`INFORMATION_SCHEMA.CLUSTER_INFO`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-cluster-info) table of the TiDB cluster, Dumpling automatically adjusts the GC safe point to block GC without affecting the original cluster.

However, in either of the following scenarios, Dumpling cannot automatically adjust the GC time:

- The data size is very large (more than 1 TB).
- Dumpling cannot connect directly to PD, for example, if the TiDB cluster is on TiDB Cloud or on Kubernetes that is separated from Dumpling.

In such scenarios, you must manually extend the GC time in advance to avoid export failure due to GC during the export process.

To manually adjust the GC time, use the following SQL statement:

```sql
SET GLOBAL tidb_gc_life_time = '720h';
```

After Dumpling exits, regardless of whether the export is successful or not, you must set the GC time back to its original value (the default value is `10m`).

```sql
SET GLOBAL tidb_gc_life_time = '10m';
```
## Option list of Dumpling
