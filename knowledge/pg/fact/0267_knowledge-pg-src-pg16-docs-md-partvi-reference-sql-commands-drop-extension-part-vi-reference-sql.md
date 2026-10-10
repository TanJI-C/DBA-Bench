# DROP EXTENSION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_extension.md`
- Source Title: `drop extension`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP EXTENSION`
- Source Line Ranges: `1-60`
- Chunk ID: `pg16_fact_0267_1527a7b578`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `2b43c97b75c39af161e0cfda446cdb9bbe5c6ca2c6675d5c56bf05a0d7f061e8`

## Retrieval Guidance

- Use When: Use for extension drop syntax and dependency handling.
- Retrieval Keywords: DROP EXTENSION, extension removal, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Extension removal syntax reference.

## Official Source Content

DROP EXTENSION
7
SQL - Language Statements

DROP EXTENSION
remove an extension

```
DROP EXTENSION [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP EXTENSION` removes extensions from the database.
Dropping an extension causes its member objects, and other explicitly
dependent routines (see [sql-alterroutine](#sql-alterroutine),
the `DEPENDS ON EXTENSION `extension_name`
` action), to be dropped as well.

You must own the extension to use `DROP EXTENSION`.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the extension does not exist. A notice is issued
in this case.

**`name`**
: The name of an installed extension.

**`CASCADE`**
: Automatically drop objects that depend on the extension,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: This option prevents the specified extensions from being dropped if
other objects, besides these extensions, their members, and their
explicitly dependent routines, depend on them. This is the default.

## Examples

To remove the extension `hstore` from the current
database:

```
DROP EXTENSION hstore;
```

This command will fail if any of `hstore`'s objects
are in use in the database, for example if any tables have columns
of the `hstore` type.  Add the `CASCADE` option to
forcibly remove those dependent objects as well.

## Compatibility

`DROP EXTENSION` is a PostgreSQL
extension.

## See Also
