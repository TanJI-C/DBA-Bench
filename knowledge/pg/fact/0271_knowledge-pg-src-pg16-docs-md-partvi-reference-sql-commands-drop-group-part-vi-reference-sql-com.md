# DROP GROUP

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_group.md`
- Source Title: `drop group`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP GROUP`
- Source Line Ranges: `1-21`
- Chunk ID: `pg16_fact_0271_f1ae1af75d`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ff2cb9f1ab937d80603df55b4c9b9d601688a10982333e9e6c3811bb586ef292`

## Retrieval Guidance

- Use When: Use for legacy group removal syntax.
- Retrieval Keywords: DROP GROUP, DROP ROLE alias, group role
- Follow-up Guidance: Prefer DROP ROLE terminology in new guidance.
- Classification Note: Compatibility reference for dropping a role/group.

## Official Source Content

DROP GROUP
7
SQL - Language Statements

DROP GROUP
remove a database role

```
DROP GROUP [ IF EXISTS ] `name` [, ...]
```

## Description

`DROP GROUP` is now an alias for
[`DROP ROLE`](#sql-droprole).

## Compatibility

There is no `DROP GROUP` statement in the SQL standard.

## See Also
