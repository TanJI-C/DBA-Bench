# SET ROLE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/set_role.md`
- Source Title: `set role`
- Source Heading Path: `Part VI Reference > SQL Commands > SET ROLE`
- Source Line Ranges: `1-109`
- Chunk ID: `pg16_fact_0328_196ee923f4`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `176bd1c5356eb876cd350fc6e1c5aa2b1a0661c48ea3b7948a4c51f8c2843905`

## Retrieval Guidance

- Use When: Use for role switching syntax and privilege behavior.
- Retrieval Keywords: SET ROLE, current role, role privileges, RESET ROLE
- Follow-up Guidance: No section split needed.
- Classification Note: Session authorization/role switching syntax reference; identity state rather than configuration-parameter semantics.

## Official Source Content

SET ROLE
7
SQL - Language Statements

SET ROLE
set the current user identifier of the current session

```
SET [ SESSION | LOCAL ] ROLE `role_name`
SET [ SESSION | LOCAL ] ROLE NONE
RESET ROLE
```

## Description

This command sets the current user
identifier of the current SQL session to be `role_name`.  The role name can be
written as either an identifier or a string literal.
After `SET ROLE`, permissions checking for SQL commands
is carried out as though the named role were the one that had logged
in originally.

The current session user must have the `SET` option for the
specified `role_name`, either
directly or indirectly via a chain of memberships with the
`SET` option.
(If the session user is a superuser, any role can be selected.)

The `SESSION` and `LOCAL` modifiers act the same
as for the regular [`SET`](#sql-set)
command.

`SET ROLE NONE` sets the current user identifier to the
current session user identifier, as returned by
`session_user`.  `RESET ROLE` sets the
current user identifier to the connection-time setting specified by the
[command-line options](#libpq-connect-options),
[`ALTER ROLE`](#sql-alterrole), or
[`ALTER DATABASE`](#sql-alterdatabase),
if any such settings exist.  Otherwise, `RESET ROLE` sets
the current user identifier to the current session user identifier.  These
forms can be executed by any user.

## Notes

Using this command, it is possible to either add privileges or restrict
one's privileges.  If the session user role has been granted memberships
`WITH INHERIT TRUE`, it automatically has all the
privileges of every such role. In this case, `SET ROLE`
effectively drops all the privileges except for those which the target role
directly possesses or inherits.  On the other hand, if the session user role
has been granted memberships `WITH INHERIT FALSE`, the
privileges of the granted roles can't be accessed by default. However, if
the role was granted `WITH SET TRUE`, the
session user can use `SET ROLE` to drop the privileges
assigned directly to the session user and instead acquire the privileges
available to the named role. If the role was granted `WITH INHERIT
FALSE, SET FALSE` then the privileges of that role cannot be
exercised either with or without `SET ROLE`.

Note that when a superuser chooses to `SET ROLE` to a
non-superuser role, they lose their superuser privileges.

`SET ROLE` has effects comparable to
[`SET SESSION AUTHORIZATION`](#sql-set-session-authorization), but the privilege
checks involved are quite different.  Also,
`SET SESSION AUTHORIZATION` determines which roles are
allowable for later `SET ROLE` commands, whereas changing
roles with `SET ROLE` does not change the set of roles
allowed to a later `SET ROLE`.

`SET ROLE` does not process session variables as specified by
the role's [`ALTER ROLE`](#sql-alterrole) settings;  this only happens during
login.

`SET ROLE` cannot be used within a
`SECURITY DEFINER` function.

## Examples

```
SELECT SESSION_USER, CURRENT_USER;

session_user | current_user
--------------+--------------
peter        | peter

SET ROLE 'paul';

SELECT SESSION_USER, CURRENT_USER;

session_user | current_user
--------------+--------------
peter        | paul
```

## Compatibility

PostgreSQL
allows identifier syntax (`"`rolename`"`), while
the SQL standard requires the role name to be written as a string
literal.  SQL does not allow this command during a transaction;
PostgreSQL does not make this
restriction because there is no reason to.
The `SESSION` and `LOCAL` modifiers are a
PostgreSQL extension, as is the
`RESET` syntax.

## See Also
