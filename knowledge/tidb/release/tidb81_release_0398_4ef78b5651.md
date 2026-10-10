# Component improvements in 6.5.4

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.4.md`
- Source Title: `TiDB 6.5.4 Release Notes`
- Source Heading Path: `TiDB 6.5.4 Release Notes > Improvements`
- Source Line Ranges: `23-73`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `br`, `ticdc`, `dm`, `dumpling`
- Topic Tags: `improvements`, `load-data`, `performance`, `scheduling`, `metrics`, `diagnostics`, `rocksdb`, `swagger`, `etcd`, `http-connections`, `write-performance`, `availability`, `backup-restore`, `restore-parameters`, `kafka`, `storage-sink`, `ddl`, `export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0398_4ef78b5651`
- Source ID: `tidb-docs-8.1:releases/release-6.5.4.md#improvements`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `480f858703986dcfdab7ffa3a9fc0c02d053940d2726bd2f78b90baa7481274f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.4#improvements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the list of component improvements introduced in TiDB 6.5.4 across TiDB, TiKV, PD, TiFlash, BR, TiCDC, DM, and Dumpling.
- Retrieval Keywords: TiDB 6.5.4 Improvements, LOAD DATA assignment expressions, reading the dumped chunks from disk, halt-scheduling configuration item, suspend PD scheduling, check_leader requests gzip compression, Max gap of safe-ts, Min safe ts region, tikv-ctl get-region-read-progress, resolved-ts and safe-ts, RocksDB configurations disable TTL periodic compaction, Titan manifest files mutex, compaction when a Region is split, block the Swagger API by default, improve the high availability of etcd, GetRegions requests memory consumption, reusing HTTP connections, TiFlash write performance IO batch optimization, removing unnecessary fsync operations, TiFlash coprocessor task queue maximum length, BR MaxIdleConns, MaxIdleConnsPerHost, WaitTiflashReady, TiCDC retries after a failure status message, synchronizing to Kafka only sending the primary key, Storage Sink hexadecimal encoding for HEX formatted data, AWS DMS format specifications, DM strict optimistic mode, incompatible DDL statements, Dumpling -sql parameter
- Follow-up Guidance: 
- Classification Note: This is a release-notes chunk classified as shared because it lists official 6.5.4 improvements for multiple components and tools.

## Official Source Content

## Improvements

+ TiDB

    - Optimize the performance of `LOAD DATA` statements that contain assignment expressions [#46081](https://github.com/pingcap/tidb/issues/46081) @[gengliqi](https://github.com/gengliqi)
    - Optimize the performance of reading the dumped chunks from disk [#45125](https://github.com/pingcap/tidb/issues/45125) @[YangKeao](https://github.com/YangKeao)
    - Add a `halt-scheduling` configuration item to suspend PD scheduling [#6493](https://github.com/tikv/pd/issues/6493) @[JmPotato](https://github.com/JmPotato)

+ TiKV

    - Use gzip compression for `check_leader` requests to reduce traffic [#14553](https://github.com/tikv/tikv/issues/14553) @[you06](https://github.com/you06)
    - Add the `Max gap of safe-ts` and `Min safe ts region` metrics and introduce the `tikv-ctl get-region-read-progress` command to better observe and diagnose the status of resolved-ts and safe-ts [#15082](https://github.com/tikv/tikv/issues/15082) @[ekexium](https://github.com/ekexium)
    - Expose some RocksDB configurations in TiKV that allow users to disable features such as TTL and periodic compaction [#14873](https://github.com/tikv/tikv/issues/14873) @[LykxSassinator](https://github.com/LykxSassinator)
    - Avoid holding mutex when writing Titan manifest files to prevent affecting other threads [#15351](https://github.com/tikv/tikv/issues/15351) @[Connor1996](https://github.com/Connor1996)
    - Optimize the compaction mechanism: when a Region is split, if there is no key to split, a compaction is triggered to eliminate excessive MVCC versions [#15282](https://github.com/tikv/tikv/issues/15282) @[SpadeA-Tang](https://github.com/SpadeA-Tang)

+ PD 

    - Support blocking the Swagger API by default when the Swagger server is not enabled [#6786](https://github.com/tikv/pd/issues/6786) @[bufferflies](https://github.com/bufferflies)
    - Improve the high availability of etcd [#6554](https://github.com/tikv/pd/issues/6554) [#6442](https://github.com/tikv/pd/issues/6442) @[lhy1024](https://github.com/lhy1024)
    - Reduce the memory consumption of `GetRegions` requests [#6835](https://github.com/tikv/pd/issues/6835) @[lhy1024](https://github.com/lhy1024)
    - Support reusing HTTP connections [#6913](https://github.com/tikv/pd/issues/6913) @[nolouch](https://github.com/nolouch)

+ TiFlash 

    - Improve TiFlash write performance through IO batch optimization [#7735](https://github.com/pingcap/tiflash/issues/7735) @[lidezhu](https://github.com/lidezhu)
    - Improve TiFlash write performance by removing unnecessary fsync operations [#7736](https://github.com/pingcap/tiflash/issues/7736) @[lidezhu](https://github.com/lidezhu)
    - Limit the maximum length of the TiFlash coprocessor task queue to avoid excessive queuing of coprocessor tasks, which impacts TiFlash's service availability [#7747](https://github.com/pingcap/tiflash/issues/7747) @[LittleFall](https://github.com/LittleFall)

+ Tools

    + Backup & Restore (BR) 

        - Enhance support for connection reuse by setting `MaxIdleConns` and `MaxIdleConnsPerHost` parameters in the HTTP client [#46011](https://github.com/pingcap/tidb/issues/46011) @[Leavrth](https://github.com/Leavrth)
        - Improve fault tolerance of BR when it fails to connect to PD or external S3 storage [#42909](https://github.com/pingcap/tidb/issues/42909) @[Leavrth](https://github.com/Leavrth)
        - Add a new restore parameter `WaitTiflashReady`. When this parameter is enabled, the restore operation will be completed after TiFlash replicas are successfully replicated [#43828](https://github.com/pingcap/tidb/issues/43828) [#46302](https://github.com/pingcap/tidb/issues/46302) @[3pointer](https://github.com/3pointer)

    + TiCDC

        - Refine the status message when TiCDC retries after a failure [#9483](https://github.com/pingcap/tiflow/issues/9483) @[asddongmen](https://github.com/asddongmen)
        - Optimize the way TiCDC handles messages that exceed the limit when synchronizing to Kafka by supporting only sending the primary key to the downstream [#9574](https://github.com/pingcap/tiflow/issues/9574) @[3AceShowHand](https://github.com/3AceShowHand)
        - Storage Sink now supports hexadecimal encoding for HEX formatted data, making it compatible with AWS DMS format specifications [#9373](https://github.com/pingcap/tiflow/issues/9373) @[CharlesCheung96](https://github.com/CharlesCheung96)

    + TiDB Data Migration (DM) 
    
        - Support strict optimistic mode for incompatible DDL statements [#9112](https://github.com/pingcap/tiflow/issues/9112) @[GMHDBJD](https://github.com/GMHDBJD)

    + Dumpling 

        - Reduce export overhead by skipping querying all databases and tables when exporting data with the `-sql` parameter [#45239](https://github.com/pingcap/tidb/issues/45239) @[lance6716](https://github.com/lance6716)
