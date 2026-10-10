# Serialization Failure Handling

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/10_concurrency_control.md`
- Source Title: `Concurrency Control`
- Source Heading Path: `Concurrency Control > Serialization Failure Handling`
- Source Line Ranges: `1085-1131`
- Chunk ID: `pg16_solution_0122_4330657dd5`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c76e865daa2aa450d7f962c8e98214f98499f8134badcf470e262a33301eab6e`

## Retrieval Guidance

- Use When: Root cause is a serialization failure or transaction abort caused by concurrent updates.
- Retrieval Keywords: serialization failure, SQLSTATE 40001, retry transaction, deadlock 40P01, unique violation, exclusion violation
- Follow-up Guidance: Retry from the beginning of transaction logic, not from the failed statement only.
- Classification Note: Provides the required remediation pattern for serialization failures: retry the complete transaction, with SQLSTATE examples including 40001 and related cases.

## Official Source Content

## Serialization Failure Handling

Both Repeatable Read and Serializable isolation levels can produce
errors that are designed to prevent serialization anomalies.  As
previously stated, applications using these levels must be prepared to
retry transactions that fail due to serialization errors.  Such an
error's message text will vary according to the precise circumstances,
but it will always have the SQLSTATE code `40001`
(`serialization_failure`).

It may also be advisable to retry deadlock failures.
These have the SQLSTATE code `40P01`
(`deadlock_detected`).

In some cases it is also appropriate to retry unique-key failures,
which have SQLSTATE code `23505`
(`unique_violation`), and exclusion constraint
failures, which have SQLSTATE code `23P01`
(`exclusion_violation`).  For example, if the
application selects a new value for a primary key column after
inspecting the currently stored keys, it could get a unique-key
failure because another application instance selected the same new key
concurrently.  This is effectively a serialization failure, but the
server will not detect it as such because it cannot "see"
the connection between the inserted value and the previous reads.
There are also some corner cases in which the server will issue a
unique-key or exclusion constraint error even though in principle it
has enough information to determine that a serialization problem
is the underlying cause.  While it's recommendable to just
retry `serialization_failure` errors unconditionally,
more care is needed when retrying these other error codes, since they
might represent persistent error conditions rather than transient
failures.

It is important to retry the complete transaction, including all logic
that decides which SQL to issue and/or which values to use.
Therefore, PostgreSQL does not offer an
automatic retry facility, since it cannot do so with any guarantee of
correctness.

Transaction retry does not guarantee that the retried transaction will
complete; multiple retries may be needed.  In cases with very high
contention, it is possible that completion of a transaction may take
many attempts.  In cases involving a conflicting prepared transaction,
it may not be possible to make progress until the prepared transaction
commits or rolls back.
