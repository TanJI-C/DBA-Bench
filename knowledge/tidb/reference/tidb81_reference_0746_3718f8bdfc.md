# Deprecated window operator concurrency variable

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_window_concurrency <span class="version-mark">New in v4.0</span>`
- Source Line Ranges: `6030-6045`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `deprecated`, `window-functions`, `concurrency`, `session-variables`, `global-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0746_3718f8bdfc`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-window-concurrency-span-class-version-mark-new-in-v4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e9d1cc491024dcebd18caade3aa85aeba93cf7d7b6e3a3a68a625ffc04762fd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-window-concurrency-span-class-version-mark-new-in-v4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the deprecated variable `tidb_window_concurrency`, its scope and default, or its relationship to `tidb_executor_concurrency` for window operator concurrency.
- Retrieval Keywords: tidb_window_concurrency, deprecated since v5.0, tidb_executor_concurrency, window operator concurrency, SESSION | GLOBAL, default value -1, value of tidb_executor_concurrency will be used instead
- Follow-up Guidance: The content states that since v5.0 this variable is deprecated and `tidb_executor_concurrency` should be used instead for setting.
- Classification Note: This is classified as reference because the content primarily documents a deprecated system variable's scope, persistence, range, default, and replacement behavior.

## Official Source Content

### tidb_window_concurrency New in v4.0

> **Warning:**
>
> Since v5.0, this variable is deprecated. Instead, use [`tidb_executor_concurrency`](#tidb_executor_concurrency-new-in-v50) for setting.

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `-1`
- Range: `[1, 256]`
- Unit: Threads
- This variable is used to set the concurrency degree of the window operator.
- A value of `-1` means that the value of `tidb_executor_concurrency` will be used instead.
