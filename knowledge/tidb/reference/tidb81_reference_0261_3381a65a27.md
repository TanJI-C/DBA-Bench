# Merge Join execution plan and process

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-joins.md`
- Source Title: `Explain Statements That Use Joins`
- Source Heading Path: `Explain Statements That Use Joins > Merge Join`
- Source Line Ranges: `267-296`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `joins`, `merge-join`, `execution-plan`, `operator-info`, `join-keys`, `memory-usage`, `sorted-order`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0261_3381a65a27`
- Source ID: `tidb-docs-8.1:explain-joins.md#merge-join`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cfd58dd3d76b7f526562ee2e76363eb4b1f7ce198c58ad9f6b3e2c71bfbe49a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-joins#merge-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-joins.md

## Retrieval Guidance

- Use When: Use this chunk when interpreting an EXPLAIN plan that shows MergeJoin or when checking how a merge join works with sorted input and join keys.
- Retrieval Keywords: Merge Join, MergeJoin_7, EXPLAIN SELECT /*+ MERGE_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;, operator info, inner join, left key:test.t1.id, right key:test.t2.id, Build, Probe, keep order:true, TableReader, TableFullScan, Join Group, sorted order, far less memory than hash join, do not execute in parallel
- Follow-up Guidance: The source also describes the merge join execution process as reading a Join Group from the Build side into memory, reading Probe-side data, and checking matches including non-equivalent conditions.
- Classification Note: This is reference content because it explains the Merge Join execution plan fields and execution process shown by EXPLAIN in TiDB SQL.

## Official Source Content

## Merge Join

Merge join is a special sort of join that applies when both sides of the join are read in sorted order. It can be described as similar to an _efficient zipper merge_: as data is read on both the `Build` and the `Probe` sides of the join, the join operation works like a streaming operation. Merge joins require far less memory than hash join but do not execute in parallel.

The following is an example:

```sql
EXPLAIN SELECT /*+ MERGE_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```

```sql
+-----------------------------+-----------+-----------+---------------+-------------------------------------------------------+
| id                          | estRows   | task      | access object | operator info                                         |
+-----------------------------+-----------+-----------+---------------+-------------------------------------------------------+
| MergeJoin_7                 | 142020.00 | root      |               | inner join, left key:test.t1.id, right key:test.t2.id |
| ├─TableReader_12(Build)     | 180000.00 | root      |               | data:TableFullScan_11                                 |
| │ └─TableFullScan_11        | 180000.00 | cop[tikv] | table:t2      | keep order:true                                       |
| └─TableReader_10(Probe)     | 142020.00 | root      |               | data:TableFullScan_9                                  |
|   └─TableFullScan_9         | 142020.00 | cop[tikv] | table:t1      | keep order:true                                       |
+-----------------------------+-----------+-----------+---------------+-------------------------------------------------------+
5 rows in set (0.00 sec)
```

For the execution process of the merge join operator, TiDB performs the following operations:

1. Read all the data of a Join Group from the `Build` side into the memory.
2. Read the data of the `Probe` side.
3. Compare whether each row of data on the `Probe` side matches a complete Join Group on the `Build` side. Apart from equivalent conditions, there are non-equivalent conditions. Here "match" mainly refers to checking whether non-equivalent conditions are met. Join Group refers to the data with the same value among all Join Keys.
