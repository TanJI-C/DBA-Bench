# DROP TEXT SEARCH CONFIGURATION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_tsconfig.md`
- Source Title: `drop tsconfig`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TEXT SEARCH CONFIGURATION`
- Source Line Ranges: `1-55`
- Chunk ID: `pg16_fact_0294_aceb533c02`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `258f36ca05c923ff9bd1ccc8f2768088b8c96f6a5599639dca65da5b9446b88f`

## Retrieval Guidance

- Use When: Use for text search configuration drop syntax.
- Retrieval Keywords: DROP TEXT SEARCH CONFIGURATION, tsconfig drop, text search
- Follow-up Guidance: No section split needed.
- Classification Note: Text search configuration object removal syntax reference.

## Official Source Content

DROP TEXT SEARCH CONFIGURATION
7
SQL - Language Statements

DROP TEXT SEARCH CONFIGURATION
remove a text search configuration

```
DROP TEXT SEARCH CONFIGURATION [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP TEXT SEARCH CONFIGURATION` drops an existing text
search configuration.  To execute this command you must be the owner of the
configuration.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the text search configuration does not exist.
A notice is issued in this case.

**`name`**
: The name (optionally schema-qualified) of an existing text search
configuration.

**`CASCADE`**
: Automatically drop objects that depend on the text search configuration,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the text search configuration if any objects depend on it.
This is the default.

## Examples

Remove the text search configuration `my_english`:

```
DROP TEXT SEARCH CONFIGURATION my_english;
```

This command will not succeed if there are any existing indexes
that reference the configuration in `to_tsvector` calls.
Add `CASCADE` to
drop such indexes along with the text search configuration.

## Compatibility

There is no `DROP TEXT SEARCH CONFIGURATION` statement in
the SQL standard.

## See Also
