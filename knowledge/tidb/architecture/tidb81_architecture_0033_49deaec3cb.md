# Bidirectional replication between primary and secondary clusters

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Perform bidirectional replication between the primary and secondary clusters`
- Source Line Ranges: `411-420`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `bidirectional-replication`, `disaster-recovery`, `multi-region`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0033_49deaec3cb`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#perform-bidirectional-replication-between-the-primary-and-secondary-clusters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08f1ba48d9f15e814611251e95857fef2b167314eeca8a7ec0821e2e4a648d64`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#perform-bidirectional-replication-between-the-primary-and-secondary-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the primary-secondary DR architecture where two regional TiDB clusters replicate each other's data using bidirectional replication.
- Retrieval Keywords: Perform bidirectional replication between the primary and secondary clusters, bidirectional replication, TiCDC bidirectional replication, two regions, replicate each other's data, planned DR switchover, do not need to stop the running changefeeds before starting a new changefeed
- Follow-up Guidance: The source directs readers to the TiCDC bidirectional replication document to build a bidirectional DR cluster.
- Classification Note: This is classified as architecture because it describes a DR topology in which two TiDB clusters in different regions act as each other's disaster recovery clusters.

## Official Source Content

### Perform bidirectional replication between the primary and secondary clusters

In this DR scenario, the TiDB clusters in two regions can act as each other's disaster recovery clusters: the business traffic is written to the corresponding TiDB cluster based on the region configuration, and the two TiDB clusters back up each other's data.

![TiCDC bidirectional replication](/media/dr/bdr-ticdc.png)

With the bidirectional replication feature, the TiDB clusters in two regions can replicate each other's data. This DR solution guarantees data security and reliability, and also ensures the write performance of the database. In a planned DR switchover, you do not need to stop the running changefeeds before starting a new changefeed, which simplifies the operation and maintenance.

To build a bidirectional DR cluster, see [TiCDC bidirectional replication](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication).
