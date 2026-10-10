# Compatibility changes and system variable updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Compatibility changes | TiDB 7.6.0 Release Notes > Compatibility changes > MySQL compatibility | TiDB 7.6.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `255-279`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `sql`
- Topic Tags: `upgrade`, `compatibility`, `mysql-compatibility`, `load-data`, `system-variables`, `ddl-v2`, `global-index`, `analyze`, `transaction-timeout`, `plan-digest`, `active-pd-follower`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0564_d4eef15978`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `621c6bfbc1312242a2693406060a5f8f03a82f36fcfad5aef9ad1ca976f5cee6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 7.6.0 compatibility changes for LOAD DATA behavior and the list of added or modified system variables introduced in the release.
- Retrieval Keywords: TiDB 7.6.0 compatibility changes, MySQL compatibility LOAD DATA, LOAD DATA transaction behavior same way as MySQL, LOAD DATA explicit commit or roll back, tidb_auto_analyze_partition_batch_size, tidb_sysproc_scan_concurrency, tidb_analyze_distsql_scan_concurrency, tidb_ddl_version, TiDB DDL V2, tidb_enable_global_index, tidb_idle_transaction_timeout, tidb_ignore_inlist_plan_digest, tidb_opt_enable_fuzzy_binding, tidb_txn_entry_size_limit, pd_enable_follower_handle_region, Active PD Follower
- Follow-up Guidance: The source notes these are upgrade-related compatibility changes from v7.5.0 to v7.6.0 and that upgrades from v7.4.0 or earlier might also require checking intermediate versions.
- Classification Note: This is a release-note compatibility section covering MySQL compatibility changes and system variable additions or modifications in TiDB 7.6.0.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v7.5.0 to the current version (v7.6.0). If you are upgrading from v7.4.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### MySQL compatibility

* Before TiDB v7.6.0, the `LOAD DATA` operation commits all rows in a single transaction or commits transactions in a batch, which is slightly different from MySQL behaviors. Starting from v7.6.0, TiDB processes `LOAD DATA` in transactions in the same way as MySQL. The `LOAD DATA` statement in a transaction no longer automatically commits the current transaction or starts a new transaction. Moreover, you can explicitly commit or roll back the `LOAD DATA` statement in a transaction. Additionally, the `LOAD DATA` statement is affected by the TiDB transaction mode setting (optimistic or pessimistic transaction). [#49079](https://github.com/pingcap/tidb/pull/49079) @[ekexium](https://github.com/ekexium)
### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`tidb_auto_analyze_partition_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_partition_batch_size-new-in-v640) | Modified | Changes the default value from `1` to `128` after further tests.  |
| [`tidb_sysproc_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_sysproc_scan_concurrency-new-in-v650) | Modified  | In a large-scale cluster, the concurrency of `scan` operations can be adjusted higher to meet the needs of `ANALYZE`. Therefore, change the maximum value from `256` to `4294967295`.  |
| [`tidb_analyze_distsql_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_distsql_scan_concurrency-new-in-v760)       |    Newly added       |    Sets the concurrency of the `scan` operation when executing the `ANALYZE` operation. The default value is `4`.  |
| [`tidb_ddl_version`](https://docs.pingcap.com/tidb/v7.6/system-variables#tidb_ddl_version-new-in-v760)  |  Newly added  | Controls whether to enable [TiDB DDL V2](https://docs.pingcap.com/tidb/v7.6/ddl-v2). Set the value to `2` to enable it and `1` to disable it. The default value is `1`. When TiDB DDL V2 is enabled, DDL statements will be executed using TiDB DDL V2. The execution speed of DDL statements for creating tables is increased by 10 times compared with TiDB DDL V1. |
| [`tidb_enable_global_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_global_index-new-in-v760)  |  Newly added   | Controls whether to support creating `Global indexes` for partitioned tables. The default value is `OFF`. `Global index` is currently in the development stage. **It is not recommended to modify the value of this system variable**. |
| [`tidb_idle_transaction_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_idle_transaction_timeout-new-in-v760) | Newly added | Controls the idle timeout for transactions in a user session. When a user session is in a transactional state and remains idle for a duration exceeding the value of this variable, TiDB will terminate the session. The default value `0` means unlimited. |
| [`tidb_ignore_inlist_plan_digest`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_ignore_inlist_plan_digest-new-in-v760) | Newly added | Controls whether TiDB ignores the element differences in the `IN` list across different queries when generating Plan Digests. The default value `OFF` means differences are not ignored. |
| [`tidb_opt_enable_fuzzy_binding`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_fuzzy_binding-new-in-v760) | Newly added | Controls whether to enable the cross-database binding feature. The default value `OFF` means cross-database binding is disabled. |
| [`tidb_txn_entry_size_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_entry_size_limit-new-in-v760) | Newly added | Dynamically modifies the TiDB configuration item [`performance.txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500). It limits the size of a single row of data in TiDB. The default value of this variable is `0`, which means that TiDB uses the value of the configuration item `txn-entry-size-limit` by default. When this variable is set to a non-zero value, `txn-entry-size-limit` is also set to the same value. |
| [`pd_enable_follower_handle_region`](https://docs.pingcap.com/tidb/stable/system-variables#pd_enable_follower_handle_region-new-in-v760) | Newly added | Controls whether to enable the [Active PD Follower](https://docs.pingcap.com/tidb/stable/tune-region-performance#use-the-active-pd-follower-feature-to-enhance-the-scalability-of-pds-region-information-query-service) feature (experimental). When the value is `OFF`, TiDB only obtains Region information from the PD leader. When the value is `ON`, TiDB evenly distributes requests for Region information to all PD servers, and PD followers can also handle Region requests, thereby reducing the CPU pressure on the PD leader. |
