# ALTER TEXT SEARCH TEMPLATE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_tstemplate.md`
- Source Title: `alter tstemplate`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER TEXT SEARCH TEMPLATE`
- Source Line Ranges: `1-37`
- Chunk ID: `pg16_fact_0203_0130c1c741`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `8e6fe7960dbaeb6ddbe2db3ae765b1559170182eb330f75c242946fd64254d25`

## Retrieval Guidance

- Use When: Use for full-text search template metadata syntax.
- Retrieval Keywords: ALTER TEXT SEARCH TEMPLATE, tstemplate owner, text search template
- Follow-up Guidance: No section split needed.
- Classification Note: Text search template object DDL reference for owner, schema, and rename.

## Official Source Content

ALTER TEXT SEARCH TEMPLATE
7
SQL - Language Statements

ALTER TEXT SEARCH TEMPLATE
change the definition of a text search template

```
ALTER TEXT SEARCH TEMPLATE `name` RENAME TO `new_name`
ALTER TEXT SEARCH TEMPLATE `name` SET SCHEMA `new_schema`
```

## Description

`ALTER TEXT SEARCH TEMPLATE` changes the definition of
a text search template.  Currently, the only supported functionality
is to change the template's name.

You must be a superuser to use `ALTER TEXT SEARCH TEMPLATE`.

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing text search template.

**`new_name`**
: The new name of the text search template.

**`new_schema`**
: The new schema for the text search template.

## Compatibility

There is no `ALTER TEXT SEARCH TEMPLATE` statement in
the SQL standard.

## See Also
