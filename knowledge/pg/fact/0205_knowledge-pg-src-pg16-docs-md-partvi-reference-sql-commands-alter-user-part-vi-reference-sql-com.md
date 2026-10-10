# alias/role attributes

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_user.md`
- Source Title: `alter user`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER USER > alias/role attributes`
- Source Line Ranges: `1-50`
- Chunk ID: `pg16_fact_0205_1701853e16`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `b91fc06d167403dce1b64de9a072b0ff7d0ac1e683cc7afec1adf3ff314354ef`

## Retrieval Guidance

- Use When: Use for compatibility syntax around role/user changes.
- Retrieval Keywords: ALTER USER, ALTER ROLE alias, user attributes, role attributes
- Follow-up Guidance: Split SET/RESET configuration_parameter separately.
- Classification Note: ALTER USER is documented as an alias for ALTER ROLE; role attribute syntax is object/security reference.

## Official Source Content

ALTER USER
7
SQL - Language Statements

ALTER USER
change a database role

```
ALTER USER `role_specification` [ WITH ] `option` [ ... ]

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

ALTER USER `name` RENAME TO `new_name`

ALTER USER { `role_specification` | ALL } [ IN DATABASE `database_name` ] SET `configuration_parameter` { TO | = } { `value` | DEFAULT }
ALTER USER { `role_specification` | ALL } [ IN DATABASE `database_name` ] SET `configuration_parameter` FROM CURRENT
ALTER USER { `role_specification` | ALL } [ IN DATABASE `database_name` ] RESET `configuration_parameter`
ALTER USER { `role_specification` | ALL } [ IN DATABASE `database_name` ] RESET ALL

where `role_specification` can be:

`role_name`
| CURRENT_ROLE
| CURRENT_USER
| SESSION_USER
```

## Description

`ALTER USER` is now an alias for
[`ALTER ROLE`](#sql-alterrole).

## Compatibility

The `ALTER USER` statement is a
PostgreSQL extension.  The SQL standard
leaves the definition of users to the implementation.

## See Also
