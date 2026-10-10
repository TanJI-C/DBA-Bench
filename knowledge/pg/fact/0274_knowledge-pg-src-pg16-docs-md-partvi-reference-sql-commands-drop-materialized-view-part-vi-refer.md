# DROP MATERIALIZED VIEW

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_materialized_view.md`
- Source Title: `drop materialized view`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP MATERIALIZED VIEW`
- Source Line Ranges: `1-52`
- Chunk ID: `pg16_fact_0274_f445ebb891`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `3cbf89e69afade44d0d9153f7d129254e5f163d6e8bb961b60f201857dbfb5c5`

## Retrieval Guidance

- Use When: Use for materialized view drop syntax.
- Retrieval Keywords: DROP MATERIALIZED VIEW, materialized view drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Materialized view removal syntax reference.

## Official Source Content

DROP MATERIALIZED VIEW
7
SQL - Language Statements

DROP MATERIALIZED VIEW
remove a materialized view

```
DROP MATERIALIZED VIEW [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP MATERIALIZED VIEW` drops an existing materialized
view. To execute this command you must be the owner of the materialized
view.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the materialized view does not exist. A notice
is issued in this case.

**`name`**
: The name (optionally schema-qualified) of the materialized view to
remove.

**`CASCADE`**
: Automatically drop objects that depend on the materialized view (such as
other materialized views, or regular views),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the materialized view if any objects depend on it.  This
is the default.

## Examples

This command will remove the materialized view called
`order_summary`:

```
DROP MATERIALIZED VIEW order_summary;
```

## Compatibility

`DROP MATERIALIZED VIEW` is a
PostgreSQL extension.

## See Also
