# Garbage collection control and retention settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_gc_concurrency <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_gc_enable <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_gc_life_time <span class="version-mark">New in v5.0</span> | System Variables > Variable reference > tidb_gc_max_wait_time <span class="version-mark">New in v6.1.0</span> | System Variables > Variable reference > tidb_gc_run_interval <span class="version-mark">New in v5.0</span>`
- Source Line Ranges: `2939-3012`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `system-variables`, `garbage-collection`, `gc-safe-point`, `retention`, `resolve-locks`, `transaction-blocking`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0167_82f97076d9`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-gc-concurrency-span-class-version-mark-new-in-v5-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eed43b100014ae40c0fc2be48070076cb7a566fd8355357a1920ead592691ef7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-gc-concurrency-span-class-version-mark-new-in-v5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact TiDB garbage collection system variables for enabling GC, retention lifetime, run interval, resolve-lock thread concurrency, or the maximum time active transactions can block the GC safe point.
- Retrieval Keywords: tidb_gc_concurrency, tidb_gc_enable, tidb_gc_life_time, tidb_gc_max_wait_time, tidb_gc_run_interval, garbage collection for TiKV, GC safe point, Resolve Locks step, active transactions block GC safe point, GC interval Go Duration, data retained for each GC, read-only for starter and essential clusters
- Follow-up Guidance: The content also describes how long-running transactions interact with tidb_gc_life_time and how larger retention values can increase storage use and affect performance.
- Classification Note: This is classified as configuration because the content specifies GC-related system variables that control TiKV garbage collection behavior, retention windows, scheduling, and blocking by active transactions.

## Official Source Content

### tidb_gc_concurrency New in v5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- Specifies the number of threads in the [Resolve Locks](https://docs.pingcap.com/tidb/stable/garbage-collection-overview#resolve-locks) step of GC. A value of `-1` means that TiDB will automatically decide the number of garbage collection threads to use.
### tidb_gc_enable New in v5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- Enables garbage collection for TiKV. Disabling garbage collection will reduce system performance, as old versions of rows will no longer be purged.
### tidb_gc_life_time New in v5.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Duration
- Default value: `10m0s`
- Range: `[10m0s, 8760h0m0s]` for TiDB Self-Managed and [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `[10m0s, 168h0m0s]` for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential)
- The time limit during which data is retained for each GC, in the format of Go Duration. When a GC happens, the current time minus this value is the safe point.

> **Note:**
>
> - In scenarios of frequent updates, a large value (days or even months) for `tidb_gc_life_time` may cause potential issues, such as:
>     - Larger storage use
>     - A large amount of history data may affect performance to a certain degree, especially for range queries such as `select count(*) from t`
> - If there is any transaction that has been running longer than `tidb_gc_life_time`, during GC, the data since `start_ts` is retained for this transaction to continue execution. For example, if `tidb_gc_life_time` is configured to 10 minutes, among all transactions being executed, the transaction that starts earliest has been running for 15 minutes, GC will retain data of the recent 15 minutes.
### tidb_gc_max_wait_time New in v6.1.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `86400`
- Range: `[600, 31536000]`
- Unit: Seconds
- This variable is used to set the maximum time that active transactions block the GC safe point. During each time of GC, the safe point does not exceed the start time of the ongoing transactions by default. If the runtime of active transactions does not exceed this variable value, the GC safe point will be blocked until the runtime exceeds this value.
### tidb_gc_run_interval New in v5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Duration
- Default value: `10m0s`
- Range: `[10m0s, 8760h0m0s]`
- Specifies the GC interval, in the format of Go Duration, for example, `"1h30m"`, and `"15m"`
