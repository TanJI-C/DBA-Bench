# Troubleshoot failed or slow TiKV nodes with PD scheduling

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/pd-scheduling-best-practices.md`
- Source Title: `PD Scheduling Best Practices`
- Source Heading Path: `PD Scheduling Best Practices > PD scheduling in common scenarios > Troubleshoot TiKV node`
- Source Line Ranges: `293-303`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `node-failure`, `replica-rebalance`, `max-store-down-time`, `slow-store-detection`, `leader-eviction`, `scheduler`, `io-pool`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0001_fc484a3b07`
- Source ID: `tidb-docs-8.1:best-practices/pd-scheduling-best-practices.md#troubleshoot-tikv-node`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a5887f50e633e599d763d2c138567c90f413f4571f34282196e8821bada510dd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#troubleshoot-tikv-node
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/pd-scheduling-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting a failed or slow TiKV node with PD scheduling behavior such as down-state timing, replica rebalancing, slow store detection, or Leader eviction.
- Retrieval Keywords: Troubleshoot TiKV node, PD scheduling, TiKV node fails, down state, max-store-down-time, replica rebalancing, take it offline, slow TiKV node detection, score ranging from 1 to 100, score higher than or equal to 80, evict-slow-store-scheduler, evict-leader-scheduler, Leader eviction, slow I/O, request accumulation, store-io-pool-size
- Follow-up Guidance: The content also notes that Leader eviction on slow nodes can be delayed by slow I/O and request accumulation, and mentions `store-io-pool-size` in relation to this situation.
- Classification Note: This chunk is classified as recovery because it describes how PD handles failed TiKV nodes, when replicas are replenished, and how slow-node scheduling and Leader eviction are used during node troubleshooting.

## Official Source Content

### Troubleshoot TiKV node

If a TiKV node fails, PD defaults to setting the corresponding node to the **down** state after 30 minutes (customizable by configuration item `max-store-down-time`), and rebalancing replicas for regions involved.

Practically, if a node failure is considered unrecoverable, you can immediately take it offline. This makes PD replenish replicas soon in another node and reduces the risk of data loss. In contrast, if a node is considered recoverable, but the recovery cannot be done in 30 minutes, you can temporarily adjust `max-store-down-time` to a larger value to avoid unnecessary replenishment of the replicas and resources waste after the timeout.

In TiDB v5.2.0, TiKV introduces the mechanism of slow TiKV node detection. By sampling the requests in TiKV, this mechanism works out a score ranging from 1 to 100. A TiKV node with a score higher than or equal to 80 is marked as slow. You can add [`evict-slow-store-scheduler`](https://docs.pingcap.com/tidb/stable/pd-control#scheduler-show--add--remove--pause--resume--config--describe) to detect and schedule slow nodes. If only one TiKV is detected as slow, and the slow score reaches the limit (80 by default), the Leader in this node will be evicted (similar to the effect of `evict-leader-scheduler`).

> **Note:**
>
> **Leader eviction** is accomplished by PD sending scheduling requests to TiKV slow nodes and then TiKV executing the received scheduling requests sequentially. Due to factors such as **slow I/O**, slow nodes might experience request accumulation, causing some Leaders to wait until the delayed requests are processed before handling **Leader eviction** requests. This results in an overall extended time for **Leader eviction**. Therefore, when you enable `evict-slow-store-scheduler`, it is recommended to enable [`store-io-pool-size`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#store-io-pool-size-new-in-v530) as well to mitigate this situation.
