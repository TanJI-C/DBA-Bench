# extended statistics examples; Multivariate N-Distinct Counts; Multivariate MCV Lists

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/11_performance_tips.md`
- Source Title: `Performance Tips`
- Source Heading Path: `Performance Tips > Using EXPLAIN > extended statistics examples; Multivariate N-Distinct Counts; Multivariate MCV Lists`
- Source Line Ranges: `8-621`
- Chunk ID: `pg16_solution_0123_fb11206dcd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e72ab0d4553dc43f564589052a6884132527105d77eed228b548ee268c954853`

## Retrieval Guidance

- Use When: Root cause is poor planner estimates for correlated columns, multi-column GROUP BY, or multi-column predicates.
- Retrieval Keywords: CREATE STATISTICS, dependencies, ndistinct, mcv, ANALYZE, extended statistics, correlated columns, misestimate
- Follow-up Guidance: Inspect pg_statistic_ext_data or pg_mcv_list_items and verify the changed plan after ANALYZE.
- Classification Note: Shows CREATE STATISTICS with dependencies, ndistinct, and mcv plus ANALYZE to fix planner misestimates for correlated columns and multi-column grouping or filtering.

## Official Source Content

## Using `EXPLAIN`

PostgreSQL devises a *query
plan* for each query it receives.  Choosing the right
plan to match the query structure and the properties of the data
is absolutely critical for good performance, so the system includes
a complex *planner* that tries to choose good plans.
You can use the [`EXPLAIN`](#sql-explain) command
to see what query plan the planner creates for any query.
Plan-reading is an art that requires some experience to master,
but this section attempts to cover the basics.

Examples in this section are drawn from the regression test database
after doing a `VACUUM ANALYZE`, using 9.3 development sources.
You should be able to get similar results if you try the examples
yourself, but your estimated costs and row counts might vary slightly
because `ANALYZE`'s statistics are random samples rather
than exact, and because costs are inherently somewhat platform-dependent.

The examples use `EXPLAIN`'s default "text" output
format, which is compact and convenient for humans to read.
If you want to feed `EXPLAIN`'s output to a program for further
analysis, you should use one of its machine-readable output formats
(XML, JSON, or YAML) instead.

### `EXPLAIN` Basics

The structure of a query plan is a tree of *plan nodes*.
Nodes at the bottom level of the tree are scan nodes: they return raw rows
from a table.  There are different types of scan nodes for different
table access methods: sequential scans, index scans, and bitmap index
scans.  There are also non-table row sources, such as `VALUES`
clauses and set-returning functions in `FROM`, which have their
own scan node types.
If the query requires joining, aggregation, sorting, or other
operations on the raw rows, then there will be additional nodes
above the scan nodes to perform these operations.  Again,
there is usually more than one possible way to do these operations,
so different node types can appear here too.  The output
of `EXPLAIN` has one line for each node in the plan
tree, showing the basic node type plus the cost estimates that the planner
made for the execution of that plan node.  Additional lines might appear,
indented from the node's summary line,
to show additional properties of the node.
The very first line (the summary line for the topmost
node) has the estimated total execution cost for the plan; it is this
number that the planner seeks to minimize.

Here is a trivial example, just to show what the output looks like:

```
EXPLAIN SELECT * FROM tenk1;

QUERY PLAN
-------------------------------------------------------------
Seq Scan on tenk1  (cost=0.00..458.00 rows=10000 width=244)
```

Since this query has no `WHERE` clause, it must scan all the
rows of the table, so the planner has chosen to use a simple sequential
scan plan.  The numbers that are quoted in parentheses are (left
to right):

- Estimated start-up cost.  This is the time expended before the output
phase can begin, e.g., time to do the sorting in a sort node.
- Estimated total cost.  This is stated on the assumption that the plan
node is run to completion, i.e., all available rows are retrieved.
In practice a node's parent node might stop short of reading all
available rows (see the `LIMIT` example below).
- Estimated number of rows output by this plan node.  Again, the node
is assumed to be run to completion.
- Estimated average width of rows output by this plan node (in bytes).

The costs are measured in arbitrary units determined by the planner's
cost parameters (see [runtime-config-query-constants](#runtime-config-query-constants)).
Traditional practice is to measure the costs in units of disk page
fetches; that is, [guc-seq-page-cost](#guc-seq-page-cost) is conventionally
set to `1.0` and the other cost parameters are set relative
to that.  The examples in this section are run with the default cost
parameters.

It's important to understand that the cost of an upper-level node includes
the cost of all its child nodes.  It's also important to realize that
the cost only reflects things that the planner cares about.
In particular, the cost does not consider the time spent transmitting
result rows to the client, which could be an important
factor in the real elapsed time; but the planner ignores it because
it cannot change it by altering the plan.  (Every correct plan will
output the same row set, we trust.)

The `rows` value is a little tricky because it is
not the number of rows processed or scanned by the
plan node, but rather the number emitted by the node.  This is often
less than the number scanned, as a result of filtering by any
`WHERE`-clause conditions that are being applied at the node.
Ideally the top-level rows estimate will approximate the number of rows
actually returned, updated, or deleted by the query.

Returning to our example:

```
EXPLAIN SELECT * FROM tenk1;

QUERY PLAN
-------------------------------------------------------------
Seq Scan on tenk1  (cost=0.00..458.00 rows=10000 width=244)
```

These numbers are derived very straightforwardly.  If you do:

```
SELECT relpages, reltuples FROM pg_class WHERE relname = 'tenk1';
```

you will find that tenk1 has 358 disk
pages and 10000 rows.  The estimated cost is computed as (disk pages read *
[guc-seq-page-cost](#guc-seq-page-cost)) + (rows scanned *
[guc-cpu-tuple-cost](#guc-cpu-tuple-cost)).  By default,
`seq_page_cost` is 1.0 and `cpu_tuple_cost` is 0.01,
so the estimated cost is (358 * 1.0) + (10000 * 0.01) = 458.

Now let's modify the query to add a `WHERE` condition:

```
EXPLAIN SELECT * FROM tenk1 WHERE unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0)
Index Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0)
Index Cond: (unique1   Seq Scan on tenk1  (cost=0.00..445.00 rows=10000 width=244)
```

If a part of the plan guarantees an ordering on a prefix of the
required sort keys, then the planner may instead decide to use an
`incremental sort` step:

```
EXPLAIN SELECT * FROM tenk1 ORDER BY four, ten LIMIT 100;
QUERY PLAN
------------------------------------------------------------------------------------------------------
Limit  (cost=521.06..538.05 rows=100 width=244)
->  Incremental Sort  (cost=521.06..2220.95 rows=10000 width=244)
Sort Key: four, ten
Presorted Key: four
->  Index Scan using index_tenk1_on_four on tenk1  (cost=0.29..1510.08 rows=10000 width=244)
```

Compared to regular sorts, sorting incrementally allows returning tuples
before the entire result set has been sorted, which particularly enables
optimizations with `LIMIT` queries.  It may also reduce
memory usage and the likelihood of spilling sorts to disk, but it comes at
the cost of the increased overhead of splitting the result set into multiple
sorting batches.

If there are separate indexes on several of the columns referenced
in `WHERE`, the planner might choose to use an AND or OR
combination of the indexes:

```
EXPLAIN SELECT * FROM tenk1 WHERE unique1  9000;

QUERY PLAN
-------------------------------------------------------------------------------------
Bitmap Heap Scan on tenk1  (cost=25.08..60.21 rows=10 width=244)
Recheck Cond: ((unique1  9000))
->  BitmapAnd  (cost=25.08..25.08 rows=10 width=0)
->  Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0)
Index Cond: (unique1   Bitmap Index Scan on tenk1_unique2  (cost=0.00..19.78 rows=999 width=0)
Index Cond: (unique2 > 9000)
```

But this requires visiting both indexes, so it's not necessarily a win
compared to using just one index and treating the other condition as
a filter.  If you vary the ranges involved you'll see the plan change
accordingly.

Here is an example showing the effects of `LIMIT`:

```
EXPLAIN SELECT * FROM tenk1 WHERE unique1  9000 LIMIT 2;

QUERY PLAN
-------------------------------------------------------------------------------------
Limit  (cost=0.29..14.48 rows=2 width=244)
->  Index Scan using tenk1_unique2 on tenk1  (cost=0.29..71.27 rows=10 width=244)
Index Cond: (unique2 > 9000)
Filter: (unique1   Bitmap Heap Scan on tenk1 t1  (cost=4.36..39.47 rows=10 width=244)
Recheck Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..4.36 rows=10 width=0)
Index Cond: (unique1   Index Scan using tenk2_unique2 on tenk2 t2  (cost=0.29..7.91 rows=1 width=244)
Index Cond: (unique2 = t1.unique2)
```

In this plan, we have a nested-loop join node with two table scans as
inputs, or children.  The indentation of the node summary lines reflects
the plan tree structure.  The join's first, or "outer", child
is a bitmap scan similar to those we saw before.  Its cost and row count
are the same as we'd get from `SELECT ... WHERE unique1 < 10`
because we are
applying the `WHERE` clause `unique1 < 10`
at that node.
The `t1.unique2 = t2.unique2` clause is not relevant yet,
so it doesn't affect the row count of the outer scan.  The nested-loop
join node will run its second,
or "inner" child once for each row obtained from the outer child.
Column values from the current outer row can be plugged into the inner
scan; here, the `t1.unique2` value from the outer row is available,
so we get a plan and costs similar to what we saw above for a simple
`SELECT ... WHERE t2.unique2 = `constant`` case.
(The estimated cost is actually a bit lower than what was seen above,
as a result of caching that's expected to occur during the repeated
index scans on `t2`.)  The
costs of the loop node are then set on the basis of the cost of the outer
scan, plus one repetition of the inner scan for each outer row (10 * 7.91,
here), plus a little CPU time for join processing.

In this example the join's output row count is the same as the product
of the two scans' row counts, but that's not true in all cases because
there can be additional `WHERE` clauses that mention both tables
and so can only be applied at the join point, not to either input scan.
Here's an example:

```
EXPLAIN SELECT *
FROM tenk1 t1, tenk2 t2
WHERE t1.unique1   Bitmap Heap Scan on tenk1 t1  (cost=4.36..39.47 rows=10 width=244)
Recheck Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..4.36 rows=10 width=0)
Index Cond: (unique1   Materialize  (cost=0.29..8.51 rows=10 width=244)
->  Index Scan using tenk2_unique2 on tenk2 t2  (cost=0.29..8.46 rows=10 width=244)
Index Cond: (unique2   Seq Scan on tenk2 t2  (cost=0.00..445.00 rows=10000 width=244)
->  Hash  (cost=229.20..229.20 rows=101 width=244)
->  Bitmap Heap Scan on tenk1 t1  (cost=5.07..229.20 rows=101 width=244)
Recheck Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0)
Index Cond: (unique1   Index Scan using tenk1_unique2 on tenk1 t1  (cost=0.29..656.28 rows=101 width=244)
Filter: (unique1   Sort  (cost=197.83..200.33 rows=1000 width=244)
Sort Key: t2.unique2
->  Seq Scan on onek t2  (cost=0.00..148.00 rows=1000 width=244)
```

Merge join requires its input data to be sorted on the join keys.  In this
plan the `tenk1` data is sorted by using an index scan to visit
the rows in the correct order, but a sequential scan and sort is preferred
for `onek`, because there are many more rows to be visited in
that table.
(Sequential-scan-and-sort frequently beats an index scan for sorting many rows,
because of the nonsequential disk access required by the index scan.)

One way to look at variant plans is to force the planner to disregard
whatever strategy it thought was the cheapest, using the enable/disable
flags described in [runtime-config-query-enable](#runtime-config-query-enable).
(This is a crude tool, but useful.  See
also [explicit-joins](#explicit-joins).)
For example, if we're unconvinced that sequential-scan-and-sort is the best way to
deal with table `onek` in the previous example, we could try

```
SET enable_sort = off;

EXPLAIN SELECT *
FROM tenk1 t1, onek t2
WHERE t1.unique1   Index Scan using tenk1_unique2 on tenk1 t1  (cost=0.29..656.28 rows=101 width=244)
Filter: (unique1   Index Scan using onek_unique2 on onek t2  (cost=0.28..224.79 rows=1000 width=244)
```

which shows that the planner thinks that sorting `onek` by
index-scanning is about 12% more expensive than sequential-scan-and-sort.
Of course, the next question is whether it's right about that.
We can investigate that using `EXPLAIN ANALYZE`, as discussed
below.

### `EXPLAIN ANALYZE`

It is possible to check the accuracy of the planner's estimates
by using `EXPLAIN`'s `ANALYZE` option.  With this
option, `EXPLAIN` actually executes the query, and then displays
the true row counts and true run time accumulated within each plan node,
along with the same estimates that a plain `EXPLAIN`
shows.  For example, we might get a result like this:

```
EXPLAIN ANALYZE SELECT *
FROM tenk1 t1, tenk2 t2
WHERE t1.unique1   Bitmap Heap Scan on tenk1 t1  (cost=4.36..39.47 rows=10 width=244) (actual time=0.057..0.121 rows=10 loops=1)
Recheck Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..4.36 rows=10 width=0) (actual time=0.024..0.024 rows=10 loops=1)
Index Cond: (unique1   Index Scan using tenk2_unique2 on tenk2 t2  (cost=0.29..7.91 rows=1 width=244) (actual time=0.021..0.022 rows=1 loops=10)
Index Cond: (unique2 = t1.unique2)
Planning time: 0.181 ms
Execution time: 0.501 ms
```

Note that the "actual time" values are in milliseconds of
real time, whereas the `cost` estimates are expressed in
arbitrary units; so they are unlikely to match up.
The thing that's usually most important to look for is whether the
estimated row counts are reasonably close to reality.  In this example
the estimates were all dead-on, but that's quite unusual in practice.

In some query plans, it is possible for a subplan node to be executed more
than once.  For example, the inner index scan will be executed once per
outer row in the above nested-loop plan.  In such cases, the
`loops` value reports the
total number of executions of the node, and the actual time and rows
values shown are averages per-execution.  This is done to make the numbers
comparable with the way that the cost estimates are shown.  Multiply by
the `loops` value to get the total time actually spent in
the node.  In the above example, we spent a total of 0.220 milliseconds
executing the index scans on `tenk2`.

In some cases `EXPLAIN ANALYZE` shows additional execution
statistics beyond the plan node execution times and row counts.
For example, Sort and Hash nodes provide extra information:

```
EXPLAIN ANALYZE SELECT *
FROM tenk1 t1, tenk2 t2
WHERE t1.unique1   Hash Join  (cost=230.47..713.98 rows=101 width=488) (actual time=0.711..7.427 rows=100 loops=1)
Hash Cond: (t2.unique2 = t1.unique2)
->  Seq Scan on tenk2 t2  (cost=0.00..445.00 rows=10000 width=244) (actual time=0.007..2.583 rows=10000 loops=1)
->  Hash  (cost=229.20..229.20 rows=101 width=244) (actual time=0.659..0.659 rows=100 loops=1)
Buckets: 1024  Batches: 1  Memory Usage: 28kB
->  Bitmap Heap Scan on tenk1 t1  (cost=5.07..229.20 rows=101 width=244) (actual time=0.080..0.526 rows=100 loops=1)
Recheck Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0) (actual time=0.049..0.049 rows=100 loops=1)
Index Cond: (unique1  polygon '(0.5,2.0)';

QUERY PLAN
------------------------------------------------------------------------------------------------------
Seq Scan on polygon_tbl  (cost=0.00..1.05 rows=1 width=32) (actual time=0.044..0.044 rows=0 loops=1)
Filter: (f1 @> '((0.5,2))'::polygon)
Rows Removed by Filter: 4
Planning time: 0.040 ms
Execution time: 0.083 ms
```

The planner thinks (quite correctly) that this sample table is too small
to bother with an index scan, so we have a plain sequential scan in which
all the rows got rejected by the filter condition.  But if we force an
index scan to be used, we see:

```
SET enable_seqscan TO off;

EXPLAIN ANALYZE SELECT * FROM polygon_tbl WHERE f1 @> polygon '(0.5,2.0)';

QUERY PLAN
--------------------------------------------------------------------------------------------------------------------------
Index Scan using gpolygonind on polygon_tbl  (cost=0.13..8.15 rows=1 width=32) (actual time=0.062..0.062 rows=0 loops=1)
Index Cond: (f1 @> '((0.5,2))'::polygon)
Rows Removed by Index Recheck: 1
Planning time: 0.034 ms
Execution time: 0.144 ms
```

Here we can see that the index returned one candidate row, which was
then rejected by a recheck of the index condition.  This happens because a
GiST index is "lossy" for polygon containment tests: it actually
returns the rows with polygons that overlap the target, and then we have
to do the exact containment test on those rows.

`EXPLAIN` has a `BUFFERS` option that can be used with
`ANALYZE` to get even more run time statistics:

```
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM tenk1 WHERE unique1  9000;

QUERY PLAN
---------------------------------------------------------------------------------------------------------------------------------
Bitmap Heap Scan on tenk1  (cost=25.08..60.21 rows=10 width=244) (actual time=0.323..0.342 rows=10 loops=1)
Recheck Cond: ((unique1  9000))
Buffers: shared hit=15
->  BitmapAnd  (cost=25.08..25.08 rows=10 width=0) (actual time=0.309..0.309 rows=0 loops=1)
Buffers: shared hit=7
->  Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.04 rows=101 width=0) (actual time=0.043..0.043 rows=100 loops=1)
Index Cond: (unique1   Bitmap Index Scan on tenk1_unique2  (cost=0.00..19.78 rows=999 width=0) (actual time=0.227..0.227 rows=999 loops=1)
Index Cond: (unique2 > 9000)
Buffers: shared hit=5
Planning time: 0.088 ms
Execution time: 0.423 ms
```

The numbers provided by `BUFFERS` help to identify which parts
of the query are the most I/O-intensive.

Keep in mind that because `EXPLAIN ANALYZE` actually
runs the query, any side-effects will happen as usual, even though
whatever results the query might output are discarded in favor of
printing the `EXPLAIN` data.  If you want to analyze a
data-modifying query without changing your tables, you can
roll the command back afterwards, for example:

```
BEGIN;

EXPLAIN ANALYZE UPDATE tenk1 SET hundred = hundred + 1 WHERE unique1   Bitmap Heap Scan on tenk1  (cost=5.08..230.08 rows=102 width=10) (actual time=0.069..0.513 rows=100 loops=1)
Recheck Cond: (unique1   Bitmap Index Scan on tenk1_unique1  (cost=0.00..5.05 rows=102 width=0) (actual time=0.036..0.037 rows=300 loops=1)
Index Cond: (unique1   Result  (cost=0.00..24.59 rows=4 width=14)
->  Append  (cost=0.00..24.54 rows=4 width=14)
->  Seq Scan on parent parent_1  (cost=0.00..0.00 rows=1 width=14)
Filter: (f1 = 101)
->  Index Scan using child1_pkey on child1 parent_2  (cost=0.15..8.17 rows=1 width=14)
Index Cond: (f1 = 101)
->  Index Scan using child2_pkey on child2 parent_3  (cost=0.15..8.17 rows=1 width=14)
Index Cond: (f1 = 101)
->  Index Scan using child3_pkey on child3 parent_4  (cost=0.15..8.17 rows=1 width=14)
Index Cond: (f1 = 101)
```

In this example the Update node needs to consider three child tables as
well as the originally-mentioned parent table.  So there are four input
scanning subplans, one per table.  For clarity, the Update node is
annotated to show the specific target tables that will be updated, in the
same order as the corresponding subplans.

The `Planning time` shown by `EXPLAIN
ANALYZE` is the time it took to generate the query plan from the
parsed query and optimize it. It does not include parsing or rewriting.

The `Execution time` shown by `EXPLAIN
ANALYZE` includes executor start-up and shut-down time, as well
as the time to run any triggers that are fired, but it does not include
parsing, rewriting, or planning time.
Time spent executing `BEFORE` triggers, if any, is included in
the time for the related Insert, Update, or Delete node; but time
spent executing `AFTER` triggers is not counted there because
`AFTER` triggers are fired after completion of the whole plan.
The total time spent in each trigger
(either `BEFORE` or `AFTER`) is also shown separately.
Note that deferred constraint triggers will not be executed
until end of transaction and are thus not considered at all by
`EXPLAIN ANALYZE`.

### Caveats

There are two significant ways in which run times measured by
`EXPLAIN ANALYZE` can deviate from normal execution of
the same query.  First, since no output rows are delivered to the client,
network transmission costs and I/O conversion costs are not included.
Second, the measurement overhead added by `EXPLAIN
ANALYZE` can be significant, especially on machines with slow
`gettimeofday()` operating-system calls. You can use the
[pgtesttiming](#pgtesttiming) tool to measure the overhead of timing
on your system.

`EXPLAIN` results should not be extrapolated to situations
much different from the one you are actually testing; for example,
results on a toy-sized table cannot be assumed to apply to large tables.
The planner's cost estimates are not linear and so it might choose
a different plan for a larger or smaller table.  An extreme example
is that on a table that only occupies one disk page, you'll nearly
always get a sequential scan plan whether indexes are available or not.
The planner realizes that it's going to take one disk page read to
process the table in any case, so there's no value in expending additional
page reads to look at an index.  (We saw this happening in the
`polygon_tbl` example above.)

There are cases in which the actual and estimated values won't match up
well, but nothing is really wrong.  One such case occurs when
plan node execution is stopped short by a `LIMIT` or similar
effect.  For example, in the `LIMIT` query we used before,

```
EXPLAIN ANALYZE SELECT * FROM tenk1 WHERE unique1  9000 LIMIT 2;

QUERY PLAN
-------------------------------------------------------------------------------------------------------------------------------
Limit  (cost=0.29..14.71 rows=2 width=244) (actual time=0.177..0.249 rows=2 loops=1)
->  Index Scan using tenk1_unique2 on tenk1  (cost=0.29..72.42 rows=10 width=244) (actual time=0.174..0.244 rows=2 loops=1)
Index Cond: (unique2 > 9000)
Filter: (unique1  5": 1.000000, "5 => 1": 0.423130}
(1 row)
```

Here it can be seen that column 1 (zip code) fully determines column
5 (city) so the coefficient is 1.0, while city only determines zip code
about 42% of the time, meaning that there are many cities (58%) that are
represented by more than a single ZIP code.

When computing the selectivity for a query involving functionally
dependent columns, the planner adjusts the per-condition selectivity
estimates using the dependency coefficients so as not to produce
an underestimate.

##### Limitations of Functional Dependencies

Functional dependencies are currently only applied when considering
simple equality conditions that compare columns to constant values,
and `IN` clauses with constant values.
They are not used to improve estimates for equality conditions
comparing two columns or comparing a column to an expression, nor for
range clauses, `LIKE` or any other type of condition.

When estimating with functional dependencies, the planner assumes that
conditions on the involved columns are compatible and hence redundant.
If they are incompatible, the correct estimate would be zero rows, but
that possibility is not considered.  For example, given a query like

```
SELECT * FROM zipcodes WHERE city = 'San Francisco' AND zip = '94105';
```

the planner will disregard the `city` clause as not
changing the selectivity, which is correct.  However, it will make
the same assumption about

```
SELECT * FROM zipcodes WHERE city = 'San Francisco' AND zip = '90210';
```

even though there will really be zero rows satisfying this query.
Functional dependency statistics do not provide enough information
to conclude that, however.

In many practical situations, this assumption is usually satisfied;
for example, there might be a GUI in the application that only allows
selecting compatible city and ZIP code values to use in a query.
But if that's not the case, functional dependencies may not be a viable
option.

#### Multivariate N-Distinct Counts

Single-column statistics store the number of distinct values in each
column.  Estimates of the number of distinct values when combining more
than one column (for example, for `GROUP BY a, b`) are
frequently wrong when the planner only has single-column statistical
data, causing it to select bad plans.

To improve such estimates, `ANALYZE` can collect n-distinct
statistics for groups of columns.  As before, it's impractical to do
this for every possible column grouping, so data is collected only for
those groups of columns appearing together in a statistics object
defined with the `ndistinct` option.  Data will be collected
for each possible combination of two or more columns from the set of
listed columns.

Continuing the previous example, the n-distinct counts in a
table of ZIP codes might look like the following:

```
CREATE STATISTICS stts2 (ndistinct) ON city, state, zip FROM zipcodes;

ANALYZE zipcodes;

SELECT stxkeys AS k, stxdndistinct AS nd
FROM pg_statistic_ext join pg_statistic_ext_data on (oid = stxoid)
WHERE stxname = 'stts2';
-[ RECORD 1 ]--------------------------------------------------------
k  | 1 2 5
nd | {"1, 2": 33178, "1, 5": 33178, "2, 5": 27435, "1, 2, 5": 33178}
(1 row)
```

This indicates that there are three combinations of columns that
have 33178 distinct values: ZIP code and state; ZIP code and city;
and ZIP code, city and state (the fact that they are all equal is
expected given that ZIP code alone is unique in this table).  On the
other hand, the combination of city and state has only 27435 distinct
values.

It's advisable to create `ndistinct` statistics objects only
on combinations of columns that are actually used for grouping, and
for which misestimation of the number of groups is resulting in bad
plans.  Otherwise, the `ANALYZE` cycles are just wasted.

#### Multivariate MCV Lists

Another type of statistic stored for each column are most-common value
lists.  This allows very accurate estimates for individual columns, but
may result in significant misestimates for queries with conditions on
multiple columns.

To improve such estimates, `ANALYZE` can collect MCV
lists on combinations of columns.  Similarly to functional dependencies
and n-distinct coefficients, it's impractical to do this for every
possible column grouping.  Even more so in this case, as the MCV list
(unlike functional dependencies and n-distinct coefficients) does store
the common column values.  So data is collected only for those groups
of columns appearing together in a statistics object defined with the
`mcv` option.

Continuing the previous example, the MCV list for a table of ZIP codes
might look like the following (unlike for simpler types of statistics,
a function is required for inspection of MCV contents):

```
CREATE STATISTICS stts3 (mcv) ON city, state FROM zipcodes;

ANALYZE zipcodes;

SELECT m.* FROM pg_statistic_ext join pg_statistic_ext_data on (oid = stxoid),
pg_mcv_list_items(stxdmcv) m WHERE stxname = 'stts3';

index |         values         | nulls | frequency | base_frequency
-------+------------------------+-------+-----------+----------------
0 | {Washington, DC}       | {f,f} |  0.003467 |        2.7e-05
1 | {Apo, AE}              | {f,f} |  0.003067 |        1.9e-05
2 | {Houston, TX}          | {f,f} |  0.002167 |       0.000133
3 | {El Paso, TX}          | {f,f} |     0.002 |       0.000113
4 | {New York, NY}         | {f,f} |  0.001967 |       0.000114
5 | {Atlanta, GA}          | {f,f} |  0.001633 |        3.3e-05
6 | {Sacramento, CA}       | {f,f} |  0.001433 |        7.8e-05
7 | {Miami, FL}            | {f,f} |    0.0014 |          6e-05
8 | {Dallas, TX}           | {f,f} |  0.001367 |        8.8e-05
9 | {Chicago, IL}          | {f,f} |  0.001333 |        5.1e-05
...
(99 rows)
```

This indicates that the most common combination of city and state is
Washington in DC, with actual frequency (in the sample) about 0.35%.
The base frequency of the combination (as computed from the simple
per-column frequencies) is only 0.0027%, resulting in two orders of
magnitude under-estimates.

It's advisable to create MCV statistics objects only
on combinations of columns that are actually used in conditions together,
and for which misestimation of the number of groups is resulting in bad
plans.  Otherwise, the `ANALYZE` and planning cycles
are just wasted.
