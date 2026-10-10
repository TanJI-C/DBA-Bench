# GRANT

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/grant.md`
- Source Title: `grant`
- Source Heading Path: `Part VI Reference > SQL Commands > GRANT`
- Source Line Ranges: `108-174, 175-248`
- Chunk ID: `pg16_fact_0306_4a141edc74`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6693a66010b4d320e6ccfd76d5438611c77eeb969aabfc20e3237947049c133a`

## Retrieval Guidance

- Use When: Use for privilege grant syntax and semantics.
- Retrieval Keywords: GRANT, privileges, role membership, GRANT OPTION, ON PARAMETER
- Follow-up Guidance: For runtime parameter value changes use SET/ALTER SYSTEM records.
- Classification Note: Privilege and role membership syntax reference; includes parameter privileges but is primarily access-control reference.

## Official Source Content

### GRANT on Database Objects

This variant of the `GRANT` command gives specific
privileges on a database object to
one or more roles.  These privileges are added
to those already granted, if any.

The key word `PUBLIC` indicates that the
privileges are to be granted to all roles, including those that might
be created later.  `PUBLIC` can be thought of as an
implicitly defined group that always includes all roles.
Any particular role will have the sum
of privileges granted directly to it, privileges granted to any role it
is presently a member of, and privileges granted to
`PUBLIC`.

If `WITH GRANT OPTION` is specified, the recipient
of the privilege can in turn grant it to others.  Without a grant
option, the recipient cannot do that.  Grant options cannot be granted
to `PUBLIC`.

If `GRANTED BY` is specified, the specified grantor must
be the current user.  This clause is currently present in this form only
for SQL compatibility.

There is no need to grant privileges to the owner of an object
(usually the user that created it),
as the owner has all privileges by default.  (The owner could,
however, choose to revoke some of their own privileges for safety.)

The right to drop an object, or to alter its definition in any way, is
not treated as a grantable privilege; it is inherent in the owner,
and cannot be granted or revoked.  (However, a similar effect can be
obtained by granting or revoking membership in the role that owns
the object; see below.)  The owner implicitly has all grant
options for the object, too.

The possible privileges are:

**`SELECT`**
: Specific types of privileges, as defined in [ddl-priv](#ddl-priv).

**`TEMP`**
: Alternative spelling for `TEMPORARY`.

**`ALL PRIVILEGES`**
: Grant all of the privileges available for the object's type.
The `PRIVILEGES` key word is optional in
PostgreSQL, though it is required by
strict SQL.

The `FUNCTION` syntax works for plain functions,
aggregate functions, and window functions, but not for procedures;
use `PROCEDURE` for those.
Alternatively, use `ROUTINE` to refer to a function,
aggregate function, window function, or procedure regardless of its
precise type.

There is also an option to grant privileges on all objects of the same
type within one or more schemas.  This functionality is currently supported
only for tables, sequences, functions, and procedures.  `ALL
TABLES` also affects views and foreign tables, just like the
specific-object `GRANT` command.  `ALL
FUNCTIONS` also affects aggregate and window functions, but not
procedures, again just like the specific-object `GRANT`
command.  Use `ALL ROUTINES` to include procedures.

### GRANT on Roles

This variant of the `GRANT` command grants membership
in a role to one or more other roles, and the modification of
membership options `SET`, `INHERIT`,
and `ADMIN`;  see [role-membership](#role-membership)
for details.  Membership in a role is significant
because it potentially allows access to the privileges granted to a role
to each of its members, and potentially also the ability to make changes
to the role itself. However, the actual permissions conferred depend on
the options associated with the grant.  To modify that options of
an existing membership, simply specify the membership with updated
option values.

Each of the options described below can be set to either
`TRUE` or `FALSE`. The keyword
`OPTION` is accepted as a synonym for
`TRUE`, so that `WITH ADMIN OPTION`
is a synonym for `WITH ADMIN TRUE`.  When altering
an existing membership the omission of an option results in the current
value being retained.

The `ADMIN` option allows the member to
in turn grant membership in the role to others, and revoke membership
in the role as well.  Without the admin option, ordinary users cannot
do that.  A role is not considered to hold `WITH ADMIN
OPTION` on itself.  Database superusers can grant or revoke
membership in any role to anyone. This option defaults to
`FALSE`.

The `INHERIT` option controls the inheritance status
of the new membership;  see [role-membership](#role-membership) for
details on inheritance.  If it is set to `TRUE`,
it causes the new member to inherit from the granted role. If
set to `FALSE`, the new member does not inherit.
If unspecified when creating a new role membership, this defaults to the
inheritance attribute of the new member.

The `SET` option, if it is set to
`TRUE`, allows the member to change to the granted
role using the
[`SET ROLE`](#sql-set-role)
command. If a role is an indirect member of another role, it can use
`SET ROLE` to change to that role only if there is a
chain of grants each of which has `SET TRUE`.
This option defaults to `TRUE`.

To create an object owned by another role or give ownership of an existing
object to another role, you must have the ability to `SET
ROLE` to that role; otherwise, commands such as `ALTER
... OWNER TO` or `CREATE DATABASE ... OWNER`
will fail.  However, a user who inherits the privileges of a role but does
not have the ability to `SET ROLE` to that role may be
able to obtain full access to the role by manipulating existing objects
owned by that role (e.g. they could redefine an existing function to act
as a Trojan horse).  Therefore, if a role's privileges are to be inherited
but should not be accessible via `SET ROLE`, it should not
own any SQL objects.

If `GRANTED BY` is specified, the grant is recorded as
having been done by the specified role. A user can only attribute a grant
to another role if they possess the privileges of that role. The role
recorded as the grantor must have `ADMIN OPTION` on the
target role, unless it is the bootstrap superuser. When a grant is recorded
as having a grantor other than the bootstrap superuser, it depends on the
grantor continuing to possess `ADMIN OPTION` on the role;
so, if `ADMIN OPTION` is revoked, dependent grants must
be revoked as well.

Unlike the case with privileges, membership in a role cannot be granted
to `PUBLIC`.  Note also that this form of the command
does not allow the noise word `GROUP`
in `role_specification`.
