# PD and TiKV release changes and compatibility notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-beta.md`
- Source Title: `TiDB 2.1 Beta Release Notes`
- Source Heading Path: `TiDB 2.1 Beta Release Notes > PD | TiDB 2.1 Beta Release Notes > TiKV`
- Source Line Ranges: `59-84`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `release-notes`, `raft-prevote`, `scheduler`, `region-merge`, `raft-learner`, `compatibility`, `metrics`, `unsafe-recovery`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0039_dc096b81eb`
- Source ID: `tidb-docs-8.1:releases/release-2.1-beta.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `07af024493d2679875b7b0d2d1908a1d7bbd9d6d1ed927da7ec8b1325ba9bf1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-beta#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-beta.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 Beta release-note details for PD and TiKV behavior changes, metrics, scheduling, Raft PreVote, raft learner, and compatibility notes.
- Retrieval Keywords: TiDB 2.1 Beta Release Notes, PD, TiKV, Raft PreVote, leader reelection, network isolation, Balance Scheduler, hotspot scheduler, region merge, raft learner, pd-recover, max-replica, Filter metrics, tikv-ctl unsafe recovery, TiKV disk space is used up, Compatibility notes, Do not support rolling back to v2.0.x or earlier, new version storage engine, upgraded from 1.x to 2.1, rolling update should be first applied to TiKV and then PD, nightly-2018-06-14, RocksDB, ingest, GC, static metric, YCSB raw get, asynchronous log, thread status
- Follow-up Guidance: This source also contains TiDB 2.1 Beta release-note details for the TiDB component in a separate section.
- Classification Note: This is a self-managed release-notes chunk covering PD and TiKV changes, including scheduler behavior, metrics, performance items, and explicit compatibility notes from the official content.

## Official Source Content

## PD

- Enable Raft PreVote between PD nodes to avoid leader reelection when network recovers after network isolation
- Optimize the issue that Balance Scheduler schedules small Regions frequently
- Optimize the hotspot scheduler to improve its adaptability in traffic statistics information jitters
- Skip the Regions with a large number of rows when scheduling `region merge`
- Enable `raft learner` by default to lower the risk of unavailable data caused by machine failure during scheduling
- Remove `max-replica` from `pd-recover`
- Add `Filter` metrics
- Fix the issue that Region information is not updated after tikv-ctl unsafe recovery
- Fix the issue that TiKV disk space is used up caused by replica migration in some scenarios
- Compatibility notes
    - Do not support rolling back to v2.0.x or earlier due to update of the new version storage engine
    - Enable `raft learner` by default in the new version of PD. If the cluster is upgraded from 1.x to 2.1, the machine should be stopped before upgrade or a rolling update should be first applied to TiKV and then PD
## TiKV

- Upgrade Rust to the `nightly-2018-06-14` version
- Enable `Raft PreVote` to avoid leader reelection generated when network recovers after network isolation
- Add a metric to display the number of files and `ingest` related information in each layer of RocksDB
- Print `key` with too many versions when GC works
- Use `static metric` to optimize multi-label metric performance (YCSB `raw get` is improved by 3%)
- Remove `box` in multiple modules and use patterns to improve the operating performance (YCSB `raw get` is improved by 3%)
- Use `asynchronous log` to improve the performance of writing logs
- Add a metric to collect the thread status
- Decease memory copy times by decreasing `box` used in the application to improve the performance
