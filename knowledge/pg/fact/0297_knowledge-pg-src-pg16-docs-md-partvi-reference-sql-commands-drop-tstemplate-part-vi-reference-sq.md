# DROP TEXT SEARCH TEMPLATE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_tstemplate.md`
- Source Title: `drop tstemplate`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TEXT SEARCH TEMPLATE`
- Source Line Ranges: `1-53`
- Chunk ID: `pg16_fact_0297_266614057c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `5572349377b483d8153bce953d5452ac251ab0593e5c898c5eabec3d010aa2b6`

## Retrieval Guidance

- Use When: Use for text search template drop syntax.
- Retrieval Keywords: DROP TEXT SEARCH TEMPLATE, tstemplate drop, text search
- Follow-up Guidance: No section split needed.
- Classification Note: Text search template object removal syntax reference.

## Official Source Content

DROP TEXT SEARCH TEMPLATE
7
SQL - Language Statements

DROP TEXT SEARCH TEMPLATE
remove a text search template

```
DROP TEXT SEARCH TEMPLATE [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP TEXT SEARCH TEMPLATE` drops an existing text search
template.  You must be a superuser to use this command.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the text search template does not exist.
A notice is issued in this case.

**`name`**
: The name (optionally schema-qualified) of an existing text search
template.

**`CASCADE`**
: Automatically drop objects that depend on the text search template,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the text search template if any objects depend on it.
This is the default.

## Examples

Remove the text search template `thesaurus`:

```
DROP TEXT SEARCH TEMPLATE thesaurus;
```

This command will not succeed if there are any existing text search
dictionaries that use the template.  Add `CASCADE` to
drop such dictionaries along with the template.

## Compatibility

There is no `DROP TEXT SEARCH TEMPLATE` statement in the
SQL standard.

## See Also
