# TiDB 8.0.0 overview and key features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes`
- Source Line Ranges: `5-58`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tidb`, `br`, `tikv`, `ticdc`
- Topic Tags: `release-overview`, `feature-summary`, `scalability`, `performance`, `observability`, `data-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0573_45265f16cd`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#tidb-8-0-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc252dc2323e2429654aa6156290698deda1516afe424d90b3cdfefb607ebcf5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#tidb-8-0-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving a high-level summary of TiDB 8.0.0 release highlights across scalability, performance, observability, and data migration features.
- Retrieval Keywords: TiDB 8.0.0 Release Notes, March 29, 2024, Disaggregation of PD to improve scalability, PD microservices, Bulk DML, tidb_dml_type = "bulk", Acceleration of cluster snapshot restore speed, BR restore cluster snapshots, auto analyze priority queue, tidb_enable_auto_analyze_priority_queue, INFORMATION_SCHEMA.TIDB_INDEX_USAGE, sys.schema_unused_indexes, TiCDC Simple protocol, TiCDC Debezium format protocol
- Follow-up Guidance: The source points to related documentation for Quick start, PD microservices, Bulk DML, BR snapshot restore, index usage statistics, and TiCDC protocols.
- Classification Note: This chunk is classified as a release overview because it summarizes the main new features and improvements introduced in TiDB 8.0.0 across multiple components.

## Official Source Content

# TiDB 8.0.0 Release Notes

Release date: March 29, 2024

TiDB version: 8.0.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v8.0/quick-start-with-tidb)

8.0.0 introduces the following key features and improvements:

<table>
<thead>
  <tr>
    <th>Category</th>
    <th>Feature/Enhancement</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="4">Scalability and Performance</td>
    <td><a href="https://docs.pingcap.com/tidb/v8.0/pd-microservices">Disaggregation of PD to improve scalability (experimental)</a> </td>
    <td>Placement Driver (PD) contains multiple critical modules to ensure the normal operation of TiDB clusters. As the workload of a cluster increases, the resource consumption of each module in PD also increases, causing mutual interference between these modules and ultimately affecting the overall service quality of the cluster. Starting from v8.0.0, TiDB addresses this issue by splitting the TSO and scheduling modules in PD into independently deployable microservices. This can significantly reduce the mutual interference between modules as the cluster scales. With this architecture, much larger clusters with much larger workloads are now possible.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.0/system-variables#tidb_dml_type-new-in-v800">Bulk DML for much larger transactions (experimental)</a></td>
    <td>Large batch DML jobs, such as extensive cleanup jobs, joins, or aggregations, can consume a significant amount of memory and have previously been limited at very large scales. Bulk DML (<code>tidb_dml_type = "bulk"</code>) is a new DML type for handling large batch DML tasks more efficiently while providing transaction guarantees and mitigating OOM issues. This feature differs from import, load, and restore operations when used for data loading.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.0/br-snapshot-guide#restore-cluster-snapshots">Acceleration of cluster snapshot restore speed (GA) </a></td>
    <td>With this feature, BR can fully leverage the scale advantage of a cluster, enabling all TiKV nodes in the cluster to participate in the preparation step of data restores. This feature can significantly improve the restore speed of large datasets in large-scale clusters. Real-world tests show that this feature can saturate the download bandwidth, with the download speed improving by 8 to 10 times, and the end-to-end restore speed improving by approximately 1.5 to 3 times.</td>
  </tr>
  <tr>
    <td>Enhance the stability of caching the schema information when there is a massive number of tables (experimental)</td>
    <td>SaaS companies using TiDB as the system of record for their multi-tenant applications often need to store a substantial number of tables. In previous versions, handling table counts in the order of a million or more was feasible, but it had the potential to degrade the overall user experience. TiDB v8.0.0 improves the situation by implementing a <a href="https://docs.pingcap.com/tidb/v8.0/system-variables#tidb_enable_auto_analyze_priority_queue-new-in-v800">priority queue</a> for <code>auto analyze</code>, making the process less rigid and enhancing stability across a wider array of tables.</td>
  </tr>
  <tr>
    <td rowspan="1">DB Operations and Observability</td>
    <td>Support monitoring index usage statistics </td>
    <td>Proper index design is a crucial prerequisite to maintaining database performance. TiDB v8.0.0 introduces the <a href="https://docs.pingcap.com/tidb/v8.0/information-schema-tidb-index-usage"><code>INFORMATION_SCHEMA.TIDB_INDEX_USAGE</code></a> table and the <a href="https://docs.pingcap.com/tidb/v8.0/sys-schema-unused-indexes"><code>sys.schema_unused_indexes</code></a> view to provide usage statistics of indexes. This feature helps you assess the efficiency of indexes in the database and optimize the index design.</td>
  </tr>
  <tr>
    <td rowspan="2">Data Migration</td>
    <td>TiCDC adds support for <a href="https://docs.pingcap.com/tidb/v8.0/ticdc-simple-protocol">the Simple protocol</a> </td>
    <td>TiCDC introduces a new protocol, the Simple protocol. This protocol provides in-band schema tracking capabilities by embedding table schema information in DDL and BOOTSTRAP events.</td>
  </tr>
  <tr>
    <td>TiCDC adds support for <a href="https://docs.pingcap.com/tidb/v8.0/ticdc-debezium">the Debezium format protocol</a> </td>
    <td>TiCDC introduces a new protocol, the Debezium protocol. TiCDC can now publish data change events to a Kafka sink using a protocol that generates Debezium style messages.</td>
  </tr>
</tbody>
</table>
