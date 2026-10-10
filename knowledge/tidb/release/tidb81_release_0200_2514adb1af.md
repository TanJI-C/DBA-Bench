# Compatibility changes in variables and configuration

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > Compatibility changes | What's New in TiDB 5.0 > Compatibility changes > System variables | What's New in TiDB 5.0 > Compatibility changes > Configuration file parameters | What's New in TiDB 5.0 > Compatibility changes > Others`
- Source Line Ranges: `26-74`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `compatibility-changes`, `system-variables`, `configuration-parameters`, `default-values`, `upgrade-checks`, `gc`, `clustered-index`, `joint-consensus`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0200_2514adb1af`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da9ce41269c8cda8ff0e573a96375f6f430ed652a2584456a0146085f94ff096`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.0 compatibility changes for system variables, configuration file parameters, default values, upgrade checks, garbage collection controls, clustered index semantics, or Joint Consensus defaults.
- Retrieval Keywords: Compatibility changes, System variables, Configuration file parameters, tidb_executor_concurrency, tidb_projection_concurrency, tidb_skip_ascii_check, tidb_enable_strict_double_type_check, tidb_dml_batch_size, set global, tidb_enable_noop_functions, CREATE TEMPORARY TABLE, tidb_gc_concurrency, tidb_gc_enable, tidb_gc_life_time, tidb_gc_run_interval, tidb_gc_scan_lock_mode, enable-joint-consensus, tidb_enable_amend_pessimistic_txn, ON or OFF, tidb_enable_clustered_index, INT_ONLY, index-limit, enable-enum-length-limit, tidb_txn_mode, performance.server-memory-quota, tikv-client.copr-cache.capacity-mb, rocksdb.rate-limiter-auto-tuned, raftstore.sync-log, gc.enable-compaction-filter, enable-cross-table-merge, feedback-probability, panic in the recoverable goroutine, VARCHAR, CHAR
- Follow-up Guidance: The chunk also includes upgrade-related notes about using `set global` for `tidb_dml_batch_size`, checking `feedback-probability` before upgrade, and the 5.0 RC to 5.0 GA display change from `OFF` to `INT_ONLY` for `tidb_enable_clustered_index`.
- Classification Note: This is a compatibility-changes chunk because the content lists added variables, replaced or deleted configuration items, changed defaults, and upgrade-impacting behavioral changes in TiDB 5.0.

## Official Source Content

## Compatibility changes
### System variables

+ Add the [`tidb_executor_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_executor_concurrency-new-in-v50) system variable to control the concurrency of multiple operators. The previous `tidb_*_concurrency` settings (such as `tidb_projection_concurrency`) still take effect but with a warning when you use them.
+ Add the [`tidb_skip_ascii_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_ascii_check-new-in-v50) system variable to specify whether to skip the ASCII validation check when the ASCII character set is written. This default value is `OFF`.
+ Add the [`tidb_enable_strict_double_type_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_strict_double_type_check-new-in-v50) system variable to determine whether the syntax like `double(N)` can be defined in the table schema. This default value is `OFF`.
+ Change the default value of [`tidb_dml_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_batch_size) from `20000` to `0`. This means that batch DML statements are no longer used by default in `LOAD`/`INSERT INTO SELECT ...`. Instead, large transactions are used to comply with the strict ACID semantics.

    > **Note:**
    >
    > The scope of the variable is changed from session to global, and the default value is changed from `20000` to `0`. If the application relies on the original default value, you need to use the `set global` statement to modify the variable to the original value after the upgrade.

+ Control temporary tables' syntax compatibility using the [`tidb_enable_noop_functions`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_noop_functions-new-in-v40) system variable. When this variable value is `OFF`, the `CREATE TEMPORARY TABLE` syntax returns an error.
+ Add the following system variables to directly control the garbage collection-related parameters:
    - [`tidb_gc_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_concurrency-new-in-v50)
    - [`tidb_gc_enable`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_enable-new-in-v50)
    - [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50)
    - [`tidb_gc_run_interval`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_run_interval-new-in-v50)
    - [`tidb_gc_scan_lock_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_scan_lock_mode-new-in-v50)
+ Change the default value of [`enable-joint-consensus`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-joint-consensus-new-in-v50) from `false` to `true`, which enables the Joint Consensus feature by default.
+ Change the value of `tidb_enable_amend_pessimistic_txn` from `0` or `1` to `ON` or `OFF`.
+ Change the default value of [`tidb_enable_clustered_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_clustered_index-new-in-v50) from `OFF` to `INT_ONLY` with the following new meanings:
    + `ON`: clustered index is enabled. Adding or deleting non-clustered indexes is supported.
    + `OFF`: clustered index is disabled. Adding or deleting non-clustered indexes is supported.
    + `INT_ONLY`: the default value. The behavior is consistent with that before v5.0. You can control whether to enable clustered index for the INT type together with `alter-primary-key = false`.

    > **Note:**
    >
    > The `INT_ONLY` value of `tidb_enable_clustered_index` in 5.0 GA has the same meaning as the `OFF` value in 5.0 RC. After upgrading from a 5.0 RC cluster with the `OFF` setting to 5.0 GA, it will be displayed as `INT_ONLY`.
### Configuration file parameters

+ Add the [`index-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#index-limit-new-in-v50) configuration item for TiDB. Its value defaults to `64` and ranges between `[64,512]`. A MySQL table supports 64 indexes at most. If its value exceeds the default setting and more than 64 indexes are created for a table, when the table schema is re-imported into MySQL, an error will be reported.
+ Add the [`enable-enum-length-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-enum-length-limit-new-in-v50) configuration item for TiDB to be compatible and consistent with MySQL's ENUM/SET length (ENUM length < 255). The default value is `true`.
+ Replace the `pessimistic-txn.enable` configuration item with the [`tidb_txn_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_mode) environment variable.
+ Replace the `performance.max-memory` configuration item with [`performance.server-memory-quota`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#server-memory-quota-new-in-v409)
+ Replace the `tikv-client.copr-cache.enable` configuration item with [`tikv-client.copr-cache.capacity-mb`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#capacity-mb). If the item's value is `0.0`, this feature is disabled. If the item's value is greater than `0.0`, this feature is enabled. Its default value is `1000.0`.
+ Replace the `rocksdb.auto-tuned` configuration item with [`rocksdb.rate-limiter-auto-tuned`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rate-limiter-auto-tuned-new-in-v50).
+ Delete the `raftstore.sync-log` configuration item. By default, written data is forcibly spilled to the disk. Before v5.0, you can explicitly disable `raftstore.sync-log`. Since v5.0, the configuration value is forcibly set to `true`.
+ Change the default value of the `gc.enable-compaction-filter` configuration item from `false` to `true`.
+ Change the default value of the `enable-cross-table-merge` configuration item from `false` to `true`.
+ Change the default value of the [`rate-limiter-auto-tuned`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#rate-limiter-auto-tuned-new-in-v50) configuration item from `false` to `true`.
### Others

+ Before the upgrade, check the value of the TiDB configuration [`feedback-probability`](https://docs.pingcap.com/tidb/v5.0/tidb-configuration-file#feedback-probability). If the value is not 0, the "panic in the recoverable goroutine" error will occur after the upgrade, but this error does not affect the upgrade.
+ Forbid conversion between `VARCHAR` type and `CHAR` type during the column type change to avoid data correctness issues.
