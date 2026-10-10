# DR solution comparison table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-solution-introduction.md`
- Source Title: `Overview of TiDB Disaster Recovery Solutions`
- Source Heading Path: `Overview of TiDB Disaster Recovery Solutions > Solution comparison`
- Source Line Ranges: `104-113`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `ticdc`, `br`
- Topic Tags: `comparison`, `tco`, `error-tolerance`, `rpo`, `rto`, `latency`, `target-system`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0236_b2a391f552`
- Source ID: `tidb-docs-8.1:dr-solution-introduction.md#solution-comparison`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `86edacafd47b5ec3857156fdc286a0eb4b96a1d83bb9eeb21096bc3b7b3c4d20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-solution-introduction#solution-comparison
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-solution-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for a side-by-side comparison of TiDB DR solutions by TCO, error tolerance objective, RPO, RTO, network latency requirement, or target system.
- Retrieval Keywords: Solution comparison, TCO, Error tolerance objective, RPO, RTO, Network latency requirement, Target system, 2-2-1, 1:1, 2-2-1:1, DR solution based on BR, Less than 30 ms between regions, Less than 100 ms between regions, Hour level, Less than 5 minutes
- Follow-up Guidance: 
- Classification Note: This chunk is classified as reference because it is a comparison table summarizing the documented DR solutions across cost, tolerance, recovery objectives, latency requirements, and target workloads.

## Official Source Content

## Solution comparison

This section compares the DR solutions mentioned in this document, based on which you can select an appropriate DR solution to satisfy your business needs.

| DR solution | TCO | Error tolerance objective | RPO | RTO | Network latency requirement | Target system |
| --- | --- | --- | --- | --- | --- | --- |
| DR solution based on multiple replicas in a single cluster (2-2-1) | High | Single region | 0 | Minute level | Less than 30 ms between regions | Production systems that have specific requirements on DR and response (RPO = 0) |
| DR solution based on primary and secondary clusters (1:1)  | Medium | Single region | Less than 10 seconds | Less than 5 minutes | Less than 100 ms between regions | Production systems that have specific requirements on DR and response (RPO > 0) |
| DR solution based on TiCDC and multiple replicas (2-2-1:1) | High | Multiple regions | Less than 10 seconds | Less than 5 minutes | Less than 30 ms for regions that use multiple replicas for DR. Less than 100 ms for the third region and other regions | Production systems that have strict requirements on DR and response |
| DR solution based on BR | Low | Single region | Less than 5 minutes |  Hour level | No special requirement | Production systems that accept an RPO of less than 5 minutes and an RTO of up to an hour |
