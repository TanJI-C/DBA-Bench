# ALTER USER MAPPING

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_user_mapping.md`
- Source Title: `alter user mapping`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER USER MAPPING`
- Source Line Ranges: `1-64`
- Chunk ID: `pg16_fact_0206_cc53f1a475`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `7393fa35e4611e8160fcdd2ea26f26a72038595006831677156c94e87c52a4e2`

## Retrieval Guidance

- Use When: Use for foreign user mapping syntax and option semantics.
- Retrieval Keywords: ALTER USER MAPPING, foreign server, user mapping options, FDW user mapping
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign user mapping object DDL reference for server-specific options.

## Official Source Content

ALTER USER MAPPING
7
SQL - Language Statements

ALTER USER MAPPING
change the definition of a user mapping

```
ALTER USER MAPPING FOR { `user_name` | USER | CURRENT_ROLE | CURRENT_USER | SESSION_USER | PUBLIC }
SERVER `server_name`
OPTIONS ( [ ADD | SET | DROP ] `option` ['`value`'] [, ... ] )
```

## Description

`ALTER USER MAPPING` changes the definition of a
user mapping.

The owner of a foreign server can alter user mappings for that
server for any user.  Also, a user can alter a user mapping for
their own user name if `USAGE` privilege on the server has
been granted to the user.

## Parameters

**`user_name`**
: User name of the mapping. `CURRENT_ROLE`, `CURRENT_USER`,
and `USER` match the name of the current
user. `PUBLIC` is used to match all present and future
user names in the system.

**`server_name`**
: Server name of the user mapping.

**`OPTIONS ( [ ADD | SET | DROP ] `option` ['`value`'] [, ... ] )`**
: Change options for the user mapping. The new options override
any previously specified
options.  `ADD`, `SET`, and `DROP`
specify the action to be performed.  `ADD` is assumed
if no operation is explicitly specified.  Option names must be
unique; options are also validated by the server's foreign-data
wrapper.

## Examples

Change the password for user mapping `bob`, server `foo`:

```
ALTER USER MAPPING FOR bob SERVER foo OPTIONS (SET password 'public');
```

## Compatibility

`ALTER USER MAPPING` conforms to ISO/IEC 9075-9
(SQL/MED).  There is a subtle syntax issue: The standard omits
the `FOR` key word.  Since both `CREATE
USER MAPPING` and `DROP USER MAPPING` use
`FOR` in analogous positions, and IBM DB2 (being
the other major SQL/MED implementation) also requires it
for `ALTER USER MAPPING`, PostgreSQL diverges from
the standard here in the interest of consistency and
interoperability.

## See Also
