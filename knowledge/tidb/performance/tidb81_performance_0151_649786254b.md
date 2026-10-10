# Stability improvements for scheduling and region merge

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Improve stability | What's New in TiDB 5.0 > Improve stability > Optimize the performance jitter issue caused by imperfect scheduling | What's New in TiDB 5.0 > Improve stability > Optimize the performance jitter issue caused by imperfect scheduling > Introduce new scheduling calculation formulas to reduce unnecessary scheduling and performance jitter | What's New in TiDB 5.0 > Improve stability > Optimize the performance jitter issue caused by imperfect scheduling > Enable the cross-table Region merge feature by default`
- Source Line Ranges: `275-296`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`
- Topic Tags: `stability`, `performance-jitter`, `scheduling`, `region-score`, `store-limit`, `cross-table-merge`, `region-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0151_649786254b`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#improve-stability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40a6cc3b4c9c7c7906b26a1a7256fae7de1c8d00388c956346b40284ac5007b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#improve-stability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this content when you need PD stability and scheduling release notes about performance jitter, new region score formulas, store-limit effects, or cross-table Region merge defaults in TiDB 5.0.
- Retrieval Keywords: performance jitter, scheduling, store-limit, region-score-formula-version, region-score-formula-version = v1, cross-table Region merge, enable-cross-table-merge, schedule.enable-cross-table-merge, empty Regions, QPS, delay, TPC-C tpmC
- Follow-up Guidance: The content says PD introduces new default scheduling calculation formulas and that the cross-table Region merge feature is enabled by default starting from v5.0, with `schedule.enable-cross-table-merge` available to disable it.
- Classification Note: This is classified as performance content because it focuses on reducing unnecessary scheduling, resource contention, and Region overhead to improve cluster stability and reduce performance jitter.

## Official Source Content

## Improve stability
### Optimize the performance jitter issue caused by imperfect scheduling

[#18005](https://github.com/pingcap/tidb/issues/18005)

The TiDB scheduling process occupies resources such as I/O, network, CPU, and memory. If TiDB does not control the scheduled tasks, QPS and delay might cause performance jitter due to resource preemption.

After the following optimizations, in the 8-hour performance test, the standard deviation of TPC-C tpmC does not exceed 2%.
#### Introduce new scheduling calculation formulas to reduce unnecessary scheduling and performance jitter

When the node capacity is always near the waterline set in the system, or when the `store-limit` is set too large, to balance the capacity load, the system frequently schedules Regions to other nodes or even schedules Regions back to their original nodes. Because scheduling occupies resources, such as I/O, network, CPU, and memory, and causes performance jitter, this type of scheduling is not necessary.

To mitigate this issue, PD introduces a new set of default scheduling calculation formulas. You can switch back to the old formulas by configuring `region-score-formula-version = v1`.
#### Enable the cross-table Region merge feature by default

[User document](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-cross-table-merge)

Before v5.0, TiDB disables the cross-table Region merge feature by default. Starting from v5.0, this feature is enabled by default to reduce the number of empty Regions and the overhead of network, memory, and CPU. You can disable this feature by modifying the `schedule.enable-cross-table-merge` configuration item.
