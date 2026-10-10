# DROP PUBLICATION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_publication.md`
- Source Title: `drop publication`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP PUBLICATION`
- Source Line Ranges: `1-45`
- Chunk ID: `pg16_fact_0281_0df222354c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `4f14dfbec7010633dedd48c7987394f0ce271a142895712d1bd083f0b8873214`

## Retrieval Guidance

- Use When: Use for publication drop syntax.
- Retrieval Keywords: DROP PUBLICATION, logical replication publication, publication drop
- Follow-up Guidance: No section split needed.
- Classification Note: Logical replication publication removal syntax reference.

## Official Source Content

DROP PUBLICATION
7
SQL - Language Statements

DROP PUBLICATION
remove a publication

```
DROP PUBLICATION [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP PUBLICATION` removes an existing publication from
the database.

A publication can only be dropped by its owner or a superuser.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the publication does not exist. A notice is
issued in this case.

**`name`**
: The name of an existing publication.

**`CASCADE`**
: These key words do not have any effect, since there are no dependencies
on publications.

## Examples

Drop a publication:

```
DROP PUBLICATION mypublication;
```

## Compatibility

`DROP PUBLICATION` is a PostgreSQL
extension.

## See Also
