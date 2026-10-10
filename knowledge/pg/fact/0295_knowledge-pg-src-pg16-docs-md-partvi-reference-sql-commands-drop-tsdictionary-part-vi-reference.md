# DROP TEXT SEARCH DICTIONARY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_tsdictionary.md`
- Source Title: `drop tsdictionary`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TEXT SEARCH DICTIONARY`
- Source Line Ranges: `1-54`
- Chunk ID: `pg16_fact_0295_fd459c2f7f`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f35bebcfa8211efb2e2107fc0312f038fbbd0130612e27d648e006cd2f8c1058`

## Retrieval Guidance

- Use When: Use for text search dictionary drop syntax.
- Retrieval Keywords: DROP TEXT SEARCH DICTIONARY, tsdictionary drop, text search
- Follow-up Guidance: No section split needed.
- Classification Note: Text search dictionary object removal syntax reference.

## Official Source Content

DROP TEXT SEARCH DICTIONARY
7
SQL - Language Statements

DROP TEXT SEARCH DICTIONARY
remove a text search dictionary

```
DROP TEXT SEARCH DICTIONARY [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP TEXT SEARCH DICTIONARY` drops an existing text
search dictionary.  To execute this command you must be the owner of the
dictionary.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the text search dictionary does not exist.
A notice is issued in this case.

**`name`**
: The name (optionally schema-qualified) of an existing text search
dictionary.

**`CASCADE`**
: Automatically drop objects that depend on the text search dictionary,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the text search dictionary if any objects depend on it.
This is the default.

## Examples

Remove the text search dictionary `english`:

```
DROP TEXT SEARCH DICTIONARY english;
```

This command will not succeed if there are any existing text search
configurations that use the dictionary.  Add `CASCADE` to
drop such configurations along with the dictionary.

## Compatibility

There is no `DROP TEXT SEARCH DICTIONARY` statement in the
SQL standard.

## See Also
