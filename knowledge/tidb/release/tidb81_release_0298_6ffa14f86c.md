# Ease of use features and dynamic configuration changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > New Features > Ease of use`
- Source Line Ranges: `132-187`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `online recovery`, `statistics`, `analyze status`, `dynamic configuration`, `system variables`, `global kill`, `api v2`, `upgrade`, `downgrade warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0298_6ffa14f86c`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#ease-of-use`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88f8f512c77faa5f11a0dee6f49719834307c998fd4d43af74d5145ade6ebee8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#ease-of-use
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when locating TiDB 6.1.0 ease-of-use changes such as online unsafe recovery, cluster-level `SHOW ANALYZE STATUS` history, dynamic configuration, `enable-global-kill`, or TiKV `api-version` V2 downgrade warnings.
- Retrieval Keywords: TiDB 6.1.0 Ease of use, online data recovery, multiple Region replicas are lost, PD Control, online unsafe recovery, SHOW ANALYZE STATUS, cluster-level statistics collection tasks, history statistics collection tasks, dynamic configuration, system variables, configuration file parameters, tidb_max_tiflash_threads, enable-global-kill, Global Kill, KILL TIDB ${id};, TiKV API V2, api-version, downgrading TiKV might result in data corruption
- Follow-up Guidance: The source also notes upgrade behavior for deprecated configuration items and warns that after enabling TiKV API V2, you cannot roll back a TiKV cluster to a version earlier than v6.1.0.
- Classification Note: This is a release-note chunk for shared self-managed ease-of-use features spanning PD, TiDB, TiKV, and TiFlash in TiDB 6.1.0.

## Official Source Content

### Ease of use

* Support a one-stop online data recovery when multiple replicas are lost

    Before TiDB v6.1.0, when multiple Region replicas are lost because of machine failure, users have to stop all TiKV servers and use TiKV Control to recover TiKV one by one. Since TiDB v6.1.0, the recovery process is fully automated, does not require to stop TiKV, and does not affect other applications online. The recovery process can be triggered using PD Control and provides a more user-friendly summary information.

    [User document](https://docs.pingcap.com/tidb/stable/online-unsafe-recovery), [#10483](https://github.com/tikv/tikv/issues/10483)

* Support viewing history statistics collection tasks

    You can use the `SHOW ANALYZE STATUS` statement to show cluster-level statistics collection tasks. Before TiDB v6.1.0, the `SHOW ANALYZE STATUS` statement shows instance-level tasks only, and history task records are cleared after a TiDB restart. Therefore, you cannot view history statistics collection time and details. Starting from TiDB v6.1.0, history records of statistics collection tasks are persisted and can be queried after a cluster restart, which provides a reference for troubleshooting query performance issues caused by statistics anomalies.

    [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-analyze-status)

* Support modifying TiDB, TiKV, and TiFlash configurations dynamically

  In earlier TiDB versions, after modifying a configuration item, you must restart the cluster to make the modification effective. This might interrupt online services. To address this issue, TiDB v6.1.0 introduces the dynamic configuration feature, which allows you to validate a parameter change without restarting the cluster. The specific optimizations are as follows:

    * Transform some TiDB configuration items to system variables, so that they can be modified dynamically and persisted. Note that the original configuration items are deprecated after transformation. For a detailed list of the transformed configuration items, see [Configuration file parameters](#configuration-file-parameters).
    * Support configuring some TiKV parameters online. For a detailed list of the parameters, see [Others](#others).
    * Transform the TiFlash configuration item `max_threads` to a system variable `tidb_max_tiflash_threads`, so that the configuration can be modified dynamically and persisted. Note that the original configuration item remains after transformation.

  For v6.1.0 clusters upgraded (including online and offline upgrades) from earlier versions, note that:

    * If the configuration items specified in the configuration file before the upgrade already exist, TiDB will automatically update the values of the configured items to those of the corresponding system variables during the upgrade process. In this way, after the upgrade, the system behavior is not affected by parameter optimization.
    * The automatic update mentioned above occurs only once during the upgrade. After the upgrade, the deprecated configuration items are no longer effective.

  This feature allows you to modify parameters dynamically, and validate and persist them, instead of restarting the system and interrupting services. This makes your daily maintenance easier.

  [User document](https://docs.pingcap.com/tidb/stable/dynamic-config)

* Support killing queries or connections globally

    You can control the Global Kill feature using the `enable-global-kill` configuration (enabled by default).

    Before TiDB v6.1.0, when an operation consumes a lot of resources and causes cluster stability issues, you have to connect to the target TiDB instance and then run the `KILL TIDB ${id};` command to terminate the target connection and operation. In the case of many TiDB instances, this method is not easy to use and prone to wrong operations. Starting from v6.1.0, the `enable-global-kill` configuration is introduced and enabled by default. You can run the kill command in any TiDB instance to terminate a specified connection and operation, without worrying about incorrectly terminating other queries or sessions by mistake when there is a proxy between the client and TiDB. Currently, TiDB does not support using Ctrl+C to terminate queries or sessions.

    [User document](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enable-global-kill-new-in-v610), [#8854](https://github.com/pingcap/tidb/issues/8854)

* TiKV API V2 (experimental)

    Before v6.1.0, when TiKV is used as Raw Key Value storage, TiKV only provides basic Key Value read and write capability because it only stores the raw data passed in by the client.

    TiKV API V2 provides a new Raw Key Value storage format and access interface, including:

    * The data is stored in MVCC and the change timestamp of the data is recorded. This feature will lay the foundation for implementing Change Data Capture and incremental backup and restore.
    * Data is scoped according to different usage and supports co-existence of a single TiDB cluster, Transactional KV, RawKV applications.

> **Warning:**
>

  Due to significant changes in the underlying storage format, after enabling API V2, you cannot roll back a TiKV cluster to a version earlier than v6.1.0. Downgrading TiKV might result in data corruption.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#api-version-new-in-v610), [#11745](https://github.com/tikv/tikv/issues/11745)
