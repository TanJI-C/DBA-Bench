# TiDB 5.4.1 overview, compatibility changes, and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.1.md`
- Source Title: `TiDB 5.4.1 Release Notes`
- Source Heading Path: `TiDB 5.4.1 Release Notes | TiDB 5.4.1 Release Notes > Compatibility changes | TiDB 5.4.1 Release Notes > Improvements`
- Source Line Ranges: `5-47`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `ticdc`, `dm`, `dashboard`, `operator`
- Topic Tags: `release-notes`, `compatibility`, `improvements`, `pointget`, `logs`, `metrics`, `statistics`, `grafana`, `kubernetes`, `kafka`, `syncer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0278_7e0c2f97bb`
- Source ID: `tidb-docs-8.1:releases/release-5.4.1.md#tidb-5-4-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46cf103cd6ebe6bd5f53954dd69ecd60126a148203b9311607d44ce7c69b3c25`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.1#tidb-5-4-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 5.4.1 release overview, confirmation that there are no product design compatibility changes, or a summary of improvements across TiDB, TiKV, PD, TiFlash, TiCDC, and DM.
- Retrieval Keywords: TiDB 5.4.1 Release Notes, Compatibility changes, does not introduce any compatibility changes in product design, Improvements, PointGet, _tidb_rowid, Apply operator, parallel, TopN pruning, Analyze Version 2, statistics, multiple Kubernetes clusters, Grafana dashboard, TiCDC, Kafka producer, DM-worker, Syncer, /tmp
- Follow-up Guidance: The content notes that bug fixes in this release might result in compatibility changes and points readers to the Bug Fixes section for more information.
- Classification Note: This is a release-notes overview chunk covering compatibility changes and improvements for multiple components in TiDB 5.4.1.

## Official Source Content

# TiDB 5.4.1 Release Notes

Release Date: May 13, 2022

TiDB version: 5.4.1
## Compatibility changes

TiDB v5.4.1 does not introduce any compatibility changes in product design. But note that bug fixes in this release might result in compatibility changes, too. For more information, see [Bug Fixes](#bug-fixes).
## Improvements

+ TiDB

    - Support using the PointGet plan for queries that read the `_tidb_rowid` column [#31543](https://github.com/pingcap/tidb/issues/31543)
    - Add more logs and metrics for the `Apply` operator to show whether it is parallel [#33887](https://github.com/pingcap/tidb/issues/33887)
    - Improve the `TopN` pruning logic for Analyze Version 2 used for collecting statistics [#34256](https://github.com/pingcap/tidb/issues/34256)
    - Support displaying multiple Kubernetes clusters in the Grafana dashboard [#32593](https://github.com/pingcap/tidb/issues/32593)

+ TiKV

    - Support displaying multiple Kubernetes clusters in the Grafana dashboard [#12104](https://github.com/tikv/tikv/issues/12104)

+ PD

    - Support displaying multiple Kubernetes clusters in the Grafana dashboard [#4673](https://github.com/tikv/pd/issues/4673)

+ TiFlash

    - Support displaying multiple Kubernetes clusters in the Grafana dashboard [#4129](https://github.com/pingcap/tiflash/issues/4129)

+ Tools

    + TiCDC

        - Support multiple Kubernetes clusters in Grafana dashboards [#4665](https://github.com/pingcap/tiflow/issues/4665)
        - Expose configuration parameters of the Kafka producer to make them configurable in TiCDC [#4385](https://github.com/pingcap/tiflow/issues/4385)

    + TiDB Data Migration (DM)

        - Support Syncer using the working directory of the DM-worker rather than `/tmp` to write internal files, and cleaning the directory after the task is stopped [#4107](https://github.com/pingcap/tiflow/issues/4107)
