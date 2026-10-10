# EXPLAIN

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/explain.md`
- Source Title: `explain`
- Source Heading Path: `Part VI Reference > SQL Commands > EXPLAIN`
- Source Line Ranges: `1-319`
- Chunk ID: `pg16_guide_0088_d6a0b97fae`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `11fad9948bcc73db3fce3c5c76573da92d192f1647e7705eebaa2402c4d169d2`

## Retrieval Guidance

- Use When: Use to diagnose slow queries, bad estimates, missing indexes, IO/cache behavior, and execution-plan regressions.
- Retrieval Keywords: EXPLAIN, EXPLAIN ANALYZE, BUFFERS, WAL, query plan, row estimates
- Follow-up Guidance: Use findings to choose ANALYZE, CREATE INDEX, CREATE STATISTICS, query rewrite, or configuration changes.
- Classification Note: Shows planner/executor evidence such as plan nodes, costs, actual rows, buffers, WAL, and timing; core diagnostic confirmation signal.

## Official Source Content

EXPLAIN
7
SQL - Language Statements

EXPLAIN
show the execution plan of a statement

```
EXPLAIN [ ( `option` [, ...] ) ] `statement`
EXPLAIN [ ANALYZE ] [ VERBOSE ] `statement`

where `option` can be one of:

ANALYZE [ `boolean` ]
VERBOSE [ `boolean` ]
COSTS [ `boolean` ]
SETTINGS [ `boolean` ]
GENERIC_PLAN [ `boolean` ]
BUFFERS [ `boolean` ]
WAL [ `boolean` ]
TIMING [ `boolean` ]
SUMMARY [ `boolean` ]
FORMAT { TEXT | XML | JSON | YAML }
```

## Description

This command displays the execution plan that the
PostgreSQL planner generates for the
supplied statement.  The execution plan shows how the table(s)
referenced by the statement will be scanned — by plain sequential scan,
index scan, etc. — and if multiple tables are referenced, what join
algorithms will be used to bring together the required rows from
each input table.

The most critical part of the display is the estimated statement execution
cost, which is the planner's guess at how long it will take to run the
statement (measured in cost units that are arbitrary, but conventionally
mean disk page fetches).  Actually two numbers
are shown: the start-up cost before the first row can be returned, and
the total cost to return all the rows.  For most queries the total cost
is what matters, but in contexts such as a subquery in `EXISTS`, the planner
will choose the smallest start-up cost instead of the smallest total cost
(since the executor will stop after getting one row, anyway).
Also, if you limit the number of rows to return with a `LIMIT` clause,
the planner makes an appropriate interpolation between the endpoint
costs to estimate which plan is really the cheapest.

The `ANALYZE` option causes the statement to be actually
executed, not only planned.  Then actual run time statistics are added to
the display, including the total elapsed time expended within each plan
node (in milliseconds) and the total number of rows it actually returned.
This is useful for seeing whether the planner's estimates
are close to reality.

> **Important:**

> Keep in mind that the statement is actually executed when
> the `ANALYZE` option is used.  Although
> `EXPLAIN` will discard any output that a
> `SELECT` would return, other side effects of the
> statement will happen as usual.  If you wish to use
> `EXPLAIN ANALYZE` on an
> `INSERT`, `UPDATE`,
> `DELETE`, `MERGE`,
> `CREATE TABLE AS`,
> or `EXECUTE` statement
> without letting the command affect your data, use this approach:
> ```
> BEGIN;
> EXPLAIN ANALYZE ...;
> ROLLBACK;
> ```
>

Only the `ANALYZE` and `VERBOSE` options
can be specified, and only in that order, without surrounding the option
list in parentheses.  Prior to PostgreSQL 9.0,
the unparenthesized syntax was the only one supported.  It is expected that
all new options will be supported only in the parenthesized syntax.

## Parameters

**`ANALYZE`**
: Carry out the command and show actual run times and other statistics.
This parameter defaults to `FALSE`.

**`VERBOSE`**
: Display additional information regarding the plan.  Specifically, include
the output column list for each node in the plan tree, schema-qualify
table and function names, always label variables in expressions with
their range table alias, and always print the name of each trigger for
which statistics are displayed.  The query identifier will also be
displayed if one has been computed, see [guc-compute-query-id](#guc-compute-query-id) for more details.  This parameter
defaults to `FALSE`.

**`COSTS`**
: Include information on the estimated startup and total cost of each
plan node, as well as the estimated number of rows and the estimated
width of each row.
This parameter defaults to `TRUE`.

**`SETTINGS`**
: Include information on configuration parameters.  Specifically, include
options affecting query planning with value different from the built-in
default value.  This parameter defaults to `FALSE`.

**`GENERIC_PLAN`**
: Allow the statement to contain parameter placeholders like
`$1`, and generate a generic plan that does not
depend on the values of those parameters.
See [`PREPARE`](#sql-prepare)
for details about generic plans and the types of statement that
support parameters.
This parameter cannot be used together with `ANALYZE`.
It defaults to `FALSE`.

**`BUFFERS`**
: Include information on buffer usage. Specifically, include the number of
shared blocks hit, read, dirtied, and written, the number of local blocks
hit, read, dirtied, and written, the number of temp blocks read and
written, and the time spent reading and writing data file blocks and
temporary file blocks (in milliseconds) if
[guc-track-io-timing](#guc-track-io-timing) is enabled.  A
*hit* means that a read was avoided because the block
was found already in cache when needed.
Shared blocks contain data from regular tables and indexes;
local blocks contain data from temporary tables and indexes;
while temporary blocks contain short-term working data used in sorts,
hashes, Materialize plan nodes, and similar cases.
The number of blocks *dirtied* indicates the number of
previously unmodified blocks that were changed by this query; while the
number of blocks *written* indicates the number of
previously-dirtied blocks evicted from cache by this backend during
query processing.
The number of blocks shown for an
upper-level node includes those used by all its child nodes.  In text
format, only non-zero values are printed.  This parameter defaults to
`FALSE`.

**`WAL`**
: Include information on WAL record generation. Specifically, include the
number of records, number of full page images (fpi) and the amount of WAL
generated in bytes. In text format, only non-zero values are printed.
This parameter may only be used when `ANALYZE` is also
enabled.  It defaults to `FALSE`.

**`TIMING`**
: Include actual startup time and time spent in each node in the output.
The overhead of repeatedly reading the system clock can slow down the
query significantly on some systems, so it may be useful to set this
parameter to `FALSE` when only actual row counts, and
not exact times, are needed.  Run time of the entire statement is
always measured, even when node-level timing is turned off with this
option.
This parameter may only be used when `ANALYZE` is also
enabled.  It defaults to `TRUE`.

**`SUMMARY`**
: Include summary information (e.g., totaled timing information) after the
query plan.  Summary information is included by default when
`ANALYZE` is used but otherwise is not included by
default, but can be enabled using this option.  Planning time in
`EXPLAIN EXECUTE` includes the time required to fetch
the plan from the cache and the time required for re-planning, if
necessary.

**`FORMAT`**
: Specify the output format, which can be TEXT, XML, JSON, or YAML.
Non-text output contains the same information as the text output
format, but is easier for programs to parse.  This parameter defaults to
`TEXT`.

**`boolean`**
: Specifies whether the selected option should be turned on or off.
You can write `TRUE`, `ON`, or
`1` to enable the option, and `FALSE`,
`OFF`, or `0` to disable it.  The
`boolean` value can also
be omitted, in which case `TRUE` is assumed.

**`statement`**
: Any `SELECT`, `INSERT`, `UPDATE`,
`DELETE`, `MERGE`,
`VALUES`, `EXECUTE`,
`DECLARE`, `CREATE TABLE AS`, or
`CREATE MATERIALIZED VIEW AS` statement, whose execution
plan you wish to see.

## Outputs

The command's result is a textual description of the plan selected
for the `statement`,
optionally annotated with execution statistics.
[using-explain](#using-explain) describes the information provided.

## Notes

In order to allow the PostgreSQL query
planner to make reasonably informed decisions when optimizing
queries, the [`pg_statistic`](#catalog-pg-statistic)
data should be up-to-date for all tables used in the query.  Normally
the [autovacuum daemon](#autovacuum) will take care
of that automatically.  But if a table has recently had substantial
changes in its contents, you might need to do a manual
[`ANALYZE`](#sql-analyze) rather than wait for autovacuum to catch up
with the changes.

In order to measure the run-time cost of each node in the execution
plan, the current implementation of `EXPLAIN
ANALYZE` adds profiling overhead to query execution.
As a result, running `EXPLAIN ANALYZE`
on a query can sometimes take significantly longer than executing
the query normally. The amount of overhead depends on the nature of
the query, as well as the platform being used.  The worst case occurs
for plan nodes that in themselves require very little time per
execution, and on machines that have relatively slow operating
system calls for obtaining the time of day.

## Examples

To show the plan for a simple query on a table with a single
`integer` column and 10000 rows:

```
EXPLAIN SELECT * FROM foo;

QUERY PLAN
---------------------------------------------------------
Seq Scan on foo  (cost=0.00..155.00 rows=10000 width=4)
(1 row)
```

Here is the same query, with JSON output formatting:

```
EXPLAIN (FORMAT JSON) SELECT * FROM foo;
QUERY PLAN
--------------------------------
[                             +
{                           +
"Plan": {                 +
"Node Type": "Seq Scan",+
"Relation Name": "foo", +
"Alias": "foo",         +
"Startup Cost": 0.00,   +
"Total Cost": 155.00,   +
"Plan Rows": 10000,     +
"Plan Width": 4         +
}                         +
}                           +
]
(1 row)
```

If there is an index and we use a query with an indexable
`WHERE` condition, `EXPLAIN`
might show a different plan:

```
EXPLAIN SELECT * FROM foo WHERE i = 4;

QUERY PLAN
--------------------------------------------------------------
Index Scan using fi on foo  (cost=0.00..5.98 rows=1 width=4)
Index Cond: (i = 4)
(2 rows)
```

Here is the same query, but in YAML format:

```
EXPLAIN (FORMAT YAML) SELECT * FROM foo WHERE i='4';
QUERY PLAN
-------------------------------
- Plan:                      +
Node Type: "Index Scan"  +
Scan Direction: "Forward"+
Index Name: "fi"         +
Relation Name: "foo"     +
Alias: "foo"             +
Startup Cost: 0.00       +
Total Cost: 5.98         +
Plan Rows: 1             +
Plan Width: 4            +
Index Cond: "(i = 4)"
(1 row)
```

XML format is left as an exercise for the reader.

Here is the same plan with cost estimates suppressed:

```
EXPLAIN (COSTS FALSE) SELECT * FROM foo WHERE i = 4;

QUERY PLAN
----------------------------
Index Scan using fi on foo
Index Cond: (i = 4)
(2 rows)
```

Here is an example of a query plan for a query using an aggregate
function:

```
EXPLAIN SELECT sum(i) FROM foo WHERE i   Index Scan using fi on foo  (cost=0.00..23.92 rows=6 width=4)
Index Cond: (i  $1 AND id   Index Scan using test_pkey on test  (cost=0.29..10.27 rows=99 width=8) (actual time=0.009..0.025 rows=99 loops=1)
Index Cond: ((id > 100) AND (id  $1 AND id   Index Scan using test_pkey on test  (cost=0.29..24.29 rows=500 width=8)
Index Cond: ((id > $1) AND (id  $1::integer AND id < $2::integer
GROUP BY foo;
```

## Compatibility

There is no `EXPLAIN` statement defined in the SQL standard.

## See Also
