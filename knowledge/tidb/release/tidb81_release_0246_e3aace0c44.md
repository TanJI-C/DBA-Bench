# TiDB 5.2.3 release date and TiKV bug fix

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.2.3.md`
- Source Title: `TiDB 5.2.3 Release Note`
- Source Heading Path: `TiDB 5.2.3 Release Note | TiDB 5.2.3 Release Note > Bug fix`
- Source Line Ranges: `5-16`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `shared`
- Topic Tags: `release-note`, `bug-fix`, `gckeys`, `compaction-filter`, `mvcc`, `gc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0246_e3aace0c44`
- Source ID: `tidb-docs-8.1:releases/release-5.2.3.md#tidb-5-2-3-release-note`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc10a3e1ee7fab0b8fa6aa5a9b38087b10b0794e272d3f17d69556c8a817cd7d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.2.3#tidb-5-2-3-release-note
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.2.3.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 5.2.3 release date or a TiKV bug fix involving `GcKeys`, multiple keys, compaction filter GC, and MVCC deletion information.
- Retrieval Keywords: TiDB 5.2.3 Release Note, Release date December 3, 2021, TiDB version 5.2.3, TiKV bug fix, GcKeys task does not work when it is called by multiple keys, compaction filter GC might not drop the MVCC deletion information, MVCC deletion information, #11217
- Follow-up Guidance: The chunk identifies the related TiKV issue as `#11217`.
- Classification Note: The classification is release / tikv because the official content is a TiDB 5.2.3 release note bug fix entry for TiKV in a self-managed release document.

## Official Source Content

# TiDB 5.2.3 Release Note

Release date: December 3, 2021

TiDB version: 5.2.3
## Bug fix

+ TiKV

    - Fix the issue that the `GcKeys` task does not work when it is called by multiple keys. Caused by this issue, compaction filter GC might not drop the MVCC deletion information. [#11217](https://github.com/tikv/tikv/issues/11217)
