# Statistics types: histogram, Count-Min Sketch, and Top-N

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Types of statistics | Introduction to Statistics > Types of statistics > Histogram | Introduction to Statistics > Types of statistics > Count-Min Sketch | Introduction to Statistics > Types of statistics > Top-N`
- Source Line Ranges: `74-108`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `histogram`, `cmsketch`, `topn`, `selectivity`, `optimizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0058_ee17c8e022`
- Source ID: `tidb-docs-8.1:statistics.md#types-of-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d85ed2a271da836c880100e3c4cd977cb01c2ba3f0f2793f42a12ab549c691c6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#types-of-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when you need to identify which statistics type TiDB uses for range predicates, equality or IN predicates, or frequency/skew information.
- Retrieval Keywords: Types of statistics, Histogram, Count-Min Sketch, Top-N, equal-depth histogram, selectivity, interval predicate, range predicate, equal/IN predicate, Version 2 of statistics, EXPLAIN, WITH NUM TOPN, WITH NUM CMSKETCH DEPTH, WITH NUM CMSKETCH WIDTH
- Follow-up Guidance: See Manual Collection for the parameters that control bucket, Top-N, and CMSketch settings.
- Classification Note: This content classifies the main statistics structures used by the optimizer and explains their roles in selectivity estimation.

## Official Source Content

## Types of statistics

This section describes three types of statistics: histogram, Count-Min Sketch, and Top-N.
### Histogram

Histogram statistics are used by the optimizer to estimate selectivity of an interval or range predicate, and might also be used to determine the number of distinct values within a column for estimation of equal/IN predicates in Version 2 of statistics (refer to [Versions of Statistics](#versions-of-statistics)).

A histogram is an approximate representation of the distribution of data. It divides the entire range of values into a series of buckets, and uses simple data to describe each bucket, such as the number of values ​​falling in the bucket. In TiDB, an equal-depth histogram is created for the specific columns of each table. The equal-depth histogram can be used to estimate the interval query.

Here "equal-depth" means that the number of values ​​falling into each bucket is as equal as possible. For example, for a given set {1.6, 1.9, 1.9, 2.0, 2.4, 2.6, 2.7, 2.7, 2.8, 2.9, 3.4, 3.5}, you want to generate 4 buckets. The equal-depth histogram is as follows. It contains four buckets [1.6, 1.9], [2.0, 2.6], [2.7, 2.8], [2.9, 3.5]. The bucket depth is 3.

![Equal-depth Histogram Example](/media/statistics-1.png)

For details about the parameter that determines the upper limit to the number of histogram buckets, refer to [Manual Collection](#manual-collection). When the number of buckets is larger, the accuracy of the histogram is higher; however, higher accuracy is at the cost of the usage of memory resources. You can adjust this number appropriately according to the actual scenario.
### Count-Min Sketch

> **Note:**
>
> Count-Min Sketch is used in statistics Version 1 only for equal/IN predicate selectivity estimation. In Version 2, Histogram statistics are used instead due to challenges in managing Count-Min sketch to avoid collisions as discussed below.

Count-Min Sketch is a hash structure. When processing an equivalence query such as `a = 1` or an `IN` query (for example, `a IN (1, 2, 3)`), TiDB uses this data structure for estimation.

A hash collision might occur since Count-Min Sketch is a hash structure. In the [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) statement, if the estimate of the equivalent query deviates greatly from the actual value, it can be considered that a larger value and a smaller value have been hashed together. In this case, you can take one of the following ways to avoid the hash collision:

- Modify the `WITH NUM TOPN` parameter. TiDB stores the high-frequency (top x) data separately, with the other data stored in Count-Min Sketch. Therefore, to prevent a larger value and a smaller value from being hashed together, you can increase the value of `WITH NUM TOPN`. In TiDB, its default value is 20. The maximum value is 1024. For more information about this parameter, see [Manual collection](#manual-collection).
- Modify two parameters `WITH NUM CMSKETCH DEPTH` and `WITH NUM CMSKETCH WIDTH`. Both affect the number of hash buckets and the collision probability. You can increase the values of the two parameters appropriately according to the actual scenario to reduce the probability of hash collision, but at the cost of higher memory usage of statistics. In TiDB, the default value of `WITH NUM CMSKETCH DEPTH` is 5, and the default value of `WITH NUM CMSKETCH WIDTH` is 2048. For more information about the two parameters, see [Manual collection](#manual-collection).
### Top-N

Top-N values are values with the top N occurrences in a column or index. Top-N statistics are often referred to as frequency statistics or data skew.

TiDB records the values and occurrences of Top-N values. Here `N` is controlled by the `WITH NUM TOPN` parameter. The default value is 20, meaning the top 20 most frequent values are collected. The maximum value is 1024. For details about the parameter, see [Manual collection](#manual-collection).
