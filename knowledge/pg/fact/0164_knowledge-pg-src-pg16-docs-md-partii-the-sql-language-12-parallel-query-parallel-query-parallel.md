# Parallel Safety; Parallel Labeling for Functions and Aggregates

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/12_parallel_query.md`
- Source Title: `Parallel Query`
- Source Heading Path: `Parallel Query > Parallel Safety; Parallel Labeling for Functions and Aggregates`
- Source Line Ranges: `325-404`
- Chunk ID: `pg16_fact_0164_4d429b481a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d5943e8f3b9e767501db17647a003c488cae1575bb492c8bf4d4ce02bfbcce47`

## Retrieval Guidance

- Use When: Need facts about why a function or aggregate is considered safe or unsafe for parallel execution.
- Retrieval Keywords: parallel safe, parallel restricted, parallel unsafe, function labeling, aggregate labeling
- Follow-up Guidance: Review function side effects and access patterns before changing parallel-safety labels.
- Classification Note: Explains PARALLEL SAFE, PARALLEL RESTRICTED, and PARALLEL UNSAFE labels for functions and aggregates.

## Official Source Content

## Parallel Safety

The planner classifies operations involved in a query as either
*parallel safe*, *parallel restricted*,
or *parallel unsafe*.  A parallel safe operation is one that
does not conflict with the use of parallel query.  A parallel restricted
operation is one that cannot be performed in a parallel worker, but that
can be performed in the leader while parallel query is in use.  Therefore,
parallel restricted operations can never occur below a `Gather`
or `Gather Merge` node, but can occur elsewhere in a plan that
contains such a node.  A parallel unsafe operation is one that cannot
be performed while parallel query is in use, not even in the leader.
When a query contains anything that is parallel unsafe, parallel query
is completely disabled for that query.

The following operations are always parallel restricted:

- Scans of common table expressions (CTEs).
- Scans of temporary tables.
- Scans of foreign tables, unless the foreign data wrapper has
an `IsForeignScanParallelSafe` API that indicates otherwise.
- Plan nodes to which an `InitPlan` is attached.
- Plan nodes that reference a correlated `SubPlan`.

### Parallel Labeling for Functions and Aggregates

The planner cannot automatically determine whether a user-defined
function or aggregate is parallel safe, parallel restricted, or parallel
unsafe, because this would require predicting every operation that the
function could possibly perform.  In general, this is equivalent to the
Halting Problem and therefore impossible.  Even for simple functions
where it could conceivably be done, we do not try, since this would be expensive
and error-prone.  Instead, all user-defined functions are assumed to
be parallel unsafe unless otherwise marked.  When using
[sql-createfunction](#sql-createfunction) or
[sql-alterfunction](#sql-alterfunction), markings can be set by specifying
`PARALLEL SAFE`, `PARALLEL RESTRICTED`, or
`PARALLEL UNSAFE` as appropriate.  When using
[sql-createaggregate](#sql-createaggregate), the
`PARALLEL` option can be specified with `SAFE`,
`RESTRICTED`, or `UNSAFE` as the corresponding value.

Functions and aggregates must be marked `PARALLEL UNSAFE` if
they write to the database, access sequences, change the transaction state
even temporarily (e.g., a PL/pgSQL function that establishes an
`EXCEPTION` block to catch errors), or make persistent changes to
settings.  Similarly, functions must be marked `PARALLEL
RESTRICTED` if they access temporary tables, client connection state,
cursors, prepared statements, or miscellaneous backend-local state that
the system cannot synchronize across workers. For example,
`setseed` and `random` are parallel restricted for
this last reason.

In general, if a function is labeled as being safe when it is restricted or
unsafe, or if it is labeled as being restricted when it is in fact unsafe,
it may throw errors or produce wrong answers when used in a parallel query.
C-language functions could in theory exhibit totally undefined behavior if
mislabeled, since there is no way for the system to protect itself against
arbitrary C code, but in most likely cases the result will be no worse than
for any other function. If in doubt, it is probably best to label functions
as `UNSAFE`.

If a function executed within a parallel worker acquires locks that are
not held by the leader, for example by querying a table not referenced in
the query, those locks will be released at worker exit, not end of
transaction. If you write a function that does this, and this behavior
difference is important to you, mark such functions as
`PARALLEL RESTRICTED`
to ensure that they execute only in the leader.

Note that the query planner does not consider deferring the evaluation of
parallel-restricted functions or aggregates involved in the query in
order to obtain a superior plan.  So, for example, if a `WHERE`
clause applied to a particular table is parallel restricted, the query
planner will not consider performing a scan of that table in the parallel
portion of a plan.  In some cases, it would be
possible (and perhaps even efficient) to include the scan of that table in
the parallel portion of the query and defer the evaluation of the
`WHERE` clause so that it happens above the `Gather`
node.  However, the planner does not do this.
