# TiFlash disaggregated architecture requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/hardware-and-software-requirements.md`
- Source Title: `Software and Hardware Recommendations`
- Source Heading Path: `Software and Hardware Recommendations > Hardware and software requirements for TiFlash disaggregated storage and compute architecture | Software and Hardware Recommendations > Hardware and software requirements for TiFlash disaggregated storage and compute architecture > Development and test environments | Software and Hardware Recommendations > Hardware and software requirements for TiFlash disaggregated storage and compute architecture > Production environment`
- Source Line Ranges: `301-328`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `shared`, `tiup`
- Topic Tags: `disaggregated-architecture`, `write-node`, `compute-node`, `hardware-requirements`, `disk-space`, `cpu`, `memory`, `network`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0369_28827db47f`
- Source ID: `tidb-docs-8.1:hardware-and-software-requirements.md#hardware-and-software-requirements-for-tiflash-disaggregated-storage-and-compute-architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `412a588c238d97a60a7b1091c4f9246e36b71ac8cfc8b0829b32d6bda195193c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements#hardware-and-software-requirements-for-tiflash-disaggregated-storage-and-compute-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/hardware-and-software-requirements.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving hardware, disk, network, and scaling requirements for TiFlash disaggregated storage and compute architecture, including Write Node and Compute Node specifications.
- Retrieval Keywords: TiFlash disaggregated storage and compute architecture, Write Node, Compute Node, starting from v7.0.0, OS and platform requirements, Network requirements, TiFlash Write Node at least 200 GB of disk space, local buffer before uploading data to Amazon S3, object storage compatible with Amazon S3, TiFlash Compute Node at least 100 GB of disk space, cache the data read from the Write Node, Development and test environments, TiFlash Write Node 16 cores+ 32 GB+ SSD 200 GB+ Gigabit Ethernet, TiFlash Compute Node 16 cores+ 32 GB+ SSD 100 GB+ Gigabit Ethernet, Production environment, TiFlash Write Node 32 cores+ 64 GB+ 1 or more SSDs 10 Gigabit Ethernet, TiFlash Compute Node 32 cores+ 64 GB+ 1 or more SSDs 10 Gigabit Ethernet, Number of Instances minimum requirement 0, TiUP scale in or out the TiFlash Compute Node, range of [0, +inf]
- Follow-up Guidance: The note says deployment tools such as TiUP can quickly scale in or out the TiFlash Compute Node within the range of [0, +inf].
- Classification Note: This is classified as reference content because it lists environment-specific hardware and software requirements and instance counts for TiFlash disaggregated Write Node and Compute Node deployments.

## Official Source Content

## Hardware and software requirements for TiFlash disaggregated storage and compute architecture

The preceding TiFlash software and hardware requirements are for the coupled storage and compute architecture. Starting from v7.0.0, TiFlash supports the [disaggregated storage and compute architecture](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3). In this architecture, TiFlash is divided into two types of nodes: the Write Node and the Compute Node. The requirements for these nodes are as follows:

- Software: remain the same as the coupled storage and compute architecture, see [OS and platform requirements](#os-and-platform-requirements).
- Network port: remain the same as the coupled storage and compute architecture, see [Network](#network-requirements).
- Disk space:
    - TiFlash Write Node: it is recommended to configure at least 200 GB of disk space, which is used as a local buffer when adding TiFlash replicas and migrating Region replicas before uploading data to Amazon S3. In addition, an object storage compatible with Amazon S3 is required.
    - TiFlash Compute Node: it is recommended to configure at least 100 GB of disk space, which is mainly used to cache the data read from the Write Node to improve performance. The cache of the Compute Node might be fully used, which is normal.
- CPU and memory requirements are described in the following sections.
### Development and test environments

| Component | CPU | Memory | Local Storage | Network | Number of Instances (Minimum Requirement) |
| --- | --- | --- | --- | --- | --- |
| TiFlash Write Node | 16 cores+ | 32 GB+ | SSD, 200 GB+ | Gigabit Ethernet | 1 |
| TiFlash Compute Node | 16 cores+ | 32 GB+ | SSD, 100 GB+ | Gigabit Ethernet | 0 (see the following note) |
### Production environment

| Component | CPU | Memory | Disk Type | Network | Number of Instances (Minimum Requirement) |
| --- | --- | --- | --- | --- | --- |
| TiFlash Write Node | 32 cores+ | 64 GB+ | 1 or more SSDs | 10 Gigabit Ethernet (2 recommended) | 1 |
| TiFlash Compute Node | 32 cores+ | 64 GB+ | 1 or more SSDs | 10 Gigabit Ethernet (2 recommended) | 0 (see the following note) |

> **Note:**
>
> You can use deployment tools such as TiUP to quickly scale in or out the TiFlash Compute Node, within the range of `[0, +inf]`.
