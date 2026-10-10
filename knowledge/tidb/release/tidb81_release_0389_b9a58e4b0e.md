# Bug fixes for TiDB Lightning and Dumpling

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.12.md`
- Source Title: `TiDB 6.5.12 Release Notes`
- Source Heading Path: `TiDB 6.5.12 Release Notes > Bug fixes`
- Source Line Ranges: `176-185`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `lightning`, `dumpling`, `tikv`, `cloud`
- Topic Tags: `bug-fixes`, `data-import`, `data-export`, `logging`, `desensitization`, `performance-regression`, `cloud-storage`, `retry`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0389_b9a58e4b0e`
- Source ID: `tidb-docs-8.1:releases/release-6.5.12.md#bug-fixes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5caeb3d778832e9ade4486ba7ca2aa9c6ec9187acd4e3efba5e41f9fb134ac10`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.12#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.12.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.12 bug fixes for TiDB Lightning import behavior or Dumpling retry behavior with cloud storage errors.
- Retrieval Keywords: TiDB 6.5.12 bug fixes, TiDB Lightning logs not properly desensitized, encoding phase lack of caching performance regression, importing data from a cloud storage high-concurrency scenarios performance degrades, TiDB Lightning Lock wait timeout metadata updates automatically retry, TiDB Lightning oversized messages sent from TiKV, error report output is truncated importing data using TiDB Lightning, Dumpling 503 error Google Cloud Storage GCS retry
- Follow-up Guidance: 
- Classification Note: The official content is a release-notes bug-fix list for the tools TiDB Lightning and Dumpling in TiDB 6.5.12.

## Official Source Content

- Fix the issue that logs are not properly desensitized [#59086](https://github.com/pingcap/tidb/issues/59086) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that the lack of caching in the encoding phase causes performance regression [#56705](https://github.com/pingcap/tidb/issues/56705) @[OliverS929](https://github.com/OliverS929)
        - Fix the issue that the performance degrades when importing data from a cloud storage in high-concurrency scenarios [#57413](https://github.com/pingcap/tidb/issues/57413) @[xuanyu66](https://github.com/xuanyu66)
        - Fix the issue that TiDB Lightning does not automatically retry when encountering `Lock wait timeout` errors during metadata updates [#53042](https://github.com/pingcap/tidb/issues/53042) @[guoshouyan](https://github.com/guoshouyan)
        - Fix the issue that TiDB Lightning fails to receive oversized messages sent from TiKV [#56114](https://github.com/pingcap/tidb/issues/56114) @[fishiu](https://github.com/fishiu)
        - Fix the issue that the error report output is truncated when importing data using TiDB Lightning [#58085](https://github.com/pingcap/tidb/issues/58085) @[lance6716](https://github.com/lance6716)

    + Dumpling

        - Fix the issue that Dumpling fails to retry properly when receiving a 503 error from Google Cloud Storage (GCS) [#56127](https://github.com/pingcap/tidb/issues/56127) @[OliverS929](https://github.com/OliverS929)
