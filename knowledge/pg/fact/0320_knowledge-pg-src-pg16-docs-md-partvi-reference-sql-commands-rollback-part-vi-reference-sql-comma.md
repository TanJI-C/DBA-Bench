# ROLLBACK

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/rollback.md`
- Source Title: `rollback`
- Source Heading Path: `Part VI Reference > SQL Commands > ROLLBACK`
- Source Line Ranges: `1-50`
- Chunk ID: `pg16_fact_0320_178a6170a3`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `a080d567bebe5b39b7e20e0c86dd6d15745e3b099f2d73958a53bd0b4e0b7a56`

## Retrieval Guidance

- Use When: Use for rollback syntax and transaction semantics.
- Retrieval Keywords: ROLLBACK, transaction abort, ABORT
- Follow-up Guidance: No section split needed.
- Classification Note: Transaction-control syntax reference for aborting the current transaction.

## Official Source Content

ROLLBACK
7
SQL - Language Statements

ROLLBACK
abort the current transaction

```
ROLLBACK [ WORK | TRANSACTION ] [ AND [ NO ] CHAIN ]
```

## Description

`ROLLBACK` rolls back the current transaction and causes
all the updates made by the transaction to be discarded.

## Parameters

**`WORK`**
: Optional key words. They have no effect.

**`AND CHAIN`**
: If `AND CHAIN` is specified, a new (not aborted)
transaction is immediately started with the same transaction
characteristics (see [sql-set-transaction](#sql-set-transaction)) as the
just finished one.  Otherwise, no new transaction is started.

## Notes

Use [`COMMIT`](#sql-commit) to
successfully terminate a transaction.

Issuing `ROLLBACK` outside of a transaction
block emits a warning and otherwise has no effect.  `ROLLBACK AND
CHAIN` outside of a transaction block is an error.

## Examples

To abort all changes:

```
ROLLBACK;
```

## Compatibility

The command `ROLLBACK` conforms to the SQL standard.  The
form `ROLLBACK TRANSACTION` is a PostgreSQL extension.

## See Also
