# Examining Index Usage

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/08_indexes.md`
- Source Title: `Indexes`
- Source Heading Path: `Indexes > Examining Index Usage`
- Source Line Ranges: `903-979`
- Chunk ID: `pg16_guide_0077_13deb0b007`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2c4a5960cfe3dca2cc4117e44982f30240a9f90eb9f95d1600a2e7c4f888f5bd`

## Retrieval Guidance

- Use When: A query is slow or an expected index is not used and the agent must confirm whether planner choice, stale statistics, costs, or predicate mismatch is the root cause.
- Retrieval Keywords: EXPLAIN, index usage, ANALYZE, enable_seqscan, enable_nestloop, statistics, cost estimate, EXPLAIN ANALYZE
- Follow-up Guidance: If estimates are wrong, refresh statistics or adjust statistics targets/cost settings; if predicate mismatch exists, redesign the query or index.
- Classification Note: Explains how to confirm index use with EXPLAIN, server statistics, ANALYZE, forced planner switches, EXPLAIN ANALYZE, cost estimates, and statistics adjustments.

## Official Source Content

## Examining Index Usage

Although indexes in PostgreSQL do not need
maintenance or tuning, it is still important to check
which indexes are actually used by the real-life query workload.
Examining index usage for an individual query is done with the
[sql-explain](#sql-explain)
command; its application for this purpose is
illustrated in [using-explain](#using-explain).
It is also possible to gather overall statistics about index usage
in a running server, as described in [monitoring-stats](#monitoring-stats).

It is difficult to formulate a general procedure for determining
which indexes to create.  There are a number of typical cases that
have been shown in the examples throughout the previous sections.
A good deal of experimentation is often necessary.
The rest of this section gives some tips for that:

- Always run [sql-analyze](#sql-analyze)
first.  This command
collects statistics about the distribution of the values in the
table.  This information is required to estimate the number of rows
returned by a query, which is needed by the planner to assign
realistic costs to each possible query plan.  In absence of any
real statistics, some default values are assumed, which are
almost certain to be inaccurate.  Examining an application's
index usage without having run `ANALYZE` is
therefore a lost cause.
See [vacuum-for-statistics](#vacuum-for-statistics)
and [autovacuum](#autovacuum) for more information.
- Use real data for experimentation.  Using test data for setting
up indexes will tell you what indexes you need for the test data,
but that is all.

It is especially fatal to use very small test data sets.
While selecting 1000 out of 100000 rows could be a candidate for
an index, selecting 1 out of 100 rows will hardly be, because the
100 rows probably fit within a single disk page, and there
is no plan that can beat sequentially fetching 1 disk page.

Also be careful when making up test data, which is often
unavoidable when the application is not yet in production.
Values that are very similar, completely random, or inserted in
sorted order will skew the statistics away from the distribution
that real data would have.
- When indexes are not used, it can be useful for testing to force
their use.  There are run-time parameters that can turn off
various plan types (see [runtime-config-query-enable](#runtime-config-query-enable)).
For instance, turning off sequential scans
(`enable_seqscan`) and nested-loop joins
(`enable_nestloop`), which are the most basic plans,
will force the system to use a different plan.  If the system
still chooses a sequential scan or nested-loop join then there is
probably a more fundamental reason why the index is not being
used; for example, the query condition does not match the index.
(What kind of query can use what kind of index is explained in
the previous sections.)
- If forcing index usage does use the index, then there are two
possibilities: Either the system is right and using the index is
indeed not appropriate, or the cost estimates of the query plans
are not reflecting reality.  So you should time your query with
and without indexes.  The `EXPLAIN ANALYZE`
command can be useful here.
- If it turns out that the cost estimates are wrong, there are,
again, two possibilities.  The total cost is computed from the
per-row costs of each plan node times the selectivity estimate of
the plan node.  The costs estimated for the plan nodes can be adjusted
via run-time parameters (described in [runtime-config-query-constants](#runtime-config-query-constants)).
An inaccurate selectivity estimate is due to
insufficient statistics.  It might be possible to improve this by
tuning the statistics-gathering parameters (see
[sql-altertable](#sql-altertable)).

If you do not succeed in adjusting the costs to be more
appropriate, then you might have to resort to forcing index usage
explicitly.  You might also want to contact the
PostgreSQL developers to examine the issue.
