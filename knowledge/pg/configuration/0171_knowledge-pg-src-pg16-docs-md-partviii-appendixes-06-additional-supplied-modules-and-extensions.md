# file_fdw - access data files in the server file system; Create a Foreign Table for PostgreSQL CSV Logs

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > file_fdw - access data files in the server file system; Create a Foreign Table for PostgreSQL CSV Logs`
- Source Line Ranges: `3170-3227`
- Chunk ID: `pg16_configuration_0171_6c49f616cb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `229d372322dc42037f744b81bf5b63e2421c1adbef14a8ac376602ffac199ad3`

## Retrieval Guidance

- Use When: Configure access to server-side files or PostgreSQL CSV logs through file_fdw.
- Retrieval Keywords: file_fdw, CREATE FOREIGN TABLE, filename, program, format csv, csvlog, log foreign table
- Follow-up Guidance: Review file access privileges and path exposure before granting use in production.
- Classification Note: The module defines foreign table/server options for reading server-side files and includes configuration for exposing PostgreSQL CSV logs as a foreign table.

## Official Source Content

## Create a Foreign Table for PostgreSQL CSV Logs

One of the obvious uses for `file_fdw` is to make
the PostgreSQL activity log available as a table for querying.  To
do this, first you must be [logging to a CSV file,](#runtime-config-logging-csvlog)
which here we
will call `pglog.csv`.  First, install `file_fdw`
as an extension:

```
CREATE EXTENSION file_fdw;
```

Then create a foreign server:

```
CREATE SERVER pglog FOREIGN DATA WRAPPER file_fdw;
```

Now you are ready to create the foreign data table.  Using the
`CREATE FOREIGN TABLE` command, you will need to define
the columns for the table, the CSV file name, and its format:

```
CREATE FOREIGN TABLE pglog (
log_time timestamp(3) with time zone,
user_name text,
database_name text,
process_id integer,
connection_from text,
session_id text,
session_line_num bigint,
command_tag text,
session_start_time timestamp with time zone,
virtual_transaction_id text,
transaction_id bigint,
error_severity text,
sql_state_code text,
message text,
detail text,
hint text,
internal_query text,
internal_query_pos integer,
context text,
query text,
query_pos integer,
location text,
application_name text,
backend_type text,
leader_pid integer,
query_id bigint
) SERVER pglog
OPTIONS ( filename 'log/pglog.csv', format 'csv' );
```

That's it — now you can query your log directly. In production, of
course, you would need to define some way to deal with log rotation.
