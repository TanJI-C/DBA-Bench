# Optimize cross-AZ network traffic costs

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/best-practices-on-public-cloud.md`
- Source Title: `TiDB Best Practices on Public Cloud`
- Source Heading Path: `TiDB Best Practices on Public Cloud > Optimize cost for cross-AZ network traffic`
- Source Line Ranges: `133-140`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `tiflash`, `tikv`
- Topic Tags: `cross-az`, `network-traffic`, `cost-optimization`, `follower-read`, `replica-read`, `mpp`, `data-shuffle`, `compression-exchange`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0057_16a771406d`
- Source ID: `tidb-docs-8.1:best-practices/best-practices-on-public-cloud.md#optimize-cost-for-cross-az-network-traffic`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef1e4912b0765ec0eaa3a34e511de3974dddfec73484c90b46d08b74f1211aac`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/best-practices-on-public-cloud#optimize-cost-for-cross-az-network-traffic
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/best-practices-on-public-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when looking for public cloud cost optimization guidance to reduce cross-AZ network traffic for TiDB reads or TiFlash MPP data shuffle.
- Retrieval Keywords: Optimize cost for cross-AZ network traffic, cross-AZ network traffic, availability zones, Follower Read, tidb_replica_read, closest-replicas, closest-adaptive, TiFlash MPP, data shuffle, compression exchange, same availability zones
- Follow-up Guidance: The content states that `tidb_replica_read` can be set to `closest-replicas` or `closest-adaptive`, and that compression exchange is enabled by default starting from v6.6.0.
- Classification Note: This is classified as performance because the content addresses reducing cross-AZ read traffic and MPP shuffle traffic to optimize network usage and related costs on public cloud.

## Official Source Content

## Optimize cost for cross-AZ network traffic

Deploying TiDB across multiple availability zones (AZs) can lead to increased costs due to cross-AZ data transfer fees. To optimize costs, it is important to reduce cross-AZ network traffic.

To reduce cross-AZ read traffic, you can enable the [Follower Read feature](https://docs.pingcap.com/tidb/stable/follower-read), which allows TiDB to prioritize selecting replicas in the same availability zone. To enable this feature, set the [`tidb_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_replica_read-new-in-v40) variable to `closest-replicas` or `closest-adaptive`.

To reduce network traffic caused by the data shuffle of TiFlash MPP tasks, it is recommended to deploy multiple TiFlash instances in the same availability zones (AZs). Starting from v6.6.0, [compression exchange](https://docs.pingcap.com/tidb/stable/explain-mpp#mpp-version-and-exchange-data-compression) is enabled by default, which reduces the network traffic caused by MPP data shuffle.
