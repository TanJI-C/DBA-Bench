# Incremental replication benchmark case for DM

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-performance-test.md`
- Source Title: `DM Cluster Performance Test`
- Source Heading Path: `DM Cluster Performance Test > Performance test > Incremental replication benchmark case | DM Cluster Performance Test > Performance test > Incremental replication benchmark case > Initialize tables | DM Cluster Performance Test > Performance test > Incremental replication benchmark case > Create a data migration task | DM Cluster Performance Test > Performance test > Incremental replication benchmark case > Generate incremental data | DM Cluster Performance Test > Performance test > Incremental replication benchmark case > Get test results`
- Source Line Ranges: `104-167`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `incremental-replication`, `sysbench`, `migration-task`, `task-configuration`, `syncers`, `worker-count`, `batch-size`, `monitoring-metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0109_b7c72a8489`
- Source ID: `tidb-docs-8.1:dm/dm-performance-test.md#incremental-replication-benchmark-case`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `907565d3b736739ff9cc674fe2de69345209815aa6aeef957dc6d8a266761577`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-performance-test#incremental-replication-benchmark-case
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented incremental replication benchmark case for DM, including the `all` mode task configuration, sysbench incremental workload, and monitoring methods for migration status and metrics.
- Retrieval Keywords: Incremental replication benchmark case, task-mode: all, name: test-all, source-id, source-1, syncer-config-name, syncers, worker-count: 16, batch: 100, sysbench --test=oltp_insert, --num-threads=32, --report-interval=10, --time=1800, dm_benchmark, query-status, Grafana, finished sqls jobs, Binlog Migration Monitoring Metrics
- Follow-up Guidance: The source states that you can tune `worker-count` and `batch` in `syncers`, use different `sysbench` statements for different scenarios, run `query-status` to observe migration status, and use Grafana to observe metrics such as `finished sqls jobs`.
- Classification Note: This is classified as performance content because it describes an incremental replication benchmark workflow and the related DM syncer settings, workload generation, and monitoring metrics.

## Official Source Content

### Incremental replication benchmark case
#### Initialize tables

Use `sysbench` to create test tables in the upstream.
#### Create a data migration task

1. Create the source of the upstream MySQL. Set `source-id` to `source-1` (if the source has been created in the [full import benchmark case](#full-import-benchmark-case), you do not need to create it again). For details, see [Load the Data Source Configurations](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#operate-data-source).

2. Create a DM migration task (in `all` mode). The following is an example of the task configuration file:

  ```yaml
  ---
  name: test-all
  task-mode: all

  # Configure the migration task using the TiDB information of your actual test environment.
  target-database:
    host: "192.168.0.1"
    port: 4000
    user: "root"
    password: ""

  mysql-instances:
    -
      source-id: "source-1"
      block-allow-list:  "instance"
      syncer-config-name: "global"

  # Configure the name of the database where sysbench generates data.
  block-allow-list:
    instance:
      do-dbs: ["dm_benchmark"]

  syncers:
    global:
      worker-count: 16
      batch: 100
  ```

For details about how to create a data migration task, see [Create a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-create-task).

> **Note:**
>
> To test the performance under different configurations, you can tune `worker-count` and `batch` in the `syncers` configuration item.
#### Generate incremental data

To continuously generate incremental data in the upstream, run the `sysbench` command:

```bash
sysbench --test=oltp_insert --tables=4 --num-threads=32 --mysql-host=172.17.4.40 --mysql-port=3306 --mysql-user=root --mysql-db=dm_benchmark --db-driver=mysql --report-interval=10 --time=1800 run
```

> **Note:**
>
> You can test the data migration performance under different scenarios by using different `sysbench` statements.
#### Get test results

To observe the migration status of DM, you can run the `query-status` command. To observe the monitoring metrics of DM, you can use Grafana. Here the monitoring metrics refer to `finished sqls jobs` (the number of jobs finished per unit time), and other related metrics. For more information, see [Binlog Migration Monitoring Metrics](https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster#binlog-replication).
