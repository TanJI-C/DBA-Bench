# ALTER GROUP

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_group.md`
- Source Title: `alter group`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER GROUP`
- Source Line Ranges: `1-77`
- Chunk ID: `pg16_fact_0178_9127d7aaf7`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `8ba55e0cf951fd786c32d08bd057043b382e483276f78d2709c610b673d560e7`

## Retrieval Guidance

- Use When: Use for group/role membership compatibility syntax.
- Retrieval Keywords: ALTER GROUP, role membership, ADD USER, DROP USER
- Follow-up Guidance: Prefer ALTER ROLE/GRANT role membership references where applicable.
- Classification Note: Compatibility alias/reference for role membership changes; ordinary access-control syntax.

## Official Source Content

ALTER GROUP
7
SQL - Language Statements

ALTER GROUP
change role name or membership

```
ALTER GROUP `role_specification` ADD USER `user_name` [, ... ]
ALTER GROUP `role_specification` DROP USER `user_name` [, ... ]

where `role_specification` can be:

`role_name`
| CURRENT_ROLE
| CURRENT_USER
| SESSION_USER

ALTER GROUP `group_name` RENAME TO `new_name`
```

## Description

`ALTER GROUP` changes the attributes of a user group.
This is an obsolete command, though still accepted for backwards
compatibility, because groups (and users too) have been superseded by the
more general concept of roles.

The first two variants add users to a group or remove them from a group.
(Any role can play the part of either a "user" or a
"group" for this purpose.)  These variants are effectively
equivalent to granting or revoking membership in the role named as the
"group"; so the preferred way to do this is to use
[`GRANT`](#sql-grant) or
[`REVOKE`](#sql-revoke). Note that
`GRANT` and `REVOKE` have additional
options which are not available with this command, such as the ability
to grant and revoke `ADMIN OPTION`, and the ability to
specify the grantor.

The third variant changes the name of the group.  This is exactly
equivalent to renaming the role with
[`ALTER ROLE`](#sql-alterrole).

## Parameters

**`group_name`**
: The name of the group (role) to modify.

**`user_name`**
: Users (roles) that are to be added to or removed from the group.
The users must already exist; `ALTER GROUP` does not
create or drop users.

**`new_name`**
: The new name of the group.

## Examples

Add users to a group:

```
ALTER GROUP staff ADD USER karl, john;
```

Remove a user from a group:

```
ALTER GROUP workers DROP USER beth;
```

## Compatibility

There is no `ALTER GROUP` statement in the SQL
standard.

## See Also
