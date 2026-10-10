# REASSIGN OWNED

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/reassign_owned.md`
- Source Title: `reassign owned`
- Source Heading Path: `Part VI Reference > SQL Commands > REASSIGN OWNED`
- Source Line Ranges: `1-60`
- Chunk ID: `pg16_fact_0317_8d9b8c8b4b`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `24ed962011eedfaa275b9b1e987493b8a1aa2430e2c4f419d3d9e6afad7d9e85`

## Retrieval Guidance

- Use When: Use for syntax to transfer objects owned by roles.
- Retrieval Keywords: REASSIGN OWNED, role removal, object ownership, new owner
- Follow-up Guidance: Compare with DROP OWNED for privilege cleanup.
- Classification Note: Ownership transfer syntax reference, commonly used before role removal but still object/reference semantics.

## Official Source Content

REASSIGN OWNED
7
SQL - Language Statements

REASSIGN OWNED
change the ownership of database objects owned by a database role

```
REASSIGN OWNED BY { `old_role` | CURRENT_ROLE | CURRENT_USER | SESSION_USER } [, ...]
TO { `new_role` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
```

## Description

`REASSIGN OWNED` instructs the system to change
the ownership of database objects owned by any of the
`old_roles` to
`new_role`.

## Parameters

**`old_role`**
: The name of a role. The ownership of all the objects within the
current database, and of all shared objects (databases, tablespaces),
owned by this role will be reassigned to
`new_role`.

**`new_role`**
: The name of the role that will be made the new owner of the
affected objects.

## Notes

`REASSIGN OWNED` is often used to prepare for the
removal of one or more roles. Because `REASSIGN
OWNED` does not affect objects within other databases,
it is usually necessary to execute this command in each database
that contains objects owned by a role that is to be removed.

`REASSIGN OWNED` requires membership on both the
source role(s) and the target role.

The [`DROP OWNED`](#sql-drop-owned) command is an alternative that
simply drops all the database objects owned by one or more roles.

The `REASSIGN OWNED` command does not affect any
privileges granted to
the `old_roles` on objects
that are not owned by them.  Likewise, it does not affect default
privileges created with `ALTER DEFAULT PRIVILEGES`.
Use `DROP OWNED` to revoke such privileges.

See [role-removal](#role-removal) for more discussion.

## Compatibility

The `REASSIGN OWNED` command is a
PostgreSQL extension.

## See Also
