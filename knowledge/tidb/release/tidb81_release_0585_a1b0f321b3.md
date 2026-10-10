# Improvements for PD, TiFlash, BR, TiCDC, DM, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Improvements`
- Source Line Ranges: `404-449`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tiflash`, `br`, `ticdc`, `dm`, `lightning`, `tidb`, `tikv`
- Topic Tags: `improvements`, `high-availability`, `load-balancing`, `monitoring`, `alerting`, `etcd`, `grpc`, `json-functions`, `backup-restore`, `restore-performance`, `log-backup`, `replication`, `changefeed`, `data-migration`, `logical-import`, `tiflash-space`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0585_a1b0f321b3`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fef96f30b1ec7ac43e135ce2183378351ef9cc62559140b8a610c6087c0057e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when answering what improvements were introduced in TiDB 8.0.0 across PD, TiFlash, BR, TiCDC, DM, and TiDB Lightning, especially for high availability, monitoring, JSON functions, restore performance, replication, and logical import behavior.
- Retrieval Keywords: TiDB 8.0.0 improvements, PD client service discovery high availability load balancing, PD client retry mechanism, cgroup CPU and memory limits monitoring and alerting, etcd watch high availability, heartbeat monitoring metrics, unhealthy etcd nodes, GC safepoint pd-ctl, hotspot scheduler historical window configuration, GRPC configurations improve availability, TiFlash JSON_EXTRACT json_path non-constant values, TiFlash JSON_LENGTH(json, path), BR --load-stats, BR --tikv-max-restore-concurrency, coarse-grained Region scatter algorithm, br log command help information, pre-allocating Table ID during restore, disable GC memory limit tuner feature within TiDB when using BR, merging SST files during data restore, creating databases in batch during data restore, slowest Region affects global checkpoint advancement, RESTORE statement table creation performance, TiCDC RowChangedEvent memory consumption, changefeed start-ts parameter valid, DM less than global checkpoint position, MariaDB primary secondary replication gtid_strict_mode off, TiDB Lightning logical-import-batch-rows, TiFlash insufficient space error
- Follow-up Guidance: The chunk also lists exact option names and phrases such as `--load-stats`, `--tikv-max-restore-concurrency`, `logical-import-batch-rows`, `JSON_EXTRACT()`, `JSON_LENGTH(json, path)`, and the DM error `less than global checkpoint position`.
- Classification Note: This is a release-notes improvement summary for multiple shared components in self-managed TiDB 8.0.0, covering operational, SQL-function, backup and restore, replication, migration, and import enhancements.

## Official Source Content

- Enhance the service discovery capability of the PD client to improve its high availability and load balancing [#7576](https://github.com/tikv/pd/issues/7576) @[CabinfeverB](https://github.com/CabinfeverB)
    - Enhance the retry mechanism of the PD client [#7673](https://github.com/tikv/pd/issues/7673) @[JmPotato](https://github.com/JmPotato)
    - Add monitoring and alerting for cgroup CPU and memory limits [#7716](https://github.com/tikv/pd/issues/7716) [#7918](https://github.com/tikv/pd/issues/7918) @[pingandb](https://github.com/pingandb) @[rleungx](https://github.com/rleungx)
    - Improve the performance and high availability when using etcd watch [#7738](https://github.com/tikv/pd/issues/7738) [#7724](https://github.com/tikv/pd/issues/7724) [#7689](https://github.com/tikv/pd/issues/7689) @[lhy1024](https://github.com/lhy1024)
    - Add more monitoring metrics for heartbeat to better analyze performance bottlenecks [#7868](https://github.com/tikv/pd/issues/7868) @[nolouch](https://github.com/nolouch)
    - Reduce the impact of the etcd leader on the PD leader [#7499](https://github.com/tikv/pd/issues/7499) @[JmPotato](https://github.com/JmPotato) @[HuSharp](https://github.com/HuSharp)
    - Enhance the detection mechanism for unhealthy etcd nodes [#7730](https://github.com/tikv/pd/issues/7730) @[JmPotato](https://github.com/JmPotato) @[HuSharp](https://github.com/HuSharp)
    - Optimize the output of GC safepoint in pd-ctl [#7767](https://github.com/tikv/pd/issues/7767) @[nolouch](https://github.com/nolouch)
    - Support dynamic modification of the historical window configuration in the hotspot scheduler [#7877](https://github.com/tikv/pd/issues/7877) @[lhy1024](https://github.com/lhy1024)
    - Reduce the lock contention issue in creating operators [#7837](https://github.com/tikv/pd/issues/7837) @[Leavrth](https://github.com/Leavrth)
    - Adjust GRPC configurations to improve availability [#7821](https://github.com/tikv/pd/issues/7821) @[rleungx](https://github.com/rleungx)

+ TiFlash

    - Support using non-constant values for the `json_path` argument in the `JSON_EXTRACT()` function [#8510](https://github.com/pingcap/tiflash/issues/8510) @[SeaRise](https://github.com/SeaRise)
    - Support the `JSON_LENGTH(json, path)` function [#8711](https://github.com/pingcap/tiflash/issues/8711) @[SeaRise](https://github.com/SeaRise)

+ Tools

    + Backup & Restore (BR)

        - Introduce a new restore parameter `--load-stats` for the `br` command-line tool, which controls whether to restore statistics [#50568](https://github.com/pingcap/tidb/issues/50568) @[Leavrth](https://github.com/Leavrth)
        - Introduce a new restore parameter `--tikv-max-restore-concurrency` for the `br` command-line tool, which controls the maximum number of download and ingest files for each TiKV node. This parameter also controls the memory consumption of a BR node by controlling the maximum length of the job queue. [#51621](https://github.com/pingcap/tidb/issues/51621) @[3pointer](https://github.com/3pointer)
        - Enhance restore performance by enabling the coarse-grained Region scatter algorithm to adaptively obtain concurrent parameters [#50701](https://github.com/pingcap/tidb/issues/50701) @[3pointer](https://github.com/3pointer)
        - Display the `log` command in the command-line help information of `br` [#50927](https://github.com/pingcap/tidb/issues/50927) @[RidRisR](https://github.com/RidRisR)
        - Support pre-allocating Table ID during the restore process to maximize the reuse of Table ID and improve restore performance [#51736](https://github.com/pingcap/tidb/issues/51736) @[Leavrth](https://github.com/Leavrth)
        - Disable the GC memory limit tuner feature within TiDB when using BR to avoid OOM issues [#51078](https://github.com/pingcap/tidb/issues/51078) @[Leavrth](https://github.com/Leavrth)
        - Improve the speed of merging SST files during data restore by using a more efficient algorithm [#50613](https://github.com/pingcap/tidb/issues/50613) @[Leavrth](https://github.com/Leavrth)
        - Support creating databases in batch during data restore [#50767](https://github.com/pingcap/tidb/issues/50767) @[Leavrth](https://github.com/Leavrth)
        - Print the information of the slowest Region that affects global checkpoint advancement in logs and metrics during log backups [#51046](https://github.com/pingcap/tidb/issues/51046) @[YuJuncen](https://github.com/YuJuncen)
        - Improve the table creation performance of the `RESTORE` statement in scenarios with large datasets [#48301](https://github.com/pingcap/tidb/issues/48301) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Optimize the memory consumption of `RowChangedEvent` to reduce memory consumption when TiCDC replicates data [#10386](https://github.com/pingcap/tiflow/issues/10386) @[lidezhu](https://github.com/lidezhu)
        - Verify that the start-ts parameter is valid when creating and resuming a changefeed task [#10499](https://github.com/pingcap/tiflow/issues/10499) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Data Migration (DM)

        - In a MariaDB primary-secondary replication scenario, where the migration path is: MariaDB primary instance -> MariaDB secondary instance -> DM -> TiDB, when `gtid_strict_mode = off` and the GTID of the MariaDB secondary instance is not strictly incrementing (for example, there is data writing to the MariaDB secondary instance), the DM task will report an error `less than global checkpoint position`. Starting from v8.0.0, TiDB is compatible with this scenario and data can be migrated downstream normally. [#10741](https://github.com/pingcap/tiflow/issues/10741) @[okJiang](https://github.com/okJiang)

    + TiDB Lightning

        - Support configuring the maximum number of rows in a batch in logical import mode using [`logical-import-batch-rows`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) [#46607](https://github.com/pingcap/tidb/issues/46607) @[kennytm](https://github.com/kennytm)
        - TiDB Lightning reports an error when the space of TiFlash is insufficient [#50324](https://github.com/pingcap/tidb/issues/50324) @[okJiang](https://github.com/okJiang)
