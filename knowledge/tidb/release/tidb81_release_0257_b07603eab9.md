# Deployment maintenance telemetry and removed feature

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.3.0.md`
- Source Title: `TiDB 5.3 Release Notes`
- Source Heading Path: `TiDB 5.3 Release Notes > New features > Deployment and maintenance | TiDB 5.3 Release Notes > Telemetry | TiDB 5.3 Release Notes > Removed feature`
- Source Line Ranges: `237-258`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tiup`, `tidb`, `ticdc`
- Topic Tags: `continuous-profiling`, `dashboard`, `telemetry`, `temporary-table`, `feature-removal`, `cyclic-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0257_b07603eab9`
- Source ID: `tidb-docs-8.1:releases/release-5.3.0.md#deployment-and-maintenance`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `192c4ad2e8f57d33052ebb9f8c95bbf480e54ae5b0ae2591d1e1d281048b62f6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.3.0#deployment-and-maintenance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.3 release-note details about Continuous Profiling in TiDB Dashboard, telemetry reporting for TEMPORARY TABLE usage, or removal of TiCDC cyclic replication.
- Retrieval Keywords: TiDB 5.3 Deployment and maintenance, Continuous Profiling experimental feature, TiDB Dashboard, stores instance performance analysis results automatically in real time, flame graph, Continuous Profile page, disabled by default, only available for clusters upgraded or installed using TiUP v1.7.0 or above, Telemetry, TEMPORARY TABLE feature is used, does not include table names or table data, Removed feature, TiCDC v5.3.0, cyclic replication feature between TiDB clusters has been removed, experimental feature in v5.0.0, related data is not affected after the upgrade
- Follow-up Guidance: The source links to the Continuous Profiling user document and to Telemetry for more information and how to disable this behavior.
- Classification Note: This is classified as a release chunk because it combines deployment and maintenance additions, telemetry-report content, and a removed TiCDC feature from the TiDB 5.3 release notes.

## Official Source Content

### Deployment and maintenance

- **Continuous Profiling (experimental feature)**

    TiDB Dashboard supports the Continuous Profiling feature, which stores instance performance analysis results automatically in real time when TiDB clusters are running. You can check the performance analysis result in a flame graph, which is more observable and shortens troubleshooting time.

    This feature is disabled by default and needs to be enabled on the **Continuous Profile** page of TiDB Dashboard.

    This feature is only available for clusters upgraded or installed using TiUP v1.7.0 or above.

    [User document](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling)
## Telemetry

TiDB adds the information to the telemetry report about whether or not the TEMPORARY TABLE feature is used. This does not include table names or table data.

To learn more about telemetry and how to disable this behavior, refer to [Telemetry](https://docs.pingcap.com/tidb/stable/telemetry).
## Removed feature

Starting from TiCDC v5.3.0, the cyclic replication feature between TiDB clusters (an experimental feature in v5.0.0) has been removed. If you have already used this feature to replicate data before upgrading TiCDC, the related data is not affected after the upgrade.
