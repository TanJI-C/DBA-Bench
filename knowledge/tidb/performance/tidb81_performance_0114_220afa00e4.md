# Correlation-type extended statistics example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/extended-statistics.md`
- Source Title: `Introduction to Extended Statistics`
- Source Heading Path: `Introduction to Extended Statistics > Usage examples for correlation-type extended statistics | Introduction to Extended Statistics > Usage examples for correlation-type extended statistics > Step 1. Define the table | Introduction to Extended Statistics > Usage examples for correlation-type extended statistics > Step 2. Execute an example query without extended statistics | Introduction to Extended Statistics > Usage examples for correlation-type extended statistics > Step 3. Enable extended statistics | Introduction to Extended Statistics > Usage examples for correlation-type extended statistics > Step 4. See how extended statistics make a difference`
- Source Line Ranges: `110-161`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `correlation`, `optimizer`, `row-estimation`, `index-selection`, `analyze`, `pearson-correlation`, `thresholds`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0114_220afa00e4`
- Source ID: `tidb-docs-8.1:extended-statistics.md#usage-examples-for-correlation-type-extended-statistics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `57a6cf9ba167bf778d93690b474a5775cb38f2e307236336fb5a92273683d7f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/extended-statistics#usage-examples-for-correlation-type-extended-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/extended-statistics.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about correlation-type extended statistics, row count estimation for range queries, or how correlation affects index selection in the optimizer.
- Retrieval Keywords: correlation-type extended statistics, ALTER TABLE t ADD STATS_EXTENDED s1 correlation(col1, col2), Pearson correlation coefficient, SELECT * FROM t WHERE col1 > 1 ORDER BY col2 LIMIT 1, row count estimation, range query, index selection, tidb_opt_correlation_threshold, tidb_opt_correlation_exp_factor, independent assumption, strictly correlated in order
- Follow-up Guidance: The source says that after ANALYZE computes the correlation for col1 and col2, the optimizer can estimate scanned rows more precisely, and if the correlation factor is below tidb_opt_correlation_threshold it falls back to the independent assumption with heuristic adjustment influenced by tidb_opt_correlation_exp_factor.
- Classification Note: This is performance content because it demonstrates how correlation-type extended statistics improve optimizer row estimation and influence index selection for a query.

## Official Source Content

## Usage examples for correlation-type extended statistics

Currently, TiDB only supports the correlation-type extended statistics. This type is used to estimate the number of rows in the range query and improve index selection. The following example shows how the correlation-type extended statistics are used to estimate the number of rows in a range query.
### Step 1. Define the table

Define a table `t` as follows:

```sql
CREATE TABLE t(col1 INT, col2 INT, KEY(col1), KEY(col2));
```

Suppose that `col1` and `col2` of table `t` both obey monotonically increasing constraints in row order. This means that the values of `col1` and `col2` are strictly correlated in order, and the correlation factor is `1`.
### Step 2. Execute an example query without extended statistics

Execute the following query without using extended statistics:

```sql
SELECT * FROM t WHERE col1 > 1 ORDER BY col2 LIMIT 1;
```

For the execution of the preceding query, the TiDB optimizer has the following options to access table `t`:

- Uses the index on `col1` to access table `t` and then sorts the result by `col2` to calculate `Top-1`.
- Uses the index on `col2` to meet the first row that satisfies `col1 > 1`. The cost of this access method mainly depends on how many rows are filtered out when TiDB scans the table in `col2`'s order.

Without extended statistics, the TiDB optimizer only supposes that `col1` and `col2` are independent, which **leads to a significant estimation error**.
### Step 3. Enable extended statistics

Set `tidb_enable_extended_stats` to `ON`, and create the extended statistics object for `col1` and `col2`:

```sql
ALTER TABLE t ADD STATS_EXTENDED s1 correlation(col1, col2);
```

When you execute `ANALYZE` after the object creation, TiDB calculates the [Pearson correlation coefficient](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient) of `col1` and `col2` of table `t`, and writes the object into the `mysql.stats_extended` table.
### Step 4. See how extended statistics make a difference

After TiDB has the extended statistics for correlation, the optimizer can estimate how many rows to be scanned more precisely.

At this time, for the query in [Stage 2. Execute an example query without extended statistics](#step-2-execute-an-example-query-without-extended-statistics), `col1` and `col2` are strictly correlated in order. If TiDB accesses table `t` by using the index on `col2` to meet the first row that satisfies `col1 > 1`, the TiDB optimizer will equivalently translate the row count estimation into the following query:

```sql
SELECT * FROM t WHERE col1 <= 1 OR col1 IS NULL;
```

The preceding query result plus one will be the final estimation for the row count. In this way, you do not need to use the independent assumption and **the significant estimation error is avoided**.

If the correlation factor (`1` in this example) is less than the value of the system variable `tidb_opt_correlation_threshold`, the optimizer will use the independent assumption, but it will also increase the estimation heuristically. The larger the value of `tidb_opt_correlation_exp_factor`, the larger the estimation result. The larger the absolute value of the correlation factor, the larger the estimation result.
