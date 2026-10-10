# BR backup auto-tune implementation details

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-auto-tune.md`
- Source Title: `Backup Auto-Tune`
- Source Heading Path: `Backup Auto-Tune <span class="version-mark">New in v5.4.0</span> > Implementation`
- Source Line Ranges: `58-87`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `dashboard`
- Topic Tags: `backup`, `auto-tune`, `implementation`, `thread-pool`, `cpu-utilization`, `internal-tuning`, `grafana`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0009_d2077a2fae`
- Source ID: `tidb-docs-8.1:br/br-auto-tune.md#implementation`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9d54f967a474670f1eed8688797303baf53db7c0d5d62f3455db9d893b8bd56`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-auto-tune#implementation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-auto-tune.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the internal implementation details of BR backup auto-tune, including how thread pool size is adjusted and which internal tuning parameters affect CPU usage calculations.
- Retrieval Keywords: Implementation, backup.auto-tune-remain-threads, backup.auto-tune-refresh-interval, round(0.2 * vCPU), 1m, thread pool size, overall CPU utilization, backup.num-threads, Backup CPU Utilization panel, Grafana dashboard
- Follow-up Guidance: It notes that these two configuration items are only for internal tuning and do not need to be configured when performing backup tasks, and it points to the Backup CPU Utilization panel for observing the adjusted thread pool size.
- Classification Note: This is classified as architecture because the content describes the internal mechanism, hidden tuning items, default formulas, refresh interval, and CPU-based thread-pool adjustment model used by auto-tune.

## Official Source Content

## Implementation

Auto-tune adjusts the size of the thread pool used by backup tasks to ensure that the overall CPU utilization of the cluster does not exceed a specific threshold.

This feature has two related configuration items not listed in the TiKV configuration file. These two configuration items are only for internal tuning. You do **not** need to configure these two configuration items when you perform backup tasks.

- `backup.auto-tune-remain-threads`:

    - Auto-tune controls the resources used by the backup tasks and ensures that at least `backup.auto-tune-remain-threads` cores are available for other tasks on the same node.
    - Default value: `round(0.2 * vCPU)`

- `backup.auto-tune-refresh-interval`:

    - Every `backup.auto-tune-refresh-interval` minute(s), auto-tune refreshes the statistics and recalculates the maximum number of CPU cores that backup tasks can use.
    - Default value: `1m`

The following is an example of how auto-tune works. `*` denotes a CPU core used by backup tasks. `^` denotes a CPU core used by other tasks. `-` denotes an idle CPU core.

```
|--------| The server has 8 logical CPU cores.
|****----| By default, `backup.num-threads` is `4`. Note that auto-tune makes sure that the thread pool size is never larger than `backup.num-threads`.
|^^****--| By default, `auto-tune-remain-threads` = round(8 * 0.2) = 2. Auto-tune adjusts the size of the thread pool to `4`.
|^^^^**--| Because the cluster workload gets higher, auto-tune adjusts the size of the thread pool to `2`. After that, the cluster still has 2 idle CPU cores.
```

In the **Backup CPU Utilization** panel, you can see the size of the thread pool adjusted by auto-tune:

![Grafana dashboard example of backup auto-tune metrics](/media/br/br-auto-throttle.png)

In the image above, the yellow semi-transparent area represents the threads available for backup tasks. You can see the CPU utilization of backup tasks does not go beyond the yellow area.
