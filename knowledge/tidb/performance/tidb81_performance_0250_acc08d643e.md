# TiFlash performance overview and resource planning

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tune-tiflash-performance.md`
- Source Title: `Tune TiFlash Performance`
- Source Heading Path: `Tune TiFlash Performance | Tune TiFlash Performance > Plan resources`
- Source Line Ranges: `5-13`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tikv`
- Topic Tags: `resource-planning`, `co-deployment`, `isolation`, `disk-allocation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0250_acc08d643e`
- Source ID: `tidb-docs-8.1:tiflash/tune-tiflash-performance.md#tune-tiflash-performance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ad4be5db79796adbbbd346fb69fdd67d72fdab1d424ae7e91890a8fe70889f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance#tune-tiflash-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tune-tiflash-performance.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiFlash resource planning, especially co-deploying TiKV and TiFlash, isolation requirements, or disk allocation guidance.
- Retrieval Keywords: Plan resources, Tune TiFlash Performance, TiFlash, TiKV, combines the deployment of both TiKV and TiFlash, no requirement on isolation, save enough resources, do not share disks, resource planning
- Follow-up Guidance: This source says that if you want to save machine resources and have no requirement on isolation, you can combine the deployment of TiKV and TiFlash, while saving enough resources for each and not sharing disks.
- Classification Note: The classification is performance for the TiFlash component because the content focuses on planning machine resources to achieve optimal TiFlash performance.

## Official Source Content

# Tune TiFlash Performance

This document introduces how to tune the performance of TiFlash by properly planning machine resources and tuning TiDB parameters. By following these methods, your TiFlash cluster can achieve optimal performance.
## Plan resources

If you want to save machine resources and have no requirement on isolation, you can use the method that combines the deployment of both TiKV and TiFlash. It is recommended that you save enough resources for TiKV and TiFlash respectively, and do not share disks.
