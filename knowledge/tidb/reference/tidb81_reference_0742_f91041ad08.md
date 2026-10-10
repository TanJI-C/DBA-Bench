# tidb_stats_load_sync_wait statistics loading wait

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_stats_load_sync_wait <span class="version-mark">New in v5.4.0</span>`
- Source Line Ranges: `5371-5385`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `session-variables`, `global-variables`, `optimizer`, `timeouts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0742_f91041ad08`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-stats-load-sync-wait-span-class-version-mark-new-in-v5-4-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13880f948c27aa43d18609c9c3b638c1a2d868589892f08bf6163dfd2e023f3e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-stats-load-sync-wait-span-class-version-mark-new-in-v5-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the system variable that controls synchronously loading statistics and how long SQL optimization waits to load complete column statistics.
- Retrieval Keywords: tidb_stats_load_sync_wait, synchronously loading statistics, load statistics, complete column statistics, SQL optimization wait, milliseconds, SET_VAR
- Follow-up Guidance: The content points to Load statistics for more details about the synchronously loading statistics feature.
- Classification Note: This is reference content because it defines the scope, type, default, range, unit, and behavior of the tidb_stats_load_sync_wait system variable.

## Official Source Content

### tidb_stats_load_sync_wait New in v5.4.0

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `100`
- Range: `[0, 2147483647]`
- Unit: Milliseconds
- This variable controls whether to enable the synchronously loading statistics feature. The value `0` means that the feature is disabled. To enable the feature, you can set this variable to a timeout (in milliseconds) that SQL optimization can wait for at most to synchronously load complete column statistics. For details, see [Load statistics](https://docs.pingcap.com/tidb/stable/statistics#load-statistics).
