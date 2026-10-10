# ABORT

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/abort.md`
- Source Title: `abort`
- Source Heading Path: `Part VI Reference > SQL Commands > ABORT`
- Source Line Ranges: `1-53`
- Chunk ID: `pg16_fact_0166_023a21d14f`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `967f07df3e200ecdf70e004c9fc2e351cd668d4ee307b94b64778a5844f77907`

## Retrieval Guidance

- Use When: Use for SQL syntax and behavior of aborting a transaction.
- Retrieval Keywords: ABORT, ROLLBACK, transaction abort, transaction control
- Follow-up Guidance: No section split needed.
- Classification Note: Transaction-control syntax/reference; equivalent to ROLLBACK and not a diagnostic signal or post-root-cause repair procedure.

## Official Source Content

ABORT
7
SQL - Language Statements

ABORT
abort the current transaction

```
ABORT [ WORK | TRANSACTION ] [ AND [ NO ] CHAIN ]
```

## Description

`ABORT` rolls back the current transaction and causes
all the updates made by the transaction to be discarded.
This command is identical
in behavior to the standard SQL command
[`ROLLBACK`](#sql-rollback),
and is present only for historical reasons.

## Parameters

**`WORK`**
: Optional key words. They have no effect.

**`AND CHAIN`**
: If `AND CHAIN` is specified, a new transaction is
immediately started with the same transaction characteristics (see [`SET TRANSACTION`](#sql-set-transaction)) as the just finished one.  Otherwise,
no new transaction is started.

## Notes

Use [`COMMIT`](#sql-commit) to
successfully terminate a transaction.

Issuing `ABORT` outside of a transaction block
emits a warning and otherwise has no effect.

## Examples

To abort all changes:

```
ABORT;
```

## Compatibility

This command is a PostgreSQL extension
present for historical reasons. `ROLLBACK` is the
equivalent standard SQL command.

## See Also
