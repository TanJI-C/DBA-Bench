# TiDB Binlog deployment overview, hardware, and package acquisition

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/deploy-tidb-binlog.md`
- Source Title: `TiDB Binlog Cluster Deployment`
- Source Heading Path: `TiDB Binlog Cluster Deployment | TiDB Binlog Cluster Deployment > Hardware requirements | TiDB Binlog Cluster Deployment > Deploy TiDB Binlog using TiUP | TiDB Binlog Cluster Deployment > Deploy TiDB Binlog using a binary package | TiDB Binlog Cluster Deployment > Deploy TiDB Binlog using a binary package > Download the official binary package`
- Source Line Ranges: `5-30`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tiup`, `ecosystem`
- Topic Tags: `deployment`, `hardware-requirements`, `binary-package`, `tiup`, `pump`, `drainer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0268_1ef9c1e434`
- Source ID: `tidb-docs-8.1:tidb-binlog/deploy-tidb-binlog.md#tidb-binlog-cluster-deployment`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `25d9aa7a5983f2bb70728c74a2ab114cc0c44526b7abe514bd661258bd7a72f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/deploy-tidb-binlog#tidb-binlog-cluster-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/deploy-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Binlog deployment overview information, including hardware requirements for Pump and Drainer, TiUP deployment references, or where to download the binary package from TiDB Toolkit.
- Retrieval Keywords: TiDB Binlog Cluster Deployment, Hardware requirements, Pump, Drainer, 64-bit universal hardware server platforms, Intel x86-64 architecture, Pump 3 8 core+ SSD 200 GB+ 16G, Drainer 1 8 core+ SAS 100 GB+ 16G, Deploy TiDB Binlog using TiUP, TiDB Binlog Deployment Topology, Deploy a TiDB Cluster Using TiUP, Deploy TiDB Binlog using a binary package, Download the official binary package, TiDB Toolkit, Download TiDB Tools
- Follow-up Guidance: The source points to TiDB Binlog Deployment Topology, Deploy a TiDB Cluster Using TiUP, and Download TiDB Tools for detailed topology, deployment, and package download information.
- Classification Note: This is classified as an operation chunk because the content describes deployment methods, hardware requirements, and package acquisition for self-managed TiDB Binlog.

## Official Source Content

# TiDB Binlog Cluster Deployment

This document describes how to [deploy TiDB Binlog using a Binary package](#deploy-tidb-binlog-using-a-binary-package).
## Hardware requirements

Pump and Drainer are deployed and operate on 64-bit universal hardware server platforms with Intel x86-64 architecture.

In environments of development, testing and production, the requirements on server hardware are as follows:

| Service     | The Number of Servers       | CPU   | Disk          | Memory   |
| :-------- | :-------- | :-------- | :--------------- | :------ |
| Pump | 3 | 8 core+    | SSD, 200 GB+ | 16G |
| Drainer | 1 | 8 core+ | SAS, 100 GB+ (If binlogs are output as local files, the disk size depends on how long these files are retained.) | 16G |
## Deploy TiDB Binlog using TiUP

It is recommended to deploy TiDB Binlog using TiUP. To do that, when deploying TiDB using TiUP, you need to add the node information of `drainer` and `pump` of TiDB Binlog in [TiDB Binlog Deployment Topology](https://docs.pingcap.com/tidb/stable/tidb-binlog-deployment-topology). For detailed deployment information, refer to [Deploy a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).
## Deploy TiDB Binlog using a binary package
### Download the official binary package

The binary package of TiDB Binlog is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).
