# DROP TRANSFORM

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_transform.md`
- Source Title: `drop transform`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TRANSFORM`
- Source Line Ranges: `1-54`
- Chunk ID: `pg16_fact_0292_a07c417d44`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `dd58e2082bcb50add0ccf4272f81a810306b211fb5a06aeab7b0cdf1c4749ba0`

## Retrieval Guidance

- Use When: Use for transform drop syntax.
- Retrieval Keywords: DROP TRANSFORM, transform drop, language transform
- Follow-up Guidance: No section split needed.
- Classification Note: Transform object removal syntax reference.

## Official Source Content

DROP TRANSFORM
7
SQL - Language Statements

DROP TRANSFORM
remove a transform

```
DROP TRANSFORM [ IF EXISTS ] FOR `type_name` LANGUAGE `lang_name` [ CASCADE | RESTRICT ]
```

## Description

`DROP TRANSFORM` removes a previously defined transform.

To be able to drop a transform, you must own the type and the language.
These are the same privileges that are required to create a transform.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the transform does not exist. A notice is issued
in this case.

**`type_name`**
: The name of the data type of the transform.

**`lang_name`**
: The name of the language of the transform.

**`CASCADE`**
: Automatically drop objects that depend on the transform,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the transform if any objects depend on it.  This is the
default.

## Examples

To drop the transform for type `hstore` and language
`plpython3u`:

```
DROP TRANSFORM FOR hstore LANGUAGE plpython3u;
```

## Compatibility

This form of `DROP TRANSFORM` is a
PostgreSQL extension.  See [sql-createtransform](#sql-createtransform) for details.

## See Also
