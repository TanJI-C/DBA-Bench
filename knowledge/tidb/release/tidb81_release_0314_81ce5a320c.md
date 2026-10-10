# TiDB 6.1.4 overview compatibility changes and improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.4.md`
- Source Title: `TiDB 6.1.4 Release Notes`
- Source Heading Path: `TiDB 6.1.4 Release Notes | TiDB 6.1.4 Release Notes > Compatibility changes | TiDB 6.1.4 Release Notes > Improvements`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `ticdc`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `improvements`, `partitioned-tables`, `dml-batching`, `redo-logs`, `object-storage`, `precheck`, `iops`, `write-amplification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0314_81ce5a320c`
- Source ID: `tidb-docs-8.1:releases/release-6.1.4.md#tidb-6-1-4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `31e97443603e8973d7eb946f79e23d823bd0f0ec89c0cebc7092f754644648c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.4#tidb-6-1-4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.1.4 release-note summary of compatibility changes and improvements across TiDB, TiFlash, TiCDC, and TiDB Lightning.
- Retrieval Keywords: TiDB 6.1.4 Release Notes, Compatibility changes, Improvements, modifying column types on partitioned tables, No longer support modifying column types on partitioned tables, TiFlash IOPS, write amplification, high update throughput workloads, TiCDC DML batch operation mode, redo logs, GCS-compatible object storage, Azure-compatible object storage, TiDB Lightning, clusterResourceCheckItem, emptyRegionCheckItem, Critical to Warning
- Follow-up Guidance: The chunk also points to the separate Bug fixes section of the TiDB 6.1.4 release notes for detailed fixes beyond these compatibility changes and improvements.
- Classification Note: This is classified as a release chunk because the official content is the TiDB 6.1.4 release notes covering compatibility changes and improvements for multiple components.

## Official Source Content

# TiDB 6.1.4 Release Notes

Release date: February 8, 2023

TiDB version: 6.1.4

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)
## Compatibility changes

- TiDB

    - No longer support modifying column types on partitioned tables because of potential correctness issues [#40620](https://github.com/pingcap/tidb/issues/40620) @[mjonss](https://github.com/mjonss)
## Improvements

- TiFlash

    - Reduce the IOPS by up to 95% and the write amplification by up to 65% for TiFlash instances under high update throughput workloads [#6460](https://github.com/pingcap/tiflash/issues/6460) @[flowbehappy](https://github.com/flowbehappy)

- Tools

    - TiCDC

        - Add the DML batch operation mode to improve the throughput when SQL statements are generated in batches [#7653](https://github.com/pingcap/tiflow/issues/7653) @[asddongmen](https://github.com/asddongmen)
        - Support storing redo logs to GCS- or Azure-compatible object storage [#7987](https://github.com/pingcap/tiflow/issues/7987) @[CharlesCheung96](https://github.com/CharlesCheung96)

    - TiDB Lightning

        - Change the severity of the precheck items `clusterResourceCheckItem` and `emptyRegionCheckItem` from `Critical` to `Warning` [#37654](https://github.com/pingcap/tidb/issues/37654) @[niubell](https://github.com/niubell)
