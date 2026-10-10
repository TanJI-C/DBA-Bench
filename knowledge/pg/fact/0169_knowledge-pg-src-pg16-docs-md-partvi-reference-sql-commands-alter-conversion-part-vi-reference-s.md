# ALTER CONVERSION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_conversion.md`
- Source Title: `alter conversion`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER CONVERSION`
- Source Line Ranges: `1-63`
- Chunk ID: `pg16_fact_0169_9a70863bc4`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `10a22f1404240ac8c2450eb8ac6ffe59727e734a117a2ae31a9d8b964aace1d5`

## Retrieval Guidance

- Use When: Use for conversion object syntax and metadata changes.
- Retrieval Keywords: ALTER CONVERSION, conversion rename, conversion owner, conversion schema
- Follow-up Guidance: No section split needed.
- Classification Note: Object-reference DDL for changing conversion name, owner, or schema.

## Official Source Content

ALTER CONVERSION
7
SQL - Language Statements

ALTER CONVERSION
change the definition of a conversion

```
ALTER CONVERSION `name` RENAME TO `new_name`
ALTER CONVERSION `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER CONVERSION `name` SET SCHEMA `new_schema`
```

## Description

`ALTER CONVERSION` changes the definition of a
conversion.

You must own the conversion to use `ALTER CONVERSION`.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have `CREATE`
privilege on the conversion's schema.
(These restrictions enforce that altering the
owner doesn't do anything you couldn't do by dropping and recreating the
conversion. However, a superuser can alter ownership of any conversion
anyway.)

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing conversion.

**`new_name`**
: The new name of the conversion.

**`new_owner`**
: The new owner of the conversion.

**`new_schema`**
: The new schema for the conversion.

## Examples

To rename the conversion `iso_8859_1_to_utf8` to
`latin1_to_unicode`:

```
ALTER CONVERSION iso_8859_1_to_utf8 RENAME TO latin1_to_unicode;
```

To change the owner of the conversion `iso_8859_1_to_utf8` to
`joe`:

```
ALTER CONVERSION iso_8859_1_to_utf8 OWNER TO joe;
```

## Compatibility

There is no `ALTER CONVERSION` statement in the SQL
standard.

## See Also
