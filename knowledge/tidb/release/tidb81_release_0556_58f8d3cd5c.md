# 7.6.0 overview and Active PD Follower scalability feature

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes | TiDB 7.6.0 Release Notes > Feature details | TiDB 7.6.0 Release Notes > Feature details > Scalability`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `dm`, `pd`, `tidb`, `tikv`, `tiproxy`
- Topic Tags: `release-notes`, `feature-overview`, `scalability`, `performance`, `reliability`, `availability`, `sql-binding`, `snapshot-restore`, `ddl`, `active-pd-follower`, `region-queries`, `mysql-8-compatibility`, `data-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0556_58f8d3cd5c`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#tidb-7-6-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db428a42c99fca9e2a4a2ed95cd86db42576ad6cc9af13d7140f146882e3a0ea`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#tidb-7-6-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 7.6.0 release-note information about new feature highlights, especially the experimental Active PD Follower capability for PD Region information query scalability and the listed 7.6.0 improvements across SQL binding, BR snapshot restore, DDL, TiProxy, and DM.
- Retrieval Keywords: TiDB 7.6.0 Release Notes, 7.6.0 introduces the following key features and improvements, Active PD Follower, pd_enable_follower_handle_region, GetRegion, ScanRegions, PD's Region information query service, cross-database SQL binding, restore-cluster-snapshots, coarse-grained Region scatter algorithm, ddl-v2, creating tables in batch, TiProxy, DM officially supports MySQL 8.0, Feature details > Scalability
- Follow-up Guidance: The content points to related documentation for pd_enable_follower_handle_region and the guide on using the Active PD Follower feature to enhance PD's Region information query service.
- Classification Note: This chunk is classified as a self-managed release note because it summarizes TiDB 7.6.0 feature highlights and provides detailed release-note content for scalability, reliability, and availability improvements.

## Official Source Content

# TiDB 7.6.0 Release Notes

Release date: January 25, 2024

TiDB version: 7.6.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.6/quick-start-with-tidb)

7.6.0 introduces the following key features and improvements:

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
    <td><a href="https://docs.pingcap.com/tidb/v7.6/sql-plan-management#cross-database-binding">Cross-database SQL binding</a></td>
    <td>When managing hundreds of databases with the same schema, it is often necessary to apply SQL bindings across these databases. For example, in SaaS or PaaS data platforms, each user typically operates separate databases with the same schema and runs similar SQL queries on them. In this case, it is impractical to bind SQL for each database one by one. TiDB v7.6.0 introduces cross-database SQL bindings that enable matching bindings across all schema-equivalent databases.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.6/br-snapshot-guide#restore-cluster-snapshots">Achieve up to 10 times faster for snapshot restore (experimental)</a></td>
    <td>BR v7.6.0 introduces an experimental coarse-grained Region scatter algorithm to accelerate snapshot restores for clusters. In clusters with many TiKV nodes, this algorithm significantly improves cluster resource efficiency by more evenly distributing load across nodes and better utilizing per-node network bandwidth. In several real-world cases, this improvement accelerates restore process by about up to 10 times.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.6/ddl-v2">Achieve up to 10 times faster for creating tables in batch (experimental)</a></td>
    <td>With the implementation of the new DDL architecture in v7.6.0, the performance of batch table creation has witnessed a remarkable improvement, up to 10 times faster. This substantial enhancement drastically reduces the time needed for creating numerous tables. This acceleration is particularly noteworthy in SaaS scenarios, where the prevalence of high volumes of tables, ranging from tens to hundreds of thousands, is a common challenge.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.6/tune-region-performance#use-the-active-pd-follower-feature-to-enhance-the-scalability-of-pds-region-information-query-service">Use Active PD Followers to enhance PD's Region information query service (experimental)</a></td>
    <td>TiDB v7.6.0 introduces an experimental feature "Active PD Follower", which allows PD followers to provide Region information query services. This feature improves the capability of the PD cluster to handle <code>GetRegion</code> and <code>ScanRegions</code> requests in clusters with a large number of TiDB nodes and Regions, thereby reducing the CPU pressure on the PD leader.</td>
  </tr>
  <tr>
    <td rowspan="2">Reliability and Availability</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.6/tiproxy-overview">Support TiProxy (experimental)</a></td>
    <td>Full support for the TiProxy service, easily deployable via deployment tooling, to manage and maintain connections to TiDB so that they live through rolling restarts, upgrades, or scaling events.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.6/dm-compatibility-catalog">Data Migration (DM) officially supports MySQL 8.0 (GA)</a></td>
    <td>Previously, using DM to migrate data from MySQL 8.0 is an experimental feature and is not available for production environments. TiDB v7.6.0 enhances the stability and compatibility of this feature to help you smoothly and quickly migrate data from MySQL 8.0 to TiDB in production environments. In v7.6.0, this feature becomes generally available (GA).</td>
  </tr>
</tbody>
</table>
## Feature details
### Scalability

* Use the Active PD Follower feature to enhance the scalability of PD's Region information query service (experimental) [#7431](https://github.com/tikv/pd/issues/7431) @[CabinfeverB](https://github.com/CabinfeverB)

    In a TiDB cluster with a large number of Regions, the PD leader might experience high CPU load due to the increased overhead of handling heartbeats and scheduling tasks. If the cluster has many TiDB instances, and there is a high concurrency of requests for Region information, the CPU pressure on the PD leader increases further and might cause PD services to become unavailable.

    To ensure high availability, TiDB v7.6.0 supports using the Active PD Follower feature to enhance the scalability of PD's Region information query service. You can enable the Active PD Follower feature by setting the system variable [`pd_enable_follower_handle_region`](https://docs.pingcap.com/tidb/stable/system-variables#pd_enable_follower_handle_region-new-in-v760) to `ON`. After this feature is enabled, TiDB evenly distributes Region information requests to all PD servers, and PD followers can also handle Region requests, thereby reducing the CPU pressure on the PD leader.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tune-region-performance#use-the-active-pd-follower-feature-to-enhance-the-scalability-of-pds-region-information-query-service).
