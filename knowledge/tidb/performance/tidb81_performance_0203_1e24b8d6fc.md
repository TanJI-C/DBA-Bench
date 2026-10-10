# Schema design optimization for conflicts and hotspots

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-sql-tuning-overview.md`
- Source Title: `SQL Tuning Overview`
- Source Heading Path: `SQL Tuning Overview > Optimize schema design | SQL Tuning Overview > Optimize schema design > Transaction conflicts | SQL Tuning Overview > Optimize schema design > Hotspot issues`
- Source Line Ranges: `96-125`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `tidb`
- Topic Tags: `schema-design`, `transaction-conflicts`, `lock-conflicts`, `hotspots`, `key-visualizer`, `heatmap`, `read-pressure`, `write-pressure`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0203_1e24b8d6fc`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-sql-tuning-overview.md#optimize-schema-design`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c2c4c4df445bc78f55fd214f6322ae7c11ef69f1c3dd137d36b79d037520547`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview#optimize-schema-design
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-sql-tuning-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about improving TiDB Cloud performance through schema design to avoid transaction conflicts or hotspot issues, especially with Key Visualizer heat maps.
- Retrieval Keywords: Optimize schema design, transaction conflicts, Troubleshoot Lock Conflicts, hotspot issues, Key Visualizer, heat map, traffic hotspots, usage patterns, basic concepts, common heatmap types, Evenly distributed workload, Alternating brightness and darkness along the X-axis, Alternating brightness and darkness along the Y-axis, Bright diagonal lines, read pressure, write pressure, tables and indexes
- Follow-up Guidance: The chunk directs readers to Troubleshoot Lock Conflicts for transaction conflicts and SQL Optimization in SQL FAQs for more information about SQL performance optimization.
- Classification Note: This is classified as performance for the cloud component because the content focuses on TiDB Cloud schema design analysis for transaction conflicts and hotspot-related performance issues.

## Official Source Content

## Optimize schema design

If you still cannot get better performance based on SQL performance tuning, you may need to check your schema design and data read model to avoid transaction conflicts and hotspots.
### Transaction conflicts

For more information on how to locate and resolve transaction conflicts, see [Troubleshoot Lock Conflicts](https://docs.pingcap.com/tidb/stable/troubleshoot-lock-conflicts#troubleshoot-lock-conflicts).
### Hotspot issues

You can analyze hotspot issues using [Key Visualizer](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#key-visualizer).

You can use Key Visualizer to analyze the usage patterns of TiDB clusters and troubleshoot traffic hotspots. This page provides a visual representation of the TiDB cluster's traffic over time.

You can observe the following information in Key Visualizer. You may need to understand some [basic concepts](https://docs.pingcap.com/tidb/stable/dashboard-key-visualizer#basic-concepts) first.

- A large heat map that shows the overall traffic over time
- The detailed information about a coordinate of the heat map
- The identification information such as tables and indexes that is displayed on the left side

In Key Visualizer, there are [four common heat map results](https://docs.pingcap.com/tidb/stable/dashboard-key-visualizer#common-heatmap-types).

- Evenly distributed workload: desired result
- Alternating brightness and darkness along the X-axis (time): need to check the resources at peak times
- Alternating brightness and darkness along the Y-axis: need to check the degree of hotspot aggregation generated
- Bright diagonal lines: need to check the business model

In both cases of X-axis and Y-axis alternating bright and dark, you need to address read and write pressure.

For more information about SQL performance optimization, see [SQL Optimization](https://docs.pingcap.com/tidb/stable/sql-faq#sql-optimization) in SQL FAQs.
