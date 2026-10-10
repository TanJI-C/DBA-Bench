# TiFlash disaggregated architecture overview and scenarios

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-disaggregated-and-s3.md`
- Source Title: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support`
- Source Heading Path: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support | TiFlash Disaggregated Storage and Compute Architecture and S3 Support > Architecture overview | TiFlash Disaggregated Storage and Compute Architecture and S3 Support > Scenarios`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `disaggregated-storage`, `disaggregated-compute`, `s3`, `object-storage`, `write-node`, `compute-node`, `scaling`, `cache`, `cold-data`, `query-workload`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0110_2c2c54957c`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-disaggregated-and-s3.md#tiflash-disaggregated-storage-and-compute-architecture-and-s3-support`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f9343a1d2d876f1e608edd97474692cc25616aeeb944c66ff30fa580d5fedef0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3#tiflash-disaggregated-storage-and-compute-architecture-and-s3-support
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-disaggregated-and-s3.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for an overview of TiFlash disaggregated storage and compute architecture, the roles of Write Node and Compute Node, or when S3 or S3-compatible object storage is involved in TiFlash query workloads.
- Retrieval Keywords: TiFlash disaggregated storage and compute architecture, Write Node, Compute Node, Amazon S3, S3-compatible object storage, MinIO, coupled storage and compute architecture, local SSD cache, NVMe SSDs, cold data, scale independently, stop all Compute Nodes, query workload peaks and valleys
- Follow-up Guidance: The source also describes cost-effective scenarios such as large amounts of cold data and workloads with obvious compute peaks and valleys.
- Classification Note: This chunk is classified as architecture because it explains the disaggregated TiFlash design, node roles, data flow, caching, scaling behavior, and suitable scenarios.

## Official Source Content

# TiFlash Disaggregated Storage and Compute Architecture and S3 Support

By default, TiFlash is deployed using the coupled storage and compute architecture, in which each TiFlash node acts as both storage and compute node. Starting from TiDB v7.0.0, TiFlash supports the disaggregated storage and compute architecture and allows to store data in Amazon S3 or S3-compatible object storage (such as MinIO).
## Architecture overview

![TiFlash Write and Compute Separation Architecture](/media/tiflash/tiflash-s3.png)

In the disaggregated storage and compute architecture, different functionalities of the TiFlash process are divided and allocated to two types of nodes: the Write Node and the Compute Node. These two types of nodes can be deployed separately and scaled independently, which means that you can decide the number of Write Nodes and Compute Nodes to be deployed as needed.

- TiFlash Write Node

    The Write Node receives Raft logs data from TiKV, converts the data into the columnar format, and periodically packages and uploads all the updated data within a certain period to S3. In addition, the Write Node manages the data on S3, such as continuously organizing data to improve query performance and deleting useless data.

    The Write Node uses local disks (usually NVMe SSDs) to cache the latest written data to avoid excessive use of memory.

- TiFlash Compute Node

    The Compute Node executes query requests sent from a TiDB node. It first accesses a Write Node to obtain data snapshots, and then reads the latest data (that is, the data not been uploaded to S3 yet) from the Write Node and most of the remaining data from S3.

    The Compute Node uses local disks (usually NVMe SSDs) as a cache for data files to avoid repeatedly reading the same data from remote locations (Write Nodes or S3) and improve query performance.

    The Compute Node is stateless and its scaling speed is at a second level. You can use this feature to reduce costs as follows:

    - When the query workload is low, reduce the number of Compute Nodes to save costs. When there are no queries, you can even stop all Compute Nodes.
    - When the query workload increases, quickly increase the number of Compute Nodes to ensure query performance.
## Scenarios

TiFlash disaggregated storage and compute architecture is suitable for cost-effective data analysis services. Because storage and compute resources can be scaled separately as needed in this architecture, you can get significant benefits in the following scenarios:

- The amount of data is large, but only a small amount of data is frequently queried. Most of the data is cold data and rarely queried. At this time, the frequently queried data is usually cached on the local SSD of the Compute Node to provide fast query performance, while most of the other cold data is stored in low-cost S3 or other object storage to save storage costs.

- The demand for compute resources has obvious peaks and valleys. For example, intensive reconciliation queries are usually performed at night, which demands high compute resources. In this case, you can consider temporarily adding more Compute Nodes at night. While at other times, you only need fewer Compute Nodes to complete regular query tasks.
