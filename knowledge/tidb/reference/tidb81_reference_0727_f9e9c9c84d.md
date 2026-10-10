# TiFlash spill-to-disk memory threshold variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_max_bytes_before_tiflash_external_group_by <span class="version-mark">New in v7.0.0</span> | System Variables > Variable reference > tidb_max_bytes_before_tiflash_external_join <span class="version-mark">New in v7.0.0</span>`
- Source Line Ranges: `3531-3586`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `system-variables`, `tiflash`, `spill-to-disk`, `memory`, `group-by`, `join`, `mpp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0727_f9e9c9c84d`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-max-bytes-before-tiflash-external-group-by-span-class-version-mark-new-in-v7-0-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7a95e4a8c900b970b859e398e35363d9050a31abda47189f361c7135c644fd44`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-max-bytes-before-tiflash-external-group-by-span-class-version-mark-new-in-v7-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables that control TiFlash spill-to-disk thresholds for Hash Aggregation with GROUP BY or Hash Join with JOIN.
- Retrieval Keywords: tidb_max_bytes_before_tiflash_external_group_by, tidb_max_bytes_before_tiflash_external_join, TiFlash Spill to Disk, spill to disk, Hash Aggregation, GROUP BY, Hash Join, JOIN, max_bytes_before_external_group_by, max_bytes_before_external_join, single TiFlash node, SET_VAR
- Follow-up Guidance: The content also references TiFlash Spill to Disk and the TiFlash configuration items max_bytes_before_external_group_by and max_bytes_before_external_join for related details.
- Classification Note: This is reference content because it specifies the exact TiFlash memory threshold variables, their ranges and defaults, SET_VAR applicability, and how values such as -1 and 0 are interpreted.

## Official Source Content

### tidb_max_bytes_before_tiflash_external_group_by New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `-1`
- Range: `[-1, 9223372036854775807]`
- This variable is used to specify the maximum memory usage of the Hash Aggregation operator with `GROUP BY` in TiFlash, in bytes. When the memory usage exceeds the specified value, TiFlash triggers the Hash Aggregation operator to spill to disk. When the value of this variable is `-1`, TiDB does not pass this variable to TiFlash. Only when the value of this variable is greater than or equal to `0`, TiDB passes this variable to TiFlash. When the value of this variable is `0`, it means that the memory usage is unlimited, that is, TiFlash Hash Aggregation operator will not trigger spilling. For details, see [TiFlash Spill to Disk](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk).

> **Note:**
>
> - If a TiDB cluster has multiple TiFlash nodes, aggregation is usually distributedly executed on multiple TiFlash nodes. This variable controls the maximum memory usage of the aggregation operator on a single TiFlash node.
> - When this variable is set to `-1`, TiFlash determines the maximum memory usage of the aggregation operator based on the value of its own configuration item [`max_bytes_before_external_group_by`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#tiflash-configuration-parameters).

> **Note:**
>
> - If a TiDB cluster has multiple TiFlash nodes, aggregation is usually distributedly executed on multiple TiFlash nodes. This variable controls the maximum memory usage of the aggregation operator on a single TiFlash node.
> - When this variable is set to `-1`, TiFlash determines the maximum memory usage of the aggregation operator based on the value of its own configuration item `max_bytes_before_external_group_by`.
### tidb_max_bytes_before_tiflash_external_join New in v7.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `-1`
- Range: `[-1, 9223372036854775807]`
- This variable is used to specify the maximum memory usage of the Hash Join operator with `JOIN` in TiFlash, in bytes. When the memory usage exceeds the specified value, TiFlash triggers the Hash Join operator to spill to disk. When the value of this variable is `-1`, TiDB does not pass this variable to TiFlash. Only when the value of this variable is greater than or equal to `0`, TiDB passes this variable to TiFlash. When the value of this variable is `0`, it means that the memory usage is unlimited, that is, TiFlash Hash Join operator will not trigger spilling. For details, see [TiFlash Spill to Disk](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk).

> **Note:**
>
> - If a TiDB cluster has multiple TiFlash nodes, join is usually distributedly executed on multiple TiFlash nodes. This variable controls the maximum memory usage of the join operator on a single TiFlash node.
> - When this variable is set to `-1`, TiFlash determines the maximum memory usage of the join operator based on the value of its own configuration item [`max_bytes_before_external_join`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#tiflash-configuration-parameters).

> **Note:**
>
> - If a TiDB cluster has multiple TiFlash nodes, join is usually distributedly executed on multiple TiFlash nodes. This variable controls the maximum memory usage of the join operator on a single TiFlash node.
> - When this variable is set to `-1`, TiFlash determines the maximum memory usage of the join operator based on the value of its own configuration item `max_bytes_before_external_join`.
