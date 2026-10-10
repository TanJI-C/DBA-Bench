# TiDB 7.0.0 release overview and key features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes`
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `ticdc`
- Topic Tags: `release-overview`, `feature-summary`, `scalability`, `performance`, `reliability`, `availability`, `sql`, `data-import`, `object-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0429_45a65f551f`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#tidb-7-0-0-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6fbcb72a49fa74cd39544462bb0a4ef8eae88307063a146a61807a9bd9c682d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#tidb-7-0-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of TiDB 7.0.0-DMR release highlights or the main new features across TiDB, TiFlash, and TiCDC.
- Retrieval Keywords: TiDB 7.0.0 Release Notes, v7.0.0-DMR, release overview, key new features and improvements, session level non-prepared SQL plan cache, TiFlash disaggregated storage and compute architecture, S3 shared storage, resource control enhancement, resource groups, TiFlash spill to disk, Row-level TTL, REORGANIZE PARTITION, LIST/RANGE partition, LOAD DATA, S3/GCS, TiCDC object storage sink, Amazon S3, GCS, Azure Blob Storage, NFS
- Follow-up Guidance: The source also points to feature-specific documentation such as non-prepared SQL plan cache, TiFlash disaggregated and S3, resource control, spill to disk, Row-level TTL, REORGANIZE PARTITION, LOAD DATA, and TiCDC sink to cloud storage.
- Classification Note: This is a release overview chunk because it summarizes the categories, features, and brief descriptions introduced in the TiDB 7.0.0 release notes.

## Official Source Content

# TiDB 7.0.0 Release Notes

Release date: March 30, 2023

TiDB version: 7.0.0-[DMR](https://docs.pingcap.com/tidb/stable/releases/versioning#development-milestone-releases)

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.0/quick-start-with-tidb)

In v7.0.0-DMR, the key new features and improvements are as follows:

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
    <td rowspan="2">Scalability and Performance<br/></td>
    <td>Session level <a href="https://docs.pingcap.com/tidb/v7.0/sql-non-prepared-plan-cache" target="_blank">non-prepared SQL plan cache</a> (experimental)</td>
    <td>Support automatically reusing plan cache at the session level to reduce compilation and shorten the query time for the same SQL patterns without manually setting prepare statements in advance.</td>
  </tr>
  <tr>
    <td>TiFlash supports the <a href="https://docs.pingcap.com/tidb/v7.0/tiflash-disaggregated-and-s3" target="_blank">disaggregated storage and compute architecture and S3 shared storage</a> (experimental)</td>
    <td>TiFlash introduces a cloud-native architecture as an option:
      <ul>
        <li>Disaggregates TiFlash's compute and storage, which is a milestone for elastic HTAP resource utilization.</li>
        <li>Introduces S3-based storage engine, which can provide shared storage at a lower cost.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td rowspan="2">Reliability and Availability<br/></td>
    <td><a href="https://docs.pingcap.com/tidb/v7.0/tidb-resource-control" target="_blank">Resource control enhancement</a> (experimental) </td>
    <td>Support using resource groups to allocate and isolate resources for various applications or workloads within one cluster. In this release, TiDB adds support for different resource binding modes (user, session, and statement levels) and user-defined priorities. Additionally, you can also use commands to perform resource calibration (estimation for the whole resource amount).</td>
  </tr>
  <tr>
    <td>TiFlash supports <a href="https://docs.pingcap.com/tidb/v7.0/tiflash-spill-disk" target="_blank">spill to disk</a></td>
    <td>TiFlash supports intermediate result spill to disk to mitigate OOMs in data-intensive operations such as aggregations, sorts, and hash joins.</td>
  </tr>
  <tr>
    <td rowspan="2">SQL</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.0/time-to-live" target="_blank">Row-level TTL</a> (GA)</td>
    <td>Support managing database size and improve performance by automatically expiring data of a certain age.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.0/partitioned-table#reorganize-partitions" target="_blank">Reorganize <code>LIST</code>/<code>RANGE</code> partition</a></td>
    <td>The <code>REORGANIZE PARTITION</code> statement can be used for merging adjacent partitions or splitting one partition into many, which provides better usability of partitioned tables.</td>
  </tr>
  <tr>
    <td rowspan="2">DB Operations and Observability<br/></td>
    <td>TiDB enhances the functionalities of <a href="https://docs.pingcap.com/tidb/v7.0/sql-statement-load-data" target="_blank"><code>LOAD DATA</code> statements</a> (experimental)</td>
    <td>TiDB enhances the functionalities of <code>LOAD DATA</code> SQL statements, such as supporting data import from S3/GCS.<br/></td>
  </tr>
  <tr>
    <td>TiCDC supports <a href="https://docs.pingcap.com/tidb/v7.0/ticdc-sink-to-cloud-storage" target="_blank">object storage sink</a> (GA)</td>
    <td>TiCDC supports replicating row change events to object storage services, including Amazon S3, GCS, Azure Blob Storage, and NFS.<br/></td>
  </tr>
</tbody>
</table>
