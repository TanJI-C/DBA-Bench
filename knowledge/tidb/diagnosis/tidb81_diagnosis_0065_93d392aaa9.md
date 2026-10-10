# PLAN REPLAYER CAPTURE task registration, inspection, results, and removal

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-replayer.md`
- Source Title: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster`
- Source Heading Path: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CAPTURE` to capture target plans > Use `PLAN REPLAYER CAPTURE` | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CAPTURE` to capture target plans > View the capture tasks | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CAPTURE` to capture target plans > View the capture results | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CAPTURE` to capture target plans > Remove the capture tasks`
- Source Line Ranges: `217-292`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `plan replayer`, `capture`, `sql digest`, `plan digest`, `tasks`, `results`, `token`, `cleanup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0065_93d392aaa9`
- Source ID: `tidb-docs-8.1:sql-plan-replayer.md#use-plan-replayer-capture`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `25b55370cb0533243f33ac490f78846969a608a41dc6d07ec82787c4dfb44bdd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-capture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-replayer.md

## Retrieval Guidance

- Use When: Use this when you need the SQL statements and tables for registering a PLAN REPLAYER CAPTURE task by sql_digest and plan_digest, checking task and result records, finding the download token, or removing a capture task.
- Retrieval Keywords: PLAN REPLAYER CAPTURE, PLAN REPLAYER CAPTURE REMOVE, sql_digest, plan_digest, mysql.plan_replayer_task, mysql.plan_replayer_status, token, SELECT * FROM mysql.plan_replayer_task, SELECT * FROM mysql.plan_replayer_status, capture tasks, capture results, replayer_*.zip, one week
- Follow-up Guidance: The content also states that the download method is the same as PLAN REPLAYER and that the result file is kept in the TiDB cluster for up to one week before TiDB deletes it.
- Classification Note: This is classified as diagnosis because it covers PLAN REPLAYER CAPTURE task registration, inspection of mysql.plan_replayer_task and mysql.plan_replayer_status, result tokens, and task removal for collecting on-site information.

## Official Source Content

### Use `PLAN REPLAYER CAPTURE`

You can register the digest of the target SQL statement and execution plan in the TiDB cluster using the following statement:

```sql
PLAN REPLAYER CAPTURE 'sql_digest' 'plan_digest';
```

If the target SQL statement has multiple execution plans and you want to capture all execution plans, you can register all the execution plans at once using the following statement:

```sql
PLAN REPLAYER CAPTURE 'sql_digest' '*';
```
### View the capture tasks

You can view the ongoing capture tasks of `PLAN REPLAYER CAPTURE` in the TiDB cluster using the following statement:

```sql
mysql> PLAN REPLAYER CAPTURE 'example_sql' 'example_plan';
Query OK, 1 row affected (0.01 sec)

mysql> SELECT * FROM mysql.plan_replayer_task;
+-------------+--------------+---------------------+
| sql_digest  | plan_digest  | update_time         |
+-------------+--------------+---------------------+
| example_sql | example_plan | 2023-01-28 11:58:22 |
+-------------+--------------+---------------------+
1 row in set (0.01 sec)
```
### View the capture results

After `PLAN REPLAYER CAPTURE` successfully captures the result, you can view the token used for file download using the following SQL statement:

```sql
mysql> SELECT * FROM mysql.plan_replayer_status;
+------------------------------------------------------------------+------------------------------------------------------------------+------------+-----------------------------------------------------------+---------------------+-------------+-----------------+
| sql_digest                                                       | plan_digest                                                      | origin_sql | token                                                     | update_time         | fail_reason | instance        |
+------------------------------------------------------------------+------------------------------------------------------------------+------------+-----------------------------------------------------------+---------------------+-------------+-----------------+
| 086e3fbd2732f7671c17f299d4320689deeeb87ba031240e1e598a0ca14f808c | 042de2a6652a6d20afc629ff90b8507b7587a1c7e1eb122c3e0b808b1d80cc02 |            | replayer_Utah4nkz2sIEzkks7tIRog==_1668746293523179156.zip | 2022-11-18 12:38:13 | NULL        | 172.16.4.4:4022 |
| b5b38322b7be560edb04f33f15b15a885e7c6209a22b56b0804622e397199b54 | 1770efeb3f91936e095f0344b629562bf1b204f6e46439b7d8f842319297c3b5 |            | replayer_Z2mUXNHDjU_WBmGdWQqifw==_1668746293560115314.zip | 2022-11-18 12:38:13 | NULL        | 172.16.4.4:4022 |
| 96d00c0b3f08795fe94e2d712fa1078ab7809faf4e81d198f276c0dede818cf9 | 8892f74ac2a42c2c6b6152352bc491b5c07c73ac3ed66487b2c990909bae83e8 |            | replayer_RZcRHJB7BaCccxFfOIAhWg==_1668746293578282450.zip | 2022-11-18 12:38:13 | NULL        | 172.16.4.4:4022 |
+------------------------------------------------------------------+------------------------------------------------------------------+------------+-----------------------------------------------------------+---------------------+-------------+-----------------+
3 rows in set (0.00 sec)
```

The method of downloading the file of `PLAN REPLAYER CAPTURE` is the same as that of `PLAN REPLAYER`. For details, see [Examples of exporting cluster information](#examples-of-exporting-cluster-information).

> **Note:**
>
> The result file of `PLAN REPLAYER CAPTURE` is kept in the TiDB cluster for up to one week. After one week, TiDB deletes the file.
### Remove the capture tasks

If a capture task is no longer needed, you can remove it using the `PLAN REPLAYER CAPTURE REMOVE` statement. For example:

```sql
mysql> PLAN REPLAYER CAPTURE '077a87a576e42360c95530ccdac7a1771c4efba17619e26be50a4cfd967204a0' '4838af52c1e07fc8694761ad193d16a689b2128bc5ced9d13beb31ae27b370ce';
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT * FROM mysql.plan_replayer_task;
+------------------------------------------------------------------+------------------------------------------------------------------+---------------------+
| sql_digest                                                       | plan_digest                                                      | update_time         |
+------------------------------------------------------------------+------------------------------------------------------------------+---------------------+
| 077a87a576e42360c95530ccdac7a1771c4efba17619e26be50a4cfd967204a0 | 4838af52c1e07fc8694761ad193d16a689b2128bc5ced9d13beb31ae27b370ce | 2024-05-21 11:26:10 |
+------------------------------------------------------------------+------------------------------------------------------------------+---------------------+
1 row in set (0.01 sec)

mysql> PLAN REPLAYER CAPTURE REMOVE '077a87a576e42360c95530ccdac7a1771c4efba17619e26be50a4cfd967204a0' '4838af52c1e07fc8694761ad193d16a689b2128bc5ced9d13beb31ae27b370ce';
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT * FROM mysql.plan_replayer_task;
Empty set (0.01 sec)
```
