# CREATE USER MAPPING

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_user_mapping.md`
- Source Title: `create user mapping`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE USER MAPPING`
- Source Line Ranges: `1-64`
- Chunk ID: `pg16_fact_0253_4025a4b11c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f96cd380801bf2448df8a85096bd0c2bcbd246613cb01faec030fff9b681add4`

## Retrieval Guidance

- Use When: Use for foreign user mapping syntax.
- Retrieval Keywords: CREATE USER MAPPING, foreign server, FDW user mapping, OPTIONS
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign user mapping creation reference.

## Official Source Content

CREATE USER MAPPING
7
SQL - Language Statements

CREATE USER MAPPING
define a new mapping of a user to a foreign server

```
CREATE USER MAPPING [ IF NOT EXISTS ] FOR { `user_name` | USER | CURRENT_ROLE | CURRENT_USER | PUBLIC }
SERVER `server_name`
[ OPTIONS ( `option` '`value`' [ , ... ] ) ]
```

## Description

`CREATE USER MAPPING` defines a mapping of a user
to a foreign server.  A user mapping typically encapsulates
connection information that a foreign-data wrapper uses together
with the information encapsulated by a foreign server to access an
external data resource.

The owner of a foreign server can create user mappings for that
server for any user.  Also, a user can create a user mapping for
their own user name if `USAGE` privilege on the server has
been granted to the user.

## Parameters

**`IF NOT EXISTS`**
: Do not throw an error if a mapping of the given user to the given foreign
server already exists. A notice is issued in this case.  Note that there
is no guarantee that the existing user mapping is anything like the one
that would have been created.

**`user_name`**
: The name of an existing user that is mapped to foreign server.
`CURRENT_ROLE`, `CURRENT_USER`, and `USER` match the name of
the current user.  When `PUBLIC` is specified, a
so-called public mapping is created that is used when no
user-specific mapping is applicable.

**`server_name`**
: The name of an existing server for which the user mapping is
to be created.

**`OPTIONS ( `option` '`value`' [, ... ] )`**
: This clause specifies the options of the user mapping.  The
options typically define the actual user name and password of
the mapping.  Option names must be unique.  The allowed option
names and values are specific to the server's foreign-data wrapper.

## Examples

Create a user mapping for user `bob`, server `foo`:

```
CREATE USER MAPPING FOR bob SERVER foo OPTIONS (user 'bob', password 'secret');
```

## Compatibility

`CREATE USER MAPPING` conforms to ISO/IEC 9075-9 (SQL/MED).

## See Also
