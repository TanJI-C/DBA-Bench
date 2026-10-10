# WITH ROLLUP overview, use cases, and prerequisites

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/group-by-modifier.md`
- Source Title: `GROUP BY Modifiers`
- Source Heading Path: `GROUP BY Modifiers | GROUP BY Modifiers > Use cases | GROUP BY Modifiers > Prerequisites`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tiflash`, `tidb`
- Topic Tags: `group-by`, `with-rollup`, `olap`, `aggregation`, `grouping-dimensions`, `mpp`, `prerequisites`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0309_dd06b48407`
- Source ID: `tidb-docs-8.1:functions-and-operators/group-by-modifier.md#group-by-modifiers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7b570d77d9f98fe08054e846f2b9135a8d59ec372814b3353816751b1b0d641f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier#group-by-modifiers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/group-by-modifier.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks what `GROUP BY ... WITH ROLLUP` does in TiDB, how rollup grouping dimensions are formed, or what prerequisites are required for valid execution plans.
- Retrieval Keywords: GROUP BY Modifiers, WITH ROLLUP, GROUP BY a,b,c WITH ROLLUP, multidimensional descending grouping, N+1 groups, {a, b, c}, {a, b}, {a}, {}, Cube syntax, TiFlash MPP mode, TiFlash replicas, Scale out a TiFlash cluster
- Follow-up Guidance: The source also points to TiFlash deployment prerequisites and the related scale-out documentation for TiFlash clusters.
- Classification Note: This is reference content because it defines `WITH ROLLUP`, explains its grouping and aggregation behavior, notes that Cube syntax is not supported, and states the TiFlash MPP prerequisites.

## Official Source Content

# GROUP BY Modifiers

Starting from v7.4.0, the `GROUP BY` clause of TiDB supports the `WITH ROLLUP` modifier.

In the `GROUP BY` clause, you can specify one or more columns as a group list and append the `WITH ROLLUP` modifier after the list. Then, TiDB will conduct multidimensional descending grouping based on the columns in the group list and provide you with summary results for each group in the output.

- Grouping method:

    - The first grouping dimension includes all columns in the group list.
    - Subsequent grouping dimensions start from the right end of the grouping list and exclude one more column at a time to form new groups.

- Aggregation summaries: for each dimension, the query performs aggregation operations, and then aggregates the results of this dimension with the results of all previous dimensions. This means that you can get aggregated data at different dimensions, from detailed to overall.

With this grouping method, if there are `N` columns in the group list, TiDB aggregates the query results on `N+1` groups.

For example:

```sql
SELECT count(1) FROM t GROUP BY a,b,c WITH ROLLUP;
```

In this example, TiDB will aggregate the calculation results of `count(1)` on 4 groups (that is, `{a, b, c}`, `{a, b}`, `{a}`, and `{}`) and output the summary results for each group.

> **Note:**
>
> Currently, TiDB does not support the Cube syntax.
## Use cases

Aggregating and summarizing data from multiple columns is commonly used in OLAP (Online Analytical Processing) scenarios. By using the `WITH ROLLUP` modifier, you can get additional rows that display super summary information from other high-level dimensions in your aggregated results. Then, you can use the super summary information for advanced data analysis and report generation.
## Prerequisites

Currently, TiDB supports generating valid execution plans for the `WITH ROLLUP` syntax only in TiFlash MPP mode. Therefore, make sure that your TiDB cluster has been deployed with TiFlash nodes and that target fact tables are configured with TiFlash replicas properly.

For more information, see [Scale out a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-out-a-tiflash-cluster).
