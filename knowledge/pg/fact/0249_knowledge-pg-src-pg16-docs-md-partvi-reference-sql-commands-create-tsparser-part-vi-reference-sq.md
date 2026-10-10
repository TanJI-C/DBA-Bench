# CREATE TEXT SEARCH PARSER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_tsparser.md`
- Source Title: `create tsparser`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE TEXT SEARCH PARSER`
- Source Line Ranges: `1-71`
- Chunk ID: `pg16_fact_0249_c85bf977dc`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `833119134496bc9105e46c39387bda3777477481b8043fe4de9f95a765025188`

## Retrieval Guidance

- Use When: Use for text search parser creation syntax.
- Retrieval Keywords: CREATE TEXT SEARCH PARSER, tsparser, start function, token function
- Follow-up Guidance: No section split needed.
- Classification Note: Full-text search parser object creation reference.

## Official Source Content

CREATE TEXT SEARCH PARSER
7
SQL - Language Statements

CREATE TEXT SEARCH PARSER
define a new text search parser

```
CREATE TEXT SEARCH PARSER `name` (
START = `start_function` ,
GETTOKEN = `gettoken_function` ,
END = `end_function` ,
LEXTYPES = `lextypes_function`
[, HEADLINE = `headline_function` ]
)
```

## Description

`CREATE TEXT SEARCH PARSER` creates a new text search
parser.  A text search parser defines a method for splitting a text
string into tokens and assigning types (categories) to the tokens.
A parser is not particularly useful by itself, but must be bound into a
text search configuration along with some text search dictionaries
to be used for searching.

If a schema name is given then the text search parser is created in the
specified schema.  Otherwise it is created in the current schema.

You must be a superuser to use `CREATE TEXT SEARCH PARSER`.
(This restriction is made because an erroneous text search parser
definition could confuse or even crash the server.)

Refer to [textsearch](#textsearch) for further information.

## Parameters

**`name`**
: The name of the text search parser to be created.  The name can be
schema-qualified.

**`start_function`**
: The name of the start function for the parser.

**`gettoken_function`**
: The name of the get-next-token function for the parser.

**`end_function`**
: The name of the end function for the parser.

**`lextypes_function`**
: The name of the lextypes function for the parser (a function that
returns information about the set of token types it produces).

**`headline_function`**
: The name of the headline function for the parser (a function that
summarizes a set of tokens).

The function names can be schema-qualified if necessary.  Argument types
are not given, since the argument list for each type of function is
predetermined.  All except the headline function are required.

The arguments can appear in any order, not only the one shown above.

## Compatibility

There is no
`CREATE TEXT SEARCH PARSER` statement in the SQL
standard.

## See Also
