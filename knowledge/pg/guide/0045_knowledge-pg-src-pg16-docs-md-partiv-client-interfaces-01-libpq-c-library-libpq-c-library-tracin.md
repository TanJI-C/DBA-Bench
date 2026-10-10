# Tracing libpq Applications; Pipeline Mode Error Handling; Connection Status and Reset Functions

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/01_libpq_-_c_library.md`
- Source Title: `libpq — C Library`
- Source Heading Path: `libpq - C Library > Tracing libpq Applications; Pipeline Mode Error Handling; Connection Status and Reset Functions`
- Source Line Ranges: `3591-3630`
- Chunk ID: `pg16_guide_0045_1b1f1ad8c9`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fd47a7c7f7eacc802c48b9dfe15ab5bca6046a4f275915a59a4ed632b715cfbe`

## Retrieval Guidance

- Use When: Diagnose libpq client behavior, pipeline failure propagation, or connection-state problems.
- Retrieval Keywords: PQtrace, PQuntrace, libpq tracing, pipeline abort, PGRES_PIPELINE_ABORTED, PQreset, PQresetStart, PQconsumeInput
- Follow-up Guidance: Use cancellation and reconnection actions only after confirming the affected connection state.
- Classification Note: These sections expose tracing and status transitions that help confirm client/server protocol flow, failed pipeline commands, and broken or reset connections.

## Official Source Content

#### Error Handling

From the client's perspective, after `PQresultStatus`
returns `PGRES_FATAL_ERROR`,
the pipeline is flagged as aborted.
`PQresultStatus` will report a
`PGRES_PIPELINE_ABORTED` result for each remaining queued
operation in an aborted pipeline. The result for
`PQpipelineSync` is reported as
`PGRES_PIPELINE_SYNC` to signal the end of the aborted pipeline
and resumption of normal result processing.

The client *must* process results with
`PQgetResult` during error recovery.

If the pipeline used an implicit transaction, then operations that have
already executed are rolled back and operations that were queued to follow
the failed operation are skipped entirely. The same behavior holds if the
pipeline starts and commits a single explicit transaction (i.e. the first
statement is `BEGIN` and the last is
`COMMIT`) except that the session remains in an aborted
transaction state at the end of the pipeline. If a pipeline contains
*multiple explicit transactions*, all transactions that
committed prior to the error remain committed, the currently in-progress
transaction is aborted, and all subsequent operations are skipped completely,
including subsequent transactions.  If a pipeline synchronization point
occurs with an explicit transaction block in aborted state, the next pipeline
will become aborted immediately unless the next command puts the transaction
in normal mode with `ROLLBACK`.

> **Note:**

> The client must not assume that work is committed when it
> *sends* a `COMMIT` — only when the
> corresponding result is received to confirm the commit is complete.
> Because errors arrive asynchronously, the application needs to be able to
> restart from the last *received* committed change and
> resend work done after that point if something goes wrong.
>
