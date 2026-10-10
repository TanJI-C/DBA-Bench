# SELECT INTO

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/select_into.md`
- Source Title: `select into`
- Source Heading Path: `Part VI Reference > SQL Commands > SELECT INTO`
- Source Line Ranges: `1-90`
- Chunk ID: `pg16_fact_0326_f7abc5f3c9`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `3f67381a562b818551c66a0f0f37484f5d431d3933c5e95b024bfdab802c6cff`

## Retrieval Guidance

- Use When: Use for SELECT INTO syntax and compatibility notes.
- Retrieval Keywords: SELECT INTO, create table as, query result table
- Follow-up Guidance: Prefer CREATE TABLE AS in new guidance where appropriate.
- Classification Note: Table creation from query result syntax reference; PostgreSQL extension/legacy form.

## Official Source Content

SELECT INTO
7
SQL - Language Statements

SELECT INTO
define a new table from the results of a query

```
[ WITH [ RECURSIVE ] `with_query` [, ...] ]
SELECT [ ALL | DISTINCT [ ON ( `expression` [, ...] ) ] ]
[ { * | `expression` [ [ AS ] `output_name` ] } [, ...] ]
INTO [ TEMPORARY | TEMP | UNLOGGED ] [ TABLE ] `new_table`
[ FROM `from_item` [, ...] ]
[ WHERE `condition` ]
[ GROUP BY `expression` [, ...] ]
[ HAVING `condition` ]
[ WINDOW `window_name` AS ( `window_definition` ) [, ...] ]
[ { UNION | INTERSECT | EXCEPT } [ ALL | DISTINCT ] `select` ]
[ ORDER BY `expression` [ ASC | DESC | USING `operator` ] [ NULLS { FIRST | LAST } ] [, ...] ]
[ LIMIT { `count` | ALL } ]
[ OFFSET `start` [ ROW | ROWS ] ]
[ FETCH { FIRST | NEXT } [ `count` ] { ROW | ROWS } ONLY ]
[ FOR { UPDATE | SHARE } [ OF `table_name` [, ...] ] [ NOWAIT ] [...] ]
```

## Description

`SELECT INTO` creates a new table and fills it
with data computed by a query.  The data is not returned to the
client, as it is with a normal `SELECT`.  The new
table's columns have the names and data types associated with the
output columns of the `SELECT`.

## Parameters

**`TEMPORARY` or `TEMP`**
: If specified, the table is created as a temporary table.  Refer
to [sql-createtable](#sql-createtable) for details.

**`UNLOGGED`**
: If specified, the table is created as an unlogged table.  Refer
to [sql-createtable](#sql-createtable) for details.

**`new_table`**
: The name (optionally schema-qualified) of the table to be created.

All other parameters are described in detail under [sql-select](#sql-select).

## Notes

[`CREATE TABLE AS`](#sql-createtableas) is functionally similar to
`SELECT INTO`.  `CREATE TABLE AS`
is the recommended syntax, since this form of `SELECT
INTO` is not available in ECPG
or PL/pgSQL, because they interpret the
`INTO` clause differently. Furthermore,
`CREATE TABLE AS` offers a superset of the
functionality provided by `SELECT INTO`.

In contrast to `CREATE TABLE AS`, `SELECT
INTO` does not allow specifying properties like a table's access
method with [sql-createtable-method](#sql-createtable-method) or the table's
tablespace with [sql-createtable-tablespace](#sql-createtable-tablespace). Use
`CREATE TABLE AS` if necessary.  Therefore, the default table
access method is chosen for the new table. See [guc-default-table-access-method](#guc-default-table-access-method) for more information.

## Examples

Create a new table `films_recent` consisting of only
recent entries from the table `films`:

```
SELECT * INTO films_recent FROM films WHERE date_prod >= '2002-01-01';
```

## Compatibility

The SQL standard uses `SELECT INTO` to
represent selecting values into scalar variables of a host program,
rather than creating a new table.  This indeed is the usage found
in ECPG (see [ecpg](#ecpg)) and
PL/pgSQL (see [plpgsql](#plpgsql)).
The PostgreSQL usage of `SELECT
INTO` to represent table creation is historical.  Some other SQL
implementations also use `SELECT INTO` in this way (but
most SQL implementations support `CREATE TABLE AS`
instead).  Apart from such compatibility considerations, it is best to use
`CREATE TABLE AS` for this purpose in new code.

## See Also
