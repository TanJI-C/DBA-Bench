# TiDB 5.1.3 release and TiKV bug fix

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.1.3.md`
- Source Title: `TiDB 5.1.3 Release Note`
- Source Heading Path: `TiDB 5.1.3 Release Note | TiDB 5.1.3 Release Note > Bug fix`
- Source Line Ranges: `5-16`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `release-note`, `bug-fix`, `gckeys`, `compaction-filter`, `gc`, `mvcc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0231_debb648d60`
- Source ID: `tidb-docs-8.1:releases/release-5.1.3.md#tidb-5-1-3-release-note`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `18046ef10f588829a223dfe3852223578c6c6d1c8db0eb5d5a3fb6733cb9b28a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.1.3#tidb-5-1-3-release-note
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.1.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a TiDB 5.1.3 release note entry about a TiKV bug where the GcKeys task fails for multiple keys and compaction filter GC might not drop MVCC deletion information.
- Retrieval Keywords: TiDB 5.1.3 Release Note, TiKV bug fix, GcKeys task, multiple keys, compaction filter GC, MVCC deletion information, #11217
- Follow-up Guidance: 
- Classification Note: The official content classifies this as a release-note bug fix in TiKV within the TiDB 5.1.3 self-managed release.

## Official Source Content

# TiDB 5.1.3 Release Note

Release date: December 3, 2021

TiDB version: 5.1.3
## Bug fix

+ TiKV

    - Fix the issue that the `GcKeys` task does not work when it is called by multiple keys. Caused by this issue, compaction filter GC might not drop the MVCC deletion information. [#11217](https://github.com/tikv/tikv/issues/11217)
