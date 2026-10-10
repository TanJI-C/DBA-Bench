# TiKV heap profiling in dashboard

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes > Feature details > Observability`
- Source Line Ranges: `119-126`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tikv`
- Topic Tags: `heap profiling`, `oom`, `flame graph`, `call graph`, `memory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0076_0464dea846`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#observability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `554041edb0ae40bd0bc4c26c10e5a3ee6dcd12b028112f29152d678ab0d60c02`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#observability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Dashboard support for TiKV heap profiling, especially for OOM or high memory usage investigation.
- Retrieval Keywords: TiDB Dashboard supports heap profiling for TiKV, TiKV OOM, high memory usage, jeprof, remote processing of heap profiles, flame graph, call graph, dashboard profiling
- Follow-up Guidance: The source points to the TiDB Dashboard profiling documentation for more information.
- Classification Note: The chunk is classified as observability for Dashboard because it describes profiling and memory-analysis views for TiKV in TiDB Dashboard.

## Official Source Content

### Observability

* TiDB Dashboard supports heap profiling for TiKV [#15927](https://github.com/tikv/tikv/issues/15927) @[Connor1996](https://github.com/Connor1996)

    Previously, addressing TiKV OOM or high memory usage issues typically required manual execution of `jeprof` to generate a heap profile in the instance environment. Starting from v7.5.0, TiKV enables remote processing of heap profiles. You can now directly access the flame graph and call graph of heap profile. This feature provides the same simple and easy-to-use experience as Go heap profiling.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-profiling).
