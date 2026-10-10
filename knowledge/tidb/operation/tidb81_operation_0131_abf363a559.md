# RDS sharded table handling, upstream table changes, and concurrency control

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/shard-merge-best-practices.md`
- Source Title: `Best Practices of Data Migration in the Shard Merge Scenario`
- Source Heading Path: `Best Practices of Data Migration in the Shard Merge Scenario > Special processing when the upstream RDS contains sharded tables | Best Practices of Data Migration in the Shard Merge Scenario > Create/drop tables in the upstream | Best Practices of Data Migration in the Shard Merge Scenario > Create/drop tables in the upstream > Create sharded tables in the upstream | Best Practices of Data Migration in the Shard Merge Scenario > Create/drop tables in the upstream > Drop sharded tables in the upstream | Best Practices of Data Migration in the Shard Merge Scenario > Speed limits and traffic flow control`
- Source Line Ranges: `120-164`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `rds`, `table-routing`, `sharded-tables`, `stop-task`, `start-task`, `binlog-position`, `query-status`, `upstream-ddl`, `concurrency`, `traffic-control`, `performance-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0131_abf363a559`
- Source ID: `tidb-docs-8.1:dm/shard-merge-best-practices.md#special-processing-when-the-upstream-rds-contains-sharded-tables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `523a6374f52c0045d67a4456021e10c00dc93c7f989d2ffbfc058aa83467b349`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/shard-merge-best-practices#special-processing-when-the-upstream-rds-contains-sharded-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/shard-merge-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need DM operational guidance for shard merge with upstream RDS binlog table names, creating or dropping upstream sharded tables, or concurrency control across multiple DM-workers.
- Retrieval Keywords: upstream RDS contains sharded tables, table routing, table names in binlog, SQL client, UCloud distributed database, _0001, dm-table-routing, create sharded tables in the upstream, drop sharded tables in the upstream, stop-task, start-task, query-status, SHOW BINLOG EVENTS, End_log_pos, DROP TABLE, Pos-M, Pos-S, syncerBinlog, task.yaml, pool-size, worker-count, speed limits and traffic flow control, DM-worker, monitoring metrics
- Follow-up Guidance: The content says to use `query-status` for verification after restarting the task and to compare `syncerBinlog` with `End_log_pos` when handling dropped sharded tables.
- Classification Note: This is classified as operation because the content describes runtime handling for RDS-specific binlog routing, task stop and start procedures for upstream table changes, and concurrency tuning based on DM and TiDB monitoring metrics.

## Official Source Content

## Special processing when the upstream RDS contains sharded tables

If the upstream data source is an RDS and it contains sharded tables, the table names in MySQL binlog might be invisible when connecting to a SQL client. For example, if the upstream is a UCloud distributed database, the table name in the binlog might have an extra prefix `_0001`. Therefore, you need to configure [table routing](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing) based on the table names in binlog, instead of those in the SQL client.
## Create/drop tables in the upstream

In [Merge and Migrate Data from Sharded Tables](https://docs.pingcap.com/tidb/stable/dm/feature-shard-merge-pessimistic#principles), it is clear that the coordination of sharding DDL lock depends on whether the downstream database receives the DDL statements of all upstream sharded tables. In addition, DM currently **does not support** dynamically creating or dropping sharded tables in the upstream. Therefore, to create or drop sharded tables in the upstream, it is recommended to perform the following steps.
### Create sharded tables in the upstream

If you need to create a new sharded table in the upstream, perform the following steps:

1. Wait for the coordination of all executed sharding DDL in the upstream sharded tables to finish.

2. Run `stop-task` to stop the data migration task.

3. Create a new sharded table in the upstream.

4. Make sure that the configuration in the `task.yaml` file allows the newly added sharded table to be merged in one downstream table with other existing sharded tables.

5. Run `start-task` to start the task.

6. Run `query-status` to verify whether the data migration task is successfully processed and whether the data from upstream has already been merged and migrated to the downstream database.
### Drop sharded tables in the upstream

If you need to drop a sharded table in the upstream, perform the following steps:

1. Drop the sharded table, run [`SHOW BINLOG EVENTS`](https://dev.mysql.com/doc/refman/8.0/en/show-binlog-events.html) to fetch the `End_log_pos` corresponding to the `DROP TABLE` statement in the binlog events, and mark it as *Pos-M*.

2. Run `query-status` to fetch the position (`syncerBinlog`) corresponding to the binlog event that has been processed by DM, and mark it as *Pos-S*.

3. When *Pos-S* is greater than *Pos-M*, it means that DM has processed all of the `DROP TABLE` statements, and the data of the table before dropping has been migrated to the downstream, so the subsequent operation can be performed. Otherwise, wait for DM to finish migrating the data.

4. Run `stop-task` to stop the task.

5. Make sure that the configuration in the `task.yaml` file ignores the dropped sharded table in the upstream.

6. Run `start-task` to start the task.

7. Run `query-status` to verify whether the data migration task is successfully processed.
## Speed limits and traffic flow control

When data from multiple upstream MySQL or MariaDB instances is merged and migrated to the same TiDB cluster in the downstream, every DM-worker corresponding to each upstream instance executes full and incremental data replication concurrently. This means that the default degree of concurrency (`pool-size` in full data migration and `worker-count` in incremental data replication) accumulates as the number of DM-workers increases, which might overload the downstream database. In this case, you need to conduct a preliminary performance analysis based on TiDB and DM monitoring metrics and adjust the value of each concurrency parameter. In the future, DM is expected to support partially automated traffic flow control.
