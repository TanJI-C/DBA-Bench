# DROP TABLE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_table.md`
- Source Title: `drop table`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP TABLE`
- Source Line Ranges: `1-63`
- Chunk ID: `pg16_fact_0290_f2f2e64d3e`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `9a0e4f181510a1ee832e39d3add838e2a7fd57b81eb889f12cd118f03b9a5686`

## Retrieval Guidance

- Use When: Use for table drop syntax and dependency behavior.
- Retrieval Keywords: DROP TABLE, table drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Table removal syntax reference.

## Official Source Content

DROP TABLE
7
SQL - Language Statements

DROP TABLE
remove a table

```
DROP TABLE [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP TABLE` removes tables from the database.
Only the table owner, the schema owner, and superuser can drop a
table.  To empty a table of rows
without destroying the table, use [`DELETE`](#sql-delete)
or [`TRUNCATE`](#sql-truncate).

`DROP TABLE` always removes any indexes, rules,
triggers, and constraints that exist for the target table.
However, to drop a table that is referenced by a view or a foreign-key
constraint of another table, `CASCADE` must be
specified. (`CASCADE` will remove a dependent view entirely,
but in the foreign-key case it will only remove the foreign-key
constraint, not the other table entirely.)

## Parameters

**`IF EXISTS`**
: Do not throw an error if the table does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of the table to drop.

**`CASCADE`**
: Automatically drop objects that depend on the table (such as
views),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the table if any objects depend on it.  This is
the default.

## Examples

To destroy two tables, `films` and
`distributors`:

```
DROP TABLE films, distributors;
```

## Compatibility

This command conforms to the SQL standard, except that the standard only
allows one table to be dropped per command, and apart from the
`IF EXISTS` option, which is a PostgreSQL
extension.

## See Also
