# TiDB 4.0 GA overview, compatibility changes, and important fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0-ga.md`
- Source Title: `TiDB 4.0 GA Release Notes`
- Source Heading Path: `TiDB 4.0 GA Release Notes | TiDB 4.0 GA Release Notes > Compatibility Changes | TiDB 4.0 GA Release Notes > Important Bug Fixes`
- Source Line Ranges: `5-30`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `ticdc`, `tikv`, `tiflash`, `br`
- Topic Tags: `release-notes`, `compatibility`, `bug-fixes`, `transactions`, `changefeed`, `backup`, `panic`, `data-loss`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0140_abf7fd4d10`
- Source ID: `tidb-docs-8.1:releases/release-4.0-ga.md#tidb-4-0-ga-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9f79c1354517d79293a82cf86239ef762df459c15c6bf731a86d9dcec7c7fae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0-ga#tidb-4-0-ga-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 4.0.0 GA compatibility changes or important fixes involving large transaction error messages, TiCDC Changefeed configuration changes, BR backup DefaultNotFound errors, ReadIndex panics, snapshot file panics after restart, or TiFlash data loss related to Raft Admin Command.
- Retrieval Keywords: TiDB 4.0.0, Compatibility Changes, Important Bug Fixes, large-sized transactions, error message, TiCDC, Changefeed configuration file, ignore-txn-start-ts, commit_ts, start_ts, TiKV, DefaultNotFound, Backup & Restore, BR, ReadIndex, snapshot files, restarted, TiFlash, data loss, Raft Admin Command
- Follow-up Guidance: This chunk also points to TiCDC transaction filtering changes from `commit_ts` to `start_ts` and the new `ignore-txn-start-ts` configuration item.
- Classification Note: The official content is a release-notes summary covering compatibility changes and important bug fixes across TiDB, TiCDC, TiKV, and TiFlash in TiDB 4.0 GA.

## Official Source Content

# TiDB 4.0 GA Release Notes

Release date: May 28, 2020

TiDB version: 4.0.0
## Compatibility Changes

* TiDB
    - Optimize the error message of the large-sized transactions for easier troubleshooting [#17219](https://github.com/pingcap/tidb/pull/17219)

* TiCDC
    - Optimize the structure of the `Changefeed` configuration file to improve usability [#588](https://github.com/pingcap/tiflow/pull/588)
    - Add the `ignore-txn-start-ts` configuration item, and change the condition from `commit_ts` to `start_ts` during transactions filtering [#589](https://github.com/pingcap/tiflow/pull/589)
## Important Bug Fixes

* TiKV
    - Fix the `DefaultNotFound` error that occurs when backing up using Backup & Restore (BR) [#7937](https://github.com/tikv/tikv/pull/7937)
    - Fix system panics caused by the out-of-order `ReadIndex` packages [#7930](https://github.com/tikv/tikv/pull/7930)
    - Fix system panics caused by incorrectly removing snapshot files after TiKV is restarted [#7927](https://github.com/tikv/tikv/pull/7927)

* TiFlash
    - Fix the possible data loss issue that occurs when the system panics because of incorrect processing logic of `Raft Admin Command`
