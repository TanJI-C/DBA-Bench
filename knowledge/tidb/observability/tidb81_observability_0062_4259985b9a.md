# TiKV transaction, resolved-ts, and memory metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-tikv-dashboard.md`
- Source Title: `Key Monitoring Metrics of TiKV`
- Source Heading Path: `Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Pessimistic Locking | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Resolved-TS | Key Monitoring Metrics of TiKV > TiKV-Details dashboard > Memory`
- Source Line Ranges: `412-441`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `ticdc`
- Topic Tags: `grafana`, `metrics`, `pessimistic-locking`, `deadlock`, `resolved-ts`, `safe-ts`, `memory`, `allocator`, `transactions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0062_4259985b9a`
- Source ID: `tidb-docs-8.1:grafana-tikv-dashboard.md#pessimistic-locking`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3b550d7ad0ffd05712bb479b2cc797161ae214c99385e9b0d08bd76f56d51d2e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#pessimistic-locking
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-tikv-dashboard.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV-Details Grafana metrics for pessimistic locking, resolved-ts or safe-ts status, and TiKV memory allocator statistics.
- Retrieval Keywords: TiKV-Details dashboard, Pessimistic Locking, Resolved-TS, Memory, Lock Manager Thread CPU, Lock Manager Handled tasks, Waiter lifetime duration, Wait table, Deadlock detect duration, Detect error, Deadlock detector leader, Total pessimistic locks memory size, In-memory pessimistic locking result, full, Resolved-TS worker CPU, Advance-TS worker CPU, Scan lock worker CPU, Max gap of resolved-ts, Max gap of safe-ts, Min Resolved TS Region, Min Safe TS Region, Check Leader Duration, Max gap of resolved-ts in Region leaders, Min Leader Resolved TS Region, Lock heap size, Allocator Stats
- Follow-up Guidance: The source also identifies Region IDs for the minimal resolved-ts and safe-ts, including Min Resolved TS Region, Min Safe TS Region, and Min Leader Resolved TS Region.
- Classification Note: The official content classifies these as observability metrics for TiKV transaction locking, resolved-ts tracking, and memory usage on the TiKV-Details dashboard.

## Official Source Content

### Pessimistic Locking

- Lock Manager Thread CPU: The CPU utilization of the lock manager thread
- Lock Manager Handled tasks: The number of tasks handled by lock manager
- Waiter lifetime duration: The waiting time of the transaction for the lock to be released
- Wait table: The status information of wait table, including the number of locks and the number of transactions waiting for the lock
- Deadlock detect duration: The time consumed for detecting deadlock
- Detect error: The number of errors encountered when detecting deadlock, including the number of deadlocks
- Deadlock detector leader: The information of the node where the deadlock detector leader is located
- Total pessimistic locks memory size: The memory size occupied by the in-memory pessimistic locks
- In-memory pessimistic locking result: The result of only saving pessimistic locks to memory. `full` means the number of times that the pessimistic lock is not saved to memory because the memory limit is exceeded.
### Resolved-TS

- Resolved-TS worker CPU: The CPU utilization of the resolved-ts worker threads
- Advance-TS worker CPU: The CPU utilization of the advance-ts worker threads
- Scan lock worker CPU: The CPU utilization of the scan lock worker threads
- Max gap of resolved-ts: The maximum time difference between the resolved-ts of all active Regions in this TiKV and the current time
- Max gap of safe-ts: The maximum time difference between the safe-ts of all active Regions in this TiKV and the current time
- Min Resolved TS Region: The ID of the Region whose resolved-ts is the minimal
- Min Safe TS Region: The ID of the Region whose safe-ts is the minimal
- Check Leader Duration: The distribution of time spent on processing leader requests. The duration is from sending requests to receiving responses in leader
- Max gap of resolved-ts in Region leaders: The maximum time difference between the resolved-ts of all active Regions in this TiKV and the current time, only for Region leaders
- Min Leader Resolved TS Region: The ID of the Region whose resolved-ts is the minimal, only for Region leaders
- Lock heap size: The size of the heap that tracks locks in the resolved-ts module
### Memory

- Allocator Stats: The statistics of the memory allocator
