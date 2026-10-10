# Parallel import overview, considerations, performance, and restrictions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-distributed-import.md`
- Source Title: `Use TiDB Lightning to Import Data in Parallel`
- Source Heading Path: `Use TiDB Lightning to Import Data in Parallel | Use TiDB Lightning to Import Data in Parallel > Considerations | Use TiDB Lightning to Import Data in Parallel > Considerations > Handle conflicts between primary keys or unique indexes | Use TiDB Lightning to Import Data in Parallel > Considerations > Optimize import performance | Use TiDB Lightning to Import Data in Parallel > Considerations > Restrictions`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `parallel-import`, `physical-import`, `metadata-registration`, `primary-key-conflicts`, `unique-index-conflicts`, `performance-tuning`, `resource-isolation`, `checkpoints`, `log-paths`, `status-address`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0454_8dfd5d03ca`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-distributed-import.md#use-tidb-lightning-to-import-data-in-parallel`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `74e163edf7f32510ec85cec2c4f758e55f5b155bfbb91ca291ec6c5a1668c026`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import#use-tidb-lightning-to-import-data-in-parallel
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-distributed-import.md

## Retrieval Guidance

- Use When: Use this content when looking for how TiDB Lightning parallel import works in physical import mode, its prerequisites, performance considerations, and multi-instance restrictions.
- Retrieval Keywords: parallel import, physical import mode, parallel-import = true, metadata registration, Row ID allocation range, global Checksum, primary key conflicts, unique index conflicts, empty tables, Apply only one backend at a time, optimize import performance, number of TiKV instances, number of TiDB Lightning instances, tikv-importer.sorted-kv-dir, checkpoint.driver = "file", checkpoint.driver = "mysql", lightning.status-addr, Web Interface, Debug API
- Follow-up Guidance: The document next provides Example 1 for Dumpling plus TiDB Lightning on sharded databases and tables and Example 2 for importing single tables in parallel.
- Classification Note: This chunk is classified as an operation topic because the official content describes considerations, restrictions, and runtime resource requirements for running multiple TiDB Lightning instances in parallel.

## Official Source Content

# Use TiDB Lightning to Import Data in Parallel

Since v5.3.0, the [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) of TiDB Lightning supports the parallel import of a single table or multiple tables. By simultaneously running multiple TiDB Lightning instances, you can import data from single or multiple tables in parallel. In this way, TiDB Lightning provides the ability to scale horizontally, which greatly reduces the time required to import large amount of data.

In technical implementation, TiDB Lightning records the meta data of each instance and the data of each imported table in the target TiDB, and coordinates the Row ID allocation range of different instances, the record of global Checksum, and the configuration changes and recovery of TiKV and PD.

You can use TiDB Lightning to import data in parallel in the following scenarios:

- Import sharded schemas and sharded tables. In this scenario, multiple tables from multiple upstream database instances are imported into the downstream TiDB database by different TiDB Lightning instances in parallel.
- Import single tables in parallel. In this scenario, single tables stored in a certain directory or cloud storage (such as Amazon S3) are imported into the downstream TiDB cluster by different TiDB Lightning instances in parallel. This is a new feature introduced in TiDB 5.3.0.

> **Note:**
>
> - Parallel import only supports initialized empty tables in TiDB and does not support migrating data to tables with data written by existing services. Otherwise, data inconsistencies may occur.
>
> - Parallel import is usually used in the physical import mode. You need to configure `parallel-import = true`.
>
> - Apply only one backend at a time when using multiple TiDB Lightning instances to import data to the same target. For example, you cannot import data to the same TiDB cluster in both the physical and logical import modes at the same time.
## Considerations

To use parallel import, you need to configure `parallel-import = true`. When TiDB Lightning is started, it registers meta data in the downstream TiDB cluster and automatically detects whether there are other instances migrating data to the target cluster at the same time. If there is, it automatically enters the parallel import mode.

But when migrating data in parallel, you need to take the following into consideration:

- Handle conflicts between primary keys or unique indexes across multiple sharded tables
- Optimize import performance
### Handle conflicts between primary keys or unique indexes

When using [the physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) to import data in parallel, ensure that there are no primary key or unique index conflicts between data sources, and between the tables in the target TiDB cluster, and there are no data writes in the target table during import. Otherwise, TiDB Lightning will fail to guarantee the correctness of the imported data, and the target table will contain inconsistent indexes after the import is completed.
### Optimize import performance

Because TiDB Lightning needs to upload the generated Key-Value data to the TiKV node where each copy of the corresponding Region is located, the import speed is limited by the size of the target cluster. It is recommended to ensure that the number of TiKV instances in the target TiDB cluster and the number of TiDB Lightning instances are greater than n:1 (n is the number of copies of the Region). At the same time, the following requirements should be met to achieve optimal import performance:

- Deploy each TiDB Lightning instance on a dedicated machine. Since one TiDB Lightning instance consumes all CPU resources by default, deploying multiple instances on a single machine cannot improve performance.
- The total size of source files for each TiDB Lightning instance performing parallel import should be smaller than 5 TiB
- The total number of TiDB Lightning instances should be smaller than 10.

When using TiDB Lightning to import shared databases and tables in parallel, choose an appropriate number of TiDB Lightning instances according to the amount of data.

- If the MySQL data volume is less than 2 TiB, you can use one TiDB Lightning instance for parallel import.
- If the MySQL data volume exceeds 2 TiB and the total number of MySQL instances is smaller than 10, it is recommended that you use one TiDB Lightning instance for each MySQL instance, and the number of parallel TiDB Lightning instances should not exceed 10.
- If the MySQL data volume exceeds 2 TiB and the total number of MySQL instances exceeds 10, it is recommended that you allocate 5 to 10 TiDB Lightning instances for importing the data exported by these MySQL instances.

Next, this document uses two examples to detail the operation steps of parallel import in different scenarios:

- Example 1: Use Dumpling + TiDB Lightning to import sharded databases and tables into TiDB in parallel
- Example 2: Import single tables in parallel
### Restrictions

TiDB Lightning exclusively uses some resources when it is running. If you need to deploy multiple TiDB Lightning instances on a single machine (which is not recommended for production environments), or on a disk shared by multiple machines, be aware of the following usage restrictions.

- Set `tikv-importer.sorted-kv-dir` to a unique path for each TiDB Lightning instance. Multiple instances sharing the same path can lead to unintended behavior and may result in import failures or data errors.
- Store each TiDB Lightning checkpoint separately. For more information about checkpoint configurations, see [TiDB Lightning Checkpoints](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints).
    - If you set checkpoint.driver = "file" (default), make sure that the path to the checkpoint is unique for each instance.
    - If you set checkpoint.driver = "mysql", you need to set a unique schema for each instance.
- The log file for each TiDB Lightning should be set to a unique path. Sharing the same log file will impact log querying and troubleshooting.
- If you use the [Web Interface](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface) or Debug API, you need to set `lightning.status-addr` to a unique address for each instance; otherwise, the TiDB Lightning process fails to start due to port conflict.
