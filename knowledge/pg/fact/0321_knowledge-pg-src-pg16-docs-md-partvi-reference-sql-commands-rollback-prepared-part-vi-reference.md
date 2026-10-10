# ROLLBACK PREPARED

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/rollback_prepared.md`
- Source Title: `rollback prepared`
- Source Heading Path: `Part VI Reference > SQL Commands > ROLLBACK PREPARED`
- Source Line Ranges: `1-53`
- Chunk ID: `pg16_fact_0321_cad2c653c3`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `db784f5f433658f41044f750cfbe2a0898a7fa95cb88ba35f21c3518a2fd83b1`

## Retrieval Guidance

- Use When: Use for aborting prepared transactions by GID.
- Retrieval Keywords: ROLLBACK PREPARED, prepared transaction, two-phase commit, 2PC
- Follow-up Guidance: Confirm prepared transaction via pg_prepared_xacts before use.
- Classification Note: Two-phase transaction rollback syntax reference.

## Official Source Content

ROLLBACK PREPARED
7
SQL - Language Statements

ROLLBACK PREPARED
cancel a transaction that was earlier prepared for two-phase commit

```
ROLLBACK PREPARED `transaction_id`
```

## Description

`ROLLBACK PREPARED` rolls back a transaction that is in
prepared state.

## Parameters

**`transaction_id`**
: The transaction identifier of the transaction that is to be
rolled back.

## Notes

To roll back a prepared transaction, you must be either the same user that
executed the transaction originally, or a superuser.  But you do not
have to be in the same session that executed the transaction.

This command cannot be executed inside a transaction block. The prepared
transaction is rolled back immediately.

All currently available prepared transactions are listed in the
[`pg_prepared_xacts`](#view-pg-prepared-xacts)
system view.

## Examples

Roll back the transaction identified by the transaction
identifier `foobar`:

```
ROLLBACK PREPARED 'foobar';
```

## Compatibility

`ROLLBACK PREPARED` is a
PostgreSQL extension.  It is intended for use by
external transaction management systems, some of which are covered by
standards (such as X/Open XA), but the SQL side of those systems is not
standardized.

## See Also
