# START TRANSACTION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/start_transaction.md`
- Source Title: `start transaction`
- Source Heading Path: `Part VI Reference > SQL Commands > START TRANSACTION`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0330_ac98262327`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `8e2267c4ff0192fb5779d78a2667ad61e32e92e1cdde6c6c4eebc9a3112c6f5b`

## Retrieval Guidance

- Use When: Use for standard transaction start syntax.
- Retrieval Keywords: START TRANSACTION, BEGIN, transaction mode, isolation level
- Follow-up Guidance: Use SET TRANSACTION record for transaction-scope configuration details.
- Classification Note: Transaction start syntax reference; overlaps BEGIN and transaction mode clauses.

## Official Source Content

START TRANSACTION
7
SQL - Language Statements

START TRANSACTION
start a transaction block

```
START TRANSACTION [ `transaction_mode` [, ...] ]

where `transaction_mode` is one of:

ISOLATION LEVEL { SERIALIZABLE | REPEATABLE READ | READ COMMITTED | READ UNCOMMITTED }
READ WRITE | READ ONLY
[ NOT ] DEFERRABLE
```

## Description

This command begins a new transaction block. If the isolation level,
read/write mode, or deferrable mode is specified, the new transaction has those
characteristics, as if [`SET TRANSACTION`](#sql-set-transaction) was executed. This is the same
as the [`BEGIN`](#sql-begin) command.

## Parameters

Refer to [sql-set-transaction](#sql-set-transaction) for information on the meaning
of the parameters to this statement.

## Compatibility

In the standard, it is not necessary to issue `START TRANSACTION`
to start a transaction block: any SQL command implicitly begins a block.
PostgreSQL's behavior can be seen as implicitly
issuing a `COMMIT` after each command that does not
follow `START TRANSACTION` (or `BEGIN`),
and it is therefore often called "autocommit".
Other relational database systems might offer an autocommit feature
as a convenience.

The `DEFERRABLE`
`transaction_mode`
is a PostgreSQL language extension.

The SQL standard requires commas between successive `transaction_modes`, but for historical
reasons PostgreSQL allows the commas to be
omitted.

See also the compatibility section of [sql-set-transaction](#sql-set-transaction).

## See Also
