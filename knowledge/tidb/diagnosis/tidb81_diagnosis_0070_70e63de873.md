# Execution plan bottleneck example and references

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-tuning-best-practice.md`
- Source Title: `A Practical Guide for SQL Tuning`
- Source Heading Path: `A Practical Guide for SQL Tuning > SQL tuning guide > Understand execution plans > Identify bottlenecks in execution plans`
- Source Line Ranges: `539-562`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `execution-plans`, `explain`, `bottlenecks`, `query-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0070_70e63de873`
- Source ID: `tidb-docs-8.1:sql-tuning-best-practice.md#identify-bottlenecks-in-execution-plans`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3068aab677487949c455c33a3cb3a15765e286622db97a06fdc391eec95076ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-tuning-best-practice#identify-bottlenecks-in-execution-plans
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-tuning-best-practice.md

## Retrieval Guidance

- Use When: Use this chunk when analyzing an execution plan to identify bottlenecks from operator rows, tasks, access objects, and execution info in `EXPLAIN` output.
- Retrieval Keywords: Identify bottlenecks in execution plans, execution plan bottleneck, EXPLAIN output, id estRows actRows task access object execution info memory disk, IndexJoin_88, TableReader_109, Selection_108, TableRangeScan_107, IndexLookUp_97, IndexRangeScan_93, TableRowIDScan_94, cop[tikv], table:labels, table:rates, index:index_rates_on_label_id(label_id), table:orders, TiDB Query Execution Plan Overview, EXPLAIN Walkthrough
- Follow-up Guidance: For more information, see TiDB Query Execution Plan Overview and EXPLAIN Walkthrough.
- Classification Note: The official content is classified as diagnosis because it shows a concrete execution plan example for understanding and locating bottlenecks in query execution.

## Official Source Content

```
+---------------------------------------+----------+---------+-----------+----------------------------------------------------------------------------------------+---------------...+----------+------+
| id                                    | estRows  | actRows | task      | access object                                                                          | execution info...| memory   | disk |
+---------------------------------------+----------+---------+-----------+----------------------------------------------------------------------------------------+---------------...+----------+------+
| Limit_24                              | 1000.00  | 1000    | root      |                                                                                        | time:1.96s, lo...| N/A      | N/A  |
| └─IndexJoin_88                        | 1000.00  | 1000    | root      |                                                                                        | time:1.96s, lo...| 1.32 MB  | N/A  |
|   ├─IndexJoin_99(Build)               | 1000.00  | 2458    | root      |                                                                                        | time:1.96s, lo...| 77.7 MB  | N/A  |
|   │ ├─TableReader_109(Build)          | 6505.62  | 158728  | root      |                                                                                        | time:1.26s, lo...| 297.0 MB | N/A  |
|   │ │ └─Selection_108                 | 6505.62  | 171583  | cop[tikv] |                                                                                        | tikv_task:{pro...| N/A      | N/A  |
|   │ │   └─TableRangeScan_107          | 80396.43 | 179616  | cop[tikv] | table:labels                                                                           | tikv_task:{pro...| N/A      | N/A  |
|   │ └─Projection_98(Probe)            | 1000.00  | 2458    | root      |                                                                                        | time:2.13s, lo...| 59.2 KB  | N/A  |
|   │   └─IndexLookUp_97                | 1000.00  | 2458    | root      | partition:all                                                                          | time:2.13s, lo...| 1.20 MB  | N/A  |
|   │     ├─Selection_95(Build)         | 6517.14  | 6481    | cop[tikv] |                                                                                        | time:798.6ms, ...| N/A      | N/A  |
|   │     │ └─IndexRangeScan_93         | 6517.14  | 6481    | cop[tikv] | table:rates, index:index_rates_on_label_id(label_id)                                   | tikv_task:{pro...| N/A      | N/A  |
|   │     └─Selection_96(Probe)         | 1000.00  | 2458    | cop[tikv] |                                                                                        | time:444.4ms, ...| N/A      | N/A  |
|   │       └─TableRowIDScan_94         | 6517.14  | 6481    | cop[tikv] | table:rates                                                                            | tikv_task:{pro...| N/A      | N/A  |
|   └─TableReader_84(Probe)             | 984.56   | 1998    | root      |                                                                                        | time:207.6ms, ...| N/A      | N/A  |
|     └─Selection_83                    | 984.56   | 1998    | cop[tikv] |                                                                                        | tikv_task:{pro...| N/A      | N/A  |
|       └─TableRangeScan_82             | 1000.00  | 2048    | cop[tikv] | table:orders                                                                           | tikv_task:{pro...| N/A      | N/A  |
+---------------------------------------+----------+---------+-----------+----------------------------------------------------------------------------------------+---------------...+----------+------+
```

For more information, see [TiDB Query Execution Plan Overview](https://docs.pingcap.com/tidb/stable/explain-overview) and [`EXPLAIN` Walkthrough](https://docs.pingcap.com/tidb/stable/explain-walkthrough).
