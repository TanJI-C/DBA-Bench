# PLAN REPLAYER import and restore workflow

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-replayer.md`
- Source Title: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster`
- Source Heading Path: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER` to import cluster information`
- Source Line Ranges: `130-200`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `plan-replayer`, `import`, `load`, `restore`, `auto-analyze`, `statistics`, `sql-bindings`, `schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0037_6793ecfe4f`
- Source ID: `tidb-docs-8.1:sql-plan-replayer.md#use-plan-replayer-to-import-cluster-information`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f7e47bdcd23ec9af0eae8f1096710fab50389333644c492cfccb8f89548e2f0a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-to-import-cluster-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-replayer.md

## Retrieval Guidance

- Use When: Use this when you need the PLAN REPLAYER LOAD syntax, import effects, auto analyze note, or the LOAD DATA LOCAL INFILE client restriction during restore of exported cluster information.
- Retrieval Keywords: PLAN REPLAYER LOAD, plan_replayer.zip, tidb_enable_auto_analyze, set @@global.tidb_enable_auto_analyze = OFF, SQL bindings, table schemas, statistics, show stats_meta, ERROR 2068 (HY000), LOAD DATA LOCAL INFILE file request rejected due to restrictions on access, --local-infile=true
- Follow-up Guidance: The content notes that importing modifies TiDB session variables, SQL bindings, table schemas, and statistics in the target cluster, and that the mysql client error 2068 can be addressed with --local-infile=true.
- Classification Note: This is classified as recovery because the content focuses on loading a previously exported ZIP file to restore on-site cluster information into another TiDB cluster.

## Official Source Content

## Use `PLAN REPLAYER` to import cluster information

> **Warning:**
>
> When you import the on-site information of a TiDB cluster to another cluster, the TiDB session variables, SQL bindings, table schemas and statistics of the latter cluster are modified.

With an existing `ZIP` file exported using `PLAN REPLAYER`, you can use the `PLAN REPLAYER` import interface to restore the on-site information of a cluster to any other TiDB cluster. The syntax is as follows:

```sql
PLAN REPLAYER LOAD 'file_name';
```

In the statement above, `file_name` is the name of the `ZIP` file to be imported.

For example:

```sql
PLAN REPLAYER LOAD 'plan_replayer.zip';
```

> **Note:**
>
> You need to disable auto analyze. Otherwise the imported statistics will be overwritten by analyze.

You can disable auto analyze by setting the [`tidb_enable_auto_analyze`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_analyze-new-in-v610) system variable to `OFF`:

```sql
set @@global.tidb_enable_auto_analyze = OFF;
```

After the cluster information is imported, the TiDB cluster is loaded with the required table schema, statistics and other information that affects the construction of the execution plan. You can view the execution plan and verify statistics in the following way:

```sql
mysql> desc t;
+-------+---------+------+------+---------+-------+
| Field | Type    | Null | Key  | Default | Extra |
+-------+---------+------+------+---------+-------+
| a     | int(11) | YES  |      | NULL    |       |
| b     | int(11) | YES  |      | NULL    |       |
+-------+---------+------+------+---------+-------+
2 rows in set (0.01 sec)

mysql> explain select * from t where a = 1 or b =1;
+-------------------------+---------+-----------+---------------+--------------------------------------+
| id                      | estRows | task      | access object | operator info                        |
+-------------------------+---------+-----------+---------------+--------------------------------------+
| TableReader_7           | 0.01    | root      |               | data:Selection_6                     |
| └─Selection_6           | 0.01    | cop[tikv] |               | or(eq(test.t.a, 1), eq(test.t.b, 1)) |
|   └─TableFullScan_5     | 6.00    | cop[tikv] | table:t       | keep order:false, stats:pseudo       |
+-------------------------+---------+-----------+---------------+--------------------------------------+
3 rows in set (0.00 sec)

mysql> show stats_meta;
+---------+------------+----------------+---------------------+--------------+-----------+
| Db_name | Table_name | Partition_name | Update_time         | Modify_count | Row_count |
+---------+------------+----------------+---------------------+--------------+-----------+
| test    | t          |                | 2022-08-26 15:52:07 |            3 |         6 |
+---------+------------+----------------+---------------------+--------------+-----------+
1 row in set (0.04 sec)
```

After the scene is loaded and restored, you can diagnose and improve the execution plan for the cluster.

> **Note:**
>
> If you use the `mysql` command-line client and encounter `ERROR 2068 (HY000): LOAD DATA LOCAL INFILE file request rejected due to restrictions on access.`, you can add `--local-infile=true` in the connection string.
