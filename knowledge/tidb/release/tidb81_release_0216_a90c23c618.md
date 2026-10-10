# TiDB 5.0.5 release note and TiKV bug fix

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.5.md`
- Source Title: `TiDB 5.0.5 Release Note`
- Source Heading Path: `TiDB 5.0.5 Release Note | TiDB 5.0.5 Release Note > Bug fix`
- Source Line Ranges: `5-16`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `shared`
- Topic Tags: `release-date`, `version`, `bug-fix`, `gc`, `mvcc`, `compaction-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0216_a90c23c618`
- Source ID: `tidb-docs-8.1:releases/release-5.0.5.md#tidb-5-0-5-release-note`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `937c5e40992012b801a3ad3a0b9a2cc4922d578cf0c422d6b08177191f7a5ae1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.5#tidb-5-0-5-release-note
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.5.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 5.0.5 release note entry about a TiKV bug fix involving GcKeys, compaction filter GC, and MVCC deletion information.
- Retrieval Keywords: TiDB 5.0.5 Release Note, Release date December 3, 2021, TiKV bug fix, GcKeys task does not work when it is called by multiple keys, compaction filter GC, MVCC deletion information, #11217
- Follow-up Guidance: The source identifies the related TiKV issue as #11217.
- Classification Note: This is classified as a release item for the tikv component because the official content is a TiDB 5.0.5 release note bug fix describing a TiKV issue.

## Official Source Content

# TiDB 5.0.5 Release Note

Release date: December 3, 2021

TiDB version: 5.0.5
## Bug fix

+ TiKV

    - Fix the issue that the `GcKeys` task does not work when it is called by multiple keys. Caused by this issue, compaction filter GC might not drop the MVCC deletion information. [#11217](https://github.com/tikv/tikv/issues/11217)
