# DM migration task performance configuration options

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-tune-configuration.md`
- Source Title: `Optimize Configuration of DM`
- Source Heading Path: `Optimize Configuration of DM | Optimize Configuration of DM > Full data export | Optimize Configuration of DM > Full data export > `rows` | Optimize Configuration of DM > Full data export > `chunk-filesize` | Optimize Configuration of DM > Full data import | Optimize Configuration of DM > Full data import > `pool-size` | Optimize Configuration of DM > Incremental data replication | Optimize Configuration of DM > Incremental data replication > `worker-count` | Optimize Configuration of DM > Incremental data replication > `batch``
- Source Line Ranges: `5-59`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `full-data-export`, `full-data-import`, `incremental-replication`, `threads`, `chunking`, `rows`, `pool-size`, `worker-count`, `batch`, `task-configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0110_bec6efe052`
- Source ID: `tidb-docs-8.1:dm/dm-tune-configuration.md#optimize-configuration-of-dm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `80811196c825a90063ca04e59662a5927c205e803b19bae89acfcf57a60ff898`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-tune-configuration#optimize-configuration-of-dm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-tune-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when searching for DM migration task performance tuning options for full data export, full data import, or incremental replication, including thread counts, chunking, and batch settings.
- Retrieval Keywords: DM, Optimize Configuration of DM, mydumpers, loaders, syncers, rows, threads, mydumper-thread, chunk-filesize, pool-size, loader-thread, worker-count, syncer-thread, batch, DM Load unit, DM Sync unit, full data export, full data import, incremental data replication, stop the task using dmctl, re-create the task
- Follow-up Guidance: The source also notes that `mydumpers`, `loaders`, and `syncers` values cannot be updated after task creation and must be changed by stopping the task using dmctl, updating the configuration file, and re-creating the task.
- Classification Note: This is classified as performance content because it explains DM task configuration options that affect export concurrency, import thread count, and incremental replication throughput.

## Official Source Content

# Optimize Configuration of DM

This document introduces how to optimize the configuration of the data migration task to improve the performance of data migration.
## Full data export

`mydumpers` is the configuration item related to full data export. This section describes how to configure performance-related options.
### `rows`

Setting the `rows` option enables concurrently exporting data from a single table using multi-thread. The value of `rows` is the maximum number of rows contained in each exported chunk. After this option is enabled, DM selects a column as the split benchmark when the data of a MySQL single table is concurrently exported. This column can be one of the following columns: the primary key column, the unique index column, and the normal index column (ordered from highest priority to lowest). Make sure this column is of integer type (for example, `INT`, `MEDIUMINT`, `BIGINT`).

The value of `rows` can be set to 10000. You can change this value according to the total number of rows in the table and the performance of the database. In addition, you need to set `threads` to control the number of concurrent threads. By default, the value of `threads` is 4. You can adjust this value as needed.
### `chunk-filesize`

During full backup, DM splits the data of each table into multiple chunks according to the value of the `chunk-filesize` option. Each chunk is saved in a file with a size of about `chunk-filesize`. In this way, data is split into multiple files and you can use the parallel processing of the DM Load unit to improve the import speed. The default value of this option is 64 (in MB). Normally, you do not need to set this option. If you set it, adjust the value of this option according to the size of the full data.

> **Note:**
>
> - You cannot update the value of `mydumpers` after the migration task is created. Be sure about the value of each option before creating the task. If you need to update the value, stop the task using dmctl, update the configuration file, and re-create the task.
> - `mydumpers`.`threads` can be replaced with the `mydumper-thread` configuration item for simplicity.
> - If `rows` is set, DM ignores the value of `chunk-filesize`.
## Full data import

`loaders` is the configuration item related to full data import. This section describes how to configure performance-related options.
### `pool-size`

The `pool-size` option determines the number of threads in the DM Load unit. The default value is 16. Normally, you do not need to set this option. If you set it, adjust the value of this option according to the size of the full data and the performance of the database.

> **Note:**
>
> - You cannot update the value of `loaders` after the migration task is created. Be sure about the value of each option before creating the task. If you need to update the value, stop the task using dmctl, update the configuration file, and re-create the task.
> - `loaders`.`pool-size` can be replaced with the `loader-thread` configuration item for simplicity.
## Incremental data replication

`syncers` is the configuration item related to incremental data replication. This section describes how to configure performance-related options.
### `worker-count`

`worker-count` determines the number of threads for concurrent replication of DMLs in the DM Sync unit. The default value is 16. To speed up data replication, increase the value of this option appropriately.
### `batch`

`batch` determines the number of DMLs included in each transaction when the data is replicated to the downstream database during the DM Sync unit. The default value is 100. Normally, you do not need to change the value of this option.

> **Note:**
>
> - You cannot update the value of `syncers` after the replication task is created. Be sure about the value of each option before creating the task. If you need to update the value, stop the task using dmctl, update the configuration file, and re-create the task.
> - `syncers`.`worker-count` can be replaced with the `syncer-thread` configuration item for simplicity.
> - You can change the values of `worker-count` and `batch` according to the actual scenario. For example, if there is a high network delay between DM and the downstream database, you can increase the value of `worker-count` and decrease the value of `batch` appropriately.
