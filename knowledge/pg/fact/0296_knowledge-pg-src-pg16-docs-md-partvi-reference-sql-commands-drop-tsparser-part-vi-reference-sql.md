# DROP TEXT SEARCH PARSER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_tsparser.md`
- Source Title: `drop tsparser`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TEXT SEARCH PARSER`
- Source Line Ranges: `1-52`
- Chunk ID: `pg16_fact_0296_ef0525e007`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `3291deb8da102b4b51a42374f2185a4f81c556bb2a2bab448561105b4e6f6934`

## Retrieval Guidance

- Use When: Use for text search parser drop syntax.
- Retrieval Keywords: DROP TEXT SEARCH PARSER, tsparser drop, text search
- Follow-up Guidance: No section split needed.
- Classification Note: Text search parser object removal syntax reference.

## Official Source Content

DROP TEXT SEARCH PARSER
7
SQL - Language Statements

DROP TEXT SEARCH PARSER
remove a text search parser

```
DROP TEXT SEARCH PARSER [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP TEXT SEARCH PARSER` drops an existing text search
parser.  You must be a superuser to use this command.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the text search parser does not exist.
A notice is issued in this case.

**`name`**
: The name (optionally schema-qualified) of an existing text search parser.

**`CASCADE`**
: Automatically drop objects that depend on the text search parser,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the text search parser if any objects depend on it.
This is the default.

## Examples

Remove the text search parser `my_parser`:

```
DROP TEXT SEARCH PARSER my_parser;
```

This command will not succeed if there are any existing text search
configurations that use the parser.  Add `CASCADE` to
drop such configurations along with the parser.

## Compatibility

There is no `DROP TEXT SEARCH PARSER` statement in the
SQL standard.

## See Also
