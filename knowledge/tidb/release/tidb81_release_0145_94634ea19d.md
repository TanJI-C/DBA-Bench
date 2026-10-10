# Bug fixes in beta.1

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-beta.1.md`
- Source Title: `TiDB 4.0.0 Beta.1 Release Notes`
- Source Heading Path: `TiDB 4.0.0 Beta.1 Release Notes > Bug Fixes`
- Source Line Ranges: `78-92`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `bug-fixes`, `views`, `plan-cache`, `partitioning`, `cast`, `web-interface`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0145_94634ea19d`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-beta.1.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `57f92aef5e787f4d401ed86e0b872913f119458f5a20c68d2cc9a7c01b7a3bd9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-beta.1#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-beta.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for bugs fixed in TiDB 4.0.0-beta.1 involving views, plan cache, partitioned tables, IsTrue outer join simplification, show binding privilege checks, CAST behavior, or TiDB Lightning web interface issues.
- Retrieval Keywords: TiDB 4.0.0 Beta.1 Release Notes, Bug Fixes, view, column name exceeds 64 characters, information_schema.views, create or replace view, BatchPointGet, plan cache, wrong partitioned table after the timezone is modified, IsTrue function, outer join simplification, show binding, CAST function, TiDB and TiKV inconsistent behaviors, TiDB Lightning web interface, Server mode
- Follow-up Guidance: This chunk includes bug fixes for TiDB, TiKV, and TiDB Lightning in the beta.1 release.
- Classification Note: The official content is classified as a release note because it summarizes resolved defects for TiDB 4.0.0-beta.1 across several components.

## Official Source Content

## Bug Fixes

* TiDB
    + Fix the issue that an error is reported when creating `view` with a column name that exceeds 64 characters [#14850](https://github.com/pingcap/tidb/pull/14850)
    + Fix the issue that duplicate data exists in `information_schema.views` because the `create or replace view` statement is incorrectly processed [#14832](https://github.com/pingcap/tidb/pull/14832)
    + Fix the incorrect results of `BatchPointGet` when `plan cache` is enabled [#14855](https://github.com/pingcap/tidb/pull/14855)
    + Fix the issue that data is inserted into the wrong partitioned table after the timezone is modified [#14370](https://github.com/pingcap/tidb/pull/14370)
    + Fix the panic occurred when rebuilding expression using the invalid name of the `IsTrue` function during the outer join simplification [#14515](https://github.com/pingcap/tidb/pull/14515)
    + Fix the incorrect privilege check for the`show binding` statement [#14443](https://github.com/pingcap/tidb/pull/14443)

* TiKV
    + Fix the inconsistent behaviors of the `CAST` function in TiDB and TiKV [#6463](https://github.com/tikv/tikv/pull/6463) [#6461](https://github.com/tikv/tikv/pull/6461) [#6459](https://github.com/tikv/tikv/pull/6459) [#6474](https://github.com/tikv/tikv/pull/6474) [#6492](https://github.com/tikv/tikv/pull/6492) [#6569](https://github.com/tikv/tikv/pull/6569)

* TiDB Lightning
    + Fix the bug that the web interface does not work outside the Server mode [#259](https://github.com/pingcap/tidb-lightning/pull/259)
