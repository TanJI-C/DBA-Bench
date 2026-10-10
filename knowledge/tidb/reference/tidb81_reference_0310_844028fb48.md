# WITH ROLLUP and GROUPING() examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/group-by-modifier.md`
- Source Title: `GROUP BY Modifiers`
- Source Heading Path: `GROUP BY Modifiers > Examples`
- Source Line Ranges: `47-162`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tiflash`, `tidb`
- Topic Tags: `examples`, `with-rollup`, `grouping-function`, `having`, `order-by`, `null-handling`, `aggregation`, `tiflash-replica`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0310_844028fb48`
- Source ID: `tidb-docs-8.1:functions-and-operators/group-by-modifier.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3de96524232716849536e56738e4c4a8ee80a245884726d13269e8eabceca838`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/group-by-modifier.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for concrete SQL examples of `WITH ROLLUP`, interpreting rollup `NULL` rows, filtering with `HAVING`, or using `GROUPING()` to distinguish native `NULL` values from rollup-generated `NULL` values.
- Retrieval Keywords: CREATE TABLE bank, ALTER TABLE bank SET TIFLASH REPLICA 1, SELECT year, month, SUM(profit) AS profit FROM bank GROUP BY year, month WITH ROLLUP, ORDER BY year desc, month desc, HAVING year IS NOT null AND month IS NOT null, GROUPING(), grouping(year), grouping(month), GROUPING(year, month) <> 0, native NULL values, 64-bit UNSIGNED LONGLONG
- Follow-up Guidance: The source further shows that `GROUPING()` accepts up to 64 grouping expressions and explains the bit-position formula for multiple parameters.
- Classification Note: This is reference content because it provides executable examples and result interpretation for `WITH ROLLUP`, `HAVING`, `ORDER BY`, TiFlash replica setup, and the `GROUPING()` function.

## Official Source Content

## Examples

Suppose you have a profit table named `bank` with the `year`, `month`, `day`, and `profit` columns.

```sql
CREATE TABLE bank
(
    year    INT,
    month   VARCHAR(32),
    day     INT,
    profit  DECIMAL(13, 7)
);

ALTER TABLE bank SET TIFLASH REPLICA 1; -- Add a TiFlash replica for the table

INSERT INTO bank VALUES(2000, "Jan", 1, 10.3),(2001, "Feb", 2, 22.4),(2000,"Mar", 3, 31.6)
```

To get the profit for the bank per year, you can use a simple `GROUP BY` clause as follows:

```sql
SELECT year, SUM(profit) AS profit FROM bank GROUP BY year;
+------+--------------------+
| year | profit             |
+------+--------------------+
| 2001 | 22.399999618530273 |
| 2000 |  41.90000057220459 |
+------+--------------------+
2 rows in set (0.15 sec)
```

In addition to yearly profits, bank reports usually also need to include the overall profit for all years or monthly divided profits for detailed profit analysis. Before v7.4.0, you have to use different `GROUP BY` clauses in multiple queries and join the results using UNION to obtain aggregated summaries. Starting from v7.4.0, you can simply achieve the desired results in a single query by appending the `WITH ROLLUP` modifier to the `GROUP BY` clause.

```sql
SELECT year, month, SUM(profit) AS profit from bank GROUP BY year, month WITH ROLLUP ORDER BY year desc, month desc;
+------+-------+--------------------+
| year | month | profit             |
+------+-------+--------------------+
| 2001 | Feb   | 22.399999618530273 |
| 2001 | NULL  | 22.399999618530273 |
| 2000 | Mar   | 31.600000381469727 |
| 2000 | Jan   | 10.300000190734863 |
| 2000 | NULL  |  41.90000057220459 |
| NULL | NULL  |  64.30000019073486 |
+------+-------+--------------------+
6 rows in set (0.025 sec)
```

The preceding results include aggregated data at different dimensions: by both year and month, by year, and overall. In the results, a row without `NULL` values indicates that the `profit` in that row is calculated by grouping both year and month. A row with a `NULL` value in the `month` column indicates that `profit` in that row is calculated by aggregating all months in a year, while a row with a `NULL` value in the `year` column indicates that `profit` in that row is calculated by aggregating all years.

Specifically:

- The `profit` value in the first row comes from the 2-dimensional group `{year, month}`, representing the aggregation result for the fine-grained `{2000, "Jan"}` group.
- The `profit` value in the second row comes from the 1-dimensional group `{year}`, representing the aggregation result for the mid-level `{2001}` group.
- The `profit` value in the last row comes from the 0-dimensional grouping `{}`, representing the overall aggregation result.

`NULL` values in the `WITH ROLLUP` results are generated just before the Aggregate operator is applied. Therefore, you can use `NULL` values in `SELECT`, `HAVING`, and `ORDER BY` clauses to further filter the aggregated results.

For example, you can use `NULL` in the `HAVING` clause to filter and view the aggregated results of 2-dimensional groups only:

```sql
SELECT year, month, SUM(profit) AS profit FROM bank GROUP BY year, month WITH ROLLUP HAVING year IS NOT null AND month IS NOT null;
+------+-------+--------------------+
| year | month | profit             |
+------+-------+--------------------+
| 2000 | Mar   | 31.600000381469727 |
| 2000 | Jan   | 10.300000190734863 |
| 2001 | Feb   | 22.399999618530273 |
+------+-------+--------------------+
3 rows in set (0.02 sec)
```

Note that if a column in the `GROUP BY` list contains native `NULL` values, the aggregation results of `WITH ROLLUP` might mislead the query results. To address this issue, you can use the `GROUPING()` function to distinguish native `NULL` values from `NULL` values generated by `WITH ROLLUP`. This function takes a grouping expression as a parameter and returns `0` or `1` to indicate whether the grouping expression is aggregated in the current result. `1` represents aggregated, and `0` represents not aggregated.

The following example shows how to use the `GROUPING()` function:

```sql
SELECT year, month, SUM(profit) AS profit, grouping(year) as grp_year, grouping(month) as grp_month FROM bank GROUP BY year, month WITH ROLLUP ORDER BY year DESC, month DESC;
+------+-------+--------------------+----------+-----------+
| year | month | profit             | grp_year | grp_month |
+------+-------+--------------------+----------+-----------+
| 2001 | Feb   | 22.399999618530273 |        0 |         0 |
| 2001 | NULL  | 22.399999618530273 |        0 |         1 |
| 2000 | Mar   | 31.600000381469727 |        0 |         0 |
| 2000 | Jan   | 10.300000190734863 |        0 |         0 |
| 2000 | NULL  |  41.90000057220459 |        0 |         1 |
| NULL | NULL  |  64.30000019073486 |        1 |         1 |
+------+-------+--------------------+----------+-----------+
6 rows in set (0.028 sec)
```

From this output, you can get an understanding of the aggregation dimension of a row directly from the results of `grp_year` and `grp_month`, which prevents interference from native `NULL` values in the `year` and `month` grouping expressions.

The `GROUPING()` function can accept up to 64 grouping expressions as parameters. In the output of multiple parameters, each parameter generates a result of `0` or `1`, and these parameters collectively form a 64-bit `UNSIGNED LONGLONG` with each bit as `0` or `1`. You can use the following formula to get the bit position of each parameter as follows:

```go
GROUPING(day, month, year):
  result for GROUPING(year)
+ result for GROUPING(month) << 1
+ result for GROUPING(day) << 2
```

By using multiple parameters in the `GROUPING()` function, you can efficiently filter aggregate results at any high dimension. For example, you can quickly filter the aggregate results for each year and all years by using `GROUPING(year, month)`.

```sql
SELECT year, month, SUM(profit) AS profit, grouping(year) as grp_year, grouping(month) as grp_month FROM bank GROUP BY year, month WITH ROLLUP HAVING GROUPING(year, month) <> 0 ORDER BY year DESC, month DESC;
+------+-------+--------------------+----------+-----------+
| year | month | profit             | grp_year | grp_month |
+------+-------+--------------------+----------+-----------+
| 2001 | NULL  | 22.399999618530273 |        0 |         1 |
| 2000 | NULL  |  41.90000057220459 |        0 |         1 |
| NULL | NULL  |  64.30000019073486 |        1 |         1 |
+------+-------+--------------------+----------+-----------+
3 rows in set (0.023 sec)
```
