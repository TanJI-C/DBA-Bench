# Wrong index troubleshooting and causes

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/wrong-index-solution.md`
- Source Title: `Wrong Index Solution`
- Source Heading Path: `Wrong Index Solution | Wrong Index Solution > Statistics health | Wrong Index Solution > Statistics health > Low health state | Wrong Index Solution > Statistics health > Near 100% health state | Wrong Index Solution > Statistics health > Other situations | Wrong Index Solution > Statistics mismatch | Wrong Index Solution > Cost information | Wrong Index Solution > Engine selection | Wrong Index Solution > Function pushdown | Wrong Index Solution > See also`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`
- Topic Tags: `wrong-index`, `query-performance`, `optimizer`, `statistics-health`, `analyze`, `statistics-mismatch`, `cost-estimation`, `explain-analyze`, `engine-selection`, `function-pushdown`, `optimizer-hints`, `sql-plan-management`, `index-design`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0143_1eb4d97ce0`
- Source ID: `tidb-docs-8.1:wrong-index-solution.md#wrong-index-solution`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `898f4db026a04c1d733da511929cc57b69285fafb7bbb68f7bce943921c952c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/wrong-index-solution#wrong-index-solution
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/wrong-index-solution.md

## Retrieval Guidance

- Use When: Use this content when troubleshooting a query where TiDB appears to choose the wrong index and you need causes and related diagnostic areas such as statistics health, statistics mismatch, cost information, engine selection, or function pushdown.
- Retrieval Keywords: Wrong Index Solution, wrong index, optimizer chooses unexpected index, outdated statistics, statistics health, ANALYZE, statistics mismatch, cost estimation, EXPLAIN FORMAT=verbose, EXPLAIN ANALYZE FORMAT=verbose, Count-Min Sketch, USE_INDEX, use index, SQL Plan Management, engine selection, engine isolation, TiKV, TiFlash, function pushdown, ADD INDEX
- Follow-up Guidance: The source points to checking table health state, using `EXPLAIN` or `EXPLAIN ANALYZE` with `FORMAT=verbose`, considering `USE_INDEX` or SQL Plan Management, reviewing engine isolation, and checking pushdown support references.
- Classification Note: This is classified as diagnosis because the official content explains why TiDB might choose an unexpected index and groups the investigation by statistics, cost, engine choice, and pushdown behavior.

## Official Source Content

# Wrong Index Solution

If you find that the execution speed of some query does not reach the expectation, the optimizer might choose the wrong index to run the query.

There are multiple reasons why the optimizer might choose an unexpected index:

- **Outdated statistics**: the optimizer relies on statistics to estimate query costs. If the statistics are outdated, the optimizer might make suboptimal choices.
- **Statistics mismatch**: even if statistics are current, they might not accurately reflect the data distribution, leading to incorrect cost estimations.
- **Incorrect cost calculation**: the optimizer might miscalculate the cost of using an index due to complex query structures or data distribution.
- **Inappropriate engine selection**: in some cases, the optimizer might select a storage engine that is not optimal for the query.
- **Function pushdown limitations**: certain functions or operations might not be pushed down to storage engines, potentially affecting query performance.
## Statistics health

You can first view the [health state of tables](https://docs.pingcap.com/tidb/stable/statistics#health-state-of-tables) in the statistics, and then solve this issue according to the different health states.
### Low health state

The low health state means TiDB has not performed the`ANALYZE` statement for a long time. You can update the statistics by running the `ANALYZE` command. After the update, if the optimizer still uses the wrong index, refer to the next section.
### Near 100% health state

The near 100% health state suggests that the `ANALYZE` statement is just completed or was completed a short time ago. In this case, the wrong index issue might be related to TiDB's estimation logic for the number of rows.

For equivalence queries, the cause might be [Count-Min Sketch](https://docs.pingcap.com/tidb/stable/statistics#count-min-sketch). You can check whether Count-Min Sketch is the cause and take corresponding solutions.

If the cause above does not apply to your problem, you can force-select indexes by using the `USE_INDEX` or `use index` optimizer hint (see [USE_INDEX](https://docs.pingcap.com/tidb/stable/optimizer-hints#use_indext1_name-idx1_name--idx2_name-) for details). Also, you can change the query behavior by using [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management) in a non-intrusive way.
### Other situations

Apart from the aforementioned situations, the wrong index issue might also be caused by data updates which renders all the indexes no longer applicable. In such cases, you need to perform analysis on the conditions and data distribution to see whether new indexes can speed up the query. If so, you can add new indexes by running the [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) command.
## Statistics mismatch

When data distribution is highly skewed, the statistics might not accurately reflect the actual data. In such cases, try configuring the options of the [`ANALYZE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table) statement. It might help improve the accuracy of statistics and better match the index.

For example, suppose you have an `orders` table with an index on the `customer_id` column, and more than 50% of the orders share the same `customer_id`. In this case, the statistics might not represent the data distribution well, affecting query performance.
## Cost information

To view detailed information on execution costs, you can execute the [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) and [`EXPLAIN ANALYZE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain-analyze) statements with the `FORMAT=verbose` option. According to the information, you can see cost differences between different execution paths.
## Engine selection

By default, TiDB chooses TiKV or TiFlash for table access based on cost estimation. You can experiment with different engines for the same query by applying engine isolation.

For more information, see [Engine isolation](https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash#engine-isolation).
## Function pushdown

To enhance query performance, TiDB can push down certain functions to the TiKV or TiFlash storage engine for execution. However, some functions do not support pushdown, which might limit available execution plans and potentially affect query performance.

For expressions that support pushdown, see [TiKV supported pushdown calculations](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down) and [TiFlash supported pushdown calculations](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations). 

Note that you can also disable the pushdown of specific expressions. For more information, see [Blocklist of optimization rules and expression pushdown](https://docs.pingcap.com/tidb/stable/blocklist-control-plan).
## See also

- [Statistics](https://docs.pingcap.com/tidb/stable/statistics)
- [Index selection](https://docs.pingcap.com/tidb/stable/choose-index)
- [Optimizer hints](https://docs.pingcap.com/tidb/stable/optimizer-hints)
- [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management)
