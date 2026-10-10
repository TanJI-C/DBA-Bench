# Hash aggregation example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-aggregation.md`
- Source Title: `Explain Statements That Use Aggregation`
- Source Heading Path: `Explain Statements Using Aggregation > Hash Aggregation`
- Source Line Ranges: `92-117`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `explain`, `hashagg`, `aggregation`, `memory`, `count`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0244_a1145db6b6`
- Source ID: `tidb-docs-8.1:explain-aggregation.md#hash-aggregation`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2927d1669d3747fa9a81aa3698dd0075591e4e580580f7b768633633e904cbda`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-aggregation#hash-aggregation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-aggregation.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving an example of Hash Aggregation in EXPLAIN, including the HASH_AGG() hint, HashAgg operators, and the count hashing function shown in operator info.
- Retrieval Keywords: Hash Aggregation, EXPLAIN SELECT /*+ HASH_AGG() */ count(*) FROM t1, HASH_AGG(), HashAgg_9, HashAgg_5, TableReader_10, TableFullScan_8, funcs:count(1)->Column#6, operator info
- Follow-up Guidance: The source states that Hash Aggregation executes in parallel using multiple threads but consumes more memory than Stream Aggregation.
- Classification Note: This is reference content because it documents the HashAgg operator example and the exact EXPLAIN output fields used to identify hash aggregation.

## Official Source Content

## Hash Aggregation

The Hash Aggregation algorithm uses a hash table to store intermediate results while performing aggregation. It executes in parallel using multiple threads but consumes more memory than Stream Aggregation.

The following is an example of the `HashAgg` operator:

```sql
EXPLAIN SELECT /*+ HASH_AGG() */ count(*) FROM t1;
```

```sql
+---------------------------+-----------+-----------+---------------+---------------------------------+
| id                        | estRows   | task      | access object | operator info                   |
+---------------------------+-----------+-----------+---------------+---------------------------------+
| HashAgg_9                 | 1.00      | root      |               | funcs:count(Column#6)->Column#5 |
| └─TableReader_10          | 1.00      | root      |               | data:HashAgg_5                  |
|   └─HashAgg_5             | 1.00      | cop[tikv] |               | funcs:count(1)->Column#6        |
|     └─TableFullScan_8     | 242020.00 | cop[tikv] | table:t1      | keep order:false                |
+---------------------------+-----------+-----------+---------------+---------------------------------+
4 rows in set (0.00 sec)
```

The `operator info` shows that the hashing function used to aggregate the data is `funcs:count(1)->Column#6`.
