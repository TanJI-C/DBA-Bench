# TIDB_DECODE_PLAN for decoding encoded execution plans

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/tidb-functions.md`
- Source Title: `TiDB Specific Functions`
- Source Heading Path: `TiDB Specific Functions > TIDB_DECODE_PLAN`
- Source Line Ranges: `271-288`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `sql-functions`, `plan-decoding`, `slow-query-log`, `execution-plan`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0353_0fb2ac11da`
- Source ID: `tidb-docs-8.1:functions-and-operators/tidb-functions.md#tidb-decode-plan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ead9051fe79e12db899250092b42ce53876a9ee5c4dd729bfdf7ea77eda8196`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb-decode-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/tidb-functions.md

## Retrieval Guidance

- Use When: Use this when searching for how `TIDB_DECODE_PLAN()` converts an encoded execution plan from the slow query log into a human-readable plan table.
- Retrieval Keywords: TIDB_DECODE_PLAN, slow query log, encoded execution plan, human-readable form, EXPLAIN, TableReader_7, Selection_6, TableFullScan_5, cop[tikv], operator info, execution info
- Follow-up Guidance: The source notes that this is useful because the captured plan reflects execution time, while re-executing the statement in `EXPLAIN` might produce different results as data distribution and statistics evolve over time.
- Classification Note: This is reference content because it documents the `TIDB_DECODE_PLAN` SQL function and illustrates its decoded execution plan output from an encoded plan string.

## Official Source Content

## TIDB_DECODE_PLAN

You can find TiDB execution plans in encoded form in the slow query log. The `TIDB_DECODE_PLAN()` function is then used to decode the encoded plans into a human-readable form.

This function is useful because a plan is captured at the time the statement is executed. Re-executing the statement in `EXPLAIN` might produce different results as data distribution and statistics evolves over time.

```sql
SELECT tidb_decode_plan('8QIYMAkzMV83CQEH8E85LjA0CWRhdGE6U2VsZWN0aW9uXzYJOTYwCXRpbWU6NzEzLjHCtXMsIGxvb3BzOjIsIGNvcF90YXNrOiB7bnVtOiAxLCBtYXg6IDU2OC41wgErRHByb2Nfa2V5czogMCwgcnBjXxEpAQwFWBAgNTQ5LglZyGNvcHJfY2FjaGVfaGl0X3JhdGlvOiAwLjAwfQkzLjk5IEtCCU4vQQoxCTFfNgkxXzAJMwm2SGx0KHRlc3QudC5hLCAxMDAwMCkNuQRrdgmiAHsFbBQzMTMuOMIBmQnEDDk2MH0BUgEEGAoyCTQzXzUFVwX1oGFibGU6dCwga2VlcCBvcmRlcjpmYWxzZSwgc3RhdHM6cHNldWRvCTk2ISE2aAAIMTUzXmYA')\G
```

```sql
*************************** 1. row ***************************
  tidb_decode_plan('8QIYMAkzMV83CQEH8E85LjA0CWRhdGE6U2VsZWN0aW9uXzYJOTYwCXRpbWU6NzEzLjHCtXMsIGxvb3BzOjIsIGNvcF90YXNrOiB7bnVtOiAxLCBtYXg6IDU2OC41wgErRHByb2Nfa2V5czogMCwgcnBjXxEpAQwFWBAgNTQ5LglZyGNvcHJfY2FjaGVfaGl0X3JhdGlvOiAwLjAwfQkzLjk5IEtCCU4vQQoxCTFfNgkxXz:     id                     task         estRows    operator info                              actRows    execution info                                                                                                                         memory     disk
    TableReader_7          root         319.04     data:Selection_6                           960        time:713.1µs, loops:2, cop_task: {num: 1, max: 568.5µs, proc_keys: 0, rpc_num: 1, rpc_time: 549.1µs, copr_cache_hit_ratio: 0.00}    3.99 KB    N/A
    └─Selection_6          cop[tikv]    319.04     lt(test.t.a, 10000)                        960        tikv_task:{time:313.8µs, loops:960}                                                                                                   N/A        N/A
      └─TableFullScan_5    cop[tikv]    960        table:t, keep order:false, stats:pseudo    960        tikv_task:{time:153µs, loops:960}                                                                                                     N/A        N/A
```
