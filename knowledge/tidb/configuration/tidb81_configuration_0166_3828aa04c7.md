# Plan baseline evolution timing and executor concurrency

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_evolve_plan_task_max_time <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_evolve_plan_task_start_time <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_executor_concurrency <span class="version-mark">New in v5.0</span>`
- Source Line Ranges: `2831-2883`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `system-variables`, `baseline-evolution`, `executor-concurrency`, `sql-operators`, `session-scope`, `global-scope`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0166_3828aa04c7`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-evolve-plan-task-max-time-span-class-version-mark-new-in-v4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2978631f23e97b058698d32ce18b50984f3e26b61e22b7f8548e4c55ac1b092e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-evolve-plan-task-max-time-span-class-version-mark-new-in-v4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact TiDB system variables for baseline evolution scheduling or for controlling SQL operator executor concurrency, including scope, defaults, ranges, and affected operators.
- Retrieval Keywords: tidb_evolve_plan_task_max_time, tidb_evolve_plan_task_start_time, tidb_executor_concurrency, baseline evolution maximum execution time, baseline evolution start time in a day, index lookup concurrency, index lookup join concurrency, hash join concurrency, hash aggregation partial final concurrency, window concurrency, projection concurrency, tidb_index_lookup_concurrency, tidb_index_lookup_join_concurrency, tidb_hash_join_concurrency, tidb_hashagg_partial_concurrency, tidb_hashagg_final_concurrency, tidb_projection_concurrency, tidb_window_concurrency, SET_VAR
- Follow-up Guidance: The content also explains how deprecated per-operator concurrency variables interact with tidb_executor_concurrency, including the effect of setting those variables to -1 and behavior after upgrade to v5.0.
- Classification Note: This is classified as configuration because the content defines TiDB system variables that control baseline evolution timing and executor thread concurrency for SQL operators.

## Official Source Content

### tidb_evolve_plan_task_max_time New in v4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `600`
- Range: `[-1, 9223372036854775807]`
- Unit: Seconds
- This variable is used to limit the maximum execution time of each execution plan in the baseline evolution feature.
### tidb_evolve_plan_task_start_time New in v4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Time
- Default value: `00:00 +0000`
- This variable is used to set the start time of baseline evolution in a day.
### tidb_executor_concurrency New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `5`
- Range: `[1, 256]`
- Unit: Threads

This variable is used to set the concurrency of the following SQL operators (to one value):

- `index lookup`
- `index lookup join`
- `hash join`
- `hash aggregation` (the `partial` and `final` phases)
- `window`
- `projection`

`tidb_executor_concurrency` incorporates the following existing system variables as a whole for easier management:

+ `tidb_index_lookup_concurrency`
+ `tidb_index_lookup_join_concurrency`
+ `tidb_hash_join_concurrency`
+ `tidb_hashagg_partial_concurrency`
+ `tidb_hashagg_final_concurrency`
+ `tidb_projection_concurrency`
+ `tidb_window_concurrency`

Since v5.0, you can still separately modify the system variables listed above (with a deprecation warning returned) and your modification only affects the corresponding single operators. After that, if you use `tidb_executor_concurrency` to modify the operator concurrency, the separately modified operators will not be affected. If you want to use `tidb_executor_concurrency` to modify the concurrency of all operators, you can set the values of all variables listed above to `-1`.

For a system upgraded to v5.0 from an earlier version, if you have not modified any value of the variables listed above (which means that the `tidb_hash_join_concurrency` value is `5` and the values of the rest are `4`), the operator concurrency previously managed by these variables will automatically be managed by `tidb_executor_concurrency`. If you have modified any of these variables, the concurrency of the corresponding operators will still be controlled by the modified variables.
