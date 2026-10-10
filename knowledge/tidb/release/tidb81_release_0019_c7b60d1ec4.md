# PD and TiKV release changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0-ga.md`
- Source Title: `TiDB 2.0 Release Notes`
- Source Heading Path: `TiDB 2.0 Release Notes > PD | TiDB 2.0 Release Notes > TiKV`
- Source Line Ranges: `59-130`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `shared`
- Topic Tags: `release-notes`, `region-merge`, `raft-learner`, `scheduler`, `tls`, `region-split`, `hotspot`, `debugging`, `metrics`, `heartbeat`, `rawkv`, `deleterange`, `coprocessor`, `readpool`, `importsst`, `lightning-import`, `rocksdb`, `stability`, `oom`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0019_c7b60d1ec4`
- Source ID: `tidb-docs-8.1:releases/release-2.0-ga.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0b437b71d6595712be5520d02b67c667f7e56ab3d3090b931d6144abfadff2de`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0-ga#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.0 GA release-note details about PD and TiKV features, scheduling, debugging interfaces, performance, or stability changes.
- Retrieval Keywords: PD release notes, TiKV release notes, Region Merge, Raft Learner, balance-leader scheduler, balance-region scheduler, hot-region scheduler, Drop Region, abnormal Regions, Region isolation level, PD leader and etcd leader, Raw DeleteRange, GetMetric API, Raw Batch Put, Raw Batch Get, Raw Batch Delete, Raw Batch Scan, Streaming Aggregation in Coprocessor, block-cache-size, ImportSST, TiKV Importer, TiDB Lightning, ReadPool, DeleteFilesInRanges, gRPC keepalive, OOM issue caused by too many snapshots, OOM issue caused by an increase of the Region number
- Follow-up Guidance: The source also includes PD operations interface items such as TLS, label-based scheduling policies, manual Region split, and scattering a specified Region.
- Classification Note: This is classified as a TiKV-related release chunk because the official content covers both PD and TiKV 2.0 GA changes, with substantial feature, performance, and stability details for those components.

## Official Source Content

## PD

- Support `Region Merge`, to merge empty Regions after deleting data [experimental]
- Support `Raft Learner` [experimental]
- Optimize the scheduler
    - Make the scheduler to adapt to different Region sizes
    - Improve the priority and speed of restoring data during TiKV outage
    - Speed up data transferring when removing a TiKV node
    - Optimize the scheduling policies to prevent the disks from becoming full when the space of TiKV nodes is insufficient
    - Improve the scheduling efficiency of the balance-leader scheduler
    - Reduce the scheduling overhead of the balance-region scheduler
    - Optimize the execution efficiency of the hot-region scheduler
- Operations interface and configuration
    - Support TLS
    - Support prioritizing the PD leaders
    - Support configuring the scheduling policies based on labels
    - Support configuring stores with a specific label not to schedule the Raft leader
    - Support splitting Region manually to handle the hotspot in a single Region
    - Support scattering a specified Region to manually adjust Region distribution in some cases
    - Add check rules for configuration parameters and improve validity check of the configuration items
- Debugging interface
    - Add the `Drop Region` debugging interface
    - Add the interfaces to enumerate the health status of each PD
- Statistics
    - Add statistics about abnormal Regions
    - Add statistics about Region isolation level
    - Add scheduling related metrics
- Performance
    - Keep the PD leader and the etcd leader together in the same node to improve write performance
    - Optimize the performance of Region heartbeat
## TiKV

- Features
    - Protect critical configuration from incorrect modification
    - Support `Region Merge` [experimental]
    - Add the `Raw DeleteRange` API
    - Add the `GetMetric` API
    - Add `Raw Batch Put`, `Raw Batch Get`, `Raw Batch Delete` and `Raw Batch Scan`
    - Add Column Family options for the RawKV API and support executing operation on a specific Column Family
    - Support Streaming and Streaming Aggregation in Coprocessor
    - Support configuring the request timeout of Coprocessor
    - Carry timestamps with Region heartbeats
    - Support modifying some RocksDB parameters online, such as `block-cache-size`
    - Support configuring the behavior of Coprocessor when it encounters some warnings or errors
    - Support starting in the importing data mode to reduce write amplification during the data importing process
    - Support manually splitting Region in halves
    - Improve the data recovery tool `tikv-ctl`
    - Return more statistics in Coprocessor to guide the behavior of TiDB
    - Support the `ImportSST` API to import SST files [experimental]
    - Add the TiKV Importer binary to integrate with TiDB Lightning to import data quickly [experimental]
- Performance
    - Optimize read performance using `ReadPool` and increase the `raw_get/get/batch_get` by 30%
    - Improve metrics performance
    - Inform PD immediately once the Raft snapshot process is completed to speed up balancing
    - Solve performance jitter caused by RocksDB flushing
    - Optimize the space reclaiming mechanism after deleting data
    - Speed up garbage cleaning while starting the server
    - Reduce the I/O overhead during replica migration using `DeleteFilesInRanges`
- Stability
    - Fix the issue that gRPC call does not get returned when the PD leader switches
    - Fix the issue that it is slow to offline nodes caused by snapshots
    - Limit the temporary space usage consumed by migrating replicas
    - Report the Regions that cannot elect a leader for a long time
    - Update the Region size information in time according to compaction events
    - Limit the size of scan lock to avoid request timeout
    - Limit the memory usage when receiving snapshots to avoid OOM
    - Increase the speed of CI test
    - Fix the OOM issue caused by too many snapshots
    - Configure `keepalive` of gRPC
    - Fix the OOM issue caused by an increase of the Region number
