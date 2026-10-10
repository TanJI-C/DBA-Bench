# Use statement summary to find queries for binding

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > Utilize the statement summary table to obtain queries that need to be bound`
- Source Line Ranges: `480-525`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statement-summary`, `sql-binding`, `plan-digest`, `historical-plan`, `query-selection`, `latency`, `plan-stability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0163_904a9e3aff`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#utilize-the-statement-summary-table-to-obtain-queries-that-need-to-be-bound`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `393edd8a19d7e3ed572dbd1c50d1366ec3169e59435a0bdba9ffdff85f7ddf27`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#utilize-the-statement-summary-table-to-obtain-queries-that-need-to-be-bound
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when identifying high-frequency unstable `SELECT` queries from statement summary tables and deriving `plan_digest` values for historical SQL bindings.
- Retrieval Keywords: statement summary, statement summary tables, INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY, INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY_HISTORY, plan_digest, digest, avg_latency, plan_in_binding = 0, stmt_type = 'Select', COUNT(DISTINCT(stmts.plan_digest)) > 1, SUM(exec_count) > 10, summary_begin_time > DATE_SUB(NOW(), interval 14 day), create global binding from history using plan digest, binding_stmt, historical execution plans
- Follow-up Guidance: The source states that after filtering qualifying queries, you can directly execute the statements in the `binding_stmt` column to create bindings.
- Classification Note: This is classified as performance because the content uses statement summary latency, execution counts, and multiple-plan detection to select queries for binding to faster historical plans.

## Official Source Content

## Utilize the statement summary table to obtain queries that need to be bound

[Statement summary](https://docs.pingcap.com/tidb/stable/statement-summary-tables) records recent SQL execution information, such as latency, execution times, and corresponding query plans. You can query statement summary tables to get qualified `plan_digest`, and then [create bindings according to these historical execution plans](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-historical-execution-plan).

The following example queries `SELECT` statements that have been executed more than 10 times in the past two weeks, and have multiple execution plans without SQL binding. It sorts the queries by the execution times, and binds the top 100 queries to their fastest plans.

```sql
WITH stmts AS (                                                -- Gets all information
  SELECT * FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY
  UNION ALL
  SELECT * FROM INFORMATION_SCHEMA.CLUSTER_STATEMENTS_SUMMARY_HISTORY 
),
best_plans AS (
  SELECT plan_digest, `digest`, avg_latency, 
  CONCAT('create global binding from history using plan digest "', plan_digest, '"') as binding_stmt 
  FROM stmts t1
  WHERE avg_latency = (SELECT min(avg_latency) FROM stmts t2   -- The plan with the lowest query latency
                       WHERE t2.`digest` = t1.`digest`)
)

SELECT any_value(digest_text) as query, 
       SUM(exec_count) as exec_count, 
       plan_hint, binding_stmt
FROM stmts, best_plans
WHERE stmts.`digest` = best_plans.`digest`
  AND summary_begin_time > DATE_SUB(NOW(), interval 14 day)    -- Executed in the past 2 weeks
  AND stmt_type = 'Select'                                     -- Only consider select statements
  AND schema_name NOT IN ('INFORMATION_SCHEMA', 'mysql')       -- Not an internal query
  AND plan_in_binding = 0                                      -- No binding yet
GROUP BY stmts.`digest`
  HAVING COUNT(DISTINCT(stmts.plan_digest)) > 1                -- This query is unstable. It has more than 1 plan.
         AND SUM(exec_count) > 10                              -- High-frequency, and has been executed more than 10 times.
ORDER BY SUM(exec_count) DESC LIMIT 100;                       -- Top 100 high-frequency queries.
```

By applying certain filtering conditions to obtain queries that meet the criteria, you can then directly execute the statements in the corresponding `binding_stmt` column to create bindings.

```
+---------------------------------------------+------------+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| query                                       | exec_count | plan_hint                                                                   | binding_stmt                                                                                                            |
+---------------------------------------------+------------+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
| select * from `t` where `a` = ? and `b` = ? |        401 | use_index(@`sel_1` `test`.`t` `a`), no_order_index(@`sel_1` `test`.`t` `a`) | create global binding from history using plan digest "0d6e97fb1191bbd08dddefa7bd007ec0c422b1416b152662768f43e64a9958a6" |
| select * from `t` where `b` = ? and `c` = ? |        104 | use_index(@`sel_1` `test`.`t` `b`), no_order_index(@`sel_1` `test`.`t` `b`) | create global binding from history using plan digest "80c2aa0aa7e6d3205755823aa8c6165092c8521fb74c06a9204b8d35fc037dd9" |
+---------------------------------------------+------------+-----------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------------------------+
```
