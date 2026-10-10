# TiDB 7.5.0 release overview and highlights

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.0.md`
- Source Title: `TiDB 7.5.0 Release Notes`
- Source Heading Path: `TiDB 7.5.0 Release Notes`
- Source Line Ranges: `5-69`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`, `dashboard`, `sql`
- Topic Tags: `release-notes`, `lts`, `highlights`, `scalability`, `performance`, `resource-control`, `mysql-compatibility`, `import-into`, `ddl`, `profiling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0518_a2ec2e8f14`
- Source ID: `tidb-docs-8.1:releases/release-7.5.0.md#tidb-7-5-0-release-notes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `796d301dd65394d06a651c0da2b713ae07b50d1016db9ea553e2f59d4710d644`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.0#tidb-7-5-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the TiDB 7.5.0 release overview, LTS status, release date, or the highlighted features introduced between 7.2.0 and 7.5.0 such as parallel ADD INDEX, Global Sort, Resource Control, MySQL 8.0 compatibility, IMPORT INTO, tidb_service_scope, DDL pause and resume, and TiDB Dashboard heap profiling for TiKV.
- Retrieval Keywords: TiDB 7.5.0 Release Notes, December 1, 2023, Long-Term Support Release, LTS, 7.1.0 to 7.5.0, ADD INDEX, Global Sort, Distributed eXecution Framework, DXF, Resource Control, runaway queries, utf8mb4_0900_ai_ci, MySQL 8.0 compatibility, IMPORT INTO, TiDB Lightning physical import mode, tidb_service_scope, DDL pause and resume, TiDB Dashboard, heap profiling, TiKV
- Follow-up Guidance: The source points to related documentation including Quick start, Production deployment, tidb-global-sort, tidb-resource-control, sql-statement-import-into, system variable tidb_service_scope, DDL-related commands, and dashboard profiling.
- Classification Note: This is a release-notes overview chunk because it summarizes the TiDB 7.5.0 release and lists cross-component highlights rather than focusing on one detailed procedure.

## Official Source Content

# TiDB 7.5.0 Release Notes

Release date: December 1, 2023

TiDB version: 7.5.0

Quick access: [Quick start](https://docs.pingcap.com/tidb/v7.5/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v7.5/production-deployment-using-tiup)

TiDB 7.5.0 is a Long-Term Support Release (LTS).

Compared with the previous LTS 7.1.0, 7.5.0 includes new features, improvements, and bug fixes released in [7.2.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-7.2.0), [7.3.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-7.3.0), and [7.4.0-DMR](https://docs.pingcap.com/tidb/stable/releases/release-7.4.0). When you upgrade from 7.1.x to 7.5.0, you can download the [TiDB Release Notes PDF](https://docs-download.pingcap.com/pdf/tidb-v7.2-to-v7.5-en-release-notes.pdf) to view all release notes between the two LTS versions. The following table lists some highlights from 7.2.0 to 7.5.0:

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
    <td>Scalability and Performance</td>
    <td>Support running multiple <code>ADD INDEX</code> statements in parallel</td>
    <td>This feature allows for concurrent jobs to add multiple indexes for a single table. Previously, it would take the time of X plus the time of Y to execute two <code>ADD INDEX</code> statements simultaneously (X and Y). With this feature, adding two indexes X and Y in one SQL can be concurrently executed, and the total execution time of DDL is significantly reduced. Especially in scenarios with wide tables, internal test data shows that performance can be improved by up to 94%.</td>
  </tr>
  <tr>
    <td rowspan="3">Reliability and Availability</td>
    <td>Optimize <a href="https://docs.pingcap.com/tidb/v7.5/tidb-global-sort" target="_blank">Global Sort</a> (experimental, introduced in v7.4.0)</td>
    <td>TiDB v7.1.0 introduced the <a href="https://docs.pingcap.com/tidb/v7.5/tidb-distributed-execution-framework" target="_blank">Distributed eXecution Framework (DXF)</a>. For tasks that take advantage of this framework, v7.4 introduces global sorting to eliminate the unnecessary I/O, CPU, and memory spikes caused by temporarily out-of-order data during data re-organization tasks. The global sorting takes advantage of external shared object storage (Amazon S3 in this first iteration) to store intermediary files during the job, adding flexibility and cost savings. Operations like <code>ADD INDEX</code> and <code>IMPORT INTO</code> will be faster, more resilient, more stable, more flexible, and cost less to run.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v7.5/tidb-resource-control#manage-background-tasks" target="_blank">Resource control for background tasks</a> (experimental, introduced in v7.4.0)</td>
    <td>In v7.1.0, the <a href="https://docs.pingcap.com/tidb/v7.5/tidb-resource-control" target="_blank">Resource Control</a> feature was introduced to mitigate resource and storage access interference between workloads. TiDB v7.4.0 applied this control to the priority of background tasks as well. In v7.4.0, Resource Control now identifies and manages the priority of background task execution, such as auto-analyze, Backup & Restore, bulk load with TiDB Lightning, and online DDL. In future releases, this control will eventually apply to all background tasks.</td>
  </tr>
  <tr>
    <td>Resource control for <a href="https://docs.pingcap.com/tidb/v7.5/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries"> managing runaway queries</a> (experimental, introduced in v7.2.0)</td>
    <td><a href="https://docs.pingcap.com/tidb/v7.5/tidb-resource-control" target="_blank">Resource Control</a> is a framework for resource-isolating workloads by Resource Groups, but it makes no calls on how individual queries affect work inside of each group. TiDB v7.2.0 introduces "runaway queries control" to let you control how TiDB identifies and treats these queries per Resource Group. Depending on needs, long running queries might be terminated or throttled, and the queries can be identified by exact SQL text, SQL digests or their plan digests, for better generalization. In v7.3.0, TiDB enables you to proactively watch for known bad queries, similar to a SQL blocklist at the database level.</td>
  </tr>
  <tr>
    <td>SQL</td>
    <td>MySQL 8.0 compatibility (introduced in v7.4.0)</td>
    <td>In MySQL 8.0, the default character set is utf8mb4, and the default collation of utf8mb4 is <code>utf8mb4_0900_ai_ci</code>. TiDB v7.4.0 adding support for this enhances compatibility with MySQL 8.0 so that migrations and replications from MySQL 8.0 databases with the default collation are now much smoother.</td>
  </tr>
  <tr>
    <td rowspan="4">DB Operations and Observability</td>
    <td>TiDB Lightning's physical import mode integrated into TiDB with <a href="https://docs.pingcap.com/tidb/v7.5/sql-statement-import-into"><code>IMPORT INTO</code></a> (GA)</td>
    <td>Before v7.2.0, to import data based on the file system, you needed to install <a href="https://docs.pingcap.com/tidb/v7.5/tidb-lightning-overview">TiDB Lightning</a> and used its physical import mode. Now, the same capability is integrated into the <code>IMPORT INTO</code> statement so you can use this statement to quickly import data without installing any additional tool. This statement also supports the <a href="https://docs.pingcap.com/tidb/v7.5/tidb-distributed-execution-framework" target="_blank">Distributed eXecution Framework (DXF)</a> for parallel import, which improves import efficiency during large-scale imports.</td>
  </tr>
  <tr>
    <td>Specify <a href="https://docs.pingcap.com/tidb/v7.5/system-variables#tidb_service_scope-new-in-v740" target="_blank">the respective TiDB nodes</a> to execute the <code>ADD INDEX</code> and <code>IMPORT INTO</code> SQL statements (GA)</td>
    <td>You have the flexibility to specify whether to execute <code>ADD INDEX</code> or <code>IMPORT INTO</code> SQL statements on some of the existing TiDB nodes or newly added TiDB nodes. This approach enables resource isolation from the rest of the TiDB nodes, preventing any impact on business operations while ensuring optimal performance for executing the preceding SQL statements. In v7.5.0, this feature becomes generally available (GA).</td>
  </tr>
  <tr>
    <td>DDL supports <a href="https://docs.pingcap.com/tidb/v7.5/ddl-introduction#ddl-related-commands">pause and resume operations</a> (GA)</td>
    <td>Adding indexes can be big resource consumers and can affect online traffic. Even when throttled in a Resource Group or isolated to labeled nodes, there may still be a need to suspend these jobs in emergencies. As of v7.2.0, TiDB now natively supports suspending any number of these background jobs at once, freeing up needed resources while avoiding having to cancel and restart the jobs.</td>
  </tr>
  <tr>
    <td>TiDB Dashboard supports heap profiling for TiKV<a href="https://docs.pingcap.com/tidb/v7.5/dashboard-profiling" target="_blank"></a></td>
    <td>Previously, addressing TiKV OOM or high memory usage issues typically required manual execution of <code>jeprof</code> to generate a heap profile in the instance environment. Starting from v7.5.0, TiKV enables remote processing of heap profiles. You can now directly access the flame graph and call graph of heap profile. This feature provides the same simple and easy-to-use experience as Go heap profiling.</td>
  </tr>
</tbody>
</table>
