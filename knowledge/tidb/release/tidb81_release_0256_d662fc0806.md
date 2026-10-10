# TiCDC data share subscription features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes > New features > TiDB data share subscription`
- Source Line Ranges: `223-236`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `eventual-consistency`, `disaster-scenarios`, `replication`, `openapi`, `rto`, `rpo`, `failover`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0256_d662fc0806`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#tidb-data-share-subscription`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13e1208668e1cdf475a6c72a50539c2fa1ef8a652fc5ea95944282ccd344a742`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#tidb-data-share-subscription
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.3 release-note information about TiCDC eventually consistent replication in disaster scenarios or TiCDC OpenAPI support for managing TiCDC tasks.
- Retrieval Keywords: TiDB 5.3 TiCDC data share subscription, TiCDC Eventually Consistent Replication, disaster scenarios, secondary relational database TiDB Aurora MySQL MariaDB, recover the secondary cluster to a certain snapshot, within 5 minutes, RTO <= 5min, RPO <= 30min, replication lag is small, incremental data, TiCDC supports the HTTP protocol OpenAPI, managing TiCDC tasks, TiCDC OpenAPI becomes a General Availability feature, query and operate TiCDC clusters using OpenAPI
- Follow-up Guidance: The source includes a user document link for eventually consistent replication in disaster scenarios.
- Classification Note: This is classified as a release chunk because it describes new TiCDC features in TiDB 5.3, specifically eventually consistent replication targets and OpenAPI GA status.

## Official Source Content

### TiDB data share subscription

- **TiCDC Eventually Consistent Replication**

    TiCDC provides the eventually consistent replication capability in disaster scenarios. When a disaster occurs in the primary TiDB cluster and the service cannot be resumed in a short period of time, TiCDC needs to provide the ability to ensure the consistency of data in the secondary cluster. Meanwhile, TiCDC needs to allow the business to quickly switch the traffic to the secondary cluster to avoid the database being unavailable for a long time and affecting the business.

    This feature supports TiCDC to replicate incremental data from a TiDB cluster to the secondary relational database TiDB/Aurora/MySQL/MariaDB. In case the primary cluster crashes, TiCDC can recover the secondary cluster to a certain snapshot in the primary cluster within 5 minutes, given the condition that before disaster the replication status of TiCDC is normal and replication lag is small. It allows data loss of less than 30 minutes, that is, RTO <= 5min, and RPO <= 30min.

    [User document](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-mysql#eventually-consistent-replication-in-disaster-scenarios)

- **TiCDC supports the HTTP protocol OpenAPI for managing TiCDC tasks**

    Since TiDB v5.3.0, TiCDC OpenAPI becomes a General Availability (GA) feature. You can query and operate TiCDC clusters using OpenAPI in the production environment.
