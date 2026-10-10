# IMPORT FOREIGN SCHEMA

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/import_foreign_schema.md`
- Source Title: `import foreign schema`
- Source Heading Path: `Part VI Reference > SQL Commands > IMPORT FOREIGN SCHEMA`
- Source Line Ranges: `1-83`
- Chunk ID: `pg16_fact_0307_6fe752a699`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `4cf17ba1ddf55c56faed29883aa25055692cd4dadb77961ead47ae1bf28f32f0`

## Retrieval Guidance

- Use When: Use for importing foreign table definitions from a foreign server.
- Retrieval Keywords: IMPORT FOREIGN SCHEMA, foreign tables, FDW, LIMIT TO, EXCEPT
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign schema import syntax reference.

## Official Source Content

IMPORT FOREIGN SCHEMA
7
SQL - Language Statements

IMPORT FOREIGN SCHEMA
import table definitions from a foreign server

```
IMPORT FOREIGN SCHEMA `remote_schema`
[ { LIMIT TO | EXCEPT } ( `table_name` [, ...] ) ]
FROM SERVER `server_name`
INTO `local_schema`
[ OPTIONS ( `option` '`value`' [, ... ] ) ]
```

## Description

`IMPORT FOREIGN SCHEMA` creates foreign tables that
represent tables existing on a foreign server.  The new foreign tables
will be owned by the user issuing the command and are created with
the correct column definitions and options to match the remote tables.

By default, all tables and views existing in a particular schema on the
foreign server are imported.  Optionally, the list of tables can be limited
to a specified subset, or specific tables can be excluded.  The new foreign
tables are all created in the target schema, which must already exist.

To use `IMPORT FOREIGN SCHEMA`, the user must have
`USAGE` privilege on the foreign server, as well as
`CREATE` privilege on the target schema.

## Parameters

**`remote_schema`**
: The remote schema to import from. The specific meaning of a remote schema
depends on the foreign data wrapper in use.

**`LIMIT TO ( `table_name` [, ...] )`**
: Import only foreign tables matching one of the given table names.
Other tables existing in the foreign schema will be ignored.

**`EXCEPT ( `table_name` [, ...] )`**
: Exclude specified foreign tables from the import.  All tables
existing in the foreign schema will be imported except the
ones listed here.

**`server_name`**
: The foreign server to import from.

**`local_schema`**
: The schema in which the imported foreign tables will be created.

**`OPTIONS ( `option` '`value`' [, ...] )`**
: Options to be used during the import.
The allowed option names and values are specific to each foreign
data wrapper.

## Examples

Import table definitions from a remote schema `foreign_films`
on server `film_server`, creating the foreign tables in
local schema `films`:

```
IMPORT FOREIGN SCHEMA foreign_films
FROM SERVER film_server INTO films;
```

As above, but import only the two tables `actors` and
`directors` (if they exist):

```
IMPORT FOREIGN SCHEMA foreign_films LIMIT TO (actors, directors)
FROM SERVER film_server INTO films;
```

## Compatibility

The `IMPORT FOREIGN SCHEMA` command conforms to the
SQL standard, except that the `OPTIONS`
clause is a PostgreSQL extension.

## See Also
