# Troubleshoot stuck or slow TiFlash replication

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/troubleshoot-tiflash.md`
- Source Title: `Troubleshoot a TiFlash Cluster`
- Source Heading Path: `Troubleshoot a TiFlash Cluster > Data replication gets stuck | Troubleshoot a TiFlash Cluster > Data replication is slow`
- Source Line Ranges: `244-275`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `pd`
- Topic Tags: `replication`, `disk-space`, `low-space-ratio`, `down-peer`, `store-limit`, `load`, `grafana`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0119_7cddb008c1`
- Source ID: `tidb-docs-8.1:tiflash/troubleshoot-tiflash.md#data-replication-gets-stuck`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0640c65ed740afc89beb588075d010afbe588b807c44a9897829f5d02f14e2e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash#data-replication-gets-stuck
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/troubleshoot-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when TiFlash replication becomes stuck after starting or when replication is slow and you need checks for disk space, down peers, store limit, and TiFlash load metrics.
- Retrieval Keywords: Data replication gets stuck, Data replication is slow, low-space-ratio, space_placeholder_file, reserve-space, ${data}/flash/, pd-ctl region check-down-peer, pd-ctl operator add remove-peer <region-id> <tiflash-store-id>, store limit, TiFlash-Summary, Applying snapshots Count, Snapshot Predecode Duration, Snapshot Flush Duration, Write Stall Duration, TiFlash-Proxy-Details, Region task worker pre-handle/generate snapshot CPU
- Follow-up Guidance: For stuck replication, the content says to check whether disk usage exceeds `low-space-ratio` and whether any `down peer` exists; for slow replication, it says to increase `store limit` and review TiFlash load indicators in Grafana.
- Classification Note: This is classified as diagnosis because the content focuses on confirming and resolving stuck or slow TiFlash replication by checking resource limits, peer status, and performance indicators.

## Official Source Content

## Data replication gets stuck

If data replication on TiFlash starts normally but then all or some data fails to be replicated after a period of time, you can confirm or resolve the issue by performing the following steps:

1. Check the disk space.

    Check whether the disk space ratio is higher than the value of `low-space-ratio` (defaulted to 0.8. When the space usage of a node exceeds 80%, the PD stops migrating data to this node to avoid exhaustion of disk space).

    - If the disk usage ratio is greater than or equal to the value of `low-space-ratio`, the disk space is insufficient. To relieve the disk space, remove unnecessary files, such as `space_placeholder_file` (if necessary, set `reserve-space` to 0MB after removing the file) under the `${data}/flash/` folder.
    - If the disk usage ratio is less than the value of `low-space-ratio`, the disk space is sufficient. Go to the next step.

2. Check whether there is any `down peer` (a `down peer` might cause the replication to get stuck).

    Run the `pd-ctl region check-down-peer` command to check whether there is any `down peer`. If any, run the `pd-ctl operator add remove-peer <region-id> <tiflash-store-id>` command to remove it.
## Data replication is slow

The causes may vary. You can address the problem by performing the following steps.

1. Increase [`store limit`](https://docs.pingcap.com/tidb/stable/configure-store-limit#usage) to accelerate replication.

2. Adjust the load on TiFlash.

    Excessively high load on TiFlash can also result in slow replication. You can check the load of TiFlash indicators on the **TiFlash-Summary** panel on Grafana:

    - `Applying snapshots Count`: `TiFlash-summary` > `raft` > `Applying snapshots Count`
    - `Snapshot Predecode Duration`: `TiFlash-summary` > `raft` > `Snapshot Predecode Duration`
    - `Snapshot Flush Duration`: `TiFlash-summary` > `raft` > `Snapshot Flush Duration`
    - `Write Stall Duration`: `TiFlash-summary` > `Storage Write Stall` > `Write Stall Duration`
    - `generate snapshot CPU`: `TiFlash-Proxy-Details` > `Thread CPU` > `Region task worker pre-handle/generate snapshot CPU`

    Based on your service priorities, adjust the load accordingly to achieve optimal performance.
