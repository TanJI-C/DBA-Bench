# DROP SEQUENCE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_sequence.md`
- Source Title: `drop sequence`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP SEQUENCE`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0286_2f9b7f57a9`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `700a9f82060054222e411fbab7b017a4581210fd81b4c5d140d86397dba92e8f`

## Retrieval Guidance

- Use When: Use for sequence drop syntax.
- Retrieval Keywords: DROP SEQUENCE, sequence drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Sequence removal syntax reference.

## Official Source Content

DROP SEQUENCE
7
SQL - Language Statements

DROP SEQUENCE
remove a sequence

```
DROP SEQUENCE [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP SEQUENCE` removes sequence number
generators. A sequence can only be dropped by its owner or a superuser.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the sequence does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of a sequence.

**`CASCADE`**
: Automatically drop objects that depend on the sequence,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the sequence if any objects depend on it.  This
is the default.

## Examples

To remove the sequence `serial`:

```
DROP SEQUENCE serial;
```

## Compatibility

`DROP SEQUENCE` conforms to the SQL
standard, except that the standard only allows one
sequence to be dropped per command, and apart from the
`IF EXISTS` option, which is a PostgreSQL
extension.

## See Also
