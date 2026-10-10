# Bug fixes across TiDB TiKV PD TiFlash and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.2.md`
- Source Title: `TiDB 6.5.2 Release Notes`
- Source Heading Path: `TiDB 6.5.2 Release Notes > Bug fixes`
- Source Line Ranges: `50-96`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`
- Topic Tags: `release-notes`, `bug-fixes`, `ddl`, `partitioned-tables`, `startup`, `transactions`, `prepared-plan-cache`, `memory-control`, `cgroup`, `placement-rules`, `leader-distribution`, `decimal`, `collation`, `pitr`, `region-splitting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0392_d1ee28931a`
- Source ID: `tidb-docs-8.1:releases/release-6.5.2.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d92778cc0588638006165a3db33db34495edac6e96fbe9e45932d714eb5ee88c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.2#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.2.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks which bugs were fixed in TiDB 6.5.2 for TiDB, TiKV, PD, TiFlash, or BR, including specific SQL statements, startup errors, memory control issues, or partitioned table problems.
- Retrieval Keywords: TiDB 6.5.2 bug fixes, ADMIN SHOW DDL JOBS, DROP TABLE, TRUNCATE TABLE, partitioned tables, TiFlash replicas, cgroup v1, can't read file memory.stat from cgroup v1: open /sys/memory.stat no such file or directory, DDL data backfill, write conflict, PointUpdate, SELECT, Cursor Fetch, Execute Fetch Close, INSERT IGNORE, REPLACE, generated columns, prepared plan cache, full index scans, IndexMerge, max_prepared_stmt_count, global memory control, tidb_server_memory_limit_sess_min_size, Index Join, dynamic trimming mode, TiKV cgroup path, : character, PD Learners, placement rule, leaders, TiFlash generated columns, Decimal division, Decimal cast, new collation, TopN, Sort, TiCDC incompatibility, BR, resolve lock, PITR, splitting Region retry
- Follow-up Guidance: The content groups the fixes by component and includes exact affected features and error text such as the cgroup startup error and issues involving prepared plan cache, partitioned tables, and PITR recovery.
- Classification Note: This is a bug-fix chunk because it is a release note section listing resolved defects and corrected behaviors across multiple components in TiDB 6.5.2.

## Official Source Content

## Bug fixes

+ TiDB
    - Fix the issue that after a new column is added in the cache table, the value is `NULL` instead of the default value of the column [#42928](https://github.com/pingcap/tidb/issues/42928) @[lqs](https://github.com/lqs)
    - Fix the issue of DDL retry caused by write conflict when executing `TRUNCATE TABLE` for partitioned tables with many partitions and TiFlash replicas [#42940](https://github.com/pingcap/tidb/issues/42940) @[mjonss](https://github.com/mjonss)
    - Fix the issue of missing table names in the `ADMIN SHOW DDL JOBS` result when a `DROP TABLE` operation is being executed [#42268](https://github.com/pingcap/tidb/issues/42268) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that TiDB server cannot start due to an error in reading the cgroup information with the error message "can't read file memory.stat from cgroup v1: open /sys/memory.stat no such file or directory" [#42659](https://github.com/pingcap/tidb/issues/42659) @[hawkingrei](https://github.com/hawkingrei)
    - Fix frequent write conflicts in transactions when performing DDL data backfill [#24427](https://github.com/pingcap/tidb/issues/24427) @[mjonss](https://github.com/mjonss)
    - Fix the issue that TiDB panic occurs due to inconsistent InfoSchema being obtained when generating the execution plan [#41622](https://github.com/pingcap/tidb/issues/41622) @[tiancaiamao](https://github.com/tiancaiamao)
    - Fix the issue that when modifying the floating-point type using DDL to keep the length unchanged and reduce the decimal places, the old data still remains the same [#41281](https://github.com/pingcap/tidb/issues/41281) @[zimulala](https://github.com/zimulala)
    - Fix the issue that after executing `PointUpdate` within a transaction, TiDB returns incorrect results for the `SELECT` statement [#28011](https://github.com/pingcap/tidb/issues/28011) @[zyguan](https://github.com/zyguan)
    - Fix the issue that, when using Cursor Fetch and running other statements among Execute, Fetch, and Close, the Fetch and Close commands might return incorrect results or cause TiDB to panic [#40094](https://github.com/pingcap/tidb/issues/40094) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that `INSERT IGNORE` and `REPLACE` statements do not lock keys that do not modify values [#42121](https://github.com/pingcap/tidb/issues/42121) @[zyguan](https://github.com/zyguan)
    - Fix the issue that TiFlash reports an error for generated columns during execution [#40663](https://github.com/pingcap/tidb/issues/40663) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that TiDB might produce incorrect results when different partitioned tables appear in a single SQL statement [#42135](https://github.com/pingcap/tidb/issues/42135) @[mjonss](https://github.com/mjonss)
    - Fix the issue that full index scans might cause errors when prepared plan cache is enabled [#42150](https://github.com/pingcap/tidb/issues/42150) @[fzzf678](https://github.com/fzzf678)
    - Fix the issue that IndexMerge might produce incorrect results when prepare plan cache is enabled [#41828](https://github.com/pingcap/tidb/issues/41828) @[qw4990](https://github.com/qw4990)
    - Fix the issue that the configuration of `max_prepared_stmt_count` does not take effect [#39735](https://github.com/pingcap/tidb/issues/39735) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)
    - Fix the issue that global memory control might incorrectly kill SQL statements with memory usage less than `tidb_server_memory_limit_sess_min_size` [#42662](https://github.com/pingcap/tidb/issues/42662) @[XuHuaiyu](https://github.com/XuHuaiyu)
    - Fix the issue that Index Join might cause panic in dynamic trimming mode of partition tables [#40596](https://github.com/pingcap/tidb/issues/40596) @[tiancaiamao](https://github.com/tiancaiamao)

+ TiKV

    - Fix the issue that TiKV does not correctly parse the `:` character when processing the cgroup path [#14538](https://github.com/tikv/tikv/issues/14538) @[SpadeA-Tang](https://github.com/SpadeA-Tang)

+ PD

    - Fix the issue that PD might unexpectedly add multiple Learners to a Region [#5786](https://github.com/tikv/pd/issues/5786) @[HunDunDM](https://github.com/HunDunDM)
    - Fix the issue that switching placement rule might cause uneven distribution of leaders [#6195](https://github.com/tikv/pd/issues/6195) @[bufferflies](https://github.com/bufferflies)

+ TiFlash

    - Fix the issue that TiFlash cannot recognize generated columns [#6801](https://github.com/pingcap/tiflash/issues/6801) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the issue that Decimal division does not round up the last digit in certain cases [#7022](https://github.com/pingcap/tiflash/issues/7022) @[LittleFall](https://github.com/LittleFall)
    - Fix the issue that Decimal cast rounds up incorrectly in certain cases [#6994](https://github.com/pingcap/tiflash/issues/6994) @[windtalker](https://github.com/windtalker)
    - Fix the issue that TopN/Sort operators produce incorrect results after enabling the new collation [#6807](https://github.com/pingcap/tiflash/issues/6807) @[xzhangxian1008](https://github.com/xzhangxian1008)
    - Fix the issue of TiFlash process failures due to TiCDC incompatibility [#7212](https://github.com/pingcap/tiflash/issues/7212) @[hongyunyan](https://github.com/hongyunyan)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that the frequency of `resolve lock` is too high when there is no PITR backup task in the TiDB cluster [#40759](https://github.com/pingcap/tidb/issues/40759) @[joccau](https://github.com/joccau)
        - Fix the issue of insufficient wait time for splitting Region retry during the PITR recovery process [#42001](https://github.com/pingcap/tidb/issues/42001) @[joccau](https://github.com/joccau)

    + TiCDC
