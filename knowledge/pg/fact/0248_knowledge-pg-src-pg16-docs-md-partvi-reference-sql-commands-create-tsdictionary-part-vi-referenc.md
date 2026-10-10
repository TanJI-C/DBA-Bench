# CREATE TEXT SEARCH DICTIONARY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_tsdictionary.md`
- Source Title: `create tsdictionary`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE TEXT SEARCH DICTIONARY`
- Source Line Ranges: `1-69`
- Chunk ID: `pg16_fact_0248_d69df7bd71`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `9e7aeafe5c35d5ef756c9dd0d99711f6bdb51a714bc4dd49c371f2bfff54ac58`

## Retrieval Guidance

- Use When: Use for text search dictionary creation syntax.
- Retrieval Keywords: CREATE TEXT SEARCH DICTIONARY, tsdictionary, dictionary template, text search
- Follow-up Guidance: No section split needed.
- Classification Note: Full-text search dictionary object creation reference.

## Official Source Content

CREATE TEXT SEARCH DICTIONARY
7
SQL - Language Statements

CREATE TEXT SEARCH DICTIONARY
define a new text search dictionary

```
CREATE TEXT SEARCH DICTIONARY `name` (
TEMPLATE = `template`
[, `option` = `value` [, ... ]]
)
```

## Description

`CREATE TEXT SEARCH DICTIONARY` creates a new text search
dictionary.  A text search dictionary specifies a way of recognizing
interesting or uninteresting words for searching.  A dictionary depends
on a text search template, which specifies the functions that actually
perform the work.  Typically the dictionary provides some options that
control the detailed behavior of the template's functions.

If a schema name is given then the text search dictionary is created in the
specified schema.  Otherwise it is created in the current schema.

The user who defines a text search dictionary becomes its owner.

Refer to [textsearch](#textsearch) for further information.

## Parameters

**`name`**
: The name of the text search dictionary to be created.  The name can be
schema-qualified.

**`template`**
: The name of the text search template that will define the basic
behavior of this dictionary.

**`option`**
: The name of a template-specific option to be set for this dictionary.

**`value`**
: The value to use for a template-specific option.  If the value
is not a simple identifier or number, it must be quoted (but you can
always quote it, if you wish).

The options can appear in any order.

## Examples

The following example command creates a Snowball-based dictionary
with a nonstandard list of stop words.

```
CREATE TEXT SEARCH DICTIONARY my_russian (
template = snowball,
language = russian,
stopwords = myrussian
);
```

## Compatibility

There is no `CREATE TEXT SEARCH DICTIONARY` statement in
the SQL standard.

## See Also
