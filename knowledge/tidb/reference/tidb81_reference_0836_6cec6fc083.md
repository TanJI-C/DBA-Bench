# TiFlash sizing, storage limits, and storage types

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/size-your-cluster.md`
- Source Title: `Determine Your TiDB Size`
- Source Heading Path: `Determine Your TiDB Size > Size TiFlash | Determine Your TiDB Size > Size TiFlash > TiFlash vCPU and RAM | Determine Your TiDB Size > Size TiFlash > TiFlash node count | Determine Your TiDB Size > Size TiFlash > TiFlash node storage | Determine Your TiDB Size > Size TiFlash > TiFlash node storage types | Determine Your TiDB Size > Size TiFlash > TiFlash node storage types > Basic storage | Determine Your TiDB Size > Size TiFlash > TiFlash node storage types > Plus storage`
- Source Line Ranges: `212-268`
- Source Scope: `cloud`
- Primary Component: `tiflash`
- Related Components: `tikv`, `cloud`
- Topic Tags: `cluster-sizing`, `vcpu`, `memory`, `node-count`, `replicas`, `availability-zones`, `storage`, `storage-types`, `aws`, `high-availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0836_6cec6fc083`
- Source ID: `tidb-docs-8.1:tidb-cloud/size-your-cluster.md#size-tiflash`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d5290a87299fe05439912ca07158f0dec481c7f867eabe27f4f2fb096a6b98d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#size-tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/size-your-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when sizing TiFlash or checking TiFlash node specifications, storage limits, replica-related node count, and storage type options for TiDB Cloud Dedicated on AWS.
- Retrieval Keywords: Size TiFlash, TiFlash vCPU and RAM, 8 vCPU 64 GiB, 16 vCPU 128 GiB, 32 vCPU 128 GiB, 32 vCPU 256 GiB, 4 vCPU 16 GiB, TiFlash unavailable, TiFlash node count, availability zones, replicas, Minimum number of TiFlash nodes, compressed size, TiFlash node storage, cannot decrease the TiFlash node storage after the cluster creation, Basic storage, Plus storage, TiDB Cloud Dedicated, AWS, Apply for TiFlash storage type
- Follow-up Guidance: The source also includes the minimum-node formula based on compressed table size, replica counts, and TiFlash capacity, plus an example calculation using 1024 GiB storage on AWS.
- Classification Note: This is reference content because it provides TiFlash sizing parameters, supported resource and storage ranges, a node-count formula, and storage type availability details.

## Official Source Content

## Size TiFlash

TiFlash synchronizes data from TiKV in real time and supports real-time analytics workloads right out of the box. It is horizontally scalable.

You can configure node count, vCPU and RAM, and storage for TiFlash.
### TiFlash vCPU and RAM

The supported vCPU and RAM sizes include the following:

- 8 vCPU, 64 GiB
- 16 vCPU, 128 GiB
- 32 vCPU, 128 GiB
- 32 vCPU, 256 GiB

Note that TiFlash is unavailable when the vCPU and RAM size of TiDB or TiKV is set as **4 vCPU, 16 GiB**.
### TiFlash node count

TiDB Cloud deploys TiFlash nodes evenly to different availability zones in a region. It is recommended that you configure at least two TiFlash nodes in each TiDB Cloud cluster and create at least two replicas of the data for high availability in your production environment.

The minimum number of TiFlash nodes depends on the TiFlash replica counts for specific tables:

Minimum number of TiFlash nodes: `min((compressed size of table A * replicas for table A + compressed size of table B * replicas for table B) / size of each TiFlash capacity, max(replicas for table A, replicas for table B))`

For example, if you configure the node storage of each TiFlash node on AWS as 1024 GiB, and set 2 replicas for table A (the compressed size is 800 GiB) and 1 replica for table B (the compressed size is 100 GiB), then the required number of TiFlash nodes is as follows:

Minimum number of TiFlash nodes: `min((800 GiB * 2 + 100 GiB * 1) / 1024 GiB, max(2, 1)) ≈ 2`
### TiFlash node storage

The supported node storage of different TiFlash vCPUs is as follows:

| TiFlash vCPU | Min node storage | Max node storage | Default node storage |
|:---------:|:----------------:|:----------------:|:--------------------:|
| 8 vCPU    | 200 GiB          | 4096 GiB         | 500 GiB              |
| 16 vCPU   | 200 GiB          | 4096 GiB         | 500 GiB              |
| 32 vCPU   | 200 GiB          | 8192 GiB         | 500 GiB              |

> **Note:**
>
> You cannot decrease the TiFlash node storage after the cluster creation.
### TiFlash node storage types

TiDB Cloud provides the following TiFlash storage types for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS:

- [Basic storage](#basic-storage-1)
- [Plus storage](#plus-storage)
#### Basic storage

The Basic storage is ideal for most workloads, providing a balance between performance and cost efficiency. 
#### Plus storage

The Plus storage provides higher performance and stability, with pricing that reflects these enhanced capabilities. Currently, this storage type is only available upon request for clusters deployed on AWS. To request it, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com) and click **Request Support**. Then, fill in "Apply for TiFlash storage type" in the **Description** field and click **Submit**.
