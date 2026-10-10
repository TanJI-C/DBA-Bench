# Hash join configuration and related optimization references

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-joins.md`
- Source Title: `Explain Statements That Use Joins`
- Source Heading Path: `Explain Statements That Use Joins > Hash Join > Configuration | Explain Statements That Use Joins > Hash Join > Related optimizations`
- Source Line Ranges: `256-266`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `hash-join`, `configuration`, `system-variables`, `memory-quota`, `concurrency`, `runtime-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0111_d614478f09`
- Source ID: `tidb-docs-8.1:explain-joins.md#configuration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36fcc1b5bc51728fb4df7cef123c6ff9462a1ac52e37ace673806269c3d108ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-joins#configuration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-joins.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented system variables and related optimization reference that affect hash join performance.
- Retrieval Keywords: tidb_mem_quota_query, tidb_hash_join_concurrency, Hash join configuration, memory quota for a query, spill the Build operator of a hash join to disk, number of concurrent hash join tasks, Runtime Filter, Related optimizations
- Follow-up Guidance: The source points to Runtime Filter as a feature that optimizes hash join performance and provides a separate Runtime Filter document for specific usage.
- Classification Note: This is performance content because it identifies hash join performance factors through system variables and a related optimization feature.

## Official Source Content

### Configuration

Hash join performance is influenced by the following system variables:

- [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query) (default value: 1GB) - if the memory quota for a query is exceeded, TiDB will attempt to spill the `Build` operator of a hash join to disk to save memory.
- [`tidb_hash_join_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_hash_join_concurrency) (default value: `5`) - the number of concurrent hash join tasks.
### Related optimizations

TiDB provides the Runtime Filter feature, which optimizes the performance of hash join and greatly improves its execution speed. For specific optimization usage, see [Runtime Filter](https://docs.pingcap.com/tidb/stable/runtime-filter).
