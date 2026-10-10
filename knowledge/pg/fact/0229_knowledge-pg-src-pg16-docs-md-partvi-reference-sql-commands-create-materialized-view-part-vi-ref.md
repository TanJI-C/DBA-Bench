# CREATE MATERIALIZED VIEW

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_materialized_view.md`
- Source Title: `create materialized view`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE MATERIALIZED VIEW`
- Source Line Ranges: `1-93`
- Chunk ID: `pg16_fact_0229_bec88e5f1a`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `7f35c8fcca5b8b8659dbac28eedb7a70c3bbf41db784ec32c1b7af1f6c029ae7`

## Retrieval Guidance

- Use When: Use for materialized view creation syntax and storage options.
- Retrieval Keywords: CREATE MATERIALIZED VIEW, materialized view, WITH DATA, WITH NO DATA, TABLESPACE
- Follow-up Guidance: Use REFRESH MATERIALIZED VIEW for stale-content remediation.
- Classification Note: Materialized view object creation reference; not itself a diagnostic signal or repair action.

## Official Source Content

CREATE MATERIALIZED VIEW
7
SQL - Language Statements

CREATE MATERIALIZED VIEW
define a new materialized view

```
CREATE MATERIALIZED VIEW [ IF NOT EXISTS ] `table_name`
[ (`column_name` [, ...] ) ]
[ USING `method` ]
[ WITH ( `storage_parameter` [= `value`] [, ... ] ) ]
[ TABLESPACE `tablespace_name` ]
AS `query`
[ WITH [ NO ] DATA ]
```

## Description

`CREATE MATERIALIZED VIEW` defines a materialized view of
a query.  The query is executed and used to populate the view at the time
the command is issued (unless `WITH NO DATA` is used) and may be
refreshed later using `REFRESH MATERIALIZED VIEW`.

`CREATE MATERIALIZED VIEW` is similar to
`CREATE TABLE AS`, except that it also remembers the query used
to initialize the view, so that it can be refreshed later upon demand.
A materialized view has many of the same properties as a table, but there
is no support for temporary materialized views.

`CREATE MATERIALIZED VIEW` requires
`CREATE` privilege on the schema used for the materialized
view.

## Parameters

**`IF NOT EXISTS`**
: Do not throw an error if a materialized view with the same name already
exists. A notice is issued in this case.  Note that there is no guarantee
that the existing materialized view is anything like the one that would
have been created.

**`table_name`**
: The name (optionally schema-qualified) of the materialized view to be
created.  The name must be distinct from the name of any other relation
(table, sequence, index, view, materialized view, or foreign table) in
the same schema.

**`column_name`**
: The name of a column in the new materialized view.  If column names are
not provided, they are taken from the output column names of the query.

**`USING `method``**
: This optional clause specifies the table access method to use to store
the contents for the new materialized view; the method needs be an
access method of type `TABLE`. See [tableam](#tableam) for more information.  If this option is not
specified, the default table access method is chosen for the new
materialized view. See [guc-default-table-access-method](#guc-default-table-access-method)
for more information.

**`WITH ( `storage_parameter` [= `value`] [, ... ] )`**
: This clause specifies optional storage parameters for the new
materialized view; see
[sql-createtable-storage-parameters](#sql-createtable-storage-parameters) in the
[sql-createtable](#sql-createtable) documentation for more
information.  All parameters supported for `CREATE
TABLE` are also supported for `CREATE MATERIALIZED
VIEW`.
See [sql-createtable](#sql-createtable) for more information.

**`TABLESPACE `tablespace_name``**
: The `tablespace_name` is the name
of the tablespace in which the new materialized view is to be created.
If not specified, [guc-default-tablespace](#guc-default-tablespace) is consulted.

**`query`**
: A [`SELECT`](#sql-select), [`TABLE`](#sql-table),
or [`VALUES`](#sql-values) command.  This query will run within a
security-restricted operation; in particular, calls to functions that
themselves create temporary tables will fail.

**`WITH [ NO ] DATA`**
: This clause specifies whether or not the materialized view should be
populated at creation time.  If not, the materialized view will be
flagged as unscannable and cannot be queried until `REFRESH
MATERIALIZED VIEW` is used.

## Compatibility

`CREATE MATERIALIZED VIEW` is a
PostgreSQL extension.

## See Also
