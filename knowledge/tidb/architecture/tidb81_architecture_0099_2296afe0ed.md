# Comparison overview: deployment, resources, configuration, and scheduling

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/import-into-vs-tidb-lightning.md`
- Source Title: `IMPORT INTO vs. TiDB Lightning`
- Source Heading Path: `IMPORT INTO vs. TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Deployment cost | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Deployment cost > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Deployment cost > TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Resource utilization | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Resource utilization > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Resource utilization > TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Task configuration and integration | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Task configuration and integration > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Task configuration and integration > TiDB Lightning | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Task scheduling | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Task scheduling > `IMPORT INTO` | IMPORT INTO vs. TiDB Lightning > Comparison between `IMPORT INTO` and TiDB Lightning > Task scheduling > TiDB Lightning`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `sql`, `tidb`
- Topic Tags: `comparison`, `deployment`, `resource-utilization`, `task-configuration`, `integration`, `distributed-execution`, `task-scheduling`, `global-sort`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0099_2296afe0ed`
- Source ID: `tidb-docs-8.1:tidb-lightning/import-into-vs-tidb-lightning.md#import-into-vs-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0fcf0a245952482d6df37035b2420f68b4cfaebe4df0f23262cb45cec8326987`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/import-into-vs-tidb-lightning#import-into-vs-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/import-into-vs-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when comparing `IMPORT INTO` and TiDB Lightning for deployment cost, resource utilization, task configuration, SQL integration, distributed execution, or task scheduling complexity.
- Retrieval Keywords: IMPORT INTO vs. TiDB Lightning, deployment cost, resource utilization, task configuration and integration, task scheduling, distributed execution, separate server deployment, task configuration files, IMPORT INTO SQL statement, TiDB Global Sort, tidb_service_scope, automatic distributed task scheduling, Amazon S3
- Follow-up Guidance: It also explains that `IMPORT INTO` can automatically split an import task into multiple sub-tasks and schedule different TiDB nodes, while parallel TiDB Lightning requires multiple configuration files and shared metadata table configuration.
- Classification Note: The chunk is classified as architecture because the official content compares how `IMPORT INTO` and TiDB Lightning are deployed, integrated, and scheduled across TiDB nodes.

## Official Source Content

# IMPORT INTO vs. TiDB Lightning

Many users have provided feedback that the deployment, configuration, and maintenance of [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) are complex, especially in scenarios involving [parallel importing](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import) of large datasets.

Based on the feedback, TiDB has gradually integrated some functionalities of TiDB Lightning into the [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) SQL statement. You can directly import data by executing `IMPORT INTO`, thereby improving the efficiency of data import. In addition, `IMPORT INTO` supports some functionalities that TiDB Lightning does not, such as automatic distributed task scheduling and [TiDB Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort).

`IMPORT INTO` is introduced in v7.2.0 and becomes generally available (GA) in v7.5.0. It will continue to be improved and optimized in future versions. Once the `IMPORT INTO` capability can fully replace TiDB Lightning, TiDB Lightning will be deprecated. At that time, relevant notification will be provided in advance in TiDB Release Notes and documentation.
## Comparison between `IMPORT INTO` and TiDB Lightning

The following sections describe the differences between `IMPORT INTO` and TiDB Lightning in multiple dimensions.
### Deployment cost
#### `IMPORT INTO`

`IMPORT INTO` does not require separate deployment. You can run it directly on TiDB nodes, which eliminates additional deployment work.
#### TiDB Lightning

By contrast, TiDB Lightning requires [separate server deployment](https://docs.pingcap.com/tidb/stable/tidb-lightning/deploy-tidb-lightning).
### Resource utilization
#### `IMPORT INTO`

The `IMPORT INTO` task and other business workloads can share TiDB resources or utilize them at different times to fully leverage the TiDB resources. To ensure stable operation of business workloads while maintaining the performance and stability of the `IMPORT INTO` task, you can specify [specific TiDB nodes](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) dedicated to `IMPORT INTO` for data import.

When you use [TiDB Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort), there is no need to mount large local disks. TiDB Global Sort can use Amazon S3 as the storage. Once the import task is completed, the temporary data stored on Amazon S3 for global sorting will be automatically deleted to save storage costs.
#### TiDB Lightning

You need separate servers to deploy and run TiDB Lightning. When no import tasks are executed, these resources remain idle. The total idle time is even longer in scenarios where import tasks are executed periodically, resulting in a waste of resources.

If the dataset to be imported is large, you also need to prepare large local disks to sort the data to be imported.
### Task configuration and integration
#### `IMPORT INTO`

You can directly write SQL statements to submit import tasks, which are easy to call and integrate.
#### TiDB Lightning

By contrast, TiDB Lightning requires you to write [task configuration files](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration). These configuration files are complex and not easily called by third parties.
### Task scheduling
#### `IMPORT INTO`

`IMPORT INTO` supports distributed execution. For example, when you import 40 TiB of source data files into one target table, after submitting the SQL statement, TiDB will automatically split the import task into multiple sub-tasks and schedule different TiDB nodes to execute these sub-tasks.
#### TiDB Lightning

By contrast, the configuration for TiDB Lightning is complex, inefficient, and prone to errors.

Assume that you start 10 TiDB Lightning instances to import data in parallel, then you need to create 10 TiDB Lightning configuration files. In each file, you need to configure the range of source files to be read by the corresponding TiDB Lightning instance. For example, TiDB Lightning instance 1 reads the first 100 files, instance 2 reads the next 100 files, and so on.

In addition, you need to configure the shared metadata table and other configuration information for these 10 TiDB Lightning instances, which is complex.
