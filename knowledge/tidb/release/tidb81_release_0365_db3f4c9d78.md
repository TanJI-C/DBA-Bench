# Stability feature: global memory control GA

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > New features > Stability`
- Source Line Ranges: `192-203`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `memory-control`, `ga`, `memory-limit`, `oom-action`, `transactions`, `system-variables`, `configuration-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0365_db3f4c9d78`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#stability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cff4de0c84bc8552a8a54dcf7134637a18d2fa35fb12c402d1870fd6c85a0142`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#stability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about TiDB 6.5.0 global memory control becoming GA, including tidb_server_memory_limit, tidb_mem_quota_query, tidb_mem_oom_action, and txn-total-size-limit compatibility.
- Retrieval Keywords: global memory control, GA, tidb_server_memory_limit, tidb_mem_quota_query, tidb_mem_oom_action, txn-total-size-limit, memory management module, CANCEL, global memory consumption, single session memory
- Follow-up Guidance: The source also links to documentation for configuring memory usage.
- Classification Note: This is classified as release because it announces the GA status and behavior changes of the global memory control feature in TiDB 6.5.0.

## Official Source Content

### Stability

* The global memory control feature is now GA [#37816](https://github.com/pingcap/tidb/issues/37816) @[wshwsh12](https://github.com/wshwsh12)

    Since v6.4.0, TiDB has introduced global memory control as an experimental feature. In v6.5.0, it becomes GA and can track the main memory consumption. When the global memory consumption reaches the threshold defined by [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640), TiDB tries to limit the memory usage by GC or canceling SQL operations, to ensure stability.

    Note that the memory consumed by the transaction in a session (the maximum value was previously set by the configuration item [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit)) is now tracked by the memory management module: when the memory consumption of a single session reaches the threshold defined by the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query), the behavior defined by the system variable [`tidb_mem_oom_action`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_oom_action-new-in-v610) will be triggered (the default is `CANCEL`, that is, canceling operations). To ensure forward compatibility, when [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit) is configured as a non-default value, TiDB will still ensure that transactions can use the memory set by `txn-total-size-limit`.

    If you are using TiDB v6.5.0 or later, it is recommended to remove [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit) and not to set a separate limit on the memory usage of transactions. Instead, use the system variables [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) and [`tidb_server_memory_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_server_memory_limit-new-in-v640) to manage global memory, which can improve the efficiency of memory usage.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/configure-memory-usage).
