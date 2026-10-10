# Observability and data migration feature details

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.3.0.md`
- Source Title: `TiDB 7.3.0 Release Notes`
- Source Heading Path: `TiDB 7.3.0 Release Notes > Feature details > Observability | TiDB 7.3.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `116-149`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `lightning`, `tikv`
- Topic Tags: `statistics-progress`, `analyze-jobs`, `show-analyze-status`, `plan-replayer`, `historical-statistics`, `data-import`, `conflict-detection`, `physical-import-mode`, `logical-import-mode`, `partitioned-raft-kv`, `diagnostic-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0496_4587aed783`
- Source ID: `tidb-docs-8.1:releases/release-7.3.0.md#observability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0061bd7f655c603c5cddb60810c6228b6e5b890a43e2796585404b503a63d56d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.3.0#observability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.3.0 feature details about statistics progress visibility, Plan Replayer historical statistics export, or TiDB Lightning data import conflict handling and diagnostic logging changes.
- Retrieval Keywords: mysql.analyze_jobs, SHOW ANALYZE STATUS, show the progress of collecting statistics, Plan Replayer, dump with stats as of timestamp, historical statistics, TiDB Lightning, conflict detection, Logical Import Mode, Physical Import Mode, error, replace, ignore, conflict records, Partitioned Raft KV, enable-diagnose-log, lightning/main, client-go, tidb
- Follow-up Guidance: The source points to documentation for SHOW ANALYZE STATUS, SQL Plan Replayer, TiDB Lightning conflict detection, and the TiDB Lightning global configuration parameter enable-diagnose-log.
- Classification Note: This is classified as a release feature-details chunk because it introduces new observability and data migration capabilities in TiDB 7.3.0 across TiDB, TiDB Lightning, and TiKV.

## Official Source Content

### Observability

* Show the progress of collecting statistics [#44033](https://github.com/pingcap/tidb/issues/44033) @[hawkingrei](https://github.com/hawkingrei)

    Collecting statistics for large tables often takes a long time. In previous versions, you cannot see the progress of collecting statistics, and therefore cannot predict the completion time. TiDB v7.3.0 introduces a feature to show the progress of collecting statistics. You can view the overall workload, current progress, and estimated completion time for each subtask using the system table `mysql.analyze_jobs` or `SHOW ANALYZE STATUS`. In scenarios such as large-scale data import and SQL performance optimization, this feature helps you understand the overall task progress and improves the user experience.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-analyze-status).

* Plan Replayer supports exporting historical statistics [#45038](https://github.com/pingcap/tidb/issues/45038) @[time-and-fate](https://github.com/time-and-fate)

    Starting from v7.3.0, with the newly added [`dump with stats as of timestamp`](https://docs.pingcap.com/tidb/stable/sql-plan-replayer) clause, you can use Plan Replayer to export the statistics of specified SQL-related objects at a specific point in time. During the diagnosis of execution plan issues, accurately capturing historical statistics can help analyze more precisely how the execution plan was generated at the time when the issue occurred. This helps identify the root cause of the issue and greatly improves efficiency in diagnosing execution plan issues.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-plan-replayer).
### Data migration

* TiDB Lightning introduces a new version of conflict data detection and handling strategy [#41629](https://github.com/pingcap/tidb/issues/41629) @[lance6716](https://github.com/lance6716)

    In previous versions, TiDB Lightning uses different conflict detection and handling methods for Logical Import Mode and Physical Import Mode, which are complex to configure and not easy for users to understand. In addition, Physical Import Mode cannot handle conflicts using the `replace` or `ignore` strategy. Starting from v7.3.0, TiDB Lightning introduces a unified conflict detection and handling strategy for both Logical Import Mode and Physical Import Mode. You can choose to report an error (`error`), replace (`replace`) or ignore (`ignore`) conflicting data when encountering conflicts. You can limit the number of conflict records, such as the task is interrupted and terminated after processing a specified number of conflict records. Furthermore, the system can record conflicting data for troubleshooting.

    For import data with many conflicts, it is recommended to use the new version of the conflict detection and handling strategy for better performance. In the lab environment, the new version strategy can improve the performance of conflict detection and handling up to three times faster than the old version. This performance value is for reference only. The actual performance might vary depending on your configuration, table structure, and the percentage of conflicting data. Note that the new version and the old version of the conflict strategy cannot be used at the same time. The old conflict detection and handling strategy will be deprecated in the future.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#conflict-detection).

* TiDB Lightning supports Partitioned Raft KV (experimental) [#14916](https://github.com/tikv/tikv/issues/14916) @[GMHDBJD](https://github.com/GMHDBJD)

    TiDB Lightning now supports Partitioned Raft KV. This feature helps improve the data import performance of TiDB Lightning.

* TiDB Lightning introduces a new parameter `enable-diagnose-log` to enhance troubleshooting by printing more diagnostic logs [#45497](https://github.com/pingcap/tidb/issues/45497) @[D3Hunter](https://github.com/D3Hunter)

    By default, this feature is disabled and TiDB Lightning only prints logs containing `lightning/main`. When enabled, TiDB Lightning prints logs for all packages (including `client-go` and `tidb`) to help diagnose issues related to `client-go` and `tidb`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-global).
