# TTL job and task system variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_ttl_delete_worker_count <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_job_enable <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_scan_batch_size <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_scan_worker_count <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_job_schedule_window_start_time <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_job_schedule_window_end_time <span class="version-mark">New in v6.5.0</span> | System Variables > Variable reference > tidb_ttl_running_tasks <span class="version-mark">New in v7.0.0</span>`
- Source Line Ranges: `5820-5911`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `cloud`
- Topic Tags: `ttl`, `job-scheduling`, `concurrency`, `batch-size`, `global-variables`, `read-only-cloud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0169_c32581ba23`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-ttl-delete-worker-count-span-class-version-mark-new-in-v6-5-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5dcd7fdaba6da413177ba42eaff7e903593ef054aa3cf018af55c579129ce892`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-ttl-delete-worker-count-span-class-version-mark-new-in-v6-5-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about TiDB TTL system variables for enabling jobs, controlling scan or delete concurrency, setting scan batch size, defining the TTL scheduling window, or limiting running TTL tasks cluster-wide.
- Retrieval Keywords: tidb_ttl_delete_worker_count, tidb_ttl_job_enable, tidb_ttl_scan_batch_size, tidb_ttl_scan_worker_count, tidb_ttl_job_schedule_window_start_time, tidb_ttl_job_schedule_window_end_time, tidb_ttl_running_tasks, TTL jobs, TTL scan jobs, expired data cleanup, scheduling window of TTL jobs, maximum number of running TTL tasks, read-only for starter and essential clusters
- Follow-up Guidance: The content points readers to Time to Live for more information and notes that a small scheduling window might cause cleanup of expired data to fail.
- Classification Note: This is classified as configuration because the content is a reference for GLOBAL TiDB system variables that control TTL job behavior, concurrency, batch size, scheduling time window, and cluster task limits.

## Official Source Content

### tidb_ttl_delete_worker_count New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `4`
- Range: `[1, 256]`
- This variable is used to set the maximum concurrency of TTL jobs on each TiDB node. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_job_enable New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- Type: Boolean
- This variable is used to control whether TTL jobs are enabled. If it is set to `OFF`, all tables with TTL attributes automatically stop cleaning up expired data. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_scan_batch_size New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `500`
- Range: `[1, 10240]`
- This variable is used to set the `LIMIT` value of each `SELECT` statement used to scan expired data in a TTL job. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_scan_worker_count New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `4`
- Range: `[1, 256]`
- This variable is used to set the maximum concurrency of TTL scan jobs on each TiDB node. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_job_schedule_window_start_time New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Time
- Persists to cluster: Yes
- Default value: `00:00 +0000`
- This variable is used to control the start time of the scheduling window of TTL jobs in the background. When you modify the value of this variable, be cautious that a small window might cause the cleanup of expired data to fail. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_job_schedule_window_end_time New in v6.5.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Time
- Persists to cluster: Yes
- Default value: `23:59 +0000`
- This variable is used to control the end time of the scheduling window of TTL jobs in the background. When you modify the value of this variable, be cautious that a small window might cause the cleanup of expired data to fail. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
### tidb_ttl_running_tasks New in v7.0.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `-1` and `[1, 256]`
- Specifies the maximum number of running TTL tasks in the entire cluster. `-1` means the number of TTL tasks is equivalent to the number of TiKV nodes. For more information, refer to [Time to Live](https://docs.pingcap.com/tidb/stable/time-to-live).
