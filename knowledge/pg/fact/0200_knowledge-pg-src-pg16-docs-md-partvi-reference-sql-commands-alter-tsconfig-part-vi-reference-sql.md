# ALTER TEXT SEARCH CONFIGURATION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_tsconfig.md`
- Source Title: `alter tsconfig`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER TEXT SEARCH CONFIGURATION`
- Source Line Ranges: `1-94`
- Chunk ID: `pg16_fact_0200_9a4fc223cd`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `e8b94e9d8aa191fba91dd32c7af5834d3e4a54b0eebc68b51e26e1f82ac087a9`

## Retrieval Guidance

- Use When: Use for full-text search configuration object syntax.
- Retrieval Keywords: ALTER TEXT SEARCH CONFIGURATION, text search mapping, ALTER MAPPING, tsconfig
- Follow-up Guidance: No section split needed.
- Classification Note: Text search configuration object DDL reference; despite the object name, it is catalog object syntax rather than server parameter configuration.

## Official Source Content

ALTER TEXT SEARCH CONFIGURATION
7
SQL - Language Statements

ALTER TEXT SEARCH CONFIGURATION
change the definition of a text search configuration

```
ALTER TEXT SEARCH CONFIGURATION `name`
ADD MAPPING FOR `token_type` [, ... ] WITH `dictionary_name` [, ... ]
ALTER TEXT SEARCH CONFIGURATION `name`
ALTER MAPPING FOR `token_type` [, ... ] WITH `dictionary_name` [, ... ]
ALTER TEXT SEARCH CONFIGURATION `name`
ALTER MAPPING REPLACE `old_dictionary` WITH `new_dictionary`
ALTER TEXT SEARCH CONFIGURATION `name`
ALTER MAPPING FOR `token_type` [, ... ] REPLACE `old_dictionary` WITH `new_dictionary`
ALTER TEXT SEARCH CONFIGURATION `name`
DROP MAPPING [ IF EXISTS ] FOR `token_type` [, ... ]
ALTER TEXT SEARCH CONFIGURATION `name` RENAME TO `new_name`
ALTER TEXT SEARCH CONFIGURATION `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER TEXT SEARCH CONFIGURATION `name` SET SCHEMA `new_schema`
```

## Description

`ALTER TEXT SEARCH CONFIGURATION` changes the definition of
a text search configuration.  You can modify
its mappings from token types to dictionaries,
or change the configuration's name or owner.

You must be the owner of the configuration to use
`ALTER TEXT SEARCH CONFIGURATION`.

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing text search
configuration.

**`token_type`**
: The name of a token type that is emitted by the configuration's
parser.

**`dictionary_name`**
: The name of a text search dictionary to be consulted for the
specified token type(s).  If multiple dictionaries are listed,
they are consulted in the specified order.

**`old_dictionary`**
: The name of a text search dictionary to be replaced in the mapping.

**`new_dictionary`**
: The name of a text search dictionary to be substituted for
`old_dictionary`.

**`new_name`**
: The new name of the text search configuration.

**`new_owner`**
: The new owner of the text search configuration.

**`new_schema`**
: The new schema for the text search configuration.

The `ADD MAPPING FOR` form installs a list of dictionaries to be
consulted for the specified token type(s); it is an error if there is
already a mapping for any of the token types.
The `ALTER MAPPING FOR` form does the same, but first removing
any existing mapping for those token types.
The `ALTER MAPPING REPLACE` forms substitute `new_dictionary` for `old_dictionary` anywhere the latter appears.
This is done for only the specified token types when `FOR`
appears, or for all mappings of the configuration when it doesn't.
The `DROP MAPPING` form removes all dictionaries for the
specified token type(s), causing tokens of those types to be ignored
by the text search configuration.  It is an error if there is no mapping
for the token types, unless `IF EXISTS` appears.

## Examples

The following example replaces the `english` dictionary
with the `swedish` dictionary anywhere that `english`
is used within `my_config`.

```
ALTER TEXT SEARCH CONFIGURATION my_config
ALTER MAPPING REPLACE english WITH swedish;
```

## Compatibility

There is no `ALTER TEXT SEARCH CONFIGURATION` statement in
the SQL standard.

## See Also
