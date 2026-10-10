# Comparison report, DIFF_RATIO, and maximum different item table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-diagnostics-report.md`
- Source Title: `TiDB Dashboard Diagnostic Report`
- Source Heading Path: `TiDB Dashboard Diagnostic Report > Comparison report | TiDB Dashboard Diagnostic Report > Comparison report > DIFF_RATIO introduction | TiDB Dashboard Diagnostic Report > Comparison report > Maximum Different Item table`
- Source Line Ranges: `320-368`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `comparison-report`, `diff-ratio`, `slow-queries`, `monitoring-metrics`, `time-range`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0069_b5babf3512`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-diagnostics-report.md#comparison-report`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4c1fa20efc47ba27efe9a5daf141b63ba5923fb5e145e21df561a44d0a0416e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-report#comparison-report
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-diagnostics-report.md

## Retrieval Guidance

- Use When: Use this chunk when you need to understand a TiDB Dashboard comparison report for two time ranges, including slow query comparison tables, `DIFF_RATIO`, and the `Maximum Different Item` table.
- Retrieval Keywords: Comparison report, Compare Report Time Range, t1, t2, Slow Queries In Time Range t2, Top 10 slow query in time range t1, Top 10 slow query in time range t2, DIFF_RATIO, AVG_DIFF_RATIO, MAX_DIFF_RATIO, MIN_DIFF_RATIO, Instance CPU Usage, Maximum Different Item, METRIC_NAME, LABEL, MAX_DIFF, TiKV, coprocessor_info
- Follow-up Guidance: The content states that `t1` is the normal or reference time range, `t2` is the abnormal time range, and `Maximum Different Item` sorts monitoring metrics by difference so you can quickly see which metric differs the most between the two ranges.
- Classification Note: This is reference content because it explains the structure and meaning of comparison report fields and tables, including the exact `DIFF_RATIO` value rules and the columns in `Maximum Different Item`.

## Official Source Content

## Comparison report

You can generate a comparison report for two time ranges. The report content is the same as the report for a single time range, except that a comparison column is added to show the difference between the two time ranges. The following sections introduce some unique tables in the comparison report and how to view the comparison report.

First, the `Compare Report Time Range` report in the basic information shows the two time ranges for comparison:

![Compare Report Time Range report](/media/dashboard/dashboard-diagnostics-compare-time.png)

In the table above, `t1` is the normal time range, or the reference time range. `t2` is the abnormal time range.

Tables related to slow queries are shown as follows:

* `Slow Queries In Time Range t2`: Shows slow queries that only appear in `t2` but not during `t1`.
* `Top 10 slow query in time range t1`: The Top 10 slow queries during `t1`.
* `Top 10 slow query in time range t2`: The Top 10 slow queries during `t2`.
### DIFF_RATIO introduction

This section introduces `DIFF_RATIO` using the `Instance CPU Usage` table as an example.

![Compare Instance CPU Usage report](/media/dashboard/dashboard-diagnostics-compare-instance-cpu-usage.png)

* `t1.AVG`, `t1.MAX`, `t1.Min` are the average value, maximum value, and minimum value of CPU usage in the `t1`.
* `t2.AVG`, `t2.MAX`, and `t2.Min` are the average value, maximum value, and minimum value ​​of CPU usage during `t2`.
* `AVG_DIFF_RATIO` is `DIFF_RATIO` of the average values during `t1` and `t2`.
* `MAX_DIFF_RATIO` is `DIFF_RATIO` of the maximum values during `t1` and `t2`.
* `MIN_DIFF_RATIO` is `DIFF_RATIO` of the minimum values during `t1` and `t2`.

`DIFF_RATIO`: Indicates the difference value between the two time ranges. It has the following values:

* If the monitoring metric has a value only within `t2` and has no value within `t1`, the value of `DIFF_RATIO` is `1`.
* If the monitoring metric has a value only within `t1`, and has no value within `t2` time range, the value of `DIFF_RATIO` is `-1`.
* If the value of `t2` is greater than that of `t1`, then `DIFF_RATIO` = `(t2.value / t1.value)-1`
* If the value of `t2` is smaller than that of `t1`, then `DIFF_RATIO` = `1-(t1.value / t2.value)`

For example, in the table above, the average CPU usage of the `tidb` node in `t2` is 2.02 times higher than that in `t1`, which is `2.02` = `1240/410-1`.
### Maximum Different Item table

The `Maximum Different Item` table compares the monitoring metrics of two time ranges, and sorts them according to the difference of the monitoring metrics. Using this table, you can quickly find out which monitoring metric has the biggest difference in the two time ranges. See the following example:

![Maximum Different Item table](/media/dashboard/dashboard-diagnostics-maximum-different-item.png)

* `Table`: Indicates this monitoring metric comes from which table in the comparison report. For example, `TiKV, coprocessor_info` indicates the `coprocessor_info` table in the TiKV component.
* `METRIC_NAME`: The monitoring metric name. Click `expand` to view the comparison of different labels of metrics.
* `LABEL`: The label corresponding to the monitoring metric. For example, the monitoring metric of `TiKV Coprocessor scan` has 2 labels, namely `instance`, `req`, `tag`, `sql_type`, which are the TiKV address, request type, operation type and operation column family.
* `MAX_DIFF`: Difference value, which is the `DIFF_RATIO` calculation of `t1.VALUE` and `t2.VALUE`.

From the table above, you can see the `t2` time range has much more Coprocessor requests than the `t1` time range, and the SQL parsing time of TiDB in `t2` is much longer.
