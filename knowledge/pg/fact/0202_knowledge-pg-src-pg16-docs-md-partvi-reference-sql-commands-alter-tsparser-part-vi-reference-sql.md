# ALTER TEXT SEARCH PARSER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_tsparser.md`
- Source Title: `alter tsparser`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER TEXT SEARCH PARSER`
- Source Line Ranges: `1-37`
- Chunk ID: `pg16_fact_0202_3f8f0e7ae2`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `0ceaf378b00f1b9aada7c3a5fc1b6370e7f4a9f316a748312957479124c65a46`

## Retrieval Guidance

- Use When: Use for full-text search parser metadata syntax.
- Retrieval Keywords: ALTER TEXT SEARCH PARSER, tsparser owner, text search parser
- Follow-up Guidance: No section split needed.
- Classification Note: Text search parser object DDL reference for owner, schema, and rename.

## Official Source Content

ALTER TEXT SEARCH PARSER
7
SQL - Language Statements

ALTER TEXT SEARCH PARSER
change the definition of a text search parser

```
ALTER TEXT SEARCH PARSER `name` RENAME TO `new_name`
ALTER TEXT SEARCH PARSER `name` SET SCHEMA `new_schema`
```

## Description

`ALTER TEXT SEARCH PARSER` changes the definition of
a text search parser.  Currently, the only supported functionality
is to change the parser's name.

You must be a superuser to use `ALTER TEXT SEARCH PARSER`.

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing text search parser.

**`new_name`**
: The new name of the text search parser.

**`new_schema`**
: The new schema for the text search parser.

## Compatibility

There is no `ALTER TEXT SEARCH PARSER` statement in
the SQL standard.

## See Also
