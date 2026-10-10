# DROP ACCESS METHOD

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_access_method.md`
- Source Title: `drop access method`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP ACCESS METHOD`
- Source Line Ranges: `1-49`
- Chunk ID: `pg16_fact_0259_b36c68c504`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `5d87821e460aa3af7562f4aaaf1c3ee7ee52ca43ba5a3759b0a8742b80f25061`

## Retrieval Guidance

- Use When: Use for access method drop syntax.
- Retrieval Keywords: DROP ACCESS METHOD, access method, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Access method object removal syntax reference.

## Official Source Content

DROP ACCESS METHOD
7
SQL - Language Statements

DROP ACCESS METHOD
remove an access method

```
DROP ACCESS METHOD [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP ACCESS METHOD` removes an existing access method.
Only superusers can drop access methods.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the access method does not exist.
A notice is issued in this case.

**`name`**
: The name of an existing access method.

**`CASCADE`**
: Automatically drop objects that depend on the access method
(such as operator classes, operator families, and indexes),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the access method if any objects depend on it.
This is the default.

## Examples

Drop the access method `heptree`:

```
DROP ACCESS METHOD heptree;
```

## Compatibility

`DROP ACCESS METHOD` is a
PostgreSQL extension.

## See Also
