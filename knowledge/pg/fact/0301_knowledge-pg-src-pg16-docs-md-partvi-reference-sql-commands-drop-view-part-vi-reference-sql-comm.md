# DROP VIEW

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_view.md`
- Source Title: `drop view`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP VIEW`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0301_b59aae85fa`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `738b5090a04cb85cf92712126342a4058ee8bc21b58ea2d534b9f7a0ed351bf7`

## Retrieval Guidance

- Use When: Use for view drop syntax and dependency behavior.
- Retrieval Keywords: DROP VIEW, view drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: View removal syntax reference.

## Official Source Content

DROP VIEW
7
SQL - Language Statements

DROP VIEW
remove a view

```
DROP VIEW [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP VIEW` drops an existing view.  To execute
this command you must be the owner of the view.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the view does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of the view to remove.

**`CASCADE`**
: Automatically drop objects that depend on the view (such as
other views),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the view if any objects depend on it.  This is
the default.

## Examples

This command will remove the view called `kinds`:

```
DROP VIEW kinds;
```

## Compatibility

This command conforms to the SQL standard, except that the standard only
allows one view to be dropped per command, and apart from the
`IF EXISTS` option, which is a PostgreSQL
extension.

## See Also
