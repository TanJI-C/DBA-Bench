# TiKV performance improvements and bug fixes in 2.1 RC2

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.2.md`
- Source Title: `TiDB 2.1 RC2 Release Notes`
- Source Heading Path: `TiDB 2.1 RC2 Release Notes > TiKV`
- Source Line Ranges: `105-119`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `lightning`
- Topic Tags: `release-notes`, `performance`, `region-splitting`, `transaction-scheduler`, `pushdown`, `configuration`, `raft`, `leader-scheduling`, `importer`, `garbage-collection`, `region-merge`, `local-reader`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0051_4fdb97a7a0`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.2.md#tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e0db44988e4173d0b46be5295a5c226f5c0ed55e468ec6b345a022103a4cb6a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.2#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiKV 2.1 RC2 release-note details about performance improvements, new configurations, and bug fixes involving Region splitting, transaction scheduling, Raft, tikv-importer, garbage cleanup, Region merge, or local reader behavior.
- Retrieval Keywords: TiKV 2.1 RC2, release notes, splitting Regions based on statistics estimation, reduce the I/O cost, transaction scheduler, reduce clone, pushdown support, built-in functions, leader-transfer-max-log-lag, leader scheduling, max-open-engines, tikv-importer, cleanup speed of garbage data, snapshot apply, commit message for crucial Raft messages, leader election, PreVote, newly split Region, follower related statistics, merging Regions, local reader uses obsolete Region information
- Follow-up Guidance: The chunk also points to specific TiKV pull requests for each listed performance improvement, configuration addition, and bug fix.
- Classification Note: This is a self-managed TiKV release-notes chunk because the official content lists TiKV-specific performance items, improvements, configuration names, and bug fixes in TiDB 2.1 RC2.

## Official Source Content

## TiKV

* Performance
    * Support splitting Regions based on statistics estimation to reduce the I/O cost [#3511](https://github.com/tikv/tikv/pull/3511)
    * Reduce clone in the transaction scheduler [#3530](https://github.com/tikv/tikv/pull/3530)
* Improvements
    * Add the pushdown support for a large number of built-in functions
    * Add the `leader-transfer-max-log-lag` configuration to fix the failure issue of leader scheduling in specific scenarios [#3507](https://github.com/tikv/tikv/pull/3507)
    * Add the `max-open-engines` configuration to limit the number of engines opened by `tikv-importer` simultaneously [#3496](https://github.com/tikv/tikv/pull/3496)
    * Limit the cleanup speed of garbage data to reduce the impact on `snapshot apply` [#3547](https://github.com/tikv/tikv/pull/3547)
    * Broadcast the commit message for crucial Raft messages to avoid unnecessary delay [#3592](https://github.com/tikv/tikv/pull/3592)
* Bug fixes
    * Fix the leader election issue caused by discarding the `PreVote` message of the newly split Region [#3557](https://github.com/tikv/tikv/pull/3557)
    * Fix follower related statistics after merging Regions [#3573](https://github.com/tikv/tikv/pull/3573)
    * Fix the issue that the local reader uses obsolete Region information [#3565](https://github.com/tikv/tikv/pull/3565)
