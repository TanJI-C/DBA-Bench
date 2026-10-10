# TiDB cost model overview and version 2

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/cost-model.md`
- Source Title: `Cost Model`
- Source Heading Path: `Cost Model | Cost Model > Cost Model Version 2`
- Source Line Ranges: `5-51`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `cost-model`, `physical-optimization`, `query-plans`, `index-selection`, `operator-cost`, `system-variables`, `versioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0014_736b9a3692`
- Source ID: `tidb-docs-8.1:cost-model.md#cost-model`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `714d77c0a56e5d7617b82177a3e612bc8843a411ca2291f9f70eaf1d96839cf5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/cost-model#cost-model
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/cost-model.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how TiDB chooses indexes or physical operators during physical optimization, or asks about Cost Model Version 2 and the related system variable.
- Retrieval Keywords: Cost Model, Cost Model Version 2, physical optimization, choose an index and operator, minimum cost plan, HashJoin, IndexJoin, tidb_cost_model_version, access cost, execution cost, query plans, index selection
- Follow-up Guidance: The source notes that switching the cost model version might cause changes to query plans.
- Classification Note: This is classified as architecture because the content explains the TiDB cost model mechanism for physical optimization, including cost calculation, plan selection, and cost model versioning.

## Official Source Content

# Cost Model

TiDB uses a cost model to choose an index and operator during [physical optimization](https://docs.pingcap.com/tidb/stable/sql-physical-optimization). The process is illustrated in the following diagram:

![CostModel](/media/cost-model.png)

TiDB calculates the access cost of each index and the execution cost of each physical operator in plans (such as HashJoin and IndexJoin) and chooses the minimum cost plan.

The following is a simplified example to explain how the cost model works. Suppose that there is a table `t`:

```sql
mysql> SHOW CREATE TABLE t;
+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                                                                                                        |
+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t     | CREATE TABLE `t` (
  `a` int(11) DEFAULT NULL,
  `b` int(11) DEFAULT NULL,
  `c` int(11) DEFAULT NULL,
  KEY `b` (`b`),
  KEY `c` (`c`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin |
+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

When executing the `SELECT * FROM t WHERE b < 100 and c < 100` statement, suppose that TiDB estimates 20 rows meet the `b < 100` condition and 500 rows meet `c < 100`, and the length of `INT` type indexes is 8. Then TiDB calculates the cost for two indexes:

+ The cost of index `b` = row count of `b < 100` \* length of index `b` = 20 * 8 = 160
+ The cost of index `c` = row count of `c < 100` \* length of index `c` = 500 * 8 = 4000

Because the cost of index `b` is lower, TiDB chooses `b` as the index.

The preceding example is simplified and only used to explain the basic principle. In real SQL executions, the TiDB cost model is more complex.
## Cost Model Version 2

TiDB v6.2.0 introduces Cost Model Version 2, a new cost model.

Cost Model Version 2 provides a more accurate regression calibration of the cost formula, adjusts some of the cost formulas, and is more accurate than the previous version of the cost formula.

To switch the version of cost model, you can set the [`tidb_cost_model_version`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cost_model_version-new-in-v620) variable.

> **Note:**
>
> Switching the version of the cost model might cause changes to query plans.
