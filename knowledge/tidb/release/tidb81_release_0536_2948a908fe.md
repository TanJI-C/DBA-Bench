# Bug fixes for TiFlash and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.2.md`
- Source Title: `TiDB 7.5.2 Release Notes`
- Source Heading Path: `TiDB 7.5.2 Release Notes > Bug fixes`
- Source Line Ranges: `195-227`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `br`, `pd`, `tikv`, `lightning`, `tidb`
- Topic Tags: `bug-fixes`, `disaggregated-storage-compute`, `query-correctness`, `panics`, `ddl`, `log-backup`, `full-backup`, `restore`, `gc-safepoint`, `pd-connection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0536_2948a908fe`
- Source ID: `tidb-docs-8.1:releases/release-7.5.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1cda151cfe9156e88cfdc8510bc42c2311f46fa016d2cdc7846629dcb090e1af`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.2 bug fixes related to TiFlash query correctness or panics in disaggregated storage and compute architecture, or BR log backup, full backup, restore, GC safepoint, and PD connection failure issues.
- Retrieval Keywords: TiDB 7.5.2 release notes bug fixes, TiFlash disaggregated storage and compute architecture, adding non-null columns null values incorrectly returned, partitioned tables empty partition query timeout, TiFlash panic compute node process is stopped, generated columns returns an error, metadata corrupted upgrading from earlier than v6.5.0 to v6.5.0 or later, ENUM column crash during chunk encoding, local_region_num incorrect values in logs, disk used_size metric Grafana incorrect, storage.remote.cache.capacity, queries permanently blocked after network isolation, invalid default values non-strict sql_mode, BR log backup data loss, full backup fails too many logs are printed, PD connection failure log backup advancer owner panic, global checkpoint advanced ahead of actual backup file write point, resuming a paused log backup task unstable network connections to PD, Region fetched from PD does not have a Leader, TiDB Lightning physical import mode, removing a log backup task after it is paused does not immediately restore the GC safepoint, BR fails to restore a transactional KV cluster due to an empty EndKey, transfer of PD leaders might cause BR to panic when restoring data, AUTO_RANDOM ID allocation progress, union clustered index
- Follow-up Guidance: This chunk also lists related fixes for TiDB Lightning physical import mode, including the case where the Region fetched from PD does not have a Leader.
- Classification Note: The classification is release/tiflash because the official content is a TiDB 7.5.2 Bug fixes section dominated by TiFlash fixes and also includes BR tool fixes.

## Official Source Content

- Fix the issue that in the disaggregated storage and compute architecture, null values might be incorrectly returned in queries after adding non-null columns in DDL operations [#9084](https://github.com/pingcap/tiflash/issues/9084) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue of query timeout when executing queries on partitioned tables that contains the empty partition [#9024](https://github.com/pingcap/tiflash/issues/9024) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that in the disaggregated storage and compute architecture, TiFlash might panic when the compute node process is stopped [#8860](https://github.com/pingcap/tiflash/issues/8860) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that querying generated columns returns an error [#8787](https://github.com/pingcap/tiflash/issues/8787) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiFlash metadata might become corrupted and cause the process to panic when upgrading a cluster from a version earlier than v6.5.0 to v6.5.0 or later [#9039](https://github.com/pingcap/tiflash/issues/9039) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the `ENUM` column might cause TiFlash to crash during chunk encoding [#8674](https://github.com/pingcap/tiflash/issues/8674) @[yibin87](https://github.com/yibin87)
    - Fix incorrect `local_region_num` values in logs [#8895](https://github.com/pingcap/tiflash/issues/8895) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that in the disaggregated storage and compute architecture, TiFlash might panic during shutdown [#8837](https://github.com/pingcap/tiflash/issues/8837) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might return transiently incorrect results in high-concurrency read scenarios [#8845](https://github.com/pingcap/tiflash/issues/8845) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that in the disaggregated storage and compute architecture, the disk `used_size` metric displayed in Grafana is incorrect after you modify the value of the `storage.remote.cache.capacity` configuration item for TiFlash compute nodes [#8920](https://github.com/pingcap/tiflash/issues/8920) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that in the disaggregated storage and compute architecture, queries might be permanently blocked after network isolation [#8806](https://github.com/pingcap/tiflash/issues/8806) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that TiFlash might panic when you insert data to columns with invalid default values in non-strict `sql_mode` [#8803](https://github.com/pingcap/tiflash/issues/8803) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)

+ Tools

    + Backup & Restore (BR)

        - Fix a rare issue that special event timing might cause the data loss in log backup [#16739](https://github.com/tikv/tikv/issues/16739) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that too many logs are printed when a full backup fails [#51572](https://github.com/pingcap/tidb/issues/51572) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that a PD connection failure could cause the TiDB instance where the log backup advancer owner is located to panic [#52597](https://github.com/pingcap/tidb/issues/52597) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the global checkpoint of log backup is advanced ahead of the actual backup file write point due to TiKV restart, which might cause a small amount of backup data loss [#16809](https://github.com/tikv/tikv/issues/16809) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that TiKV might panic when resuming a paused log backup task with unstable network connections to PD [#17020](https://github.com/tikv/tikv/issues/17020) @[YuJuncen](https://github.com/YuJuncen)
        - Fix an unstable test case [#52547](https://github.com/pingcap/tidb/issues/52547) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the Region fetched from PD does not have a Leader when restoring data using BR or importing data using TiDB Lightning in physical import mode [#51124](https://github.com/pingcap/tidb/issues/51124) [#50501](https://github.com/pingcap/tidb/issues/50501) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that TiKV panics when a full backup fails to find a peer in some extreme cases [#16394](https://github.com/tikv/tikv/issues/16394) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that removing a log backup task after it is paused does not immediately restore the GC safepoint [#52082](https://github.com/pingcap/tidb/issues/52082) @[3pointer](https://github.com/3pointer)
        - Fix the unstable test case `TestClearCache` [#50743](https://github.com/pingcap/tidb/issues/50743) @[3pointer](https://github.com/3pointer)
        - Fix the issue that BR fails to restore a transactional KV cluster due to an empty `EndKey` [#52574](https://github.com/pingcap/tidb/issues/52574) @[3pointer](https://github.com/3pointer)
        - Fix the issue that the transfer of PD leaders might cause BR to panic when restoring data [#53724](https://github.com/pingcap/tidb/issues/53724) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that BR could not back up the `AUTO_RANDOM` ID allocation progress in a union clustered index that contains an `AUTO_RANDOM` column [#52255](https://github.com/pingcap/tidb/issues/52255) @[Leavrth](https://github.com/Leavrth)

    + TiCDC
