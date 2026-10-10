# ALTER SCHEMA

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_schema.md`
- Source Title: `alter schema`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER SCHEMA`
- Source Line Ranges: `1-43`
- Chunk ID: `pg16_fact_0192_62e8a19d85`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `1d3d924ccdfe08c837301ddc57335fbc54ae47711f499a17dc0a1162a033debd`

## Retrieval Guidance

- Use When: Use for schema metadata syntax.
- Retrieval Keywords: ALTER SCHEMA, schema rename, schema owner
- Follow-up Guidance: No section split needed.
- Classification Note: Schema object DDL reference for rename and owner changes.

## Official Source Content

ALTER SCHEMA
7
SQL - Language Statements

ALTER SCHEMA
change the definition of a schema

```
ALTER SCHEMA `name` RENAME TO `new_name`
ALTER SCHEMA `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
```

## Description

`ALTER SCHEMA` changes the definition of a schema.

You must own the schema to use `ALTER SCHEMA`.
To rename a schema you must also have the
`CREATE` privilege for the database.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have the
`CREATE` privilege for the database.
(Note that superusers have all these privileges automatically.)

## Parameters

**`name`**
: The name of an existing schema.

**`new_name`**
: The new name of the schema.  The new name cannot
begin with `pg_`, as such names
are reserved for system schemas.

**`new_owner`**
: The new owner of the schema.

## Compatibility

There is no `ALTER SCHEMA` statement in the SQL
standard.

## See Also
