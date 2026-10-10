# Column Pruning overview and optimizer behavior

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/column-pruning.md`
- Source Title: `Column Pruning`
- Source Heading Path: `Column Pruning`
- Source Line Ranges: `5-20`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `column-pruning`, `optimizer`, `logical-optimization`, `query-plan`, `datasource`, `selection`, `io-reduction`, `rule-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0082_bcf2ce197c`
- Source ID: `tidb-docs-8.1:column-pruning.md#column-pruning`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `18c96f468d22b3a82678be6f8a13b7e459692dde189a3221164e01c4de5f9d2f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/column-pruning#column-pruning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/column-pruning.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB logical optimization removes unused columns from a query plan to reduce I/O and resource waste.
- Retrieval Keywords: Column Pruning, columnPruner, logical optimization phase, top-down scanning, Selection operator, DataSource operator, reduce I/O resources, unused columns, redundant columns, select a from t where b> 5, blocklist of optimization rules and expression pushdown
- Follow-up Guidance: The source also notes that disabling this optimization rule is described in The Blocklist of Optimization Rules and Expression Pushdown.
- Classification Note: This is classified as performance because the content explains an optimizer rule that prunes redundant columns to reduce I/O resource usage and improve subsequent optimization.

## Official Source Content

# Column Pruning

The basic idea of column pruning is that for columns not used in the operator, the optimizer does not need to retain them during optimization. Removing these columns reduces the use of I/O resources and facilitates the subsequent optimization. The following is an example of column repetition:

Suppose there are four columns (a, b, c, and d) in table t. You can execute the following statement:

```sql
select a from t where b> 5
```

In this query, only column a and column b are used, and column c and column d are redundant. Regarding the query plan of this statement, the `Selection` operator uses column b. Then the `DataSource` operator uses columns a and column b. Columns c and column d can be pruned because the `DataSource` operator does not read them.

Therefore, when TiDB performs a top-down scanning during the logic optimization phase, redundant columns are pruned to reduce waste of resources. This scanning process is called "Column Pruning", corresponding to the `columnPruner` rule. If you want to disable this rule, refer to [The Blocklist of Optimization Rules and Expression Pushdown](https://docs.pingcap.com/tidb/stable/blocklist-control-plan).
