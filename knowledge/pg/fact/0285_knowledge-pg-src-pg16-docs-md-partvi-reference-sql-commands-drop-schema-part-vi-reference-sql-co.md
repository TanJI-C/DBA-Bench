# DROP SCHEMA

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_schema.md`
- Source Title: `drop schema`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP SCHEMA`
- Source Line Ranges: `1-61`
- Chunk ID: `pg16_fact_0285_cd49e87182`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `43d18f06046b54aec619d40f67b3646939b99c3413ba720feec39efb2658c865`

## Retrieval Guidance

- Use When: Use for schema drop syntax and dependency behavior.
- Retrieval Keywords: DROP SCHEMA, schema drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Schema removal syntax reference.

## Official Source Content

DROP SCHEMA
7
SQL - Language Statements

DROP SCHEMA
remove a schema

```
DROP SCHEMA [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP SCHEMA` removes schemas from the database.

A schema can only be dropped by its owner or a superuser.  Note that
the owner can drop the schema (and thereby all contained objects)
even if they do not own some of the objects within the schema.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the schema does not exist. A notice is issued
in this case.

**`name`**
: The name of a schema.

**`CASCADE`**
: Automatically drop objects (tables, functions, etc.) that are
contained in the schema,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the schema if it contains any objects.  This is
the default.

## Notes

Using the `CASCADE` option might make the command
remove objects in other schemas besides the one(s) named.

## Examples

To remove schema `mystuff` from the database,
along with everything it contains:

```
DROP SCHEMA mystuff CASCADE;
```

## Compatibility

`DROP SCHEMA` is fully conforming with the SQL
standard, except that the standard only allows one schema to be
dropped per command, and apart from the
`IF EXISTS` option, which is a PostgreSQL
extension.

## See Also
