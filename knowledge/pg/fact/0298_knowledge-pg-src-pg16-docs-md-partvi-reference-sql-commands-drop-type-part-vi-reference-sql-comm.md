# DROP TYPE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_type.md`
- Source Title: `drop type`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TYPE`
- Source Line Ranges: `1-53`
- Chunk ID: `pg16_fact_0298_2ac59881fa`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `5e597cd28481e121909aced36f0f89b6575efbd74e09967cd014c24c277ded24`

## Retrieval Guidance

- Use When: Use for type drop syntax and dependency behavior.
- Retrieval Keywords: DROP TYPE, type drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Type object removal syntax reference.

## Official Source Content

DROP TYPE
7
SQL - Language Statements

DROP TYPE
remove a data type

```
DROP TYPE [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP TYPE` removes a user-defined data type.
Only the owner of a type can remove it.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the type does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of the data type to remove.

**`CASCADE`**
: Automatically drop objects that depend on the type (such as
table columns, functions, and operators),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the type if any objects depend on it.  This is
the default.

## Examples

To remove the data type `box`:

```
DROP TYPE box;
```

## Compatibility

This command is similar to the corresponding command in the SQL
standard, apart from the `IF EXISTS`
option, which is a PostgreSQL extension.
But note that much of the `CREATE TYPE` command
and the data type extension mechanisms in
PostgreSQL differ from the SQL standard.

## See Also
