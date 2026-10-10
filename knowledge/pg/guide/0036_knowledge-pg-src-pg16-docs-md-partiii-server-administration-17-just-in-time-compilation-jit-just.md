# When to JIT?

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/17_just-in-time_compilation_(jit).md`
- Source Title: `Just-in-Time Compilation (JIT)`
- Source Heading Path: `Just-in-Time Compilation (JIT) > When to JIT?`
- Source Line Ranges: `59-136`
- Chunk ID: `pg16_guide_0036_a36a908365`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b34d0800d2658d9c01c656b02dab86d7a5d33a6abd5d5d25218be18cee4c292f`

## Retrieval Guidance

- Use When: 诊断 JIT 是否启用、为何没启用或短查询因 JIT 变慢。
- Retrieval Keywords: When to JIT, jit_above_cost, jit_inline_above_cost, jit_optimize_above_cost, EXPLAIN ANALYZE JIT, prepared statements
- Follow-up Guidance: 比较计划 cost、JIT Timing 和 prepare-time 参数值。
- Classification Note: 说明用 planner cost、JIT 阈值和 EXPLAIN ANALYZE 判断是否使用/值得使用 JIT。

## Official Source Content

## When to JIT?

JIT compilation is beneficial primarily for long-running
CPU-bound queries. Frequently these will be analytical queries.  For short
queries the added overhead of performing JIT compilation
will often be higher than the time it can save.

To determine whether JIT compilation should be used,
the total estimated cost of a query (see
[planner-stats-details](#planner-stats-details) and
[runtime-config-query-constants](#runtime-config-query-constants)) is used.
The estimated cost of the query will be compared with the setting of [guc-jit-above-cost](#guc-jit-above-cost). If the cost is higher,
JIT compilation will be performed.
Two further decisions are then needed.
Firstly, if the estimated cost is more
than the setting of [guc-jit-inline-above-cost](#guc-jit-inline-above-cost), short
functions and operators used in the query will be inlined.
Secondly, if the estimated cost is more than the setting of [guc-jit-optimize-above-cost](#guc-jit-optimize-above-cost), expensive optimizations are
applied to improve the generated code.
Each of these options increases the JIT compilation
overhead, but can reduce query execution time considerably.

These cost-based decisions will be made at plan time, not execution
time. This means that when prepared statements are in use, and a generic
plan is used (see [sql-prepare](#sql-prepare)), the values of the
configuration parameters in effect at prepare time control the decisions,
not the settings at execution time.

> **Note:**

> If [guc-jit](#guc-jit) is set to `off`, or if no
> JIT implementation is available (for example because
> the server was compiled without `--with-llvm`),
> JIT will not be performed, even if it would be
> beneficial based on the above criteria.  Setting [guc-jit](#guc-jit)
> to `off` has effects at both plan and execution time.
>

[sql-explain](#sql-explain) can be used to see whether
JIT is used or not.  As an example, here is a query that
is not using JIT:

```
=# EXPLAIN ANALYZE SELECT SUM(relpages) FROM pg_class;
QUERY PLAN
-------------------------------------------------------------------------------------------------------------
Aggregate  (cost=16.27..16.29 rows=1 width=8) (actual time=0.303..0.303 rows=1 loops=1)
->  Seq Scan on pg_class  (cost=0.00..15.42 rows=342 width=4) (actual time=0.017..0.111 rows=356 loops=1)
Planning Time: 0.116 ms
Execution Time: 0.365 ms
(4 rows)
```

Given the cost of the plan, it is entirely reasonable that no
JIT was used; the cost of JIT would
have been bigger than the potential savings. Adjusting the cost limits
will lead to JIT use:

```
=# SET jit_above_cost = 10;
SET
=# EXPLAIN ANALYZE SELECT SUM(relpages) FROM pg_class;
QUERY PLAN
-------------------------------------------------------------------------------------------------------------
Aggregate  (cost=16.27..16.29 rows=1 width=8) (actual time=6.049..6.049 rows=1 loops=1)
->  Seq Scan on pg_class  (cost=0.00..15.42 rows=342 width=4) (actual time=0.019..0.052 rows=356 loops=1)
Planning Time: 0.133 ms
JIT:
Functions: 3
Options: Inlining false, Optimization false, Expressions true, Deforming true
Timing: Generation 1.259 ms, Inlining 0.000 ms, Optimization 0.797 ms, Emission 5.048 ms, Total 7.104 ms
Execution Time: 7.416 ms
```

As visible here, JIT was used, but inlining and
expensive optimization were not. If [guc-jit-inline-above-cost](#guc-jit-inline-above-cost) or [guc-jit-optimize-above-cost](#guc-jit-optimize-above-cost) were also lowered,
that would change.
