# CREATE GROUP

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_group.md`
- Source Title: `create group`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE GROUP`
- Source Line Ranges: `1-41`
- Chunk ID: `pg16_fact_0227_5d92bcf19d`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ce06c6b94222369026820b385bc86962b1f7a988f6409bc61ea1e3b90cb78d81`

## Retrieval Guidance

- Use When: Use for legacy group creation syntax.
- Retrieval Keywords: CREATE GROUP, CREATE ROLE alias, group role
- Follow-up Guidance: Prefer CREATE ROLE for new guidance.
- Classification Note: Compatibility reference for creating a role/group.

## Official Source Content

CREATE GROUP
7
SQL - Language Statements

CREATE GROUP
define a new database role

```
CREATE GROUP `name` [ [ WITH ] `option` [ ... ] ]

where `option` can be:

SUPERUSER | NOSUPERUSER
| CREATEDB | NOCREATEDB
| CREATEROLE | NOCREATEROLE
| INHERIT | NOINHERIT
| LOGIN | NOLOGIN
| REPLICATION | NOREPLICATION
| BYPASSRLS | NOBYPASSRLS
| CONNECTION LIMIT `connlimit`
| [ ENCRYPTED ] PASSWORD '`password`' | PASSWORD NULL
| VALID UNTIL '`timestamp`'
| IN ROLE `role_name` [, ...]
| IN GROUP `role_name` [, ...]
| ROLE `role_name` [, ...]
| ADMIN `role_name` [, ...]
| USER `role_name` [, ...]
| SYSID `uid`
```

## Description

`CREATE GROUP` is now an alias for
[sql-createrole](#sql-createrole).

## Compatibility

There is no `CREATE GROUP` statement in the SQL
standard.

## See Also
