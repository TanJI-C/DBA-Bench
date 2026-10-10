# END

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/end.md`
- Source Title: `end`
- Source Heading Path: `Part VI Reference > SQL Commands > END`
- Source Line Ranges: `1-52`
- Chunk ID: `pg16_fact_0303_f4fc69704a`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `731c1c7aae42aff4c322b664de51d395df4b5ce0aaeaae0585445a500a5bc18c`

## Retrieval Guidance

- Use When: Use for END transaction syntax.
- Retrieval Keywords: END, COMMIT, transaction end
- Follow-up Guidance: No section split needed.
- Classification Note: Transaction-control syntax reference; synonym for COMMIT.

## Official Source Content

END
7
SQL - Language Statements

END
commit the current transaction

```
END [ WORK | TRANSACTION ] [ AND [ NO ] CHAIN ]
```

## Description

`END` commits the current transaction. All changes
made by the transaction become visible to others and are guaranteed
to be durable if a crash occurs.  This command is a
PostgreSQL extension
that is equivalent to [`COMMIT`](#sql-commit).

## Parameters

**`WORK`**
: Optional key words. They have no effect.

**`AND CHAIN`**
: If `AND CHAIN` is specified, a new transaction is
immediately started with the same transaction characteristics (see [sql-set-transaction](#sql-set-transaction)) as the just finished one.  Otherwise,
no new transaction is started.

## Notes

Use [`ROLLBACK`](#sql-rollback) to
abort a transaction.

Issuing `END` when not inside a transaction does
no harm, but it will provoke a warning message.

## Examples

To commit the current transaction and make all changes permanent:

```
END;
```

## Compatibility

`END` is a PostgreSQL
extension that provides functionality equivalent to [`COMMIT`](#sql-commit), which is
specified in the SQL standard.

## See Also
