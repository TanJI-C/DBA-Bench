# Release overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.4.md`
- Source Title: `TiDB 5.1.4 Release Notes`
- Source Heading Path: `TiDB 5.1.4 Release Notes | TiDB 5.1.4 Release Notes > Compatibility changes | TiDB 5.1.4 Release Notes > Improvements`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`
- Topic Tags: `release-notes`, `compatibility`, `default-values`, `ttl`, `partition-pruning`, `memory-usage`, `sst-import`, `scheduler-exit`, `function-pushdown`, `mpp`, `changefeed`, `monitoring`, `backoff`, `replication-latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0232_b74173e6ca`
- Source ID: `tidb-docs-8.1:releases/release-5.1.4.md#tidb-5-1-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bdc5eec77ba7dc2145522e96ebb79fb676845b3d16e2c6c4b2b31acbd5a118ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.4#tidb-5-1-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.1.4 release-note items about compatibility changes, default value changes, or improvement summaries across TiDB, TiKV, PD, TiFlash, and TiCDC.
- Retrieval Keywords: TiDB 5.1.4 Release Notes, Compatibility changes, Improvements, tidb_analyze_version, storage.enable-ttl, RawKV mode, max-message-bytes, partition pruning, IN expression, Range partition tables, IndexJoin, memory usage, procfs v0.12.0, Raft client, SST files, Import thread pool, Apply thread pool, scheduler exit, ADDDATE(), DATE_ADD(), INET6_ATON(), INET6_NTOA(), INET_ATON(), INET_NTOA(), DAG request, max supported depth, changefeed, exponential backoff, replication latency, incremental scan, EventFeed retry rate limited, no owner alert, mounter row, table sink total row, buffer sink total row, gRPC congestion, KV client recover
- Follow-up Guidance: The same release notes continue with a Bug fixes section for TiDB, TiKV, PD, and TiFlash.
- Classification Note: This is a release-notes summary chunk covering compatibility changes and improvements in TiDB 5.1.4 for multiple components.

## Official Source Content

# TiDB 5.1.4 Release Notes

Release Date: February 22, 2022

TiDB version: 5.1.4
## Compatibility changes

+ TiDB

    - Change the default value of the system variable [`tidb_analyze_version`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_version-new-in-v510) from `2` to `1` [#31748](https://github.com/pingcap/tidb/issues/31748)
    - Since v5.1.4, if TiKV is configured with `storage.enable-ttl = true`, the requests from TiDB are rejected, because the TTL feature of TiKV only supports the [RawKV mode](https://tikv.org/docs/5.1/concepts/explore-tikv-features/ttl/) [#27303](https://github.com/pingcap/tidb/issues/27303)

+ Tools

    + TiCDC

        - Set the default value of `max-message-bytes` to 10M [#4041](https://github.com/pingcap/tiflow/issues/4041)
## Improvements

+ TiDB

    - Support partition pruning for the built-in `IN` expression in Range partition tables [#26739](https://github.com/pingcap/tidb/issues/26739)
    - Improve the accuracy of tracking memory usage when `IndexJoin` is executed [#28650](https://github.com/pingcap/tidb/issues/28650)

+ TiKV

    - Update the proc filesystem (procfs) to v0.12.0 [#11702](https://github.com/tikv/tikv/issues/11702)
    - Improve the error log report in the Raft client [#11959](https://github.com/tikv/tikv/issues/11959)
    - Increase the speed of inserting SST files by moving the verification process to the `Import` thread pool from the `Apply` thread pool [#11239](https://github.com/tikv/tikv/issues/11239)

+ PD

    - Speed up the exit process of schedulers [#4146](https://github.com/tikv/pd/issues/4146)

+ TiFlash

    - Support pushing down `ADDDATE()` and `DATE_ADD()` to TiFlash
    - Support pushing down `INET6_ATON()` and `INET6_NTOA()` to TiFlash
    - Support pushing down `INET_ATON()` and `INET_NTOA()` to TiFlash
    - Increase the max supported depth of an expression or a plan tree in a DAG request from `100` to `200`

+ Tools

    + TiCDC

        - Add the exponential backoff mechanism for restarting a changefeed. [#3329](https://github.com/pingcap/tiflow/issues/3329)
        - Reduce the replication latency when replicating many tables [#3900](https://github.com/pingcap/tiflow/issues/3900)
        - Add metrics for observing the remaining time of incremental scan [#2985](https://github.com/pingcap/tiflow/issues/2985)
        - Reduce the count of "EventFeed retry rate limited" logs [#4006](https://github.com/pingcap/tiflow/issues/4006)
        - Add more Prometheus and Grafana monitoring metrics and alerts, including `no owner alert`, `mounter row`, `table sink total row`, and `buffer sink total row` [#4054](https://github.com/pingcap/tiflow/issues/4054) [#1606](https://github.com/pingcap/tiflow/issues/1606)
        - Optimize rate limiting control on TiKV reloads to reduce gPRC congestion during changefeed initialization [#3110](https://github.com/pingcap/ticdc/issues/3110)
        - Reduce the time for the KV client to recover when a TiKV store is down [#3191](https://github.com/pingcap/tiflow/issues/3191)
