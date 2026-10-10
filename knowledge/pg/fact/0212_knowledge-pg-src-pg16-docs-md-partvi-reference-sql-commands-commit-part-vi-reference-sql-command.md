# COMMIT

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/commit.md`
- Source Title: `commit`
- Source Heading Path: `Part VI Reference > SQL Commands > COMMIT`
- Source Line Ranges: `1-50`
- Chunk ID: `pg16_fact_0212_8a49186294`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `e7a33f234314d5755eaee90ecae5fe4ad37d73668d0ad1bcf7b99b8929398a9e`

## Retrieval Guidance

- Use When: Use for commit syntax and transaction semantics.
- Retrieval Keywords: COMMIT, END transaction, transaction commit
- Follow-up Guidance: No section split needed.
- Classification Note: Transaction-control syntax reference for committing a transaction.

## Official Source Content

COMMIT
7
SQL - Language Statements

COMMIT
commit the current transaction

```
COMMIT [ WORK | TRANSACTION ] [ AND [ NO ] CHAIN ]
```

## Description

`COMMIT` commits the current transaction. All
changes made by the transaction become visible to others
and are guaranteed to be durable if a crash occurs.

## Parameters

**`WORK`**
: Optional key words. They have no effect.

**`AND CHAIN`**
: If `AND CHAIN` is specified, a new transaction is
immediately started with the same transaction characteristics (see [sql-set-transaction](#sql-set-transaction)) as the just finished one.  Otherwise,
no new transaction is started.

## Notes

Use [sql-rollback](#sql-rollback) to
abort a transaction.

Issuing `COMMIT` when not inside a transaction does
no harm, but it will provoke a warning message.  `COMMIT AND
CHAIN` when not inside a transaction is an error.

## Examples

To commit the current transaction and make all changes permanent:

```
COMMIT;
```

## Compatibility

The command `COMMIT` conforms to the SQL standard.  The
form `COMMIT TRANSACTION` is a PostgreSQL extension.

## See Also
