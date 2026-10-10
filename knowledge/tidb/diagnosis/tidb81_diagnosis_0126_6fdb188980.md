# Incorrect TiDB execution plan latency troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-cpu-issues.md`
- Source Title: `Troubleshoot Increased Read and Write Latency`
- Source Heading Path: `Troubleshoot Increased Read and Write Latency | Troubleshoot Increased Read and Write Latency > Common causes | Troubleshoot Increased Read and Write Latency > Common causes > Incorrect TiDB execution plan | Troubleshoot Increased Read and Write Latency > Common causes > Incorrect TiDB execution plan > Phenomenon | Troubleshoot Increased Read and Write Latency > Common causes > Incorrect TiDB execution plan > Possible reason | Troubleshoot Increased Read and Write Latency > Common causes > Incorrect TiDB execution plan > Troubleshooting methods`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `latency`, `slow-log`, `execution-plan`, `statistics`, `analyze`, `plan-binding`, `index-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0126_6fdb188980`
- Source ID: `tidb-docs-8.1:troubleshoot-cpu-issues.md#troubleshoot-increased-read-and-write-latency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88065b35c3517edc75276a4457ef5c10094a3215eff9ac8982a70dfe41a50c15`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues#troubleshoot-increased-read-and-write-latency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-cpu-issues.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing increased read or write latency caused by an unstable TiDB execution plan, incorrect index selection, large Scan Keys, or inaccurate statistics.
- Retrieval Keywords: incorrect TiDB execution plan, select tidb_decode_plan('xxx...'), Scan Keys, analyze table, auto analyze, tidb_auto_analyze_ratio, tidb_auto_analyze_start_time, tidb_auto_analyze_end_time, use index, create global binding, force index, SQL Plan Management, Join Order
- Follow-up Guidance: The content points to updating statistics with analyze or auto analyze settings and to binding the execution plan with use index, create global binding, or SQL Plan Management depending on the version references in the source.
- Classification Note: This is classified as diagnosis content because it lists phenomena, a possible reason of inaccurate statistics, and troubleshooting methods for latency caused by wrong execution plans.

## Official Source Content

# Troubleshoot Increased Read and Write Latency

This document introduces the possible causes of read and write latency and jitters, and how to troubleshoot these issues.
## Common causes
### Incorrect TiDB execution plan

The execution plan of queries is unstable and might select the incorrect index, which causes higher latency.
#### Phenomenon

* If the query execution plan is output in the slow log, you can directly view the plan. Execute the `select tidb_decode_plan('xxx...')` statement to parse the detailed execution plan.
* The number of scanned keys in the monitor abnormally increases; in the slow log, the number of `Scan Keys` are large.
* The SQL execution duration in TiDB is greatly different than that in other databases such as MySQL. You can compare the execution plan of other databases (for example, whether `Join Order` is different).
#### Possible reason

The statistics is inaccurate.
#### Troubleshooting methods

* Update the statistical information
    * Execute `analyze table` manually and execute `analyze` periodically with the `crontab` command to keep the statistics accurate.
    * Execute `auto analyze` automatically. Lower the threshold value of `analyze ratio`, increase the frequency of information collection, and set the start and end time of the execution. See the following examples:
        * `set global tidb_auto_analyze_ratio=0.2;`
        * `set global tidb_auto_analyze_start_time='00:00 +0800';`
        * `set global tidb_auto_analyze_end_time='06:00 +0800';`
* Bind the execution plan
    * Modify the application SQL statements and execute `use index` to consistently use the index of the column.
    * In 3.0 versions, you do not need to modify the application SQL statements. Use `create global binding` to create the binding SQL statement of `force index`.
    * In 4.0 versions, [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management) is supported, which avoids the performance decrease caused by unstable execution plans.
