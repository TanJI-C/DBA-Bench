# Large single table import practices and troubleshooting

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/data-import-best-practices.md`
- Source Title: `Best Practices for Importing 50 TiB Data`
- Source Heading Path: `Best Practices for Importing 50 TiB Data > Best practices for importing a large single table | Best Practices for Importing 50 TiB Data > Best practices for importing a large single table > Generate source files | Best Practices for Importing 50 TiB Data > Best practices for importing a large single table > Plan cluster topology | Best Practices for Importing 50 TiB Data > Best practices for importing a large single table > Change configuration parameters | Best Practices for Importing 50 TiB Data > Best practices for importing a large single table > Disable the analyze operation | Best Practices for Importing 50 TiB Data > Troubleshooting`
- Source Line Ranges: `114-155`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `large-table-import`, `source-files`, `cluster-topology`, `configuration-tuning`, `scatter-region-latency`, `analyze`, `troubleshooting`, `checkpointing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0238_12a111decb`
- Source ID: `tidb-docs-8.1:tidb-lightning/data-import-best-practices.md#best-practices-for-importing-a-large-single-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0a9304fb394ba43d2b9786da1a0a9ca6e24e73cb06dc4dd7aff0414d873d591`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/data-import-best-practices#best-practices-for-importing-a-large-single-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/data-import-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for best practices and troubleshooting pointers for importing a large single table with TiDB Lightning, including source file layout, cluster sizing, parameter tuning, long PD Scatter Region latency, and analyze handling.
- Retrieval Keywords: large single table, table size exceeds 10 TiB, number of rows exceeds 1 billion, more than 50 columns, wide table, Prepare source files, standard CSV file, strict-format, 20 GiB, TiDB Lightning instances, process 5 TiB to 10 TiB of source data, one TiDB Lightning instance on each node, region-concurrency, send-kv-pairs, 3200, send-kv-size, GOMEMLIMIT, PD Scatter Region latency exceeds 30 minutes, I/O bottlenecks, raftstore.apply-pool-size, region-split-concurrency, analyze="off", ANALYZE TABLE, Troubleshoot TiDB Lightning
- Follow-up Guidance: If problems occur while using TiDB Lightning, the source points to Troubleshoot TiDB Lightning, and after import it mentions manually executing ANALYZE TABLE when analyze is disabled.
- Classification Note: This is classified as performance content because the official text focuses on import throughput and latency optimization for large single table loads in TiDB Lightning, including concurrency, memory, file generation, and scatter-region behavior.

## Official Source Content

## Best practices for importing a large single table

Importing multiple tables can increase the time required for checksum and analyze operations, sometimes exceeding the time required for data import itself. However, it is generally not necessary to adjust the configuration. If one or more large tables exist among the multiple tables, it is recommended to separate the source files of these large tables and import them separately.

This section provides the best practices for importing large single tables. There is no strict definition for a large single table, but it is generally considered to meet one of the following criteria:

- The table size exceeds 10 TiB.
- The number of rows exceeds 1 billion and the number of columns exceeds 50 in a wide table.
### Generate source files

Follow the steps outlined in the [Prepare source files](#prepare-source-files).

For a large single table, if global sorting is not achievable but sorting within each file based on the primary key is possible, and the file is a standard CSV file, it is recommended to generate large single files with each around 20 GiB.

Then, enable `strict-format`. This approach reduces the overlap of primary and unique keys in the imported files between TiDB Lightning instances, and TiDB Lightning instances can split the large files before importing to achieve optimal import performance.
### Plan cluster topology

Prepare TiDB Lightning instances to make each instance process 5 TiB to 10 TiB of source data. Deploy one TiDB Lightning instance on each node. For the specifications of the nodes, refer to the [environment requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#environment-requirements) of TiDB Lightning instances.
### Change configuration parameters

- Set `region-concurrency` to 75% of the number of cores of the TiDB Lightning instance.
- Set `send-kv-pairs` to `3200`. This method applies to TiDB v7.1.0 and earlier versions. Starting from v7.2.0, this parameter is replaced by `send-kv-size`, and no additional setting is required.
- Adjust `GOMEMLIMIT` to 80% of the memory on the node where the instance is located.

If the PD Scatter Region latency during the import process exceeds 30 minutes, consider the following optimizations:

- Check whether the TiKV cluster encounters any I/O bottlenecks.
- Increase TiKV `raftstore.apply-pool-size` from the default value of `2` to `4` or `8`.
- Reduce TiDB Lightning `region-split-concurrency` to half the number of CPU cores, with a minimum value of `1`.
### Disable the analyze operation

In the case of a large single table (for example, with over 1 billion rows and more than 50 columns), it is recommended to disable the `analyze` operation (`analyze="off"`) during the import process, and manually execute the [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement after the import is completed.

For more information about the configuration of `analyze`, see [TiDB Lightning task configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task).
## Troubleshooting

If you encounter problems while using TiDB Lightning, see [Troubleshoot TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/troubleshoot-tidb-lightning).
