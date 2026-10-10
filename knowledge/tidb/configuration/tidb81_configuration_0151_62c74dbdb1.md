# Statement summary persistence limitations and enablement

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statement-summary-tables.md`
- Source Title: `Statement Summary Tables`
- Source Heading Path: `Statement Summary Tables > Limitation | Statement Summary Tables > Persist statements summary`
- Source Line Ranges: `210-266`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `statement-summary`, `persistence`, `restart`, `experimental-feature`, `configuration-file`, `history-data`, `disk-storage`, `retention`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0151_62c74dbdb1`
- Source ID: `tidb-docs-8.1:statement-summary-tables.md#limitation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7c9792caf3932ddb8c319053c2fc3e46937cc49a336682376cb0de54cf285a5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statement-summary-tables#limitation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statement-summary-tables.md

## Retrieval Guidance

- Use When: Use this content when you need the documented limitation that statement summary data is in memory by default, or the Self-Managed configuration details and caveats for enabling `tidb_stmt_summary_enable_persistent` so history data is written to disk and survives TiDB server restarts.
- Retrieval Keywords: statement summary persistence, tidb_stmt_summary_enable_persistent, TiDB Self-Managed, statements_summary_history, cluster_statements_summary_history, tidb_stmt_summary_filename, tidb_stmt_summary_file_max_days, tidb_stmt_summary_file_max_size, tidb_stmt_summary_file_max_backups, history data written to disk, data lost after TiDB server restarts, experimental feature, tidb_stmt_summary_refresh_interval
- Follow-up Guidance: The source provides the `[instance]` configuration snippet for `tidb_stmt_summary_enable_persistent = true` and notes that queries on `statements_summary_history` or `cluster_statements_summary_history` combine in-memory and on-disk data after persistence is enabled.
- Classification Note: This is classified as configuration because it describes the persistence-related configuration items, their applicability and defaults, and how they change statement summary storage and retention behavior.

## Official Source Content

## Limitation

By default, statements summary tables are saved in memory. When a TiDB server restarts, all data will be lost.

To address this issue, TiDB v6.6.0 experimentally introduces the [statement summary persistence](#persist-statements-summary) feature, which is disabled by default. After this feature is enabled, the history data is no longer saved in memory, but directly written to disks. In this way, the history data is still available if a TiDB server restarts.
## Persist statements summary

This section is only applicable to TiDB Self-Managed. For TiDB Cloud, the value of the `tidb_stmt_summary_enable_persistent` parameter is `false` by default and does not support dynamic modification.

> **Warning:**
>
> Statements summary persistence is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

As described in the [Limitation](#limitation) section, statements summary tables are saved in memory by default. Once a TiDB server restarts, all the statements summary will be lost. Starting from v6.6.0, TiDB experimentally provides the configuration item [`tidb_stmt_summary_enable_persistent`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_enable_persistent-new-in-v660) to allow users to enable or disable statements summary persistence.

As described in the [Limitation](#limitation) section, statements summary tables are saved in memory by default. Once a TiDB server restarts, all the statements summary will be lost. Starting from v6.6.0, TiDB experimentally provides the configuration item `tidb_stmt_summary_enable_persistent` to allow users to enable or disable statements summary persistence.

To enable statements summary persistence, you can add the following configuration items to the TiDB configuration file:

```toml
[instance]
tidb_stmt_summary_enable_persistent = true
# The following entries use the default values, which can be modified as needed.
# tidb_stmt_summary_filename = "tidb-statements.log"
# tidb_stmt_summary_file_max_days = 3
# tidb_stmt_summary_file_max_size = 64 # MiB
# tidb_stmt_summary_file_max_backups = 0
```

After statements summary persistence is enabled, the memory keeps only the current real-time data and no history data. Once the real-time data is refreshed as history data, the history data is written to the disk at an interval of `tidb_stmt_summary_refresh_interval` described in the [Parameter configuration](#parameter-configuration) section. Queries on the `statements_summary_history` or `cluster_statements_summary_history` table will return results combining both in-memory and on-disk data.

> **Note:**
>
> - When statements summary persistence is enabled, the `tidb_stmt_summary_history_size` configuration described in the [Parameter configuration](#parameter-configuration) section will no longer take effect because the memory does not keep the history data. Instead, the following three configurations will be used to control the retention period and size of history data for persistence: [`tidb_stmt_summary_file_max_days`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_days-new-in-v660), [`tidb_stmt_summary_file_max_size`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_size-new-in-v660), and [`tidb_stmt_summary_file_max_backups`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tidb_stmt_summary_file_max_backups-new-in-v660).
> - The smaller the value of `tidb_stmt_summary_refresh_interval`, the more immediate data is written to the disk. However, this also means more redundant data is written to the disk.
