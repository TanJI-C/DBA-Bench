# Large-scale TiDB Lightning import best practices and tuning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/data-import-best-practices.md`
- Source Title: `Best Practices for Importing 50 TiB Data`
- Source Heading Path: `Best Practices for Importing 50 TiB Data | Best Practices for Importing 50 TiB Data > Key factors | Best Practices for Importing 50 TiB Data > Prepare source files | Best Practices for Importing 50 TiB Data > Estimate storage space | Best Practices for Importing 50 TiB Data > Change configuration parameters | Best Practices for Importing 50 TiB Data > Resolve the "checksum mismatch" error | Best Practices for Importing 50 TiB Data > Enable checkpoint`
- Source Line Ranges: `5-113`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`, `pd`, `shared`
- Topic Tags: `large-scale-import`, `physical-import-mode`, `parallel-import`, `source-files`, `primary-key-ordering`, `storage-estimation`, `configuration-tuning`, `checksum-validation`, `conflict-detection`, `checkpoints`, `oom-prevention`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0237_948e1a5635`
- Source ID: `tidb-docs-8.1:tidb-lightning/data-import-best-practices.md#best-practices-for-importing-50-tib-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a4ef750c46900d01df3048290cd8b6246678fa79a5b3f9bb0dfe2c9d8cf7c6d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/data-import-best-practices#best-practices-for-importing-50-tib-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/data-import-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for official best practices and tuning factors for large-scale TiDB Lightning physical import mode, including source file preparation, storage estimation, configuration parameters, checksum mismatch handling, and checkpoints for imports up to and beyond 50 TiB.
- Retrieval Keywords: TiDB Lightning, Physical Import Mode, parallel import, Best Practices for Importing 50 TiB Data, large single table, source files, primary key sorted, overlapping primary keys, non-null unique indexes, secondary indexes, compression ratio, region-concurrency, send-kv-pairs, send-kv-size, disk-quota, GOMEMLIMIT, ADMIN CHECKSUM, ANALYZE TABLE, checksum mismatch, conflict detection, checkpoint, Lightning Checkpoints, strict-format, 96 MiB, 256 MiB, storage space estimation, (A+B)*3/α, reserve 20% of storage space, kill command without -9
- Follow-up Guidance: If more detail is needed, follow up with the linked topics for TiDB Lightning physical import mode, distributed import, configuration parameters, conflict detection, and Lightning Checkpoints mentioned in the content.
- Classification Note: This chunk is classified as performance for the lightning component because the official content centers on import efficiency, scalability, resource tuning, and failure avoidance during large-scale TiDB Lightning data import.

## Official Source Content

# Best Practices for Importing 50 TiB Data

This document provides best practices for importing large volumes of data into TiDB, including some key factors and steps that affect data import. We have successfully imported data of a large single table over 50 TiB into both the internal environment and customer's environment, and have accumulated best practices based on these real application scenarios, which can help you import data more smoothly and efficiently.

TiDB Lightning ([Physical Import Mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode)) is a comprehensive and efficient data import tool used for importing data into empty tables and initializing empty clusters, and uses files as the data source. TiDB Lightning provides two running modes: a single instance and [parallel import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import). You can import source files of different sizes.

- If the data size of the source files is within 10 TiB, it is recommended to use a single instance of TiDB Lightning for the import.
- If the data size of the source files exceeds 10 TiB, it is recommended to use multiple instances of TiDB Lightning for [Parallel Import](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import).
- If the source file data scale is exceptionally large (larger than 50 TiB), in addition to parallel importing, you need to make certain preparations and optimizations based on the characteristics of the source data, table definitions, and parameter configurations to achieve smoother and faster large-scale data import.

The following sections apply to both importing multiple tables and importing large single tables:

- [Key factors](#key-factors)
- [Prepare source files](#prepare-source-files)
- [Estimate storage space](#estimate-storage-space)
- [Change configuration parameters](#change-configuration-parameters)
- [Resolve the "checksum mismatch" error](#resolve-the-checksum-mismatch-error)
- [Enable checkpoint](#enable-checkpoint)
- [Troubleshooting](#troubleshooting)

The best practices for importing large single tables are described separately in the following section because of its special requirements:

- [Best practices for importing a large single table](#best-practices-for-importing-a-large-single-table)
## Key factors

When you import data, some key factors can affect import performance and might even cause import to fail. Some common critical factors are as follows:

- Source files

    - Whether the data within a single file is sorted by the primary key. Sorted data can achieve optimal import performance.
    - Whether overlapping primary keys or non-null unique indexes exist between source files imported by multiple TiDB Lightning instances. The smaller the overlap is, the better the import performance.

- Table definitions

    - The number and size of secondary indexes per table can affect the import speed. Fewer indexes result in faster imports and less space consumption after import.
    - Index data size = Number of indexes \* Index size \* Number of rows.

- Compression ratio

    - Data imported into a TiDB cluster is stored in a compressed format. The compression ratio cannot be calculated in advance. It can only be determined after the data is actually imported into the TiKV cluster.
    - As a best practice, you can first import a small portion of the data (for example, 10%) to obtain the corresponding compression ratio of the cluster, and then use it to estimate the compression ratio of the entire data import.

- Configuration parameters

    - `region-concurrency`: The concurrency of TiDB Lightning main logical processing.
    - `send-kv-pairs`: The number of Key-Value pairs sent by TiDB Lightning to TiKV in a single request.
    - `disk-quota`: The disk quota used by TiDB Lightning local temp files when using the physical import mode.
    - `GOMEMLIMIT`: TiDB Lightning is implemented in the Go language. [Configure `GOMEMLIMIT` properly.](#change-configuration-parameters)

- Data validation

    After data and index import is completed, the [`ADMIN CHECKSUM`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table) statement is executed on each table, and the checksum value is compared with the local checksum value of TiDB Lightning. When many tables exist, or an individual table has a large number of rows, the checksum phase can take a long time.

- The analyze operation

    After the checksum is successfully completed, the [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement is executed on each table to generate the optimal execution plan. The analyze operation can be time-consuming when dealing with a large number of tables or an individual table with a significant amount of data.

- Relevant issues

    During the actual process of importing 50 TiB of data, certain issues might occur that are only exposed when dealing with a massive number of source files and large-scale clusters. When choosing a product version, it is recommended to check whether the corresponding issues have been fixed.

    The following issues have been resolved in v6.5.3, v7.1.0, and later versions:

    - [Issue-14745](https://github.com/tikv/tikv/issues/14745): After the import is completed, a large number of temporary files are left in the TiKV import directory.
    - [Issue-6426](https://github.com/tikv/pd/issues/6426): The PD [range scheduling](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#scope-of-pausing-scheduling-during-import) interface might fail to scatter regions, resulting in timeout issues. Before v6.2.0, global scheduling is disabled by default, which can avoid triggering this problem.
    - [Issue-43079](https://github.com/pingcap/tidb/pull/43079): TiDB Lightning fails to refresh the Region Peers information during retry for NotLeader errors.
    - [Issue-43291](https://github.com/pingcap/tidb/issues/43291): TiDB Lightning does not retry in cases where temporary files are not found (the "No such file or directory" error).
## Prepare source files

- When generating source files, it is preferable to sort them by the primary key within a single file. If the table definition does not have a primary key, you can add an auto-increment primary key. In this case, the order of the file content does not matter.
- When assigning source files to multiple TiDB Lightning instances, try to avoid the situation where overlapping primary keys or non-null unique indexes exist between multiple source files. If the generated files are globally sorted, they can be distributed into different TiDB Lightning instances based on ranges to achieve optimal import performance.
- Control each file to be less than 96 MiB in size during file generation.
- If a file is exceptionally large and exceeds 256 MiB, enable [`strict-format`](https://docs.pingcap.com/tidb/stable/migrate-from-csv-files-to-tidb#step-4-tune-the-import-performance-optional).
## Estimate storage space

You can use either of the following two methods to estimate the storage space required for importing data:

- Assuming the total data size is **A**, the total index size is **B**, the replication factor is **3**, and the compression ratio is **α** (typically around 2.5), the overall occupied space can be calculated as: **(A+B)\*3/α**. This method is primarily used for estimating without performing any data import, to plan the cluster topology.
- Import only 10% of the data and multiply the actual occupied space by 10 to estimate the final space usage for that batch of data. This method is more accurate, especially when you import a large amount of data.

Note that it is recommended to reserve 20% of storage space, because background tasks such as compaction and snapshot replication also consume a portion of the storage space.
## Change configuration parameters

- `region-concurrency`: The concurrency of TiDB Lightning main logical processing. During parallel importing, it is recommended to set it to 75% of the CPU cores to prevent resource overload and potential OOM issues.
- `send-kv-pairs`: The number of Key-Value pairs sent by TiDB Lightning to TiKV in a single request. It is recommended to adjust this value based on the formula send-kv-pairs \* row-size < 1 MiB. Starting from v7.2.0, this parameter is replaced by `send-kv-size`, and no additional setting is required.
- `disk-quota`: It is recommended to ensure that the sorting directory space of TiDB Lightning is larger than the size of the data source. If you cannot ensure that, you can set `disk-quota` to 80% of the sorting directory space of TiDB Lightning. In this way, TiDB Lightning will sort and write data in batches according to the specified `disk-quota`, but note that this approach might result in lower import performance compared to a complete sorting process.
- `GOMEMLIMIT`: TiDB Lightning is implemented in the Go language. Setting `GOMEMLIMIT` to 80% of the instance memory to reduce the probability of OOM caused by the Go GC mechanism.

For more information about TiDB Lightning parameters, see [TiDB Lightning configuration parameters](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
## Resolve the "checksum mismatch" error

Conflicts might occur during data validation. The error message is "checksum mismatch". To resolve this issue, take the following steps as needed:

1. In the source data, check for conflicted primary keys or unique keys, and resolve the conflicts before reimporting. In most cases, this is the most common cause.
2. Check if the table primary key or unique key definition is reasonable. If not, modify the table definition and reimport data.
3. If the issue persists after following the preceding two steps, further examination is required to determine whether a small amount (less than 10%) of unexpected conflicting data exists in the source data. To let TiDB Lightning detect and resolve conflicting data, enable [conflict detection](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#conflict-detection).
## Enable checkpoint

For importing a large volume of data, it is essential to refer to [Lightning Checkpoints](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints) and enable checkpoints. It is recommended to prioritize using MySQL as the driver to avoid losing the checkpoint information if TiDB Lightning is running in a container environment where the container might exit and delete the checkpoint information.

If you encounter insufficient space in downstream TiKV during import, you can manually run the `kill` command (without the `-9` option) on all TiDB Lightning instances. After scaling up the capacity, you can resume the import based on the checkpoint information.
