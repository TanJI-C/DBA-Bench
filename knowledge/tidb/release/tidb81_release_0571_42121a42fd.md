# Bug fixes for TiFlash, BR, TiCDC, and DM

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Bug fixes`
- Source Line Ranges: `482-522`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `br`, `ticdc`, `dm`
- Topic Tags: `bug-fixes`, `memory`, `flashback`, `recover-table`, `ddl`, `object-storage`, `pitr`, `log-backup`, `replication`, `checkpoint-ts`, `gtid`, `migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0571_42121a42fd`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `53d34a755b8b03d9688b2ac13fd23974666770f87c9f9da6d2eee60cf54b37cc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.6.0 bug fixes affecting TiFlash, BR, TiCDC, or DM in areas such as memory usage, flashback and recovery, object storage, PITR and log backup, checkpoint-ts, or migration errors.
- Retrieval Keywords: TiDB 7.6.0 bug fixes, TiFlash memory leak memory limitation during query, #8447, TiFlash replicas garbage collected after FLASHBACK DATABASE, #8450, memory usage increases significantly due to slow queries, #8564, RECOVER TABLE FLASHBACK TABLE TiFlash replica data cannot be recovered, #1664, ColumnRef in (Literal, Func...) incorrect results, #8631, TiFlash panic concurrent DDL execution, #8578, GC owner object storage disaggregated storage and compute architecture, #8519, lowerUTF8 upperUTF8 different bytes, #8484, ENUM value is 0 incorrectly handles ENUM, #8311, INET_NTOA incompatibility, #8211, OOM scanning multiple partitioned tables during stream read, #8505, short queries print excessive info logs, #8592, TiFlash might crash when it is stopped, #8550, GREATEST LEAST constant string parameters invalid memory access, #8604, BR incorrect URIs external storage files, #48452, log backup task failing to connect to PD during task initialization, #16056, log backup task memory leak after startup, #16070, mysql.gc_delete_range PITR returns an error, #49346, Unsupported collation restore data from backups of an old version, #49466, permissions not updated timely after user tables recovered through snapshots, #49394, TiCDC WHERE clause does not use the primary key DELETE statements, #9812, TiCDC panic replicating data to an object storage service, #10137, kv-client initialization data race, #10095, TiCDC mistakenly closes the connection with TiKV, #10239, TiCDC server panic lossy DDL statements upstream, #9739, checkpoint-ts stuck downstream MySQL, #10334, DM event type truncate not valid upgrade fail, #10282, performance degradation GTID mode, #9676, downstream table structure contains shard_row_id_bits, #10308
- Follow-up Guidance: 
- Classification Note: The content is classified as release notes because it enumerates TiDB 7.6.0 bug fixes for TiFlash and data tools including BR, TiCDC, and DM, with issue numbers and concise problem statements.

## Official Source Content

- Fix the issue of memory leak when TiFlash encounters memory limitation during query [#8447](https://github.com/pingcap/tiflash/issues/8447) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that data of TiFlash replicas would still be garbage collected after executing `FLASHBACK DATABASE` [#8450](https://github.com/pingcap/tiflash/issues/8450) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the memory usage increases significantly due to slow queries [#8564](https://github.com/pingcap/tiflash/issues/8564) @[JinheLin](https://github.com/JinheLin)
    - Fix the issue that some TiFlash replica data cannot be recovered through `RECOVER TABLE` or `FLASHBACK TABLE` in scenarios with frequent execution of `CREATE TABLE` and `DROP TABLE` [#1664](https://github.com/pingcap/tiflash/issues/1664) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that query results are incorrect when querying with filtering conditions like `ColumnRef in (Literal, Func...)` [#8631](https://github.com/pingcap/tiflash/issues/8631) @[Lloyd-Pottiger](https://github.com/Lloyd-Pottiger)
    - Fix the TiFlash panic issue when TiFlash encounters conflicts during concurrent DDL execution [#8578](https://github.com/pingcap/tiflash/issues/8578) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that TiFlash might not be able to select the GC owner of object storage data under the disaggregated storage and compute architecture [#8519](https://github.com/pingcap/tiflash/issues/8519) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Fix the issue that the `lowerUTF8` and `upperUTF8` functions do not allow characters in different cases to occupy different bytes [#8484](https://github.com/pingcap/tiflash/issues/8484) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that TiFlash incorrectly handles `ENUM` when the `ENUM` value is 0 [#8311](https://github.com/pingcap/tiflash/issues/8311) @[solotzg](https://github.com/solotzg)
    - Fix the incompatibility issue in the `INET_NTOA()` expression [#8211](https://github.com/pingcap/tiflash/issues/8211) @[solotzg](https://github.com/solotzg)
    - Fix the potential OOM issue that might occur when scanning multiple partitioned tables during stream read [#8505](https://github.com/pingcap/tiflash/issues/8505) @[gengliqi](https://github.com/gengliqi)
    - Fix the issue that short queries executed successfully print excessive info logs [#8592](https://github.com/pingcap/tiflash/issues/8592) @[windtalker](https://github.com/windtalker)
    - Fix the issue that TiFlash might crash when it is stopped [#8550](https://github.com/pingcap/tiflash/issues/8550) @[guo-shaoge](https://github.com/guo-shaoge)
    - Fix the random invalid memory access issue that might occur with `GREATEST` or `LEAST` functions containing constant string parameters [#8604](https://github.com/pingcap/tiflash/issues/8604) @[windtalker](https://github.com/windtalker)

+ Tools

    + Backup & Restore (BR)

        - Fix the issue that BR generates incorrect URIs for external storage files [#48452](https://github.com/pingcap/tidb/issues/48452) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the log backup task can start but does not work properly if failing to connect to PD during task initialization [#16056](https://github.com/tikv/tikv/issues/16056) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that the log backup task might encounter memory leak and fail to run properly after startup [#16070](https://github.com/tikv/tikv/issues/16070) @[YuJuncen](https://github.com/YuJuncen)
        - Fix the issue that inserting data into the system table `mysql.gc_delete_range` during the PITR process returns an error [#49346](https://github.com/pingcap/tidb/issues/49346) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that the `Unsupported collation` error is reported when you restore data from backups of an old version [#49466](https://github.com/pingcap/tidb/issues/49466) @[3pointer](https://github.com/3pointer)
        - Fix the issue that permissions are not updated timely after user tables are recovered through snapshots in certain scenarios [#49394](https://github.com/pingcap/tidb/issues/49394) @[Leavrth](https://github.com/Leavrth)

    + TiCDC

        - Fix the issue that the `WHERE` clause does not use the primary key as a condition when replicating `DELETE` statements in certain scenarios [#9812](https://github.com/pingcap/tiflow/issues/9812) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the TiCDC server might panic when replicating data to an object storage service [#10137](https://github.com/pingcap/tiflow/issues/10137) @[sdojjy](https://github.com/sdojjy)
        - Fix the potential data race issue during `kv-client` initialization [#10095](https://github.com/pingcap/tiflow/issues/10095) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC mistakenly closes the connection with TiKV in certain special scenarios [#10239](https://github.com/pingcap/tiflow/issues/10239) @[hicqu](https://github.com/hicqu)
        - Fix the issue that TiCDC server might panic when executing lossy DDL statements in upstream [#9739](https://github.com/pingcap/tiflow/issues/9739) @[hicqu](https://github.com/hicqu)
        - Fix the issue that `checkpoint-ts` might get stuck when TiCDC replicates data to downstream MySQL [#10334](https://github.com/pingcap/tiflow/issues/10334) @[zhangjinpeng87](https://github.com/zhangjinpeng87)

    + TiDB Data Migration (DM)

        - Fix the issue that DM encounters "event type truncate not valid" error that causes the upgrade to fail [#10282](https://github.com/pingcap/tiflow/issues/10282) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the performance degradation issue when replicating data in GTID mode [#9676](https://github.com/pingcap/tiflow/issues/9676) @[feran-morgan-pingcap](https://github.com/feran-morgan-pingcap)
        - Fix the issue that a migration task error occurs when the downstream table structure contains `shard_row_id_bits` [#10308](https://github.com/pingcap/tiflow/issues/10308) @[GMHDBJD](https://github.com/GMHDBJD)
