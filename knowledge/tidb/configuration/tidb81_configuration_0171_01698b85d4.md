# SPLIT REGION wait behavior and timeout variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_wait_split_region_finish | System Variables > Variable reference > tidb_wait_split_region_timeout`
- Source Line Ranges: `6001-6029`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`
- Topic Tags: `split-region`, `region-scatter`, `timeout`, `session-variables`, `batch-write`, `data-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0171_01698b85d4`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-wait-split-region-finish`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e90f07aa937aaa2c26c8f5ce1d06ee2b3b6974bf0d6d50217d10294cd16bb3a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-wait-split-region-finish
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how the SESSION variables `tidb_wait_split_region_finish` and `tidb_wait_split_region_timeout` affect `SPLIT REGION` wait behavior, scattering completion, and timeout errors.
- Retrieval Keywords: tidb_wait_split_region_finish, tidb_wait_split_region_timeout, SPLIT REGION, SPLIT REGIONS statement waits until all Regions are scattered, return before finishing scattering all Regions, timeout error is returned, PD scheduling, TiKV loads, batch-write, data importing
- Follow-up Guidance: The content notes that write and read performances for a Region being scattered might be affected, and in batch-write or data importing scenarios it recommends importing data after Regions scattering is finished.
- Classification Note: This is classified as configuration because the content defines SESSION system variables, their types, defaults, ranges, and execution behavior for the `SPLIT REGION` statement.

## Official Source Content

### tidb_wait_split_region_finish

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `ON`
- It usually takes a long time to scatter Regions, which is determined by PD scheduling and TiKV loads. This variable is used to set whether to return the result to the client after all Regions are scattered completely when the `SPLIT REGION` statement is being executed:
    - `ON` requires that the `SPLIT REGIONS` statement waits until all Regions are scattered.
    - `OFF` permits the `SPLIT REGIONS` statement to return before finishing scattering all Regions.
- Note that when scattering Regions, the write and read performances for the Region that is being scattered might be affected. In batch-write or data importing scenarios, it is recommended to import data after Regions scattering is finished.
### tidb_wait_split_region_timeout

> **Note:**
>
> This variable is read-only for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `300`
- Range: `[1, 2147483647]`
- Unit: Seconds
- This variable is used to set the timeout for executing the `SPLIT REGION` statement. If a statement is not executed completely within the specified time value, a timeout error is returned.
