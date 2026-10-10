# Role Membership

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/07_database_roles.md`
- Source Title: `Database Roles`
- Source Heading Path: `Database Roles > Role Membership`
- Source Line Ranges: `225-360`
- Chunk ID: `pg16_configuration_0105_2e4bebf8b8`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e605f858776abd17e48087f439dd2ca55bf051d7e94b1d7009a4daf821bbf438`

## Retrieval Guidance

- Use When: 需要用角色组管理权限继承和临时切换角色。
- Retrieval Keywords: GRANT role TO user, REVOKE role, SET ROLE, INHERIT, WITH SET, group role, membership
- Follow-up Guidance: 特殊属性如 SUPERUSER/CREATEDB 不像对象权限一样自动继承，需 SET ROLE。
- Classification Note: 定义 GRANT/REVOKE role membership、WITH INHERIT/SET、SET ROLE、成员链和循环限制。

## Official Source Content

## Role Membership

It is frequently convenient to group users together to ease
management of privileges: that way, privileges can be granted to, or
revoked from, a group as a whole.  In PostgreSQL
this is done by creating a role that represents the group, and then
granting *membership* in the group role to individual user
roles.

To set up a group role, first create the role:

```
CREATE ROLE `name`;
```

Typically a role being used as a group would not have the `LOGIN`
attribute, though you can set it if you wish.

Once the group role exists, you can add and remove members using the
[`GRANT`](#sql-grant) and
[`REVOKE`](#sql-revoke) commands:

```
GRANT `group_role` TO `role1`, ... ;
REVOKE `group_role` FROM `role1`, ... ;
```

You can grant membership to other group roles, too (since there isn't
really any distinction between group roles and non-group roles).  The
database will not let you set up circular membership loops.  Also,
it is not permitted to grant membership in a role to
`PUBLIC`.

The members of a group role can use the privileges of the role in two
ways.  First, member roles that have been granted membership with the
`SET` option can do
[`SET ROLE`](#sql-set-role) to
temporarily "become" the group role.  In this state, the
database session has access to the privileges of the group role rather
than the original login role, and any database objects created are
considered owned by the group role not the login role.  Second, member
roles that have been granted membership with the
`INHERIT` option automatically have use of the
privileges of those directly or indirectly a member of, though the
chain stops at memberships lacking the inherit option.  As an example,
suppose we have done:

```
CREATE ROLE joe LOGIN;
CREATE ROLE admin;
CREATE ROLE wheel;
CREATE ROLE island;
GRANT admin TO joe WITH INHERIT TRUE;
GRANT wheel TO admin WITH INHERIT FALSE;
GRANT island TO joe WITH INHERIT TRUE, SET FALSE;
```

Immediately after connecting as role `joe`, a database
session will have use of privileges granted directly to `joe`
plus any privileges granted to `admin` and
`island`, because `joe`
"inherits" those privileges.  However, privileges
granted to `wheel` are not available, because even though
`joe` is indirectly a member of `wheel`, the
membership is via `admin` which was granted using
`WITH INHERIT FALSE`. After:

```
SET ROLE admin;
```

the session would have use of only those privileges granted to
`admin`, and not those granted to `joe` or
`island`.  After:

```
SET ROLE wheel;
```

the session would have use of only those privileges granted to
`wheel`, and not those granted to either `joe`
or `admin`.  The original privilege state can be restored
with any of:

```
SET ROLE joe;
SET ROLE NONE;
RESET ROLE;
```

> **Note:**

> The `SET ROLE` command always allows selecting any role
> that the original login role is directly or indirectly a member of,
> provided that there is a chain of membership grants each of which has
> `SET TRUE` (which is the default).
> Thus, in the above example, it is not necessary to become
> `admin` before becoming `wheel`.
> On the other hand, it is not possible to become `island`
> at all; `joe` can only access those privileges via
> inheritance.
>

> **Note:**

> In the SQL standard, there is a clear distinction between users and roles,
> and users do not automatically inherit privileges while roles do.  This
> behavior can be obtained in PostgreSQL by giving
> roles being used as SQL roles the `INHERIT` attribute, while
> giving roles being used as SQL users the `NOINHERIT` attribute.
> However, PostgreSQL defaults to giving all roles
> the `INHERIT` attribute, for backward compatibility with pre-8.1
> releases in which users always had use of permissions granted to groups
> they were members of.
>

The role attributes `LOGIN`, `SUPERUSER`,
`CREATEDB`, and `CREATEROLE` can be thought of as
special privileges, but they are never inherited as ordinary privileges
on database objects are.  You must actually `SET ROLE` to a
specific role having one of these attributes in order to make use of
the attribute.  Continuing the above example, we might choose to
grant `CREATEDB` and `CREATEROLE` to the
`admin` role.  Then a session connecting as role `joe`
would not have these privileges immediately, only after doing
`SET ROLE admin`.

To destroy a group role, use [`DROP ROLE`](#sql-droprole):

```
DROP ROLE `name`;
```

Any memberships in the group role are automatically revoked (but the
member roles are not otherwise affected).
