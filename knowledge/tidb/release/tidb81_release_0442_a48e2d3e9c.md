# TiDB 7.1.0 release overview and key feature summary

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes | TiDB 7.1.0 Release Notes > Feature details`
- Source Line Ranges: `5-84`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `release-notes`, `lts`, `feature-summary`, `performance`, `reliability`, `sql`, `security`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0442_a48e2d3e9c`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#tidb-7-1-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e0e13240c851438750e31a64016aba1d218fd5fcac245a4ef75448c608e3678`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#tidb-7-1-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 7.1.0 release overview, its LTS status, release date, or the official summary of key features and improvements across TiDB, TiKV, and TiFlash.
- Retrieval Keywords: TiDB 7.1.0 Release Notes, Release date May 31, 2023, TiDB version 7.1.0, Long-Term Support Release, LTS, previous LTS 6.5.0, 6.6.0-DMR, 7.0.0-DMR, Feature details, Scalability and Performance, Reliability and availability, SQL, Security, TiFlash disaggregated storage and compute architecture, S3 shared storage, TiKV batch aggregating data requests, tidb_store_batch_size, Load-based replica read, tidb_load_based_replica_read_threshold, partitioned Raft KV storage engine, Resource control by resource groups, TiFlash spill to disk, Multi-valued indexes, Row-level TTL, Generated columns, LDAP authentication, Audit log enhancement
- Follow-up Guidance: For more detailed retrieval, follow the feature names in this summary to their linked documentation pages such as disaggregated TiFlash and S3, system variables, resource control, TTL, generated columns, and security compatibility with MySQL.
- Classification Note: This is a release-notes overview chunk because the official content states TiDB 7.1.0 is an LTS release and summarizes major features, improvements, and availability notes by category.

## Official Source Content

# TiDB 7.1.0 Release Notes

Release date: May 31, 2023

TiDB version: 7.1.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.1/production-deployment-using-tiup)

TiDB 7.1.0 is a Long-Term Support Release (LTS).

Compared with the previous LTS 6.5.0, 7.1.0 not only includes new features, improvements, and bug fixes released in [6.6.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-6.6.0), [7.0.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-7.0.0), but also introduces the following key features and improvements:

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
    <td rowspan="4">Scalability and Performance</td>
    <td>TiFlash supports the <a href="https://docs.pingcap.com/tidb/v7.1/tiflash-disaggregated-and-s3" target="_blank">disaggregated storage and compute architecture and S3 shared storage</a> (experimental, introduced in v7.0.0)</td>
    <td>TiFlash introduces a cloud-native architecture as an option:
      <ul>
        <li>Disaggregates TiFlash's compute and storage, which is a milestone for elastic HTAP resource utilization.</li>
        <li>Introduces S3-based storage engine, which can provide shared storage at a lower cost.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>TiKV supports <a href="https://docs.pingcap.com/tidb/v7.1/system-variables#tidb_store_batch_size" target="_blank">batch aggregating data requests</a> (introduced in v6.6.0) </td>
    <td>This enhancement significantly reduces total RPCs in TiKV batch-get operations. In situations where data is highly dispersed and the gRPC thread pool has insufficient resources, batching coprocessor requests can improve performance by more than 50%.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.1/troubleshoot-hot-spot-issues#scatter-read-hotspots" target="_blank">Load-based replica read</a></td>
    <td>In a read hotspot scenario, TiDB can redirect read requests for a hotspot TiKV node to its replicas. This feature efficiently scatters read hotspots and optimizes the use of cluster resources. To control the threshold for triggering load-based replica read, you can adjust the system variable <a href="https://docs.pingcap.com/tidb/v7.1/system-variables#tidb_load_based_replica_read_threshold-new-in-v700" target="_blank"><code>tidb_load_based_replica_read_threshold</code></a>.</td>
  </tr>
  <tr>
      <td>TiKV supports<a href="https://docs.pingcap.com/tidb/v7.1/partitioned-raft-kv" target="_blank"> partitioned Raft KV storage engine </a> (experimental)</td>
    <td>TiKV introduces a new generation of storage engine, the partitioned Raft KV. By allowing each data Region to have a dedicated RocksDB instance, it can expand the cluster's storage capacity from TB-level to PB-level and provide more stable write latency and stronger scalability.</td>
    </tr>
  <tr>
    <td rowspan="2">Reliability and availability</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.1/tidb-resource-control" target="_blank">Resource control by resource groups</a> (GA)</td>
   <td>Support resource management based on resource groups, which allocates and isolates resources for different workloads in the same cluster. This feature significantly enhances the stability of multi-application clusters and lays the foundation for multi-tenancy. In v7.1.0, this feature introduces the ability to estimate system capacity based on actual workload or hardware deployment.</td>
  </tr>
  <tr>
    <td>TiFlash supports <a href="https://docs.pingcap.com/tidb/v7.1/tiflash-spill-disk" target="_blank">spill to disk</a> (introduced in v7.0.0)</td>
    <td>TiFlash supports intermediate result spill to disk to mitigate OOMs in data-intensive operations such as aggregations, sorts, and hash joins.</td>
  </tr>
  <tr>
    <td rowspan="3">SQL</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.1/sql-statement-create-index#multi-valued-indexes" target="_blank">Multi-valued indexes</a> (GA)</td>
    <td>Support MySQL-compatible multi-valued indexes and enhance the JSON type to improve compatibility with MySQL 8.0. This feature improves the efficiency of membership checks on multi-valued columns.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.1/time-to-live" target="_blank">Row-level TTL</a> (GA in v7.0.0)</td>
    <td>Support managing database size and improve performance by automatically expiring data of a certain age.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.1/generated-columns" target="_blank">Generated columns</a> (GA)</td>
    <td>Values in a generated column are calculated by a SQL expression in the column definition in real time. This feature pushes some application logic to the database level, thus improving query efficiency.</td>
  </tr>
  <tr>
    <td rowspan="2">Security</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.1/security-compatibility-with-mysql" target="_blank">LDAP authentication</a></td>
    <td>TiDB supports LDAP authentication, which is compatible with <a href="https://dev.mysql.com/doc/refman/8.0/en/ldap-pluggable-authentication.html" target="_blank">MySQL 8.0</a>.</td>
  </tr>
  <tr>
    <td><a href="https://static.pingcap.com/files/2023/09/18204824/TiDB-Database-Auditing-User-Guide1.pdf" target="_blank">Audit log enhancement</a> (<a href="https://www.pingcap.com/tidb-enterprise" target="_blank">Enterprise Edition</a> only)</td>
    <td>TiDB Enterprise Edition enhances the database auditing feature. It significantly improves the system auditing capacity by providing more fine-grained event filtering controls, more user-friendly filter settings, a new file output format in JSON, and lifecycle management of audit logs.</td>
  </tr>
</tbody>
</table>
## Feature details
