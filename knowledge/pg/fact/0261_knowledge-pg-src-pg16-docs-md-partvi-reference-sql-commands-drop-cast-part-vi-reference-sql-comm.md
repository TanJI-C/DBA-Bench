# DROP CAST

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_cast.md`
- Source Title: `drop cast`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP CAST`
- Source Line Ranges: `1-48`
- Chunk ID: `pg16_fact_0261_401c141b45`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `1a8770ddecc72a634e12b895c0ff4b551e9b07db234065fa5e8f2c1aeeb0d8fa`

## Retrieval Guidance

- Use When: Use for cast drop syntax.
- Retrieval Keywords: DROP CAST, type cast, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Cast object removal syntax reference.

## Official Source Content

DROP CAST
7
SQL - Language Statements

DROP CAST
remove a cast

```
DROP CAST [ IF EXISTS ] (`source_type` AS `target_type`) [ CASCADE | RESTRICT ]
```

## Description

`DROP CAST` removes a previously defined cast.

To be able to drop a cast, you must own the source or the target
data type.  These are the same privileges that are required to
create a cast.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the cast does not exist. A notice is issued
in this case.

**`source_type`**
: The name of the source data type of the cast.

**`target_type`**
: The name of the target data type of the cast.

**`CASCADE`**
: These key words do not have any effect, since there are no
dependencies on casts.

## Examples

To drop the cast from type `text` to type `int`:

```
DROP CAST (text AS int);
```

## Compatibility

The `DROP CAST` command conforms to the SQL standard.

## See Also
