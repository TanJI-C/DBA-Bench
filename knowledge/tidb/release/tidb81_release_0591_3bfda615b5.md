# TiDB 8.1.0 overview and highlights table

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes`
- Source Line Ranges: `5-91`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `dm`, `pd`, `sql`, `ticdc`, `tidb`, `tikv`, `tiproxy`
- Topic Tags: `release-date`, `lts`, `highlights`, `scalability`, `performance`, `reliability`, `availability`, `observability`, `data-migration`, `sql-binding`, `resource-control`, `client-authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0591_3bfda615b5`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#tidb-8-1-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60ef6436c0338a14e84416f0d48d66e78943f7b3989b33dce2c69ef0b199b1ff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#tidb-8-1-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for the TiDB 8.1.0 release overview, release date, LTS status, or the highlighted features introduced or made GA from 7.6.0 to 8.1.0 across TiDB components.
- Retrieval Keywords: TiDB 8.1.0 Release Notes, Release date: May 24, 2024, TiDB version: 8.1.0, Long-Term Support Release, LTS, 7.5.0, 7.6.0-DMR, 8.0.0-DMR, Acceleration of cluster snapshot restore speed, BR, restore cluster snapshots, Achieve up to 10 times faster for creating tables in batch, Active PD Follower, GetRegion, ScanRegions, tidb_dml_type = "bulk", Bulk DML, Global Sort, IMPORT INTO, CREATE INDEX, Cross-database SQL binding, TiProxy, DM officially supports MySQL 8.0, managing queries that consume more resources than expected, INFORMATION_SCHEMA.TIDB_INDEX_USAGE, sys.schema_unused_indexes, TiCDC Simple protocol, TiCDC Debezium protocol, TiCDC client authentication, mutual Transport Layer Security, mTLS
- Follow-up Guidance: For upgrade context from 7.5.x to 8.1.0, the content points to the TiDB Release Notes PDF that covers all release notes between the two LTS versions.
- Classification Note: This is a release overview chunk because it summarizes TiDB 8.1.0 release metadata and a cross-component highlights table spanning scalability, reliability, observability, and data migration.

## Official Source Content

# TiDB 8.1.0 Release Notes

Release date: May 24, 2024

TiDB version: 8.1.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v8.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v8.1/production-deployment-using-tiup)

TiDB 8.1.0 is a Long-Term Support Release (LTS).

Compared with the previous LTS 7.5.0, 8.1.0 includes new features, improvements, and bug fixes released in [7.6.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-7.6.0) and [8.0.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-8.0.0). When you upgrade from 7.5.x to 8.1.0, you can download the [TiDB Release Notes PDF](https://docs-download.pingcap.com/pdf/tidb-v7.6-to-v8.1-en-release-notes.pdf) to view all release notes between the two LTS versions. The following table lists some highlights from 7.6.0 to 8.1.0:
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
    <td rowspan="5">Scalability and Performance</td>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/br-snapshot-guide#restore-cluster-snapshots">Acceleration of cluster snapshot restore speed</a> (GA in v8.0.0)</td>
    <td>With this feature, BR can fully leverage the scale advantage of a cluster, enabling all TiKV nodes in the cluster to participate in the preparation step of data restores. This feature can significantly improve the restore speed of large datasets in large-scale clusters. Real-world tests show that this feature can saturate the download bandwidth, with the download speed improving by 8 to 10 times, and the end-to-end restore speed improving by approximately 1.5 to 3 times.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/accelerated-table-creation">Achieve up to 10 times faster for creating tables in batch</a> (experimental, introduced in v7.6.0)</td>
    <td>With the implementation of the new DDL architecture in v7.6.0, the performance of batch table creation has witnessed a remarkable improvement, up to 10 times faster. This substantial enhancement drastically reduces the time needed for creating numerous tables. This acceleration is particularly noteworthy in SaaS scenarios, where the prevalence of high volumes of tables, ranging from tens to hundreds of thousands, is a common challenge.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/tune-region-performance#use-the-active-pd-follower-feature-to-enhance-the-scalability-of-pds-region-information-query-service">Use Active PD Followers to enhance PD's Region information query service</a> (experimental, introduced in v7.6.0)</td>
    <td>TiDB v7.6.0 introduces an experimental feature "Active PD Follower", which allows PD followers to provide Region information query services. This feature improves the capability of the PD cluster to handle <code>GetRegion</code> and <code>ScanRegions</code> requests in clusters with a large number of TiDB nodes and Regions, thereby reducing the CPU pressure on PD leaders.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/system-variables#tidb_dml_type-new-in-v800">Bulk DML for much larger transactions</a> (experimental, introduced in v8.0.0)</td>
    <td>Large batch DML jobs, such as extensive cleanup jobs, joins, or aggregations, can consume a significant amount of memory and have previously been limited at very large scales. Bulk DML (<code>tidb_dml_type = "bulk"</code>) is a new DML type for handling large batch DML tasks more efficiently while providing transaction guarantees and mitigating OOM issues. This feature differs from import, load, and restore operations when used for data loading.</td>
  </tr>
  <tr>
    <td>Enhance the stability of caching the schema information when there is a massive number of tables (experimental, introduced in v8.0.0)</td>
    <td>SaaS companies using TiDB as the system of record for their multi-tenant applications often need to store a substantial number of tables. In previous versions, handling table counts in the order of a million or more was feasible, but it had the potential to degrade the overall user experience. TiDB v8.0.0 improves the situation by implementing a <a href="https://docs.pingcap.com/tidb/v8.1/system-variables#tidb_enable_auto_analyze_priority_queue-new-in-v800">priority queue</a> for <code>auto analyze</code>, making the process less rigid and enhancing stability across a wider array of tables.</td>
  </tr>
  <tr>
    <td rowspan="5">Reliability and availability</td>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/tidb-global-sort">Global Sort</a> (GA in v8.0.0)</td>
    <td>The Global Sort feature aims to improve the stability and efficiency of <code>IMPORT INTO</code> and <code>CREATE INDEX</code>. By globally sorting the data to be processed, this feature improves the stability, controllability, and scalability of data writing to TiKV, consequently enhancing the user experience and service quality of data import and index creation. With global sorting enabled, each <code>IMPORT INTO</code> or <code>CREATE INDEX</code> statement now supports importing or adding indexes for up to 40 TiB of data.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/sql-plan-management#cross-database-binding">Cross-database SQL binding</a> (introduced in v7.6.0)</td>
    <td>When managing hundreds of databases with the same schema, it is often necessary to apply SQL bindings across these databases. For example, in SaaS or PaaS data platforms, each user typically operates separate databases with the same schema and runs similar SQL queries on them. In this case, it is impractical to bind SQL for each database one by one. TiDB v7.6.0 introduces cross-database SQL bindings that enable matching bindings across all schema-equivalent databases.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/tiproxy-overview">Support TiProxy</a> (GA in v8.0.0)</td>
    <td>Full support for the TiProxy service, easily deployable via deployment tooling, to manage and maintain connections to TiDB so that they live through rolling restarts, upgrades, or scaling events.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v8.1/dm-compatibility-catalog">Data Migration (DM) officially supports MySQL 8.0</a> (GA in v7.6.0)</td>
    <td>Previously, using DM to migrate data from MySQL 8.0 is an experimental feature and is not available for production environments. TiDB v7.6.0 enhances the stability and compatibility of this feature to help you smoothly and quickly migrate data from MySQL 8.0 to TiDB in production environments. In v7.6.0, this feature becomes generally available (GA).</td>
  </tr>
  <tr>
    <td>TiDB resource control supports <a href="https://docs.pingcap.com/tidb/v8.1/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries">managing queries that consume more resources than expected</a> (GA in v8.1.0)</td>
    <td>Through the rules of resource groups, TiDB can automatically identify queries that consume more resources than expected, and then limit or cancel these queries. Even if the queries are not identified by the rules, you can still manually add query characteristics and take corresponding measures to reduce the impact of the sudden query performance problem on the entire database.</td>
  </tr>
  <tr>
    <td rowspan="1">DB Operations and Observability</td>
    <td>Support monitoring index usage statistics (introduced in v8.0.0)</td>
    <td>Proper index design is a crucial prerequisite to maintaining database performance. TiDB v8.0.0 introduces the <a href="https://docs.pingcap.com/tidb/v8.1/information-schema-tidb-index-usage"><code>INFORMATION_SCHEMA.TIDB_INDEX_USAGE</code></a> table and the <a href="https://docs.pingcap.com/tidb/v8.1/sys-schema-unused-indexes"><code>sys.schema_unused_indexes</code></a> view to provide usage statistics of indexes. This feature helps you assess the efficiency of indexes in the database and optimize the index design.</td>
  </tr>
  <tr>
    <td rowspan="3">Data Migration</td>
    <td>TiCDC supports <a href="https://docs.pingcap.com/tidb/v8.1/ticdc-simple-protocol">the Simple protocol</a> (introduced in v8.0.0)</td>
    <td>TiCDC introduces a new protocol, the Simple protocol. This protocol provides in-band schema tracking capabilities by embedding table schema information in DDL and BOOTSTRAP events.</td>
  </tr>
  <tr>
    <td>TiCDC supports <a href="https://docs.pingcap.com/tidb/v8.1/ticdc-debezium">the Debezium format protocol</a> (introduced in v8.0.0)</td>
    <td>TiCDC introduces a new protocol, the Debezium protocol. TiCDC can now publish data change events to a Kafka sink using a protocol that generates Debezium style messages.</td>
  </tr>
  <tr>
    <td>TiCDC supports <a href="https://docs.pingcap.com/tidb/v8.1/ticdc-client-authentication">client authentication</a> (introduced in v8.1.0)</td>
    <td>TiCDC supports client authentication using mutual Transport Layer Security (mTLS) or TiDB username and password. This feature enables CLI or OpenAPI clients to authenticate their connections to TiCDC.</td>
  </tr>
</tbody>
</table>
