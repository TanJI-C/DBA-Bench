# Bug fixes across TiDB, PD, TiFlash, BR, and TiCDC section start

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `429-480`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tiflash`, `br`, `ticdc`
- Topic Tags: `bug-fixes`, `upgrade`, `indexes`, `statistics`, `partitioned-tables`, `locking`, `leader-distribution`, `pitr`, `log-backup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0439_15cee7c359`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `63792b22a69f554ade0c5181d6c1f7f460486b7ef1513c34f8cd22a64e851dd7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.0.0 bug fixes across TiDB, PD, TiFlash, and BR related to upgrade issues, add index behavior, statistics, partitioned tables, locking, leader distribution, and PITR log backup or recovery.
- Retrieval Keywords: TiDB 7.0.0 Bug fixes, missing updates when upgrading TiDB from v6.5.1 to a later version, #41502, default values of some system variables are not modified after upgrading, #41423, Coprocessor request types related to adding indexes are displayed as unknown, #41400, PessimisticLockNotFound when adding an index, #41515, found duplicate key when adding a unique index, #41630, panic when adding an index, #41880, TiFlash reports an error for generated columns during execution, #40663, statistics correctly when there is a time type, #41938, full index scans prepared plan cache errors, #42150, IFNULL(NOT NULL COLUMN, ...) incorrect results, #41734, partitioned table single Region incorrect results, #41801, different partitioned tables appear in a single SQL statement, #42135, statistics auto-collection partitioned table after adding a new index, #41638, read incorrect column statistics information after collecting statistics twice in a row, #42073, IndexMerge incorrect results prepare plan cache, #41828, IndexMerge goroutine leakage, #41605, non-BIGINT unsigned integers compared with strings/decimals incorrect results, #41736, ANALYZE memory over-limit current ANALYZE statement killed, #41825, batch coprocessor data race information collection, #41412, printing MVCC information for partitioned tables, #40629, fair lock mode adds locking to non-existent keys, #41527, INSERT IGNORE and REPLACE statements do not lock keys that do not modify values, #42121, Region Scatter uneven distribution of leaders, #6017, getting PD members during startup data race, #6069, collecting hotspot statistics data race, #6069, switching placement rule uneven distribution of leaders, #6195, Decimal division does not round up the last digit, #7022, Decimal cast rounds up incorrectly, #6994, TopN/Sort incorrect results after enabling the new collation, #6807, aggregating a result set larger than 12 million rows on a single TiFlash node, #6993, BR PITR recovery splitting Region retry insufficient wait time, #42001, memory is limited during the PITR recovery process, #41983, PITR log backup progress does not advance when a PD node is down, #14184, latency of the PITR log backup progress increases when Region leadership migration occurs, #13638
- Follow-up Guidance: The next chunk continues the same Bug fixes section with TiCDC, DM, and TiDB Lightning fixes.
- Classification Note: This is a release-notes bug-fix summary chunk covering multiple components under the TiDB 7.0.0 Bug fixes section.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue of missing updates when upgrading TiDB from v6.5.1 to a later version [#41502](https://github.com/pingcap/tidb/issues/41502) @[chrysan](https://github.com/chrysan)
    - Fix the issue that the default values of some system variables are not modified after upgrading [#41423](https://github.com/pingcap/tidb/issues/41423) @[crazycs520](https://github.com/crazycs520)
    - Fix the issue that Coprocessor request types related to adding indexes are displayed as unknown [#41400](https://github.com/pingcap/tidb/issues/41400) @[tangenta](https://github.com/tangenta)
    - Fix the issue of returning "PessimisticLockNotFound" when adding an index [#41515](https://github.com/pingcap/tidb/issues/41515) @[tangenta](https://github.com/tangenta)
    - Fix the issue of mistakenly returning `found duplicate key` when adding a unique index [#41630](https://github.com/pingcap/tidb/issues/41630) @[tangenta](https://github.com/tangenta)
    - Fix the panic issue when adding an index [#41880](https://github.com/pingcap/tidb/issues/41880) @[tangenta](https://github.com/tangenta)
    - Fix the issue that TiFlash reports an error for generated columns during execution [#40663](https://github.com/pingcap/tidb/issues/40663) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiDB might not be able to obtain statistics correctly when there is a time type [#41938](https://github.com/pingcap/tidb/issues/41938) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that full index scans might cause errors when prepared plan cache is enabled [#42150](https://github.com/pingcap/tidb/issues/42150) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that `IFNULL(NOT NULL COLUMN, ...)` might return incorrect results [#41734](https://github.com/pingcap/tidb/issues/41734) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that TiDB might produce incorrect results when all data in a partitioned table is in a single Region [#41801](https://github.com/pingcap/tidb/issues/41801) @[Defined2014](https://github.com/Defined2014)
    - Fix the issue that TiDB might produce incorrect results when different partitioned tables appear in a single SQL statement [#42135](https://github.com/pingcap/tidb/issues/42135) @[mjonss](https://github.com/mjonss)
    - Fix the issue that statistics auto-collection might not trigger correctly on a partitioned table after adding a new index to the partitioned table [#41638](https://github.com/pingcap/tidb/issues/41638) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that TiDB might read incorrect column statistics information after collecting statistics twice in a row [#42073](https://github.com/pingcap/tidb/issues/42073) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that IndexMerge might produce incorrect results when prepare plan cache is enabled [#41828](https://github.com/pingcap/tidb/issues/41828) @[qw4990](https://github.com/qw4990)
    - Fix the issue that IndexMerge might have goroutine leakage [#41605](https://github.com/pingcap/tidb/issues/41605) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that non-BIGINT unsigned integers might produce incorrect results when compared with strings/decimals [#41736](https://github.com/pingcap/tidb/issues/41736) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that killing a previous `ANALYZE` statement due to memory over-limit might cause the current `ANALYZE` statement in the same session to be killed [#41825](https://github.com/pingcap/tidb/issues/41825) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that data race might occur during the information collection process of the batch coprocessor [#41412](https://github.com/pingcap/tidb/issues/41412) @[you06](https://github.com/you06)
    - Fix the issue that an assertion error prevents printing MVCC information for partitioned tables [#40629](https://github.com/pingcap/tidb/issues/40629) @[ekexium](https://github.com/ekexium)
    - Fix the issue that fair lock mode adds locking to non-existent keys [#41527](https://github.com/pingcap/tidb/issues/41527) @[ekexium](https://github.com/ekexium)
    - Fix the issue that `INSERT IGNORE` and `REPLACE` statements do not lock keys that do not modify values [#42121](https://github.com/pingcap/tidb/issues/42121) @[zyguan](https://github.com/zyguan)

+ PD

    - Fix the issue that the Region Scatter operation might cause uneven distribution of leaders [#6017](https://github.com/tikv/pd/issues/6017) @[HunDunDM](https://github.com/HunDunDM)
    - Fix the issue that data race might occur when getting PD members during startup [#6069](https://github.com/tikv/pd/issues/6069) @[rleungx](https://github.com/rleungx)
    - Fix the issue that data race might occur when collecting hotspot statistics [#6069](https://github.com/tikv/pd/issues/6069) @[lhy1024](https://github.com/lhy1024)
    - Fix the issue that switching placement rule might cause uneven distribution of leaders [#6195](https://github.com/tikv/pd/issues/6195) @[bufferflies](https://github.com/bufferflies)

+ TiFlash

    - Fix the issue that Decimal division does not round up the last digit in certain cases [#7022](https://github.com/pingcap/tiflash/issues/7022) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that Decimal cast rounds up incorrectly in certain cases [#6994](https://github.com/pingcap/tiflash/issues/6994) @[windtalker](https://github.com/windtalker)
    - Fix the issue that TopN/Sort operators produce incorrect results after enabling the new collation [#6807](https://github.com/pingcap/tiflash/issues/6807) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue that TiFlash reports an error when aggregating a result set larger than 12 million rows on a single TiFlash node [#6993](https://github.com/pingcap/tiflash/issues/6993) @[windtalker](https://github.com/windtalker)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue of insufficient wait time for splitting Region retry during the PITR recovery process [#42001](https://github.com/pingcap/tidb/issues/42001) @[joccau](https://github.com/joccau)
        - Fix the issue of recovery failures due to `memory is limited` error encountered during the PITR recovery process [#41983](https://github.com/pingcap/tidb/issues/41983) @[joccau](https://github.com/joccau)
        - Fix the issue that PITR log backup progress does not advance when a PD node is down [#14184](https://github.com/tikv/tikv/issues/14184) @[YuJuncen](https://github.com/YuJuncen)
        - Alleviate the issue that the latency of the PITR log backup progress increases when Region leadership migration occurs [#13638](https://github.com/tikv/tikv/issues/13638) @[YuJuncen](https://github.com/YuJuncen)

    + TiCDC
