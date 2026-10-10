# DROP OWNED

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_owned.md`
- Source Title: `drop owned`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP OWNED`
- Source Line Ranges: `1-60`
- Chunk ID: `pg16_fact_0278_4ef33851df`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `d8089d030a2cc9716049674dbd1d3d078c96399cd566e8b5bc0dae8a89efc040`

## Retrieval Guidance

- Use When: Use for syntax when preparing to remove roles and their owned objects.
- Retrieval Keywords: DROP OWNED, role removal, owned objects, revoke privileges, CASCADE
- Follow-up Guidance: Review destructive CASCADE behavior and compare REASSIGN OWNED.
- Classification Note: Role-owned object cleanup syntax reference; useful operationally, but primarily documents object/privilege removal semantics.

## Official Source Content

DROP OWNED
7
SQL - Language Statements

DROP OWNED
remove database objects owned by a database role

```
DROP OWNED BY { `name` | CURRENT_ROLE | CURRENT_USER | SESSION_USER } [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP OWNED` drops all the objects within the current
database that are owned by one of the specified roles. Any
privileges granted to the given roles on objects in the current
database or on shared objects (databases, tablespaces, configuration
parameters) will also be revoked.

## Parameters

**`name`**
: The name of a role whose objects will be dropped, and whose
privileges will be revoked.

**`CASCADE`**
: Automatically drop objects that depend on the affected objects,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the objects owned by a role if any other database
objects depend on one of the affected objects. This is the default.

## Notes

`DROP OWNED` is often used to prepare for the
removal of one or more roles. Because `DROP OWNED`
only affects the objects in the current database, it is usually
necessary to execute this command in each database that contains
objects owned by a role that is to be removed.

Using the `CASCADE` option might make the command
recurse to objects owned by other users.

The [`REASSIGN OWNED`](#sql-reassign-owned) command is an alternative that
reassigns the ownership of all the database objects owned by one or
more roles.  However, `REASSIGN OWNED` does not deal with
privileges for other objects.

Databases and tablespaces owned by the role(s) will not be removed.

See [role-removal](#role-removal) for more discussion.

## Compatibility

The `DROP OWNED` command is a
PostgreSQL extension.

## See Also
