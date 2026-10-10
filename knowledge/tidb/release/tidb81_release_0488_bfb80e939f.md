# Release overview and feature details heading

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.2.0.md`
- Source Title: `TiDB 7.2.0 Release Notes`
- Source Heading Path: `TiDB 7.2.0 Release Notes | TiDB 7.2.0 Release Notes > Feature details`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `lightning`
- Topic Tags: `release-date`, `feature-overview`, `performance`, `sql`, `ddl`, `data-import`, `observability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0488_bfb80e939f`
- Source ID: `tidb-docs-8.1:releases/release-7.2.0.md#tidb-7-2-0-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6e80c365189c3f12a416356106fa05f3f8f7bd24af5029304260d324a3f6711`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.2.0#tidb-7-2-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for a high-level overview of TiDB 7.2.0 release date and the main features introduced in this release.
- Retrieval Keywords: TiDB 7.2.0 Release Notes, Release date June 29 2023, TiDB version 7.2.0, Feature details, resource groups managing runaway queries, TiFlash pipeline execution model, IMPORT INTO, DDL pause and resume operations, Quick start
- Follow-up Guidance: Follow up with the detailed sections for Performance, SQL, or DDL and observability features if the user wants specifics about a listed feature.
- Classification Note: This is classified as a release chunk because it summarizes the TiDB 7.2.0 release and lists the major features across shared components.

## Official Source Content

# TiDB 7.2.0 Release Notes

Release date: June 29, 2023

TiDB version: 7.2.0

Quick access: [Quick start](https://docs-archive.pingcap.com/tidb/v7.2/quick-start-with-tidb)

7.2.0 introduces the following key features and improvements:

<table>
<thead>
  <tr>
    <th>Category</th>
    <th>Feature</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="2">Scalability and Performance</td>
    <td>Resource groups support <a href="https://docs-archive.pingcap.com/tidb/v7.2/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries"> managing runaway queries</a> (experimental)</td>
    <td>You can now manage query timeout with more granularity, allowing for different behaviors based on query classifications. Queries meeting your specified threshold can be deprioritized or terminated.
    </td>
  </tr>
  <tr>
    <td>TiFlash supports the <a href="https://docs-archive.pingcap.com/tidb/v7.2/tiflash-pipeline-model">pipeline execution model</a> (experimental)</td>
    <td>TiFlash supports a pipeline execution model to optimize thread resource control.</td>
  </tr>
  <tr>
    <td rowspan="1">SQL</td>
    <td>Support a new SQL statement, <a href="https://docs-archive.pingcap.com/tidb/v7.2/sql-statement-import-into">IMPORT INTO</a>, for data import (experimental)</td>
   <td>To simplify the deployment and maintenance of TiDB Lightning, TiDB introduces a new SQL statement <code>IMPORT INTO</code>, which integrates physical import mode of TiDB Lightning, including remote import from Amazon S3 or Google Cloud Storage (GCS) directly into TiDB.</td>
  </tr>
  <tr>
    <td rowspan="2">DB Operations and Observability</td>
    <td>DDL supports <a href="https://docs-archive.pingcap.com/tidb/v7.2/ddl-introduction#ddl-related-commands">pause and resume operations</a> (experimental)</td>
    <td>This new capability lets you temporarily suspend resource-intensive DDL operations, such as index creation, to conserve resources and minimize the impact on online traffic. You can seamlessly resume these operations when ready, without the need to cancel and restart. This feature enhances resource utilization, improves user experience, and streamlines schema changes.</td>
  </tr>
</tbody>
</table>
## Feature details
