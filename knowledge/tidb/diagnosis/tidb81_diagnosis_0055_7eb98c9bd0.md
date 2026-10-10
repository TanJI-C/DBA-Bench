# Diagnosis procedures for slow read and write queries

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/latency-breakdown.md`
- Source Title: `Latency Breakdown`
- Source Heading Path: `Latency Breakdown > Diagnosis use cases | Latency Breakdown > Diagnosis use cases > Slow read queries | Latency Breakdown > Diagnosis use cases > Slow write queries`
- Source Line Ranges: `858-875`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tidb`, `tikv`
- Topic Tags: `latency`, `slow-queries`, `read-queries`, `write-queries`, `top-sql`, `database-time`, `conflicts`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0055_7eb98c9bd0`
- Source ID: `tidb-docs-8.1:latency-breakdown.md#diagnosis-use-cases`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f68f870c2189e2f4dc389ddcd295f98381fb57271e4607e25bcc7f8ee16b3402`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/latency-breakdown#diagnosis-use-cases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/latency-breakdown.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing whether slow database time comes from read queries or write queries and identifying the documented panels and metrics to inspect.
- Retrieval Keywords: Diagnosis procedures for slow read and write queries, Diagnosis use cases, Database Time panel, Performance Overview Dashboard, slow read queries, slow write queries, SELECT statements account for a significant portion of the database time, Top SQL statements, TiDB Dashboard, Point get, Batch point get, table scan, index scan, tikv_scheduler_latch_wait_duration_seconds_sum{type="acquire_pessimistic_lock"} by (instance), hot Regions, conflicts in the application, Lock, Commit
- Follow-up Guidance: For slow writes, the chunk says to first check `tikv_scheduler_latch_wait_duration_seconds_sum{type="acquire_pessimistic_lock"} by (instance)` to distinguish hot Region conflicts from application-wide conflicts before analyzing Lock and Commit durations.
- Classification Note: This chunk is classified as diagnosis because it gives documented procedures for analyzing slow read and slow write queries using dashboard panels, Top SQL, and a specific conflict metric.

## Official Source Content

## Diagnosis use cases

The preceding sections explain the details about time cost metrics during querying. This section introduces common procedures of metrics analysis when you encounter slow read or write queries. All metrics can be checked in the Database Time panel of [Performance Overview Dashboard](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard).
### Slow read queries

If `SELECT` statements account for a significant portion of the database time, you can assume that TiDB is slow at read queries.

The execution plans of slow queries can be found in the [Top SQL statements](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-overview#top-sql-statements) panel of TiDB Dashboard. To investigate the time costs of slow read queries, you can analyze [Point get](#point-get), [Batch point get](#batch-point-get) and some [simple coprocessor queries](#table-scan--index-scan) according to the preceding descriptions.
### Slow write queries

Before investigating slow writes, you need to troubleshoot the cause of the conflicts by checking `tikv_scheduler_latch_wait_duration_seconds_sum{type="acquire_pessimistic_lock"} by (instance)`:

- If this metric is high in some specific TiKV instances, there might be conflicts in hot Regions.
- If this metric is high across all instances, there might be conflicts in the application.

After confirming the cause of conflicts from the application, you can investigate slow write queries by analyzing the duration of [Lock](#lock) and [Commit](#commit).
