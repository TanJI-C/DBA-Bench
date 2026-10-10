# DROP FOREIGN DATA WRAPPER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_foreign_data_wrapper.md`
- Source Title: `drop foreign data wrapper`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP FOREIGN DATA WRAPPER`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0268_1aba87d5f8`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `0f3584ff0c108e74b4dde75c655cc6ee8554a03ef9cd7da32f9c08b6c9e4fba7`

## Retrieval Guidance

- Use When: Use for FDW drop syntax.
- Retrieval Keywords: DROP FOREIGN DATA WRAPPER, FDW drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign data wrapper removal syntax reference.

## Official Source Content

DROP FOREIGN DATA WRAPPER
7
SQL - Language Statements

DROP FOREIGN DATA WRAPPER
remove a foreign-data wrapper

```
DROP FOREIGN DATA WRAPPER [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP FOREIGN DATA WRAPPER` removes an existing
foreign-data wrapper.  To execute this command, the current user
must be the owner of the foreign-data wrapper.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the foreign-data wrapper does not
exist.  A notice is issued in this case.

**`name`**
: The name of an existing foreign-data wrapper.

**`CASCADE`**
: Automatically drop objects that depend on the foreign-data
wrapper (such as foreign tables and servers),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the foreign-data wrapper if any objects depend
on it.  This is the default.

## Examples

Drop the foreign-data wrapper `dbi`:

```
DROP FOREIGN DATA WRAPPER dbi;
```

## Compatibility

`DROP FOREIGN DATA WRAPPER` conforms to ISO/IEC
9075-9 (SQL/MED).  The `IF EXISTS` clause is
a PostgreSQL extension.

## See Also
