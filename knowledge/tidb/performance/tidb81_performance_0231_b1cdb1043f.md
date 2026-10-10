# tikv scaling and small region merging

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/v8.5-performance-highlights.md`
- Source Title: `TiDB Cloud Performance Highlights for TiDB v8.5.0`
- Source Heading Path: `TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance | TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance > Challenge | TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance > Solution | TiDB Cloud Performance Highlights for TiDB v8.5.0 > TiKV scaling performance > Test environment`
- Source Line Ranges: `203-216`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `scaling`, `regions`, `small regions`, `resource utilization`, `horizontal scaling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0231_b1cdb1043f`
- Source ID: `tidb-docs-8.1:tidb-cloud/v8.5-performance-highlights.md#tikv-scaling-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1abcb373b333ca4ae870c5aaf8e41686beaa814609d1dfd9a5fc7c7ee765dc4c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/v8.5-performance-highlights#tikv-scaling-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/v8.5-performance-highlights.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV scaling performance improvements related to many small or empty tables, tiny Regions, and merging small Regions.
- Retrieval Keywords: TiKV scaling performance, Horizontal scaling, scaling out TiKV nodes, small Regions, tiny Regions, merging small Regions, 1 million or more, resource utilization, internal overhead, large number of databases and tables
- Follow-up Guidance: The chunk provides the challenge and solution summary and indicates a following test environment section for TiKV scaling performance.
- Classification Note: This is classified as TiKV performance content because the official content discusses scaling out TiKV nodes and improving the performance of merging small Regions.

## Official Source Content

## TiKV scaling performance
### Challenge

Horizontal scaling is a core capability of TiKV, enabling the system to scale in or out as needed. As business demands grow and the number of tenants increases, TiDB clusters experience rapid growth in databases, tables, and data volume. Scaling out TiKV nodes quickly becomes essential to maintaining service quality.

In some scenarios, TiDB hosts a large number of databases and tables. When these tables are small or empty, TiKV accumulates a significant number of tiny Regions, especially when the number of tables grows to a large scale (such as 1 million or more). These small Regions introduce a substantial maintenance burden, increase resource overhead, and reduce efficiency.
### Solution

To address this issue, TiDB v8.5.0 improves the performance of merging small Regions, reducing internal overhead and improving resource utilization. Additionally, TiDB v8.5.0 includes several other enhancements to further improve TiKV scaling performance.
### Test environment
