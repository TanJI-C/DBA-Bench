# Primary-secondary DR overview and architecture

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters | DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC | DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Architecture`
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `tidb`, `tikv`, `pd`
- Topic Tags: `disaster-recovery`, `primary-secondary`, `architecture`, `high-availability`, `rpo`, `rto`, `regional-failure`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0032_bcd9d4488b`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#dr-solution-based-on-primary-and-secondary-clusters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b0ce594f1716db5a82c330f8f4ff079e44ee7736ffa224144b096db8be22029b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#dr-solution-based-on-primary-and-secondary-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the architecture, benefits, and availability characteristics of a TiCDC-based primary-secondary disaster recovery setup with a primary cluster and a secondary cluster.
- Retrieval Keywords: DR Solution Based on Primary and Secondary Clusters, Set up primary and secondary clusters based on TiCDC, Architecture, primary cluster, secondary cluster, TiCDC, regional failures, High availability, Fast switchover, Data consistency, RPO in seconds, RTO can be minutes or even lower, read and write requests, read-only business, Do not run multiple changefeeds
- Follow-up Guidance: The source also states that this document covers setting up the clusters, replicating data, monitoring the clusters, performing a DR switchover, querying business data on the secondary cluster, and bidirectional replication.
- Classification Note: This chunk is classified as architecture because it describes the primary-secondary DR topology, cluster roles, failure tolerance, and RPO/RTO characteristics rather than step-by-step procedures.

## Official Source Content

# DR Solution Based on Primary and Secondary Clusters

Disaster recovery (DR) based on primary and secondary databases is a common solution. In this solution, the DR system has a primary cluster and a secondary cluster. The primary cluster handles user requests, while the secondary cluster backs up data from the primary cluster. When the primary cluster fails, the secondary cluster takes over services and continues to provide services using the backup data. This ensures that the business system continues to run normally without any interruptions caused by a failure.

The primary-secondary DR solution has the following benefits:

- High availability: The primary-secondary architecture enhances system availability, ensuring fast recovery from any failure.
- Fast switchover: When the primary cluster fails, the system can quickly switch to the secondary cluster and continue to provide services.
- Data consistency: The secondary cluster backs up the data from the primary cluster in almost real time. In this way, the data is basically up-to-date when the system switches to the secondary cluster due to a failure.

This document includes the following contents:

- Set up a primary cluster and a secondary cluster.
- Replicate data from the primary cluster to the secondary cluster.
- Monitor the clusters.
- Perform a DR switchover.

Meanwhile, this document also describes how to query business data on the secondary cluster and how to perform bidirectional replication between the primary and secondary clusters.
## Set up primary and secondary clusters based on TiCDC
### Architecture

![TiCDC secondary cluster architecture](/media/dr/dr-ticdc-secondary-cluster.png)

The preceding architecture includes two TiDB clusters: a primary cluster and a secondary cluster.

- Primary cluster: The active cluster that runs in region 1 and has three replicas. This cluster handles read and write requests.
- Secondary cluster: The standby cluster that runs in region 2 and replicates data from the primary cluster through TiCDC.

This DR architecture is simple and easy to use. Being capable of tolerating regional failures, the DR system guarantees that the write performance of the primary cluster does not deteriorate, and the secondary cluster can handle some read-only business that is not latency-sensitive. The Recovery Point Objective (RPO) of this solution is in seconds, and the Recovery Time Objective (RTO) can be minutes or even lower. This is a solution recommended by many database vendors for important production systems.

> **Note:**
>
> - ["Region" in TiKV](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group) means a range of data while the term "region" means a physical location. The two terms are not interchangeable.
> - Do not run multiple changefeeds to replicate data to the secondary cluster, or run another secondary cluster with the presence of a secondary cluster already. Otherwise, the integrity of data transactions of the secondary cluster cannot be guaranteed.
