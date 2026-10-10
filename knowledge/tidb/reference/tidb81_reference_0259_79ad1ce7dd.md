# Hash join execution and runtime statistics

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-joins.md`
- Source Title: `Explain Statements That Use Joins`
- Source Heading Path: `Explain Statements That Use Joins > Hash Join | Explain Statements That Use Joins > Hash Join > Runtime Statistics`
- Source Line Ranges: `185-229`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `hash-join`, `execution-plan`, `build-side`, `probe-side`, `memory-quota`, `temporary-storage`, `explain-analyze`, `runtime-statistics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0259_79ad1ce7dd`
- Source ID: `tidb-docs-8.1:explain-joins.md#hash-join`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a8eae9b57400527a4c9167ef2bc4cc5f4ce0cfbffa3de1d8a3311a6220946134`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-joins#hash-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-joins.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how `HashJoin` executes, what `Build` and `Probe` mean in `EXPLAIN`, or how `EXPLAIN ANALYZE` reports memory and temporary disk usage for hash join.
- Retrieval Keywords: Hash Join, HashJoin_27, Build side, Probe side, HASH_JOIN(t1, t2), EXPLAIN ANALYZE, operator info, execution info, tidb_mem_quota_query, tidb_enable_tmp_storage_on_oom, temporary storage, disk used for temporary storage, equal:[eq(test.t1.id, test.t2.id)]
- Follow-up Guidance: The source explains that when `tidb_mem_quota_query` is exceeded and `tidb_enable_tmp_storage_on_oom` is `ON`, TiDB might create the `Build` operator on disk and record memory-related runtime statistics in `EXPLAIN ANALYZE`.
- Classification Note: This is reference content because it explains hash join execution order, `EXPLAIN` fields, and runtime statistics behavior documented by the official examples.

## Official Source Content

## Hash Join

In a hash join operation, TiDB reads and caches the data on the `Build` side of the join in a hash table, and then reads the data on the `Probe` side of the join, probing the hash table to access required rows. Hash joins require more memory to execute than index joins but execute much faster when there are a lot of rows that need to be joined. The hash join operator is multi-threaded in TiDB and executes in parallel.

An example of hash join is as follows:

```sql
EXPLAIN SELECT /*+ HASH_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```

```sql
+-----------------------------+-----------+-----------+---------------+------------------------------------------------+
| id                          | estRows   | task      | access object | operator info                                  |
+-----------------------------+-----------+-----------+---------------+------------------------------------------------+
| HashJoin_27                 | 142020.00 | root      |               | inner join, equal:[eq(test.t1.id, test.t2.id)] |
| ├─TableReader_29(Build)     | 142020.00 | root      |               | data:TableFullScan_28                          |
| │ └─TableFullScan_28        | 142020.00 | cop[tikv] | table:t1      | keep order:false                               |
| └─TableReader_31(Probe)     | 180000.00 | root      |               | data:TableFullScan_30                          |
|   └─TableFullScan_30        | 180000.00 | cop[tikv] | table:t2      | keep order:false                               |
+-----------------------------+-----------+-----------+---------------+------------------------------------------------+
5 rows in set (0.00 sec)
```

For the execution process of `HashJoin_27`, TiDB performs the following operations in order:

1. Cache the data of the `Build` side in memory.
2. Construct a Hash Table on the `Build` side based on the cached data.
3. Read the data at the `Probe` side.
4. Use the data of the `Probe` side to probe the Hash Table.
5. Return qualified data to the user.

The `operator info` column in the `EXPLAIN` result table also records other information about `HashJoin_27`, including whether the query is Inner Join or Outer Join, and what are the conditions of Join. In the above example, the query is an Inner Join, where the Join condition `equal:[eq(test.t1.id, test.t2.id)]` partly corresponds with the query condition `WHERE t1.id = t2.id`. The operator info of the other Join operators in the following examples is similar to this one.
### Runtime Statistics

If [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) (default value: 1 GB) is exceeded, and the [`tidb_enable_tmp_storage_on_oom`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tmp_storage_on_oom) value is `ON` (default), TiDB will attempt to use temporary storage, and might create the `Build` operator (used as part of the hash join) on disk. Runtime statistics such as memory usage are recorded in the `execution info` of the `EXPLAIN ANALYZE` result table. The following example shows the output of `EXPLAIN ANALYZE` with a 1 GB (default) and a 500 MB quota for `tidb_mem_quota_query`. At 500 MB, disk is used for temporary storage:

```sql
EXPLAIN ANALYZE SELECT /*+ HASH_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
SET tidb_mem_quota_query=500 * 1024 * 1024;
EXPLAIN ANALYZE SELECT /*+ HASH_JOIN(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;
```
