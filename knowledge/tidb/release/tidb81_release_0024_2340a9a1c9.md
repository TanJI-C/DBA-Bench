# TiKV changes in TiDB 2.0 RC3

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0-rc.3.md`
- Source Title: `TiDB 2.0 RC3 Release Notes`
- Source Heading Path: `TiDB 2.0 RC3 Release Notes > TiKV`
- Source Line Ranges: `38-59`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`
- Topic Tags: `release-notes`, `region-merge`, `raft-snapshot`, `coprocessor`, `readpool`, `timeouts`, `space-management`, `data-recovery`, `rocksdb`, `deleterange`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0024_2340a9a1c9`
- Source ID: `tidb-docs-8.1:releases/release-2.0-rc.3.md#tikv`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb9eaeb2909a09cd89dbb2e3a1cb750c481acaa1e01261cabaed450fe12bf3ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0-rc.3#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0-rc.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV 2.0 RC3 release-note items about Region Merge, snapshot and heartbeat behavior, Coprocessor streaming and timeout settings, RocksDB operations, DeleteRange, or recovery tooling.
- Retrieval Keywords: TiKV 2.0 RC3, Region Merge, Raft snapshot process completed, Raw DeleteRange API, GetMetric API, RocksDB sync files, space reclaiming after deleting data, tikv-ctl, snapshot, streaming in Coprocessor, Readpool, raw_get, get, batch_get, request timeout of Coprocessor, streaming aggregation in Coprocessor, Region heartbeats, snapshot files disk space, cannot elect a leader for a long time, garbage cleaning when starting the server, compaction events, scan lock, DeleteRange, Region deletion, modifying RocksDB parameters online
- Follow-up Guidance: The source also states that TiKV records and reports Regions that cannot elect a leader for a long time and carries time information in Region heartbeats.
- Classification Note: This is a TiKV release-notes chunk because it lists TiKV 2.0 RC3 storage-engine, Coprocessor, Region management, timeout, recovery, and RocksDB-related changes.

## Official Source Content

## TiKV

- Support Region Merge
- Inform PD immediately once the Raft snapshot process is completed, to speed up balancing
- Add the Raw DeleteRange API
- Add the GetMetric API
- Reduce the I/O fluctuation caused by RocksDB sync files
- Optimize the space reclaiming mechanism after deleting data
- Improve the data recovery tool `tikv-ctl`
- Fix the issue that it is slow to make nodes down caused by snapshot
- Support streaming in Coprocessor
- Support Readpool and increase the `raw_get/get/batch_get` by 30%
- Support configuring the request timeout of Coprocessor
- Support streaming aggregation in Coprocessor
- Carry time information in Region heartbeats
- Limit the space usage of snapshot files to avoid consuming too much disk space
- Record and report the Regions that cannot elect a leader for a long time
- Speed up garbage cleaning when starting the server
- Update the size information about the corresponding Region according to compaction events
- Limit the size of `scan lock` to avoid request timeout
- Use `DeleteRange` to speed up Region deletion
- Support modifying RocksDB parameters online
