# Global Sort overview, use cases, and limitations

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-global-sort.md`
- Source Title: `TiDB Global Sort`
- Source Heading Path: `TiDB Global Sort | TiDB Global Sort > Overview | TiDB Global Sort > Use cases | TiDB Global Sort > Limitations`
- Source Line Ranges: `5-35`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`, `cloud`
- Topic Tags: `global-sort`, `dxf`, `s3`, `resource-recommendations`, `import-into`, `create-index`, `limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0097_8118d8d8f0`
- Source ID: `tidb-docs-8.1:tidb-global-sort.md#tidb-global-sort`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `616ffa46e0d4a423707c583e205c56b6785a3866660c13539a33253e46f9a262`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-global-sort#tidb-global-sort
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-global-sort.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks what TiDB Global Sort is, which operations it supports, its cloud storage support, or its stated limitations and resource notes.
- Retrieval Keywords: TiDB Global Sort, Distributed eXecution Framework, DXF, IMPORT INTO, CREATE INDEX, Amazon S3, global sort service on cloud, tidb_service_scope, ADD INDEX, resource recommendations, 16 cores of CPU, 32 GiB of memory, Starter, Essential, not used as a component of the query execution process
- Follow-up Guidance: The source also notes workload isolation by adding new TiDB nodes, configuring tidb_service_scope, and connecting to these nodes to create tasks for backend tasks such as ADD INDEX and IMPORT INTO.
- Classification Note: This chunk is classified as architecture because it describes the Global Sort feature overview, supported use cases in DXF, cloud storage support, and feature limitations.

## Official Source Content

# TiDB Global Sort

> **Note:**
>
> - Currently, the Global Sort process consumes a large amount of computing and memory resources of TiDB nodes. In scenarios such as adding indexes online while user business applications are running, it is recommended to add new TiDB nodes to the cluster, configure the [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) variable for these nodes, and connect to these nodes to create tasks. In this way, the distributed framework schedules tasks to these nodes, isolating the workload from other TiDB nodes to reduce the impact of executing backend tasks such as `ADD INDEX` and `IMPORT INTO` on user business applications.
> - When the Global Sort feature is used, it is recommended to use TiDB nodes with at least 16 cores of CPU and 32 GiB of memory to avoid OOM.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Overview

The TiDB Global Sort feature enhances the stability and efficiency of data import and DDL (Data Definition Language) operations. It serves as a general operator in the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework), providing a global sort service on cloud.

Currently, the Global Sort feature supports using Amazon S3 as cloud storage.
## Use cases

The Global Sort feature enhances the stability and efficiency of `IMPORT INTO` and `CREATE INDEX`. By globally sorting the data that are processed by the tasks, it improves the stability, controllability, and scalability of writing data to TiKV. This provides an enhanced user experience for data import and DDL tasks, as well as higher-quality services.

The Global Sort feature executes tasks within the unified DXF, ensuring efficient and parallel sorting of data on a global scale.
## Limitations

Currently, the Global Sort feature is not used as a component of the query execution process responsible for sorting query results.
