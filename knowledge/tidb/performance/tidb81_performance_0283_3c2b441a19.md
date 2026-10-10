# Tune Region performance with Region size, buckets, and Active PD Follower

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-region-performance.md`
- Source Title: `Tune Region Performance`
- Source Heading Path: `Tune Region Performance | Tune Region Performance > Overview | Tune Region Performance > Use `region-split-size` to adjust Region size | Tune Region Performance > Use bucket to increase concurrency | Tune Region Performance > Use the Active PD Follower feature to enhance the scalability of PD's Region information query service`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `tidb`, `tiflash`, `dumpling`
- Topic Tags: `region-size`, `region-split-size`, `buckets`, `query-concurrency`, `active-pd-follower`, `region-information`, `pd-leader-load`, `experimental-features`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0283_3c2b441a19`
- Source ID: `tidb-docs-8.1:tune-region-performance.md#tune-region-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6323e98094d16d92735e49b13653799d7c704a943a4a698fee4a08b8af2efb5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-region-performance#tune-region-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-region-performance.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to tune Region performance with larger Region size, buckets for concurrent queries, or Active PD Follower for PD Region information query scalability in a TiDB cluster with many Regions.
- Retrieval Keywords: coprocessor.region-split-size, region-split-size, Region size, 96 MiB, 48 MiB, 256 MiB, 1 GiB, 10 GiB, coprocessor.enable-region-bucket, enable-region-bucket, coprocessor.region-bucket-size, region-bucket-size, bucket, concurrent query, scan concurrency, pd_enable_follower_handle_region, Active PD Follower, PD leader, PD follower, Region information query service, many Regions, PD leader CPU load, TiFlash, Dumpling, Hibernate Region, Region Merge
- Follow-up Guidance: The content also notes fallback behavior when a PD follower is unavailable or returns outdated Region information, and it mentions TiFlash and Dumpling constraints when increasing Region size.
- Classification Note: This is classified as performance because the official content focuses on reducing overhead from many Regions, improving query concurrency, and reducing PD leader CPU pressure for Region information requests.

## Official Source Content

# Tune Region Performance

This document introduces how to tune Region performance by adjusting the Region size and how to use bucket to optimize concurrent queries when the Region size is large. In addition, this document introduces how to enhance the ability of PD to provide Region information to TiDB nodes by enabling the Active PD Follower feature.
## Overview

TiKV automatically [shards bottom-layered data](https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#data-sharding). Data is split into multiple Regions based on the key ranges. When the size of a Region exceeds a threshold, TiKV splits it into two or more Regions.

In scenarios involving large datasets, if the Region size is relatively small, TiKV might have too many Regions, which causes more resource consumption and [performance regression](https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#performance-problem). Since v6.1.0, TiDB supports customizing Region size. The default size of a Region is 96 MiB. To reduce the number of Regions, you can adjust Regions to a larger size.

To reduce the performance overhead of many Regions, you can also enable [Hibernate Region](https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#method-4-increase-the-number-of-tikv-instances) or [`Region Merge`](https://docs.pingcap.com/tidb/stable/best-practices/massive-regions-best-practices#method-5-adjust-raft-base-tick-interval).
## Use `region-split-size` to adjust Region size

> **Note:**
>
> The recommended range for the Region size is [48 MiB, 256 MiB]. Commonly used sizes include 96 MiB, 128 MiB, and 256 MiB. It is NOT recommended to set the Region size beyond 1 GiB. Avoid setting the size to more than 10 GiB. An excessively large Region size might result in the following side effects:
>
> + Performance jitters
> + Decreased query performance, especially for queries that deal with a large range of data
> + Slower Region scheduling

To adjust the Region size, you can use the [`coprocessor.region-split-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-split-size) configuration item. When TiFlash or the Dumpling tool is used, the Region size should not exceed 1 GiB. After increasing the Region size, you need to reduce the concurrency if the Dumpling tool is used; otherwise, TiDB might run out of memory.
## Use bucket to increase concurrency

> **Warning:**
>
> Currently, this is an experimental feature introduced in TiDB v6.1.0. It is not recommended that you use it in production environments.

After Regions are set to a larger size, if you want to further improve the query concurrency, you can set [`coprocessor.enable-region-bucket`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-region-bucket-new-in-v610) to `true`. When you use this configuration, Regions are divided into buckets. Buckets are smaller ranges within a Region and are used as the unit of concurrent query to improve the scan concurrency. You can control the bucket size using [`coprocessor.region-bucket-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#region-bucket-size-new-in-v610).
## Use the Active PD Follower feature to enhance the scalability of PD's Region information query service

> **Warning:**
>
> The Active PD Follower feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

In a TiDB cluster with a large number of Regions, the PD leader might experience high CPU load due to the increased overhead of handling heartbeats and scheduling tasks. If the cluster has many TiDB instances, and there is a high concurrency of requests for Region information, the CPU pressure on the PD leader increases further and might cause PD services to become unavailable.

To ensure high availability, the PD leader synchronizes Region information with its followers in real time. PD followers maintain and store Region information in memory, enabling them to process Region information requests. You can enable the Active PD Follower feature by setting the system variable [`pd_enable_follower_handle_region`](https://docs.pingcap.com/tidb/stable/system-variables#pd_enable_follower_handle_region-new-in-v760) to `ON`. After this feature is enabled, TiDB evenly distributes Region information requests to all PD servers, and PD followers can also directly handle Region requests, thereby reducing the CPU pressure on the PD leader.

PD ensures that the Region information in TiDB is always up-to-date by maintaining the status of Region synchronization streams and using the fallback mechanism of TiKV client-go. 

- When the network between the PD leader and a follower is unstable or a follower is unavailable, the Region synchronization stream is disconnected, and the PD follower rejects Region information requests. In this case, TiDB automatically retries the request to the PD leader and temporarily marks the follower as unavailable. 
- When the network is stable, because there might be a delay in the synchronization between the leader and the follower, some Region information obtained from the follower might be outdated. In this case, if the KV request corresponding to the Region fails, TiDB automatically re-requests the latest Region information from the PD leader and sends the KV request to TiKV again.
