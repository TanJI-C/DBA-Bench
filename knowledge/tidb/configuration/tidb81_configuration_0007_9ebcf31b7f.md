# Optimization rule blocklist overview and usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/blocklist-control-plan.md`
- Source Title: `The Blocklist of Optimization Rules and Expression Pushdown`
- Source Heading Path: `The Blocklist of Optimization Rules and Expression Pushdown | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of optimization rules | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of optimization rules > Important optimization rules | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of optimization rules > Disable optimization rules | The Blocklist of Optimization Rules and Expression Pushdown > The blocklist of optimization rules > Disable optimization rules > Usage`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `optimizer`, `blocklist`, `optimization-rules`, `rule-disable`, `admin-reload`, `privileges`, `join-reorder`, `pushdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0007_9ebcf31b7f`
- Source ID: `tidb-docs-8.1:blocklist-control-plan.md#the-blocklist-of-optimization-rules-and-expression-pushdown`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `be01c9dcaf8258277648cfb18cc89e83a145219d3aa176aba4b879de20b0e24f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/blocklist-control-plan#the-blocklist-of-optimization-rules-and-expression-pushdown
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/blocklist-control-plan.md

## Retrieval Guidance

- Use When: Use this chunk when searching how to disable or re-enable TiDB optimization rules through the optimizer rule blocklist and reload the change.
- Retrieval Keywords: mysql.opt_rule_blacklist, admin reload opt_rule_blacklist, join_reorder, topn_push_down, column_prune, predicate_push_down, partition_processor, aggregation_push_down, derive_topn_from_window, super privilege, disable optimization rules, re-enable optimization rule
- Follow-up Guidance: The source shows inserting rule names into `mysql.opt_rule_blacklist` and running `admin reload opt_rule_blacklist`, or deleting the names and reloading to re-enable them.
- Classification Note: This is classified as configuration because the content defines optimizer rule names and SQL-based blocklist settings in `mysql.opt_rule_blacklist` that control TiDB optimizer behavior.

## Official Source Content

# The Blocklist of Optimization Rules and Expression Pushdown

This document introduces how to use the blocklist of optimization rules and the blocklist of expression pushdown to control the behavior of TiDB.
## The blocklist of optimization rules

The blocklist of optimization rules is one way to tune optimization rules, mainly used to manually disable some optimization rules.
### Important optimization rules

|**Optimization Rule**|**Rule Name**|**Description**|
| :--- | :--- | :--- |
| Column pruning | column_prune | One operator will prune the column if it is not needed by the upper executor. |
| Decorrelate subquery | decorrelate | Tries to rewrite the correlated subquery to non-correlated join or aggregation. |
| Aggregation elimination | aggregation_eliminate | Tries to remove unnecessary aggregation operators from the execution plan. |
| Projection elimination | projection_eliminate | Removes unnecessary projection operators from the execution plan. |
| Max/Min elimination | max_min_eliminate | Rewrites some max/min functions in aggregation to the `order by` + `limit 1` form. |
| Predicate pushdown | predicate_push_down | Tries to push predicates down to the operator that is closer to the data source. |
| Outer join elimination | outer_join_eliminate | Tries to remove the unnecessary left join or right join from the execution plan. |
| Partition pruning | partition_processor | Prunes partitions which are rejected by the predicates and rewrite partitioned table query to the `UnionAll + Partition Datasource` form. |
| Aggregation pushdown | aggregation_push_down | Tries to push aggregations down to their children. |
| TopN pushdown | topn_push_down | Tries to push the TopN operator to the place closer to the data source. |
| Join reorder | join_reorder | Decides the order of multi-table joins. |
| Derive TopN or Limit from window functions | derive_topn_from_window | Derives the TopN or Limit operator from window functions. |
### Disable optimization rules

You can use the blocklist of optimization rules to disable some of them if some rules lead to a sub-optimal execution plan for special queries.
#### Usage

> **Note:**
>
> All the following operations need the `super privilege` privilege of the database. Each optimization rule has a name. For example, the name of column pruning is `column_prune`. The names of all optimization rules can be found in the second column of the table [Important Optimization Rules](#important-optimization-rules).

- If you want to disable some rules, write its name to the `mysql.opt_rule_blacklist` table. For example:

    ```sql
    INSERT INTO mysql.opt_rule_blacklist VALUES("join_reorder"), ("topn_push_down");
    ```

    Executing the following SQL statement can make the above operation take effect immediately. The effective range includes all old connections of the corresponding TiDB server:

    ```sql
    admin reload opt_rule_blacklist;
    ```

    > **Note:**
    >
    > `admin reload opt_rule_blacklist` only takes effect on the TiDB server where the above statement has been run. If you want all TiDB servers of the cluster to take effect, run this command on each TiDB server.

- If you want to re-enable a rule, delete the corresponding data in the table, and then run the `admin reload` statement:

    ```sql
    DELETE FROM mysql.opt_rule_blacklist WHERE name IN ("join_reorder", "topn_push_down");
    ```

    ```sql
    admin reload opt_rule_blacklist;
    ```
