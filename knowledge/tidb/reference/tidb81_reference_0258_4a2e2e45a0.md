# Index join plan selection, variations, and configuration

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/explain-joins.md`
- Source Title: `Explain Statements That Use Joins`
- Source Heading Path: `Explain Statements That Use Joins > Index Join | Explain Statements That Use Joins > Index Join > Variations of Index Join | Explain Statements That Use Joins > Index Join > Configuration`
- Source Line Ranges: `169-184`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `explain`, `join`, `index-join`, `optimizer-hints`, `plan-management`, `system-variables`, `concurrency`, `batch-size`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0258_4a2e2e45a0`
- Source ID: `tidb-docs-8.1:explain-joins.md#index-join`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `497c06a45b2991c57939726509ff2603e15acd77d11fc35fd5add203aae303dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/explain-joins#index-join
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/explain-joins.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB selects or varies index join plans, how to reference `INL_JOIN` and `INL_HASH_JOIN`, or which system variables affect index join performance.
- Retrieval Keywords: Index Join, Variations of Index Join, INL_JOIN, INL_HASH_JOIN, index join plan selection, SQL Plan Management, tidb_index_join_batch_size, tidb_index_lookup_join_concurrency, index lookup join batch size, concurrent index lookup tasks
- Follow-up Guidance: The source notes that if a frequent query gets a worse hash join plan than index join, SQL Plan Management can bind a hint to the query.
- Classification Note: This is reference content because it describes index join variations, optimizer hint identifiers, and related system variables for configuration.

## Official Source Content

> **Note:**
>
> In the above example, the SQL Optimizer selects the hash join plan which performs worse than the index join. Query optimization is an [NP-complete problem](https://en.wikipedia.org/wiki/NP-completeness), and less-than-optimal plans might be chosen. If this is a frequent query, it is recommended to use [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management) to bind a hint to a query, which can be easier to manage than inserting hints into queries that your application sends to TiDB.
### Variations of Index Join

An index join operation using the hint [`INL_JOIN`](https://docs.pingcap.com/tidb/stable/optimizer-hints#inl_joint1_name--tl_name-) creates a hash table of the intermediate results before joining on the outer table. TiDB also supports creating a hash table on the outer table using the hint [`INL_HASH_JOIN`](https://docs.pingcap.com/tidb/stable/optimizer-hints#inl_hash_join). Each of these variations of index join is automatically selected by the SQL Optimizer.
### Configuration

Index join performance is influenced by the following system variables:

- [`tidb_index_join_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_index_join_batch_size) (default value: `25000`) - the batch size of `index lookup join` operations.
- [`tidb_index_lookup_join_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_index_lookup_join_concurrency) (default value: `4`) - the number of concurrent index lookup tasks.
