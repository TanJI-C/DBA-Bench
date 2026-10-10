# DROP ROLE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_role.md`
- Source Title: `drop role`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP ROLE`
- Source Line Ranges: `1-63`
- Chunk ID: `pg16_fact_0282_4a02af1b62`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ade7288b956a0fd6b4d48fbf1a343dfbbe75fcff01baf9aabfaf1645f828f8b4`

## Retrieval Guidance

- Use When: Use for role drop syntax and restrictions.
- Retrieval Keywords: DROP ROLE, role removal, user removal, IF EXISTS
- Follow-up Guidance: Review DROP OWNED/REASSIGN OWNED before operational removal.
- Classification Note: Role removal syntax reference.

## Official Source Content

DROP ROLE
7
SQL - Language Statements

DROP ROLE
remove a database role

```
DROP ROLE [ IF EXISTS ] `name` [, ...]
```

## Description

`DROP ROLE` removes the specified role(s).
To drop a superuser role, you must be a superuser yourself;
to drop non-superuser roles, you must have `CREATEROLE`
privilege and have been granted `ADMIN OPTION` on the role.

A role cannot be removed if it is still referenced in any database
of the cluster; an error will be raised if so.  Before dropping the role,
you must drop all the objects it owns (or reassign their ownership)
and revoke any privileges the role has been granted on other objects.
The [`REASSIGN
OWNED`](#sql-reassign-owned) and [`DROP
OWNED`](#sql-drop-owned)
commands can be useful for this purpose; see [role-removal](#role-removal)
for more discussion.

However, it is not necessary to remove role memberships involving
the role; `DROP ROLE` automatically revokes any memberships
of the target role in other roles, and of other roles in the target role.
The other roles are not dropped nor otherwise affected.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the role does not exist. A notice is issued
in this case.

**`name`**
: The name of the role to remove.

## Notes

PostgreSQL includes a program [app-dropuser](#app-dropuser) that has the
same functionality as this command (in fact, it calls this command)
but can be run from the command shell.

## Examples

To drop a role:

```
DROP ROLE jonathan;
```

## Compatibility

The SQL standard defines `DROP ROLE`, but it allows
only one role to be dropped at a time, and it specifies different
privilege requirements than PostgreSQL uses.

## See Also
