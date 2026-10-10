# ALTER SERVER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_server.md`
- Source Title: `alter server`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER SERVER`
- Source Line Ranges: `1-72`
- Chunk ID: `pg16_fact_0194_3a28c91ec3`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ccbdf56a173e04cce17ea401172bfe2402ecc9e284c2bc29dff1cca10508cd89`

## Retrieval Guidance

- Use When: Use for foreign server object syntax.
- Retrieval Keywords: ALTER SERVER, foreign server options, server version, FDW server
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign server object DDL reference for version, options, owner, and rename.

## Official Source Content

ALTER SERVER
7
SQL - Language Statements

ALTER SERVER
change the definition of a foreign server

```
ALTER SERVER `name` [ VERSION '`new_version`' ]
[ OPTIONS ( [ ADD | SET | DROP ] `option` ['`value`'] [, ... ] ) ]
ALTER SERVER `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER SERVER `name` RENAME TO `new_name`
```

## Description

`ALTER SERVER` changes the definition of a foreign
server.  The first form changes the server version string or the
generic options of the server (at least one clause is required).
The second form changes the owner of the server.

To alter the server you must be the owner of the server.
Additionally to alter the owner, you must be able to
`SET ROLE` to the new owning role, and you must
have `USAGE` privilege on the server's foreign-data
wrapper.  (Note that superusers satisfy all these criteria
automatically.)

## Parameters

**`name`**
: The name of an existing server.

**`new_version`**
: New server version.

**`OPTIONS ( [ ADD | SET | DROP ] `option` ['`value`'] [, ... ] )`**
: Change options for the
server.  `ADD`, `SET`, and `DROP`
specify the action to be performed.  `ADD` is assumed
if no operation is explicitly specified.  Option names must be
unique; names and values are also validated using the server's
foreign-data wrapper library.

**`new_owner`**
: The user name of the new owner of the foreign server.

**`new_name`**
: The new name for the foreign server.

## Examples

Alter server `foo`, add connection options:

```
ALTER SERVER foo OPTIONS (host 'foo', dbname 'foodb');
```

Alter server `foo`, change version,
change `host` option:

```
ALTER SERVER foo VERSION '8.4' OPTIONS (SET host 'baz');
```

## Compatibility

`ALTER SERVER` conforms to ISO/IEC 9075-9 (SQL/MED).
The `OWNER TO` and `RENAME` forms are
PostgreSQL extensions.

## See Also
