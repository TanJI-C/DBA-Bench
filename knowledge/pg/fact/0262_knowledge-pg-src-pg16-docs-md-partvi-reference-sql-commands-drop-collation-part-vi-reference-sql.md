# DROP COLLATION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_collation.md`
- Source Title: `drop collation`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP COLLATION`
- Source Line Ranges: `1-50`
- Chunk ID: `pg16_fact_0262_9edf431002`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ccb045d2d750136a144d16ad3d99aad4ea9ada501cb7da51c5174597433582ff`

## Retrieval Guidance

- Use When: Use for collation drop syntax.
- Retrieval Keywords: DROP COLLATION, collation object, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Collation object removal syntax reference.

## Official Source Content

DROP COLLATION
7
SQL - Language Statements

DROP COLLATION
remove a collation

```
DROP COLLATION [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP COLLATION` removes a previously defined collation.
To be able to drop a collation, you must own the collation.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the collation does not exist.
A notice is issued in this case.

**`name`**
: The name of the collation. The collation name can be
schema-qualified.

**`CASCADE`**
: Automatically drop objects that depend on the collation,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the collation if any objects depend on it.  This
is the default.

## Examples

To drop the collation named `german`:

```
DROP COLLATION german;
```

## Compatibility

The `DROP COLLATION` command conforms to the
SQL standard, apart from the `IF
EXISTS` option, which is a PostgreSQL extension.

## See Also
