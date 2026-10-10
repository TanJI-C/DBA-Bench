# PD microservices overview, scenarios, and restrictions

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-microservices.md`
- Source Title: `PD Microservices`
- Source Heading Path: `PD Microservices | PD Microservices > Usage scenarios | PD Microservices > Restrictions`
- Source Line Ranges: `5-40`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`
- Topic Tags: `microservices`, `tso`, `scheduling`, `high-availability`, `performance-bottleneck`, `service-quality`, `limitations`, `compatibility`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0052_b3e4c0365c`
- Source ID: `tidb-docs-8.1:pd-microservices.md#pd-microservices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb7943f074d495a945dd7fa6f3f4ba22582a8139e5b95bcea330957671f5551c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-microservices#pd-microservices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-microservices.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what PD microservice mode splits out, when it is intended to help, and what restrictions or incompatibilities apply.
- Retrieval Keywords: PD Microservices, microservice mode, tso microservice, scheduling microservice, timestamp allocation, cluster scheduling, routing service for metadata, primary-secondary fault-tolerant mode, high availability, experimental, not recommended in production environments, performance bottlenecks in PD, long-tail latency, jitter in TSO allocations, service unavailability, update the scheduling microservice independently, tso microservice does not support dynamic start and stop, restart the PD cluster, TiDB component supports a direct connection to the tso microservice through service discovery, forward requests to the tso microservice through PD, DR Auto-Sync, tidb_enable_tso_follower_proxy, hibernate Regions, primary and secondary switchover, peer-stale-state-check-interval
- Follow-up Guidance: If the performance bottleneck of a cluster is not caused by PD, there is no need to enable microservices because they increase the number of components and raise operational costs.
- Classification Note: This is classified as architecture because the content defines the PD microservice split, the roles of the `tso` and `scheduling` services, and their stated usage scenarios and restrictions.

## Official Source Content

# PD Microservices

Starting from v8.0.0, PD supports the microservice mode, which splits the timestamp allocation and cluster scheduling functions of PD into the following two independently deployed microservices. In this way, these two functions are decoupled from the routing function of PD, which allows PD to focus on the routing service for metadata.

- `tso` microservice: provides monotonically increasing timestamp allocation for the entire cluster.
- `scheduling` microservice: provides scheduling functions for the entire cluster, including but not limited to load balancing, hot spot handling, replica repair, and replica placement.

Each microservice is deployed as an independent process. If you configure more than one replica for a microservice, the microservice automatically implements a primary-secondary fault-tolerant mode to ensure high availability and reliability of the service.

> **Warning:**
>
> Currently, the PD microservices feature is experimental. It is not recommended that you use it in production environments. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/tikv/pd/issues) on GitHub.
## Usage scenarios

PD microservices are typically used to address performance bottlenecks in PD and improve PD service quality. With this feature, you can avoid the following issues:

- Long-tail latency or jitter in TSO allocations due to excessive pressure in PD clusters
- Service unavailability of the entire cluster due to failures in the scheduling module
- Bottleneck issues solely caused by PD

In addition, when the scheduling module is changed, you can update the `scheduling` microservice independently without restarting PD, thus avoiding any impact on the overall service of the cluster.

> **Note:**
>
> If the performance bottleneck of a cluster is not caused by PD, there is no need to enable microservices, because using microservices increases the number of components and raises operational costs.
## Restrictions

- Currently, the `tso` microservice does not support dynamic start and stop. After enabling or disabling the `tso` microservice, you need to restart the PD cluster for the changes to take effect.
- Only the TiDB component supports a direct connection to the `tso` microservice through service discovery, while other components need to forward requests to the `tso` microservice through PD to obtain timestamps.
- Microservices are not compatible with the [Data Replication Auto Synchronous (DR Auto-Sync)](https://docs.pingcap.com/tidb/stable/two-data-centers-in-one-city-deployment) feature.
- Microservices are not compatible with the TiDB system variable [`tidb_enable_tso_follower_proxy`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tso_follower_proxy-new-in-v530).
- Because [hibernate Regions](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#hibernate-regions) might exist in a cluster, during a primary and secondary switchover of the `scheduling` microservice, the scheduling function of the cluster might be unavailable for a certain period (up to [`peer-stale-state-check-interval`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#peer-stale-state-check-interval), which is five minutes by default) to avoid redundant scheduling.
