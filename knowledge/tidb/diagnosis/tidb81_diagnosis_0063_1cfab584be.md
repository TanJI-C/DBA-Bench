# PLAN REPLAYER export overview and dump examples

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-replayer.md`
- Source Title: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster`
- Source Heading Path: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER` to export cluster information | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER` to export cluster information > Examples of exporting cluster information`
- Source Line Ranges: `5-129`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `plan-replayer`, `export`, `dump`, `historical-statistics`, `session-variable`, `http-download`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0063_1cfab584be`
- Source ID: `tidb-docs-8.1:sql-plan-replayer.md#use-plan-replayer-to-save-and-restore-the-on-site-information-of-a-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7f3572d421837f8a8230d8426f3c511b30b66c167d70540fa97bc47c0ffad46c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-to-save-and-restore-the-on-site-information-of-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-replayer.md

## Retrieval Guidance

- Use When: Use this when you need the syntax, contents, returned token, retention, or download path for exporting on-site troubleshooting information with PLAN REPLAYER DUMP.
- Retrieval Keywords: PLAN REPLAYER DUMP, WITH STATS AS OF TIMESTAMP, EXPLAIN ANALYZE, tidb_last_plan_replayer_token, plan_replayer/dump, replayer_*.zip, errors.txt, historical statistics, sqls.txt, HTTP interface
- Follow-up Guidance: The exported ZIP file can be downloaded from http://${tidb-server-ip}:${tidb-server-status-port}/plan_replayer/dump/${file_token}, and TiDB stores it for at most one hour.
- Classification Note: This is classified as diagnosis because the content explains how to export optimizer, schema, statistics, bindings, and session information for troubleshooting without exporting table data.

## Official Source Content

# Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster

When you locate and troubleshoot the issues of a TiDB cluster, you often need to provide information on the system and the execution plan. To help you get the information and troubleshoot cluster issues in a more convenient and efficient way, the `PLAN REPLAYER` command is introduced in TiDB v5.3.0. This command enables you to easily save and restore the on-site information of a cluster, improves the efficiency of troubleshooting, and helps you more easily archive the issue for management.

The features of `PLAN REPLAYER` are as follows:

- Exports the information of a TiDB cluster at an on-site troubleshooting to a ZIP-formatted file for storage.
- Imports into a cluster the ZIP-formatted file exported from another TiDB cluster. This file contains the information of the latter TiDB cluster at an on-site troubleshooting.
## Use `PLAN REPLAYER` to export cluster information

You can use `PLAN REPLAYER` to save the on-site information of a TiDB cluster. The export interface is as follows:

```sql
PLAN REPLAYER DUMP [WITH STATS AS OF TIMESTAMP expression] EXPLAIN [ANALYZE] sql-statement;
```

Based on `sql-statement`, TiDB sorts out and exports the following on-site information:

- TiDB version
- TiDB configuration
- TiDB session variables
- TiDB SQL bindings
- The table schema in `sql-statement`
- The statistics of the table in `sql-statement`
- The result of `EXPLAIN [ANALYZE] sql-statement`
- Some internal procedures of query optimization

If historical statistics are [enabled](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_historical_stats), you can specify a time in the `PLAN REPLAYER` statement to get the historical statistics for the corresponding time. You can directly specify a time and date or specify a timestamp. TiDB looks for the historical statistics before the specified time and exports the latest one among them.

If there are no historical statistics before the specified time, TiDB exports the latest statistics, which is consistent with the behavior when no time is specified. In addition, TiDB prints the error messages in the `errors.txt` file within the exported `ZIP` file.

> **Note:**
>
> `PLAN REPLAYER` **DOES NOT** export any table data.
### Examples of exporting cluster information

```sql
use test;
create table t(a int, b int);
insert into t values(1,1), (2, 2), (3, 3);
analyze table t;

plan replayer dump explain select * from t;
plan replayer dump with stats as of timestamp '2023-07-17 12:00:00' explain select * from t;
plan replayer dump with stats as of timestamp '442012134592479233' explain select * from t;
```

`PLAN REPLAYER DUMP` packages the table information above into a `ZIP` file and returns the file identifier as the execution result.

> **Note:**
>
> The `ZIP` file is stored in a TiDB cluster for at most one hour. After one hour, TiDB will delete it.

```sql
MySQL [test]> plan replayer dump explain select * from t;
```

```sql
+------------------------------------------------------------------+
| Dump_link                                                        |
+------------------------------------------------------------------+
| replayer_JOGvpu4t7dssySqJfTtS4A==_1635750890568691080.zip |
+------------------------------------------------------------------+
1 row in set (0.015 sec)
```

Alternatively, you can use the session variable [`tidb_last_plan_replayer_token`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_last_plan_replayer_token-new-in-v630) to obtain the result of the last `PLAN REPLAYER DUMP` execution.

```sql
SELECT @@tidb_last_plan_replayer_token;
```

```sql
+-----------------------------------------------------------+
| @@tidb_last_plan_replayer_token                           |
+-----------------------------------------------------------+
| replayer_Fdamsm3C7ZiPJ-LQqgVjkA==_1663304195885090000.zip |
+-----------------------------------------------------------+
1 row in set (0.00 sec)
```

When there are multiple SQL statements, you can obtain the result of the `PLAN REPLAYER DUMP` execution using a file. The results of multiple SQL statements are separated by `;` in this file.

```sql
plan replayer dump explain 'sqls.txt';
```

```sql
Query OK, 0 rows affected (0.03 sec)
```

```sql
SELECT @@tidb_last_plan_replayer_token;
```

```sql
+-----------------------------------------------------------+
| @@tidb_last_plan_replayer_token                           |
+-----------------------------------------------------------+
| replayer_LEDKg8sb-K0u24QesiH8ig==_1663226556509182000.zip |
+-----------------------------------------------------------+
1 row in set (0.00 sec)
```

Because the file cannot be downloaded on MySQL Client, you need to use the TiDB HTTP interface and the file identifier to download the file:

```shell
http://${tidb-server-ip}:${tidb-server-status-port}/plan_replayer/dump/${file_token}
```

`${tidb-server-ip}:${tidb-server-status-port}` is the address of any TiDB server in the cluster. For example:

```shell
curl http://127.0.0.1:10080/plan_replayer/dump/replayer_JOGvpu4t7dssySqJfTtS4A==_1635750890568691080.zip > plan_replayer.zip
```
