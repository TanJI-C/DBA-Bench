# Full import benchmark case for DM

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-performance-test.md`
- Source Title: `DM Cluster Performance Test`
- Source Heading Path: `DM Cluster Performance Test > Performance test > Full import benchmark case | DM Cluster Performance Test > Performance test > Full import benchmark case > Generate test data | DM Cluster Performance Test > Performance test > Full import benchmark case > Create a data migration task | DM Cluster Performance Test > Performance test > Full import benchmark case > Get test results`
- Source Line Ranges: `39-103`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`
- Topic Tags: `full-import`, `sysbench`, `migration-task`, `task-configuration`, `loader-thread`, `mydumpers`, `throughput-measurement`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0108_6e3cc1b16f`
- Source ID: `tidb-docs-8.1:dm/dm-performance-test.md#full-import-benchmark-case`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `75bea475c597469bdb9608d7263074473fbddde2bedef5a679e249d0fd8d9de1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-performance-test#full-import-benchmark-case
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-performance-test.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented full import benchmark case for DM, including test data generation, `full` mode task configuration, and how to recognize import completion in logs.
- Retrieval Keywords: Full import benchmark case, sysbench --test=oltp_insert, --tables=4, --table-size=50000000, dm_benchmark, source-id, source-1, task-mode: full, name: test-full, mydumper-config-name, loader-thread: 16, block-allow-list, do-dbs, mydumpers, rows: 32000, threads: 32, all data files have been finished, loader.go:604, cost time
- Follow-up Guidance: The source notes that `rows` in `mydumpers` can enable concurrently exporting data from a single table using multi-thread, and that `loader-thread`, `rows`, and `threads` can be tuned to test performance under different configurations.
- Classification Note: This is classified as performance content because it provides a benchmark procedure for full data import, including sysbench data generation, DM task parameters, and throughput calculation from import time.

## Official Source Content

### Full import benchmark case
#### Generate test data

Use `sysbench` to create test tables upstream and generate test data for full import. Execute the following `sysbench` command to generate test data:

```bash
sysbench --test=oltp_insert --tables=4 --mysql-host=172.16.4.40 --mysql-port=3306 --mysql-user=root --mysql-db=dm_benchmark --db-driver=mysql --table-size=50000000 prepare
```
#### Create a data migration task

1. Create an upstream MySQL source and set `source-id` to `source-1`. For details, see [Load the Data Source Configurations](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#operate-data-source).

2. Create a migration task (in `full` mode). The following is a task configuration template:

  ```yaml
  ---
  name: test-full
  task-mode: full

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
      mydumper-config-name: "global"
      loader-thread: 16

  # Configure the name of the database where sysbench generates data.
  block-allow-list:
    instance:
      do-dbs: ["dm_benchmark"]

  mydumpers:
    global:
      rows: 32000
      threads: 32
  ```

For details about how to create a migration task, see [Create a Data Migration Task](https://docs.pingcap.com/tidb/stable/dm/dm-create-task).

> **Note:**
>
> - To enable concurrently exporting data from a single table using multi-thread, you can use the `rows` option in the `mydumpers` configuration item. This speeds up data export.
> - To test the performance under different configurations, you can tune `loader-thread` in the `mysql-instances` configuration, as well as `rows` and `threads` in the `mydumpers` configuration item.
#### Get test results

Observe the DM-worker log. When you see `all data files have been finished`, it means that full data has been imported. In this case, you can see the time consumed to import data. The sample log is as follows:

```
 [INFO] [loader.go:604] ["all data files have been finished"] [task=test] [unit=load] ["cost time"=52.439796ms]
```

According to the size of the test data and the time consumed to import data, you can calculate the migration speed of the full data.
