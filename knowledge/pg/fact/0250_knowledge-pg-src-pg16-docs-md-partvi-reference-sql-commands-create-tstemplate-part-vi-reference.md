# CREATE TEXT SEARCH TEMPLATE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_tstemplate.md`
- Source Title: `create tstemplate`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE TEXT SEARCH TEMPLATE`
- Source Line Ranges: `1-62`
- Chunk ID: `pg16_fact_0250_34bfe5939a`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `e09be2b468edc22a96c1826f7c0e14d3124143da6938032fadd6d2abbf2938f0`

## Retrieval Guidance

- Use When: Use for text search template creation syntax.
- Retrieval Keywords: CREATE TEXT SEARCH TEMPLATE, tstemplate, lexize function
- Follow-up Guidance: No section split needed.
- Classification Note: Full-text search template object creation reference.

## Official Source Content

CREATE TEXT SEARCH TEMPLATE
7
SQL - Language Statements

CREATE TEXT SEARCH TEMPLATE
define a new text search template

```
CREATE TEXT SEARCH TEMPLATE `name` (
[ INIT = `init_function` , ]
LEXIZE = `lexize_function`
)
```

## Description

`CREATE TEXT SEARCH TEMPLATE` creates a new text search
template.  Text search templates define the functions that implement
text search dictionaries.  A template is not useful by itself, but must
be instantiated as a dictionary to be used.  The dictionary typically
specifies parameters to be given to the template functions.

If a schema name is given then the text search template is created in the
specified schema.  Otherwise it is created in the current schema.

You must be a superuser to use `CREATE TEXT SEARCH
TEMPLATE`.  This restriction is made because an erroneous text
search template definition could confuse or even crash the server.
The reason for separating templates from dictionaries is that a template
encapsulates the "unsafe" aspects of defining a dictionary.
The parameters that can be set when defining a dictionary are safe for
unprivileged users to set, and so creating a dictionary need not be a
privileged operation.

Refer to [textsearch](#textsearch) for further information.

## Parameters

**`name`**
: The name of the text search template to be created.  The name can be
schema-qualified.

**`init_function`**
: The name of the init function for the template.

**`lexize_function`**
: The name of the lexize function for the template.

The function names can be schema-qualified if necessary.  Argument types
are not given, since the argument list for each type of function is
predetermined.  The lexize function is required, but the init function
is optional.

The arguments can appear in any order, not only the one shown above.

## Compatibility

There is no
`CREATE TEXT SEARCH TEMPLATE` statement in the SQL
standard.

## See Also
