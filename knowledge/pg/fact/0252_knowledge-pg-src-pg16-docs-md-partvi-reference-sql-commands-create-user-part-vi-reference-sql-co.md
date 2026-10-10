# CREATE USER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_user.md`
- Source Title: `create user`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE USER`
- Source Line Ranges: `1-47`
- Chunk ID: `pg16_fact_0252_658249cbba`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `893792684435bb0671ca0551ba408b1b5c32e679a7345a60085fb8c5a7e868fd`

## Retrieval Guidance

- Use When: Use for legacy user creation syntax.
- Retrieval Keywords: CREATE USER, CREATE ROLE alias, LOGIN role, user account
- Follow-up Guidance: Prefer CREATE ROLE terminology in new guidance.
- Classification Note: Compatibility alias for CREATE ROLE with LOGIN; role/user object syntax reference.

## Official Source Content

CREATE USER
7
SQL - Language Statements

CREATE USER
define a new database role

```
CREATE USER `name` [ [ WITH ] `option` [ ... ] ]

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

`CREATE USER` is now an alias for
[`CREATE ROLE`](#sql-createrole).
The only difference is that when the command is spelled
`CREATE USER`, `LOGIN` is assumed
by default, whereas `NOLOGIN` is assumed when
the command is spelled
`CREATE ROLE`.

## Compatibility

The `CREATE USER` statement is a
PostgreSQL extension.  The SQL standard
leaves the definition of users to the implementation.

## See Also
