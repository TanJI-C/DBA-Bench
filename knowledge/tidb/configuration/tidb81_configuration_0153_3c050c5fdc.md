# ANALYZE concurrency controls and related references

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Manage `ANALYZE` tasks and concurrency > Control `ANALYZE` concurrency | Introduction to Statistics > Manage `ANALYZE` tasks and concurrency > Control `ANALYZE` concurrency > `tidb_build_stats_concurrency` | Introduction to Statistics > Manage `ANALYZE` tasks and concurrency > Control `ANALYZE` concurrency > `tidb_build_sampling_stats_concurrency` | Introduction to Statistics > Manage `ANALYZE` tasks and concurrency > Control `ANALYZE` concurrency > `tidb_analyze_partition_concurrency` | Introduction to Statistics > Manage `ANALYZE` tasks and concurrency > Control `ANALYZE` concurrency > `tidb_analyze_distsql_scan_concurrency` | Introduction to Statistics > See also`
- Source Line Ranges: `754-809`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `analyze`, `concurrency`, `system-variables`, `sampling`, `partitions`, `distsql`, `statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0153_3c050c5fdc`
- Source ID: `tidb-docs-8.1:statistics.md#control-analyze-concurrency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63bf6e8df10d02882682321ffa34f46726124a4e0c2bdb3765e52917246be0b3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#control-analyze-concurrency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented `ANALYZE` concurrency system variables, their relationship, defaults, and what parts of statistics collection they control.
- Retrieval Keywords: Control `ANALYZE` concurrency, tidb_build_stats_concurrency, tidb_build_sampling_stats_concurrency, tidb_analyze_partition_concurrency, tidb_analyze_distsql_scan_concurrency, actual total concurrency, building statistics during manual `ANALYZE`, merging samples collected from different Regions, saving `ANALYZE` results, scanning TiKV Regions
- Follow-up Guidance: The source also lists related references: `LOAD STATS`, `DROP STATS`, `LOCK STATS`, `UNLOCK STATS`, and `SHOW STATS_LOCKED`.
- Classification Note: This is classified as configuration because the content defines system variables that control `ANALYZE` concurrency, their interaction, and default values.

## Official Source Content

### Control `ANALYZE` concurrency

When you run the `ANALYZE` statement, you can adjust the concurrency using system variables, to control its effect on the system.

The relationships of the relevant system variables are shown below:

![analyze_concurrency](/media/analyze_concurrency.png)

`tidb_build_stats_concurrency`, `tidb_build_sampling_stats_concurrency`, and `tidb_analyze_partition_concurrency` are in an upstream-downstream relationship, as shown in the preceding diagram. The actual total concurrency is: `tidb_build_stats_concurrency` * (`tidb_build_sampling_stats_concurrency` + `tidb_analyze_partition_concurrency`). When modifying these variables, you need to consider their respective values at the same time. It is recommended to adjust them one by one in the order of `tidb_analyze_partition_concurrency`, `tidb_build_sampling_stats_concurrency`, `tidb_build_stats_concurrency`, and observe the impact on the system. The larger the values of these three variables, the greater the resource overhead on the system.
#### `tidb_build_stats_concurrency`

This variable controls the concurrency for building statistics during manual `ANALYZE`, such as the number of table or partition analysis tasks that can be processed simultaneously. The default value is `2`. The default value is `4` for v7.4.0 and earlier versions.
#### `tidb_build_sampling_stats_concurrency`

This variable controls the following aspects of `ANALYZE` concurrency:

- The concurrency for merging samples collected from different Regions.
- The concurrency for collecting statistics on special indexes (such as indexes on generated virtual columns), for example, the number of indexes that TiDB can concurrently collect statistics for.

The default value is `2`.
#### `tidb_analyze_partition_concurrency`

This variable controls the concurrency for saving `ANALYZE` results (writing TopN and histograms to system tables). The default value is `2`. The default value is `1` for v7.4.0 and earlier versions.
#### `tidb_analyze_distsql_scan_concurrency`

This variable controls the following aspects of `ANALYZE` concurrency:

- The concurrency of scanning TiKV Regions.
- The concurrency of scanning Regions for special indexes (indexes generated from virtual columns).

The default value is `4`.
## See also

* [LOAD STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-stats)
* [DROP STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-stats)
* [LOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats)
* [UNLOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats)
* [SHOW STATS_LOCKED](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-locked)

* [LOAD STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-stats)
* [LOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-lock-stats)
* [UNLOCK STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-unlock-stats)
* [SHOW STATS_LOCKED](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-stats-locked)
