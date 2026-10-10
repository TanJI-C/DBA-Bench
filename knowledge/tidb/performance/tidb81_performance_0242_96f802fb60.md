# Overview and common performance tuning directions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-performance-tuning-config.md`
- Source Title: `Configure TiDB for Optimal Performance`
- Source Heading Path: `Configure TiDB for Optimal Performance | Configure TiDB for Optimal Performance > Overview | Configure TiDB for Optimal Performance > Key settings for common workloads`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `pd`
- Topic Tags: `performance-tuning`, `overview`, `common-workloads`, `plan-cache`, `optimizer`, `titan`, `compaction`, `flow-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0242_96f802fb60`
- Source ID: `tidb-docs-8.1:tidb-performance-tuning-config.md#configure-tidb-for-optimal-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e2c2840fe9a1ee3988549fecbffaaccd2780c617952286cc9d004ca23cd8cc8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-performance-tuning-config#configure-tidb-for-optimal-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-performance-tuning-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an overview of TiDB performance tuning directions and common settings that improve workloads involving plan cache, optimizer behavior, Titan, and TiKV write-path stability.
- Retrieval Keywords: Configure TiDB for Optimal Performance, Overview, Key settings for common workloads, SQL Prepared Execution Plan Cache, Non-prepared plan cache, Optimizer Fix Controls, Titan, TiKV compaction, flow control, write-intensive workloads, default settings prioritize stability over performance
- Follow-up Guidance: The source points to common tuning areas including SQL Prepared Execution Plan Cache, Non-prepared plan cache, Optimizer Fix Controls, Titan, and TiKV compaction and flow control configurations.
- Classification Note: This chunk is classified as performance because the official content summarizes non-default settings and trade-offs for optimizing TiDB, TiKV, and PD behavior for workload performance.

## Official Source Content

# Configure TiDB for Optimal Performance

This guide describes how to optimize the performance of TiDB, including:

- Best practices for common workloads.
- Strategies for handling challenging performance scenarios.

> **Note:**
>
> The optimization techniques in this guide can help achieve optimal performance in TiDB. However, performance tuning often involves balancing multiple factors, and no single solution addresses all performance needs. Some techniques in this guide use experimental features, which are marked accordingly. Although these optimizations can significantly improve performance, they might not be suitable for production environments and require careful evaluation before implementation.
## Overview

Optimizing TiDB for peak performance requires careful tuning of various settings. In many cases, achieving optimal performance involves adjusting configurations beyond their default values.

The default settings prioritize stability over performance. To maximize performance, you might need to use more aggressive configurations and, in some cases, experimental features. These recommendations are based on production deployment experience and performance optimization research.

This guide describes the non-default settings, including their benefits and potential trade-offs. Use this information to optimize TiDB settings for your workload requirements.
## Key settings for common workloads

The following settings are commonly used to optimize TiDB performance:

- Enhance execution plan cache, such as [SQL Prepared Execution Plan Cache](https://docs.pingcap.com/tidb/stable/sql-prepared-plan-cache) and [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache).
- Optimize the behavior of the TiDB optimizer by using [Optimizer Fix Controls](https://docs.pingcap.com/tidb/stable/optimizer-fix-controls).
- Use the [Titan](https://docs.pingcap.com/tidb/stable/storage-engine/titan-overview) storage engine more aggressively.
- Fine-tune TiKV's compaction and flow control configurations, to ensure optimal and stable performance under write-intensive workloads.

These settings can significantly improve performance for many workloads. However, as with any optimization, thoroughly test them in your environment before deploying to production.
