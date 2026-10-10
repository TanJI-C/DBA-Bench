# Optimizer Fix Controls reference entries

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-fix-controls.md`
- Source Title: `Optimizer Fix Controls`
- Source Heading Path: `Optimizer Fix Controls > Optimizer Fix Controls reference | Optimizer Fix Controls > Optimizer Fix Controls reference > [`33031`](https://github.com/pingcap/tidb/issues/33031) <span class="version-mark">New in v8.0.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`44262`](https://github.com/pingcap/tidb/issues/44262) <span class="version-mark">New in v6.5.3 and v7.2.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`44389`](https://github.com/pingcap/tidb/issues/44389) <span class="version-mark">New in v6.5.3 and v7.2.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`44823`](https://github.com/pingcap/tidb/issues/44823) <span class="version-mark">New in v7.3.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`44830`](https://github.com/pingcap/tidb/issues/44830) <span class="version-mark">New in v6.5.7 and v7.3.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`44855`](https://github.com/pingcap/tidb/issues/44855) <span class="version-mark">New in v6.5.4 and v7.3.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`45132`](https://github.com/pingcap/tidb/issues/45132) <span class="version-mark">New in v7.4.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`45798`](https://github.com/pingcap/tidb/issues/45798) <span class="version-mark">New in v7.5.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`46177`](https://github.com/pingcap/tidb/issues/46177) <span class="version-mark">New in v6.5.6, v7.1.3 and v7.5.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`52869`](https://github.com/pingcap/tidb/issues/52869) <span class="version-mark">New in v8.1.0</span> | Optimizer Fix Controls > Optimizer Fix Controls reference > [`56318`](https://github.com/pingcap/tidb/issues/56318)`
- Source Line Ranges: `27-101`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `optimizer`, `reference`, `plan-cache`, `partitioned-tables`, `dynamic-pruning`, `statistics`, `index-range-scan`, `indexjoin`, `access-path`, `generated-columns`, `index-merge`, `starter-tier`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0452_bdb60c5419`
- Source ID: `tidb-docs-8.1:optimizer-fix-controls.md#optimizer-fix-controls-reference`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4004a50f6ec99d277f8a6a2ab4aaeefdaf3aa2738e84262f4c18190f64a0f24b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-fix-controls#optimizer-fix-controls-reference
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-fix-controls.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the reference meanings, default values, possible values, or controlled behaviors of specific optimizer fix control IDs.
- Retrieval Keywords: Optimizer Fix Controls reference, 33031, 44262, 44389, 44823, 44830, 44855, 45132, 45798, 46177, 52869, 56318, plan cache for partitioned tables, Dynamic pruning mode GlobalStats, IndexRangeScan scan ranges, PointGet operator, IndexJoin Probe Selection IndexScan row count, access path heuristic threshold, generated columns, enforced plans, index merge, ORDER BY heavy expression twice
- Follow-up Guidance: The chunk lists each fix control ID with its default value, possible values, and the exact optimizer or plan cache behavior that the fix controls.
- Classification Note: This is classified as reference because the content is a catalog of individual fix control entries with identifier-specific defaults, values, and behavior descriptions.

## Official Source Content

## Optimizer Fix Controls reference
### [`33031`](https://github.com/pingcap/tidb/issues/33031) New in v8.0.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- This variable controls whether to allow plan cache for partitioned tables. If it is set to `ON`, neither [Prepared statement plan cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) nor [Non-prepared statement plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) will be enabled for [partitioned tables](https://docs.pingcap.com/tidb/stable/partitioned-table).
### [`44262`](https://github.com/pingcap/tidb/issues/44262) New in v6.5.3 and v7.2.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- This variable controls whether to allow the use of [Dynamic pruning mode](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) to access the partitioned table when the [GlobalStats](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-of-partitioned-tables-in-dynamic-pruning-mode) are missing.
### [`44389`](https://github.com/pingcap/tidb/issues/44389) New in v6.5.3 and v7.2.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- For filters such as `c = 10 and (a = 'xx' or (a = 'kk' and b = 1))`, this variable controls whether to try to build more comprehensive scan ranges for `IndexRangeScan`.
### [`44823`](https://github.com/pingcap/tidb/issues/44823) New in v7.3.0

- Default value: `200`
- Possible values: `[0, 2147483647]`
- To save memory, Plan Cache does not cache queries with parameters exceeding the specified number of this variable. `0` means no limit.
### [`44830`](https://github.com/pingcap/tidb/issues/44830) New in v6.5.7 and v7.3.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- This variable controls whether Plan Cache is allowed to cache execution plans with the `PointGet` operator generated during physical optimization.
### [`44855`](https://github.com/pingcap/tidb/issues/44855) New in v6.5.4 and v7.3.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- In some scenarios, when the `Probe` side of an `IndexJoin` operator contains a `Selection` operator, TiDB severely overestimates the row count of `IndexScan`. This might cause suboptimal query plans to be selected instead of `IndexJoin`.
- To mitigate this issue, TiDB has introduced an improvement. However, due to potential query plan fallback risks, this improvement is disabled by default.
- This variable controls whether to enable the preceding improvement.
### [`45132`](https://github.com/pingcap/tidb/issues/45132) New in v7.4.0

- Default value: `1000`
- Possible values: `[0, 2147483647]`
- This variable sets the threshold for the optimizer's heuristic strategy to select access paths. If the estimated rows for an access path (such as `Index_A`) is much smaller than that of other access paths (default `1000` times), the optimizer skips the cost comparison and directly selects `Index_A`.
- `0` means to disable this heuristic strategy.
### [`45798`](https://github.com/pingcap/tidb/issues/45798) New in v7.5.0

- Default value: `ON`
- Possible values: `ON`, `OFF`
- This variable controls whether Plan Cache is allowed to cache execution plans that access [generated columns](https://docs.pingcap.com/tidb/stable/generated-columns).
### [`46177`](https://github.com/pingcap/tidb/issues/46177) New in v6.5.6, v7.1.3 and v7.5.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- This variable controls whether the optimizer explores enforced plans during query optimization after finding an unenforced plan.
### [`52869`](https://github.com/pingcap/tidb/issues/52869) New in v8.1.0

- Default value: `OFF`
- Possible values: `ON`, `OFF`
- As stated in the **Note** of [Explain Statements Using Index Merge](https://docs.pingcap.com/tidb/stable/explain-index-merge#examples), if the optimizer can choose the single index scan method (other than full table scan) for a query plan, the optimizer will not automatically use index merge.
- You can remove this limitation by enabling this fix control. Removing this limitation enables the optimizer to choose index merge automatically in more queries, but might cause the optimizer to ignore the optimal execution plans. Therefore, it is recommended to conduct sufficient tests on actual use cases before removing this limitation to make sure that it will not cause performance regressions.
### [`56318`](https://github.com/pingcap/tidb/issues/56318)

> **Note:**
>
> This is only available for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter).

- Default value: `ON`
- Possible values: `ON`, `OFF`
- This variable controls whether to avoid calculating the heavy expression used in the `ORDER BY` statement twice.
