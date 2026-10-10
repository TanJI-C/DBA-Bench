# COMMIT PREPARED

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/commit_prepared.md`
- Source Title: `commit prepared`
- Source Heading Path: `Part VI Reference > SQL Commands > COMMIT PREPARED`
- Source Line Ranges: `1-53`
- Chunk ID: `pg16_fact_0213_59a68f484b`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `02b651d020cc95e56d19138ec8ee63e3f902303b7018850b88070aed68e03064`

## Retrieval Guidance

- Use When: Use for prepared transaction commit syntax.
- Retrieval Keywords: COMMIT PREPARED, two-phase commit, prepared transaction, 2PC
- Follow-up Guidance: Confirm prepared transaction identity via pg_prepared_xacts before operational use.
- Classification Note: Two-phase transaction syntax reference; operationally sensitive but primarily command semantics/reference.

## Official Source Content

COMMIT PREPARED
7
SQL - Language Statements

COMMIT PREPARED
commit a transaction that was earlier prepared for two-phase commit

```
COMMIT PREPARED `transaction_id`
```

## Description

`COMMIT PREPARED` commits a transaction that is in
prepared state.

## Parameters

**`transaction_id`**
: The transaction identifier of the transaction that is to be
committed.

## Notes

To commit a prepared transaction, you must be either the same user that
executed the transaction originally, or a superuser.  But you do not
have to be in the same session that executed the transaction.

This command cannot be executed inside a transaction block. The prepared
transaction is committed immediately.

All currently available prepared transactions are listed in the
[`pg_prepared_xacts`](#view-pg-prepared-xacts)
system view.

## Examples

Commit the transaction identified by the transaction
identifier `foobar`:

```
COMMIT PREPARED 'foobar';
```

## Compatibility

`COMMIT PREPARED` is a
PostgreSQL extension.  It is intended for use by
external transaction management systems, some of which are covered by
standards (such as X/Open XA), but the SQL side of those systems is not
standardized.

## See Also
