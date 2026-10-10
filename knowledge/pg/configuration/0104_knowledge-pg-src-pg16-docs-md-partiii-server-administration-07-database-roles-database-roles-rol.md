# Role Attributes

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/07_database_roles.md`
- Source Title: `Database Roles`
- Source Heading Path: `Database Roles > Role Attributes`
- Source Line Ranges: `103-224`
- Chunk ID: `pg16_configuration_0104_8b7d05b469`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e28520e06bbc4c88d17e11dbe793c1ca69ace9f8c2887c050cb45a4372b0ffa`

## Retrieval Guidance

- Use When: 需要配置角色能力、权限属性、连接数限制或角色级默认 GUC。
- Retrieval Keywords: LOGIN, SUPERUSER, CREATEDB, CREATEROLE, REPLICATION, PASSWORD, NOINHERIT, BYPASSRLS, CONNECTION LIMIT, ALTER ROLE SET
- Follow-up Guidance: superuser、BYPASSRLS、CREATEROLE 等高权限变更需审查。
- Classification Note: 定义 LOGIN、SUPERUSER、CREATEDB、REPLICATION、PASSWORD、INHERIT、BYPASSRLS、CONNECTION LIMIT 和角色级 SET 默认值。

## Official Source Content

## Role Attributes

A database role can have a number of attributes that define its
privileges and interact with the client authentication system.

**login privilege**
: Only roles that have the `LOGIN` attribute can be used
as the initial role name for a database connection.  A role with
the `LOGIN` attribute can be considered the same
as a "database user".  To create a role with login privilege,
use either:

```
CREATE ROLE `name` LOGIN;
CREATE USER `name`;
```

(`CREATE USER` is equivalent to `CREATE ROLE`
except that `CREATE USER` includes `LOGIN` by
default, while `CREATE ROLE` does not.)

**superuser status**
: A database superuser bypasses all permission checks, except the right
to log in.  This is a dangerous privilege and should not be used
carelessly; it is best to do most of your work as a role that is not a
superuser.  To create a new database superuser, use `CREATE
ROLE `name` SUPERUSER`.  You must do
this as a role that is already a superuser.

**database creation**
: A role must be explicitly given permission to create databases
(except for superusers, since those bypass all permission
checks). To create such a role, use `CREATE ROLE
`name` CREATEDB`.

**initiating replication**
: A role must explicitly be given permission to initiate streaming
replication (except for superusers, since those bypass all permission
checks). A role used for streaming replication must
have `LOGIN` permission as well. To create such a role, use
`CREATE ROLE `name` REPLICATION
LOGIN`.

**password**
: A password is only significant if the client authentication
method requires the user to supply a password when connecting
to the database. The `password` and
`md5` authentication methods
make use of passwords. Database passwords are separate from
operating system passwords. Specify a password upon role
creation with `CREATE ROLE
`name` PASSWORD '`string`'`.

**inheritance of privileges**
: A role inherits the privileges of roles it is a member of, by default.
However, to create a role which does not inherit privileges by
default, use `CREATE ROLE `name`
NOINHERIT`.  Alternatively, inheritance can be overridden
for individual grants by using `WITH INHERIT TRUE`
or `WITH INHERIT FALSE`.

**bypassing row-level security**
: A role must be explicitly given permission to bypass every row-level security (RLS) policy
(except for superusers, since those bypass all permission checks).
To create such a role, use `CREATE ROLE `name` BYPASSRLS` as a superuser.

**connection limit**
: Connection limit can specify how many concurrent connections a role can make.
-1 (the default) means no limit. Specify connection limit upon role creation with
`CREATE ROLE `name` CONNECTION LIMIT '`integer`'`.

A role's attributes can be modified after creation with
`ALTER ROLE`.
See the reference pages for the [sql-createrole](#sql-createrole)
and [sql-alterrole](#sql-alterrole) commands for details.

A role can also have role-specific defaults for many of the run-time
configuration settings described in [runtime-config](#runtime-config).  For example, if for some reason you
want to disable index scans (hint: not a good idea) anytime you
connect, you can use:

```
ALTER ROLE myname SET enable_indexscan TO off;
```

This will save the setting (but not set it immediately).  In
subsequent connections by this role it will appear as though
`SET enable_indexscan TO off` had been executed
just before the session started.
You can still alter this setting during the session; it will only
be the default. To remove a role-specific default setting, use
`ALTER ROLE `rolename` RESET `varname``.
Note that role-specific defaults attached to roles without
`LOGIN` privilege are fairly useless, since they will never
be invoked.

When a non-superuser creates a role using the `CREATEROLE`
privilege, the created role is automatically granted back to the creating
user, just as if the bootstrap superuser had executed the command
`GRANT created_user TO creating_user WITH ADMIN TRUE, SET FALSE,
INHERIT FALSE`. Since a `CREATEROLE` user can
only exercise special privileges with regard to an existing role if they
have `ADMIN OPTION` on it, this grant is just sufficient
to allow a `CREATEROLE` user to administer the roles they
created. However, because it is created with `INHERIT FALSE, SET
FALSE`, the `CREATEROLE` user doesn't inherit the
privileges of the created role, nor can it access the privileges of that
role using `SET ROLE`. However, since any user who has
`ADMIN OPTION` on a role can grant membership in that
role to any other user, the `CREATEROLE` user can gain
access to the created role by simply granting that role back to
themselves with the `INHERIT` and/or `SET`
options. Thus, the fact that privileges are not inherited by default nor
is `SET ROLE` granted by default is a safeguard against
accidents, not a security feature. Also note that, because this automatic
grant is granted by the bootstrap user, it cannot be removed or changed by
the `CREATEROLE` user; however, any superuser could
revoke it, modify it, and/or issue additional such grants to other
`CREATEROLE` users. Whichever `CREATEROLE`
users have `ADMIN OPTION` on a role at any given time
can administer it.
