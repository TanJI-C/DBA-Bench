# DROP DATABASE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_database.md`
- Source Title: `drop database`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP DATABASE`
- Source Line Ranges: `1-63`
- Chunk ID: `pg16_fact_0264_2431db467b`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f5c1d2831e353fb73aefd56fc0c332f9c23dd3ddc279807aa00ba66a2928cbf2`

## Retrieval Guidance

- Use When: Use for database drop syntax and restrictions.
- Retrieval Keywords: DROP DATABASE, WITH FORCE, drop database, terminate connections
- Follow-up Guidance: Confirm destructive intent and backups outside this classification.
- Classification Note: Database removal syntax reference; destructive general DDL rather than a diagnostic or standard remediation record.

## Official Source Content

DROP DATABASE
7
SQL - Language Statements

DROP DATABASE
remove a database

```
DROP DATABASE [ IF EXISTS ] `name` [ [ WITH ] ( `option` [, ...] ) ]

where `option` can be:

FORCE
```

## Description

`DROP DATABASE` drops a database. It removes the
catalog entries for the database and deletes the directory
containing the data.  It can only be executed by the database owner.
It cannot be executed while you are connected to the target database.
(Connect to `postgres` or any other database to issue this
command.)
Also, if anyone else is connected to the target database, this command will
fail unless you use the `FORCE` option described below.

`DROP DATABASE` cannot be undone.  Use it with care!

## Parameters

**`IF EXISTS`**
: Do not throw an error if the database does not exist. A notice is issued
in this case.

**`name`**
: The name of the database to remove.

**`FORCE`**
: Attempt to terminate all existing connections to the target database.
It doesn't terminate if prepared transactions, active logical replication
slots or subscriptions are present in the target database.

This terminates background worker connections and connections that the
current user has permission to terminate
with `pg_terminate_backend`, described in
[functions-admin-signal](#functions-admin-signal).  If connections would remain,
this command will fail.

## Notes

`DROP DATABASE` cannot be executed inside a transaction
block.

This command cannot be executed while connected to the target
database. Thus, it might be more convenient to use the program
[app-dropdb](#app-dropdb) instead,
which is a wrapper around this command.

## Compatibility

There is no `DROP DATABASE` statement in the SQL standard.

## See Also
