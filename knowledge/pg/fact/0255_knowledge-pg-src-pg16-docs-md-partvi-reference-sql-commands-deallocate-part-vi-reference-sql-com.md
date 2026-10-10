# DEALLOCATE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/deallocate.md`
- Source Title: `deallocate`
- Source Heading Path: `Part VI Reference > SQL Commands > DEALLOCATE`
- Source Line Ranges: `1-36`
- Chunk ID: `pg16_fact_0255_068d657017`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `1c5dc6f300769d9f42b71cd56dc8e2cee2ff94f1d1df1076082a89d04ac585e5`

## Retrieval Guidance

- Use When: Use for freeing prepared statements.
- Retrieval Keywords: DEALLOCATE, prepared statement, PREPARE, deallocate all
- Follow-up Guidance: No section split needed.
- Classification Note: Prepared statement lifecycle syntax reference.

## Official Source Content

DEALLOCATE
7
SQL - Language Statements

DEALLOCATE
deallocate a prepared statement

```
DEALLOCATE [ PREPARE ] { `name` | ALL }
```

## Description

`DEALLOCATE` is used to deallocate a previously
prepared SQL statement. If you do not explicitly deallocate a
prepared statement, it is deallocated when the session ends.

For more information on prepared statements, see [sql-prepare](#sql-prepare).

## Parameters

**`PREPARE`**
: This key word is ignored.

**`name`**
: The name of the prepared statement to deallocate.

**`ALL`**
: Deallocate all prepared statements.

## Compatibility

The SQL standard includes a `DEALLOCATE`
statement, but it is only for use in embedded SQL.

## See Also
