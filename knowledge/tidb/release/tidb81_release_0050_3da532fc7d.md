# TiDB 2.1 RC2 PD release changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.2.md`
- Source Title: `TiDB 2.1 RC2 Release Notes`
- Source Heading Path: `TiDB 2.1 RC2 Release Notes > PD`
- Source Line Ranges: `89-104`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: none
- Topic Tags: `release-notes`, `features`, `scheduling`, `replicas`, `coordinator`, `memory-usage`, `pd-ctl`, `tso`, `bug-fixes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0050_3da532fc7d`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.2.md#pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e09a468e76746d435199cd8a58e9d52a9bbd9ac19ed69ab85b35d9af0b07e9d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.2#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.2.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 2.1 RC2 release-note details for PD features, scheduling and replica improvements, pd-ctl queries, TSO decoding, memory usage, or a pd-ctl hot store bug fix.
- Retrieval Keywords: TiDB 2.1 RC2 Release Notes, PD, TiDB 2.1 RC2 PD release changes, GetAllStores interface, scheduling estimation in Simulator, down stores make up replicas as soon as possible, Coordinator restart unnecessary scheduling, memory usage reduce the overhead caused by heartbeats, pd-ctl specific store Region information, pd-ctl topN Region information based on version comparison, more accurate TSO decoding in pd-ctl, hot store command exit wrongly
- Follow-up Guidance: 
- Classification Note: The official content is a self-managed TiDB release-notes section for PD in version 2.1 RC2, organized into features, improvements, and bug fix items.

## Official Source Content

## PD

* Features
    * Support the `GetAllStores` interface [#1228](https://github.com/pingcap/pd/pull/1228)
    * Add the statistics of scheduling estimation in Simulator [#1218](https://github.com/pingcap/pd/pull/1218)
* Improvements
    * Optimize the handling process of down stores to make up replicas as soon as possible [#1222](https://github.com/pingcap/pd/pull/1222)
    * Optimize the start of Coordinator to reduce the unnecessary scheduling caused by restarting PD [#1225](https://github.com/pingcap/pd/pull/1225)
    * Optimize the memory usage to reduce the overhead caused by heartbeats [#1195](https://github.com/pingcap/pd/pull/1195)
    * Optimize error handling and improve the log information [#1227](https://github.com/pingcap/pd/pull/1227)
    * Support querying the Region information of a specific store in pd-ctl [#1231](https://github.com/pingcap/pd/pull/1231)
    * Support querying the topN Region information based on version comparison in pd-ctl [#1233](https://github.com/pingcap/pd/pull/1233)
    * Support more accurate TSO decoding in pd-ctl [#1242](https://github.com/pingcap/pd/pull/1242)
* Bug fix
    * Fix the issue that pd-ctl uses the `hot store` command to exit wrongly [#1244](https://github.com/pingcap/pd/pull/1244)
