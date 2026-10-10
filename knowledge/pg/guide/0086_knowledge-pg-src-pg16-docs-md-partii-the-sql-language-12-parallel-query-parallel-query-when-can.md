# When Can Parallel Query Be Used

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/12_parallel_query.md`
- Source Title: `Parallel Query`
- Source Heading Path: `Parallel Query > When Can Parallel Query Be Used`
- Source Line Ranges: `87-165`
- Chunk ID: `pg16_guide_0086_b035d044f0`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1233d4e56049b44988caf155425c86525ce5e3ed8b224ca0f694a1a956a06eb`

## Retrieval Guidance

- Use When: Need to confirm why PostgreSQL did not choose or execute a parallel plan.
- Retrieval Keywords: parallel query blocker, parallel plan, data-modifying statement, cursor, parallel unsafe, serializable, PARALLEL SAFE
- Follow-up Guidance: Check query shape, function parallel safety, transaction state, and relevant parallel settings.
- Classification Note: Lists conditions and blockers for parallel plans, making it useful for diagnosing why a plan is serial rather than parallel.

## Official Source Content

## When Can Parallel Query Be Used?

There are several settings that can cause the query planner not to
generate a parallel query plan under any circumstances.  In order for
any parallel query plans whatsoever to be generated, the following
settings must be configured as indicated.

- [guc-max-parallel-workers-per-gather](#guc-max-parallel-workers-per-gather) must be set to a
value that is greater than zero. This is a special case of the more
general principle that no more workers should be used than the number
configured via `max_parallel_workers_per_gather`.

In addition, the system must not be running in single-user mode.  Since
the entire database system is running as a single process in this situation,
no background workers will be available.

Even when it is in general possible for parallel query plans to be
generated, the planner will not generate them for a given query
if any of the following are true:

- The query writes any data or locks any database rows. If a query
contains a data-modifying operation either at the top level or within
a CTE, no parallel plans for that query will be generated.  As an
exception, the following commands, which create a new table and populate
it, can use a parallel plan for the underlying `SELECT`
part of the query:

`CREATE TABLE ... AS`
- `SELECT INTO`
- `CREATE MATERIALIZED VIEW`
- `REFRESH MATERIALIZED VIEW`

The query might be suspended during execution. In any situation in
which the system thinks that partial or incremental execution might
occur, no parallel plan is generated. For example, a cursor created
using [DECLARE CURSOR](#sql-declare) will never use
a parallel plan. Similarly, a PL/pgSQL loop of the form
`FOR x IN query LOOP .. END LOOP` will never use a
parallel plan, because the parallel query system is unable to verify
that the code in the loop is safe to execute while parallel query is
active.

The query uses any function marked `PARALLEL UNSAFE`.
Most system-defined functions are `PARALLEL SAFE`,
but user-defined functions are marked `PARALLEL
UNSAFE` by default. See the discussion of
[parallel-safety](#parallel-safety).

The query is running inside of another query that is already parallel.
For example, if a function called by a parallel query issues an SQL
query itself, that query will never use a parallel plan. This is a
limitation of the current implementation, but it may not be desirable
to remove this limitation, since it could result in a single query
using a very large number of processes.

Even when a parallel query plan is generated for a particular query, there
are several circumstances under which it will be impossible to execute
that plan in parallel at execution time.  If this occurs, the leader
will execute the portion of the plan below the `Gather`
node entirely by itself, almost as if the `Gather` node were
not present.  This will happen if any of the following conditions are met:

- No background workers can be obtained because of the limitation that
the total number of background workers cannot exceed
[guc-max-worker-processes](#guc-max-worker-processes).
- No background workers can be obtained because of the limitation that
the total number of background workers launched for purposes of
parallel query cannot exceed [guc-max-parallel-workers](#guc-max-parallel-workers).
- The client sends an Execute message with a non-zero fetch count.
See the discussion of the
[extended query protocol](#protocol-flow-ext-query).
Since [libpq](#libpq) currently provides no way to
send such a message, this can only occur when using a client that
does not rely on libpq.  If this is a frequent
occurrence, it may be a good idea to set
[guc-max-parallel-workers-per-gather](#guc-max-parallel-workers-per-gather) to zero in
sessions where it is likely, so as to avoid generating query plans
that may be suboptimal when run serially.
