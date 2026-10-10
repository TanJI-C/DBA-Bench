# DROP SERVER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_server.md`
- Source Title: `drop server`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP SERVER`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0287_2915307c9d`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `b7ef00d68bbc4ec5bf4c0d9d85b60a316212a29e76f6361a06f7933070444fda`

## Retrieval Guidance

- Use When: Use for foreign server drop syntax.
- Retrieval Keywords: DROP SERVER, foreign server drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign server removal syntax reference.

## Official Source Content

DROP SERVER
7
SQL - Language Statements

DROP SERVER
remove a foreign server descriptor

```
DROP SERVER [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP SERVER` removes an existing foreign server
descriptor.  To execute this command, the current user must be the
owner of the server.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the server does not exist.  A notice is
issued in this case.

**`name`**
: The name of an existing server.

**`CASCADE`**
: Automatically drop objects that depend on the server (such as
user mappings),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the server if any objects depend on it.  This is
the default.

## Examples

Drop a server `foo` if it exists:

```
DROP SERVER IF EXISTS foo;
```

## Compatibility

`DROP SERVER` conforms to ISO/IEC 9075-9
(SQL/MED).  The `IF EXISTS` clause is
a PostgreSQL extension.

## See Also
