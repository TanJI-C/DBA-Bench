# TiDB 7.5.7 improvements across TiDB, TiKV, PD, TiFlash, and BR

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.7.md`
- Source Title: `TiDB 7.5.7 Release Notes`
- Source Heading Path: `TiDB 7.5.7 Release Notes > Improvements`
- Source Line Ranges: `22-68`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`, `tiflash`, `br`
- Topic Tags: `release-notes`, `improvements`, `performance`, `observability`, `flow-control`, `ddl`, `dml`, `optimizer`, `statistics`, `compaction`, `snapshot`, `region-merge`, `metrics`, `slow-logs`, `backup-restore`, `s3`, `imdsv2`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0553_2493d2f10e`
- Source ID: `tidb-docs-8.1:releases/release-7.5.7.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `897ae07359183472a031a1e00f7a9825934946916312f70f95ade802e6f80415`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.7#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.7.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB 7.5.7 improvements across TiDB, TiKV, PD, TiFlash, and BR, including performance, observability, flow control, slow logs, and backup-related changes.
- Retrieval Keywords: TiDB 7.5.7 Release Notes, Improvements, flow control interfaces for Region splitting and data ingestion, write speed to TiKV during index addition, tidb_opt_ordering_index_selectivity_threshold, ANALYZE, constant folding, NOT NULL, IS NULL evaluations into FALSE, constant propagation, JOIN operations, temporary index merging, TiKV compaction, async snapshot, Region Merge, CompactedEvent, split-check worker, memory usage per thread, SST ingest is experiencing slowdowns, get_sst_key_ranges, flow-control configurations for write operations, ingesting SST files without blocking foreground writes, slow logs for peer and store messages, PD GO runtime-related monitoring metrics, TiFlash OOM risks, storage snapshots, BR, IMDSv2, IAM role, Amazon S3, Download API, filtering out data within a certain time range
- Follow-up Guidance: The chunk breaks the improvements down by component, covering TiDB, TiKV, PD, TiFlash, and Backup & Restore (BR).
- Classification Note: This is classified as a release chunk because it is the improvements section of the TiDB 7.5.7 release notes spanning multiple components.

## Official Source Content

## Improvements

+ TiDB

    - Add flow control interfaces for Region splitting and data ingestion during data import [#61553](https://github.com/pingcap/tidb/issues/61553) @[tangenta](https://github.com/tangenta)
    - Optimize the performance of obtaining data distribution information when performing simple queries on tables with large data volumes [#53850](https://github.com/pingcap/tidb/issues/53850) @[you06](https://github.com/you06)
    - Add a monitoring metric to observe the write speed to TiKV during index addition [#60925](https://github.com/pingcap/tidb/issues/60925) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Optimize the locking logic of DML during DDL execution to reduce lock conflicts between DML and DDL operations, improving DDL performance in some scenarios. However, due to the additional secondary index locking operations, DML performance might decrease slightly [#62337](https://github.com/pingcap/tidb/issues/62337) @[lcwangchao](https://github.com/lcwangchao)
    - Improve the behavior when the system variable [`tidb_opt_ordering_index_selectivity_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_ordering_index_selectivity_threshold-new-in-v700) is set to `1`, enhancing the control capability of this variable [#60242](https://github.com/pingcap/tidb/issues/60242) @[time-and-fate](https://github.com/time-and-fate)
    - Avoid refreshing statistics across the entire cluster after `ANALYZE` statement execution, reducing the execution time of `ANALYZE` [#57631](https://github.com/pingcap/tidb/issues/57631) @[0xPoe](https://github.com/0xPoe)
    - Support constant folding for columns with `NOT NULL` constraints, folding `IS NULL` evaluations into `FALSE` [#62050](https://github.com/pingcap/tidb/issues/62050) @[hawkingrei](https://github.com/hawkingrei)
    - The optimizer supports constant propagation in more types of `JOIN` operations [#51700](https://github.com/pingcap/tidb/issues/51700) @[hawkingrei](https://github.com/hawkingrei)
    - Improve the performance of temporary index merging when extensive lock conflicts exist between DML and DDL operations [#61433](https://github.com/pingcap/tidb/issues/61433) @[tangenta](https://github.com/tangenta)

+ TiKV

    - Optimize the trigger logic of TiKV compaction to process all data segments in order of reclamation efficiency, reducing the performance impact of MVCC redundant data [#18571](https://github.com/tikv/tikv/issues/18571) @[v01dstar](https://github.com/v01dstar)
    - Optimize the tail latency of async snapshot and write operations in environments with a large number of SST files [#18743](https://github.com/tikv/tikv/issues/18743) @[Connor1996](https://github.com/Connor1996)
    - Improve the speed of Region Merge in scenarios with empty tables and small Regions [#17376](https://github.com/tikv/tikv/issues/17376) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize the handling of `CompactedEvent` in Raftstore by moving it to the `split-check` worker, reducing blocking on the main Raftstore thread [#18532](https://github.com/tikv/tikv/issues/18532) @[LykxSassinator](https://github.com/LykxSassinator)
    - Add metrics for memory usage per thread [#15927](https://github.com/tikv/tikv/issues/15927) @[Connor1996](https://github.com/Connor1996)
    - Log only `SST ingest is experiencing slowdowns` when SST ingest is too slow, and skip calling `get_sst_key_ranges` to avoid performance jitter [#18549](https://github.com/tikv/tikv/issues/18549) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize the jittery access delay when restarting TiKV due to waiting for the log to be applied, improving the stability of TiKV [#15874](https://github.com/tikv/tikv/issues/15874) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize the cleanup mechanism of residual data to mitigate the impact on request latency [#18107](https://github.com/tikv/tikv/issues/18107) @[LykxSassinator](https://github.com/LykxSassinator)
    - Optimize the performance of `fetch_entries_to` in Raft Engine to reduce contention and improve performance under mixed workloads [#18605](https://github.com/tikv/tikv/issues/18605) @[LykxSassinator](https://github.com/LykxSassinator)
    - Support dynamically modifying flow-control configurations for write operations [#17395](https://github.com/tikv/tikv/issues/17395) @[glorv](https://github.com/glorv)
    - Support ingesting SST files without blocking foreground writes, reducing the impact of latency [#18081](https://github.com/tikv/tikv/issues/18081) @[hhwyt](https://github.com/hhwyt)
    - Optimize the detection mechanism for I/O jitter on KvDB disks when KvDB and RaftDB use separate mount paths [#18463](https://github.com/tikv/tikv/issues/18463) @[LykxSassinator](https://github.com/LykxSassinator)
    - Add slow logs for peer and store messages [#16600](https://github.com/tikv/tikv/issues/16600) @[Connor1996](https://github.com/Connor1996)

+ PD

    - Add GO runtime-related monitoring metrics in Prometheus [#8931](https://github.com/tikv/pd/issues/8931) @[bufferflies](https://github.com/bufferflies)
    - Reduce unnecessary error logs [#9370](https://github.com/tikv/pd/issues/9370) @[bufferflies](https://github.com/bufferflies)

+ TiFlash

    - Enhance the observability for TiFlash OOM risks in wide table scenarios [#10272](https://github.com/pingcap/tiflash/issues/10272) @[JaySon-Huang](https://github.com/JaySon-Huang)
    - Increase the maximum retry count when acquiring storage snapshots to improve query stability for large tables [#10300](https://github.com/pingcap/tiflash/issues/10300) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + Backup & Restore (BR)

        - When deploying TiDB on Amazon EC2, BR supports AWS Instance Metadata Service Version 2 (IMDSv2). You can configure your EC2 instance to allow BR to use the IAM role associated with the instance for appropriate permissions to access Amazon S3 [#16443](https://github.com/tikv/tikv/issues/16443) @[pingyu](https://github.com/pingyu)
        - The Download API of TiKV supports filtering out data within a certain time range when downloading backup files, which avoids importing outdated or future data versions during restore [#18399](https://github.com/tikv/tikv/issues/18399) @[3pointer](https://github.com/3pointer)
