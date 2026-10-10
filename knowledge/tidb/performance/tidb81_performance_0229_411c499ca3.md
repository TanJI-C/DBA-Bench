# cloud disk IO jitter mitigation

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-highlights.md`
- Source Title: `TiDB Cloud Performance Highlights for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Performance Highlights for TiDB v8.5.0 > IO latency jitter | TiDB Cloud Performance Highlights for TiDB v8.5.0 > IO latency jitter > Challenge | TiDB Cloud Performance Highlights for TiDB v8.5.0 > IO latency jitter > Solution | TiDB Cloud Performance Highlights for TiDB v8.5.0 > IO latency jitter > Test environment | TiDB Cloud Performance Highlights for TiDB v8.5.0 > IO latency jitter > Test results | TiDB Cloud Performance Highlights for TiDB v8.5.0 > IO latency jitter > Further improvements`
- Source Line Ranges: `63-162`
- Source Scope: `cloud`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `ecosystem`
- Topic Tags: `io jitter`, `failover`, `latency`, `replica selection`, `slow node`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0229_411c499ca3`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-highlights.md#io-latency-jitter`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f86cdbb53d9cc4f9433a2b1c84772ed798401d46003a50b68c134e9c6d628510`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-highlights#io-latency-jitter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-highlights.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB v8.5.0 mitigates cloud disk IO latency jitter, including failover behavior, slow-node detection, replica selection, and latency impact reductions.
- Retrieval Keywords: IO latency jitter, cloud disk IO jitter, Leader write optimization, Enhanced slow-node detection, slow score detection, evict-leader scheduler, slow node detection mechanism, evict-slow-store-scheduler, Unified health controller, Replica Selector V2, KV client, tikv_client_read_timeout, stale reads, follower reads, P99/999 latency reduced by up to 98%, Failover not available
- Follow-up Guidance: The chunk also provides workload-specific failover time and P99/P999 comparisons for IO delays of 2 ms, 5 ms, 10 ms, 50 ms, and 100 ms, plus further improvement notes for latency-sensitive and read-heavy scenarios.
- Classification Note: This is classified as performance content spanning TiDB, TiKV, PD, and related components because the official content describes coordinated improvements for cloud IO jitter handling, failover, and replica selection.

## Official Source Content

## IO latency jitter
### Challenge

In cloud environments, transient or sustained IO latency fluctuations on cloud disks are a common challenge. These fluctuations can increase request latency, causing timeouts, errors, and disruptions to normal business operations, ultimately degrading service quality.
### Solution

TiDB v8.5.0 introduces multiple enhancements to mitigate the impact of cloud disk IO jitter on performance:

- **Leader write optimization**: allows the leader to apply committed but not yet persisted Raft logs early, reducing IO jitter's effect on write latency for the leader peer.
- **Enhanced slow-node detection**: improves the slow-node detection algorithm, enabling slow score detection by default. This triggers the evict-leader scheduler to restore performance when a slow node is identified. The [slow node detection mechanism](https://docs.pingcap.com/tidb/v8.5/pd-scheduling-best-practices#troubleshoot-tikv-node) uses [evict-slow-store-scheduler](https://docs.pingcap.com/tidb/v8.5/pd-control#scheduler-show--add--remove--pause--resume--config--describe) to detect and manage slow nodes, reducing the effects of cloud disk jitter.

- **Unified health controller**: adds a unified health controller in TiKV and a feedback mechanism to the KV client. The KV client optimizes error handling and replica selection based on TiKV node health and performance.
- **Improved replica selector**: introduces Replica Selector V2 in the KV client, with refined state transitions that eliminate unnecessary retries and backoff operations.
- **Additional fixes and improvements**: includes enhancements to critical components such as the region cache and KV client health checker, while avoiding unnecessary IO operations in TiKV's store loop.
### Test environment

- Cluster topology: TiDB (32 vCPU, 64 GiB) \* 3 + TiKV (32 vCPU, 64 GiB) \* 6
- Workload: a read/write ratio of 2:1, with simulated cloud disk IO delays or hangs on one TiKV node
### Test results

Based on the preceding test setup, failovers are now improved in multiple IO delay scenarios, and P99/999 latency during impacts is reduced by up to 98%.

In the following table of test results, the **Current** column shows the results with improvements to reduce IO latency jitter, while the **Original** column shows the results without these improvements:

<table>
    <thead>
        <tr>
            <th rowspan="2">Workload description</th>
            <th colspan="2">Failover time</th>
            <th colspan="2">Maximum latency during impacts (P999)</th>
            <th colspan="2">Maximum latency during impacts (P99)</th>
        </tr>
        <tr>
            <th>Current</th>
            <th>Original</th>
            <th>Current</th>
            <th>Original</th>
            <th>Current</th>
            <th>Original</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>IO delay of 2 ms lasts for 10 mins</td>
            <td>Almost no effect</td>
            <td>Failover not available</td>
            <td>14 ms</td>
            <td>232 ms</td>
            <td>7.9 ms</td>
            <td>22.9 ms</td>
        </tr>
        <tr>
            <td>IO delay of 5 ms lasts for 10 mins</td>
            <td>2 mins</td>
            <td>Failover not available</td>
            <td>37.9 ms</td>
            <td>462 ms</td>
            <td>10 ms</td>
            <td>246 ms</td>
        </tr>
        <tr>
            <td>IO delay of 10 ms lasts for 10 mins</td>
            <td>3 mins</td>
            <td>Failover not available</td>
            <td>69 ms</td>
            <td>3 s</td>
            <td>25 ms</td>
            <td>1.45 s</td>
        </tr>
        <tr>
            <td>IO delay of 50 ms lasts for 10 mins</td>
            <td>3 mins</td>
            <td>Failover not available</td>
            <td>1.36 s</td>
            <td>13.2 s</td>
            <td>238 ms</td>
            <td>6.7 s</td>
        </tr>
        <tr>
            <td>IO delay of 100 ms lasts for 10 mins</td>
            <td>3 mins</td>
            <td>Failover not available</td>
            <td>7.53 s</td>
            <td>32 s</td>
            <td>1.7 s</td>
            <td>26 s</td>
        </tr>
    </tbody>
</table>
### Further improvements

The severity of disk jitter might also be highly related to users' workload profiles. In latency-sensitive scenarios, designing applications in conjunction with TiDB features can further minimize the impact of IO jitter on applications. For example, in read-heavy and latency-sensitive environments, adjusting the [`tikv_client_read_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tikv_client_read_timeout-new-in-v740) system variable according to latency requirements and using stale reads or follower reads can enable faster failover retries to other replica peers for KV requests sent from TiDB. This reduces the impact of IO jitter on a single TiKV node and helps improve query latency. Note that the effectiveness of this feature depends on the workload profile, which should be evaluated before implementation.

Additionally, users [deploying TiDB on public cloud](https://docs.pingcap.com/tidb/dev/best-practices-on-public-cloud) can reduce the probability of jitter by choosing cloud disks with higher performance.
