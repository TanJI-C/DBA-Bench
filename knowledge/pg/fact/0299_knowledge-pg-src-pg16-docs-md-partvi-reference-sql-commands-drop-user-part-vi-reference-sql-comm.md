# DROP USER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_user.md`
- Source Title: `drop user`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP USER`
- Source Line Ranges: `1-23`
- Chunk ID: `pg16_fact_0299_d3d7bdfc9e`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `5cd516392c4528b0697ea6baa8f947cab09ce18b79abc9379b32efc04414fa97`

## Retrieval Guidance

- Use When: Use for legacy user removal syntax.
- Retrieval Keywords: DROP USER, DROP ROLE alias, user removal
- Follow-up Guidance: Prefer DROP ROLE terminology in new guidance.
- Classification Note: Compatibility alias for DROP ROLE; user/role removal syntax reference.

## Official Source Content

DROP USER
7
SQL - Language Statements

DROP USER
remove a database role

```
DROP USER [ IF EXISTS ] `name` [, ...]
```

## Description

`DROP USER` is simply an alternate spelling of
[`DROP ROLE`](#sql-droprole).

## Compatibility

The `DROP USER` statement is a
PostgreSQL extension.  The SQL standard
leaves the definition of users to the implementation.

## See Also
