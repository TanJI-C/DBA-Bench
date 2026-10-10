# Bug fixes for TiFlash, BR, TiCDC, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.5.md`
- Source Title: `TiDB 7.1.5 Release Notes`
- Source Heading Path: `TiDB 7.1.5 Release Notes > Bug fixes`
- Source Line Ranges: `88-119`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `br`, `tikv`, `pd`, `tidb`, `ticdc`, `lightning`
- Topic Tags: `bug-fixes`, `tiflash`, `backup-restore`, `log-backup`, `gc-safepoint`, `changefeed`, `ddl`, `object-storage`, `csv`, `lightning`, `parquet`, `logs`, `data-loss`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0478_93ea05f198`
- Source ID: `tidb-docs-8.1:releases/release-7.1.5.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7be483d1f87f5ca3e10294d1722a5a11c5db8e9300e30667fafbc985170ab57b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.5#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.1.5 bug fixes across TiFlash, BR, TiCDC, and TiDB Lightning involving crashes, panics, changefeed issues, log backup, GC safepoint, CSV or object storage sink behavior, Parquet import, or backup data loss.
- Retrieval Keywords: TiDB 7.1.5 bug fixes, TiFlash local_region_num incorrect logs, querying generated columns returns an error, ENUM column crash during chunk encoding, invalid default values non-strict sql_mode TiFlash panic, TIME column precision modified Region migration split merge queries might fail, BR log backup paused remove task GC safepoint, too many logs printed when a full backup fails, AUTO_RANDOM composite clustered index backup, TiKV panics when a full backup fails to find a peer, PD connection failure log backup advancer owner panic, global checkpoint of log backup advanced ahead of actual backup file write point, backup data loss log backup TiKV restart, special event timing data loss in log backup, TiCDC Exchange Partition With Validation changefeed stuck, snapshot lost caused by GC, checkpoint-ts smaller than GC safepoint, TiCDC panics when scheduling table replication tasks, wrong CSV file due to wrong BarrierTS, eventual consistency object storage sink temporary failure, open-protocol old value STRING default value actual type, TiDB Lightning panics importing empty table Parquet, sensitive information in logs printed in server mode
- Follow-up Guidance: 
- Classification Note: This chunk is classified as a release note bug-fix summary for the shared area because it lists fixed issues across multiple components: TiFlash, BR, TiCDC, and TiDB Lightning.

## Official Source Content

- Fix incorrect `local_region_num` values in logs [#8895](https://github.com/pingcap/tiflash/issues/8895) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that querying generated columns returns an error [#8787](https://github.com/pingcap/tiflash/issues/8787) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that the `ENUM` column might cause TiFlash to crash during chunk encoding [#8674](https://github.com/pingcap/tiflash/issues/8674) @[yibin87](https://github.com/yibin87)
    - Fix the issue that TiFlash might panic when you insert data to columns with invalid default values in non-strict `sql_mode` [#8803](https://github.com/pingcap/tiflash/issues/8803) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the issue that if Region migration, split, or merge occurs after the precision of a `TIME` column is modified, queries might fail [#8601](https://github.com/pingcap/tiflash/issues/8601) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that removing a log backup task after it is paused does not immediately restore the GC safepoint [#52082](https://github.com/pingcap/tidb/issues/52082) @[3pointer](https://github.com/3pointer)
        - Fix the issue that too many logs are printed when a full backup fails [#51572](https://github.com/pingcap/tidb/issues/51572) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that BR could not back up the `AUTO_RANDOM` ID allocation progress if the `AUTO_RANDOM` column is in a composite clustered index [#52255](https://github.com/pingcap/tidb/issues/52255) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that TiKV panics when a full backup fails to find a peer in some extreme cases [#16394](https://github.com/tikv/tikv/issues/16394) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that a PD connection failure could cause the TiDB instance where the log backup advancer owner is located to panic [#52597](https://github.com/pingcap/tidb/issues/52597) @[YuJuncen](https://github.com/YuJuncen)
        - Fix an unstable test case [#52547](https://github.com/pingcap/tidb/issues/52547) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the global checkpoint of log backup is advanced ahead of the actual backup file write point due to TiKV restart, which might cause a small amount of backup data loss [#16809](https://github.com/tikv/tikv/issues/16809) @[YuJuncen](https://github.com/YuJuncen)
        - Fix a rare issue that special event timing might cause the data loss in log backup [#16739](https://github.com/tikv/tikv/issues/16739) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC

        - Fix the issue that TiCDC fails to execute the `Exchange Partition ... With Validation` DDL downstream after it is written upstream, causing the changefeed to get stuck [#10859](https://github.com/pingcap/tiflow/issues/10859) @[hongyunyan](https://github.com/hongyunyan)
        - Fix the issue that `snapshot lost caused by GC` is not reported in time when resuming a changefeed and the `checkpoint-ts` of the changefeed is smaller than the GC safepoint of TiDB [#10463](https://github.com/pingcap/tiflow/issues/10463) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that TiCDC panics when scheduling table replication tasks [#10613](https://github.com/pingcap/tiflow/issues/10613) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that data is written to a wrong CSV file due to wrong BarrierTS in scenarios where DDL statements are executed frequently [#10668](https://github.com/pingcap/tiflow/issues/10668) @[lidezhu](https://github.com/lidezhu)
        - Fix the issue that a changefeed with eventual consistency enabled might fail when the object storage sink encounters a temporary failure [#10710](https://github.com/pingcap/tiflow/issues/10710) @[CharlesCheung96](https://github.com/CharlesCheung96)
        - Fix the issue that the old value part of `open-protocol` incorrectly outputs the default value according to the `STRING` type instead of its actual type [#10803](https://github.com/pingcap/tiflow/issues/10803) @[3AceShowHand](https://github.com/3AceShowHand)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning panics when importing an empty table of Parquet format [#52518](https://github.com/pingcap/tidb/issues/52518) @[kennytm](https://github.com/kennytm)
        - Fix the issue that sensitive information in logs is printed in server mode [#36374](https://github.com/pingcap/tidb/issues/36374) @[kennytm](https://github.com/kennytm)
