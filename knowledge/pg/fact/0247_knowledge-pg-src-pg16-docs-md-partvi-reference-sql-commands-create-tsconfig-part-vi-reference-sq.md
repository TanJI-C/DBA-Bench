# CREATE TEXT SEARCH CONFIGURATION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_tsconfig.md`
- Source Title: `create tsconfig`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE TEXT SEARCH CONFIGURATION`
- Source Line Ranges: `1-59`
- Chunk ID: `pg16_fact_0247_894517661b`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `91d5f9f4cf9ce1afbf5da990777704d4bc96834bfa7bacc70b176737b68cc748`

## Retrieval Guidance

- Use When: Use for text search configuration object syntax.
- Retrieval Keywords: CREATE TEXT SEARCH CONFIGURATION, tsconfig, parser, text search
- Follow-up Guidance: No section split needed.
- Classification Note: Full-text search configuration object creation reference.

## Official Source Content

CREATE TEXT SEARCH CONFIGURATION
7
SQL - Language Statements

CREATE TEXT SEARCH CONFIGURATION
define a new text search configuration

```
CREATE TEXT SEARCH CONFIGURATION `name` (
PARSER = `parser_name` |
COPY = `source_config`
)
```

## Description

`CREATE TEXT SEARCH CONFIGURATION` creates a new text
search configuration.  A text search configuration specifies a text
search parser that can divide a string into tokens, plus dictionaries
that can be used to determine which tokens are of interest for searching.

If only the parser is specified, then the new text search configuration
initially has no mappings from token types to dictionaries, and therefore
will ignore all words.  Subsequent `ALTER TEXT SEARCH
CONFIGURATION` commands must be used to create mappings to
make the configuration useful.  Alternatively, an existing text search
configuration can be copied.

If a schema name is given then the text search configuration is created in
the specified schema.  Otherwise it is created in the current schema.

The user who defines a text search configuration becomes its owner.

Refer to [textsearch](#textsearch) for further information.

## Parameters

**`name`**
: The name of the text search configuration to be created.  The name can be
schema-qualified.

**`parser_name`**
: The name of the text search parser to use for this configuration.

**`source_config`**
: The name of an existing text search configuration to copy.

## Notes

The `PARSER` and `COPY` options are mutually
exclusive, because when an existing configuration is copied, its
parser selection is copied too.

## Compatibility

There is no `CREATE TEXT SEARCH CONFIGURATION` statement
in the SQL standard.

## See Also
