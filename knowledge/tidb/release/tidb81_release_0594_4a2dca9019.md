# Compatibility changes: behavior changes and system variable updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Compatibility changes | TiDB 8.1.0 Release Notes > Compatibility changes > Behavior changes | TiDB 8.1.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `160-180`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `tidb`, `ticdc`, `pd`
- Topic Tags: `upgrade`, `compatibility`, `behavior-changes`, `system-variables`, `deprecated`, `telemetry`, `auto-analyze`, `distributed-execution-framework`, `service-scope`, `tls`, `auto-increment`, `force-rebase`, `split-update`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0594_4a2dca9019`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3dea967c8af7e845ecdea55728000f7888432165c91a7bbd5c3462aee9798001`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 8.1.0 compatibility changes involving Lightning TLS values, auto-increment failover behavior, TiCDC split-update behavior, or system variable changes.
- Retrieval Keywords: Compatibility changes, Behavior changes, System variables, tidb.tls, false, skip-verify, preferred, AUTO_ID_CACHE=1, forceRebase, centralized auto-increment ID allocating service, TiCDC split UPDATE into DELETE and INSERT, commitTS, thresholdTS, tidb_enable_telemetry, tidb_auto_analyze_ratio, tidb_enable_dist_task, tidb_service_scope, Task scheduling
- Follow-up Guidance: See the linked documentation for the detailed behavior and variable descriptions.
- Classification Note: This chunk is classified as compatibility changes, including behavior changes and system variable updates for TiDB 8.1.0.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v8.0.0 to the current version (v8.1.0). If you are upgrading from v7.6.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### Behavior changes

* In earlier versions, the `tidb.tls` configuration item in TiDB Lightning treats values `"false"` and `""` the same, as well as treating the values `"preferred"` and `"skip-verify"` the same. Starting from v8.1.0, TiDB Lightning distinguishes the behavior of `"false"`, `""`, `"skip-verify"`, and `"preferred"` for `tidb.tls`. For more information, see [TiDB Lightning configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
* For tables with `AUTO_ID_CACHE=1`, TiDB supports a [centralized auto-increment ID allocating service](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode). In earlier versions, the primary TiDB node of this service automatically performs a `forceRebase` operation when the TiDB process exits (for example, during the TiDB node restart) to keep auto-assigned IDs as consecutive as possible. However, when there are too many tables with `AUTO_ID_CACHE=1`, executing `forceRebase` becomes very time-consuming, preventing TiDB from restarting promptly and even blocking data writes, thus affecting system availability. To resolve this issue, starting from v8.1.0, TiDB removes the `forceRebase` behavior, but this change will cause some auto-assigned IDs to be non-consecutive during the failover.
* In earlier versions, when processing a transaction containing `UPDATE` changes, if the primary key or non-null unique index value is modified in an `UPDATE` event, TiCDC splits this event into `DELETE` and `INSERT` events. In v8.1.0, when using the MySQL sink, TiCDC splits an `UPDATE` event into `DELETE` and `INSERT` events if the transaction `commitTS` for the `UPDATE` change is less than TiCDC `thresholdTS` (which is the current timestamp that TiCDC fetches from PD at TiCDC startup). This behavior change addresses the issue of downstream data inconsistencies caused by the potentially incorrect order of `UPDATE` events received by TiCDC, which can lead to an incorrect order of split `DELETE` and `INSERT` events. For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-split-update-behavior#split-update-events-for-mysql-sinks).
### System variables

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`tidb_enable_telemetry`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_telemetry-new-in-v402-and-deprecated-in-v810) | Deprecated | Starting from v8.1.0, the telemetry feature in TiDB is removed, and this variable is no longer functional. It is retained solely for compatibility with earlier versions. |
| [`tidb_auto_analyze_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_auto_analyze_ratio) | Modified | Changes the value range from `[0, 18446744073709551615]` to `(0, 1]`. |
| [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) | Modified | Changes the default value from `OFF` to `ON`. This means that Distributed eXecution Framework (DXF) is enabled by default, which fully utilizes the resources of the TiDB cluster and greatly improves the performance of `ADD INDEX` and `IMPORT INTO` tasks. If you want to upgrade a cluster with the DXF enabled to v8.1.0 or later, disable the DXF (by setting `tidb_enable_dist_task` to `OFF`) before the upgrade, which avoids `ADD INDEX` operations during the upgrade causing data index inconsistency. After the upgrade, you can manually enable the DXF. |
| [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) | Modified | Changes the optional value from `""` or `background` to a string with a length of up to 64 characters, which enables you to control the service scope of each TiDB node more flexibly. Valid characters include digits `0-9`, letters `a-zA-Z`, underscores `_`, and hyphens `-`. The Distributed eXecution Framework (DXF) determines which TiDB nodes can be scheduled to execute distributed tasks based on the value of this variable. For specific rules, see [Task scheduling](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework#task-scheduling). |
