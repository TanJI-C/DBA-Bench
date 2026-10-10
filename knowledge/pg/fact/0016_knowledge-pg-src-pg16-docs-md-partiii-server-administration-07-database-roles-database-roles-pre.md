# Predefined Roles

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/07_database_roles.md`
- Source Title: `Database Roles`
- Source Heading Path: `Database Roles > Predefined Roles`
- Source Line Ranges: `419-492`
- Chunk ID: `pg16_fact_0016_945775290e`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ffd90441e8cd60fab9771b39cf4892b6d71dd6c2c50a30e85f23cc43c14f2f1f`

## Retrieval Guidance

- Use When: 需要查询内置角色授予后会获得哪些能力。
- Retrieval Keywords: predefined roles, pg_read_all_data, pg_write_all_data, pg_monitor, pg_signal_backend, pg_read_server_files, pg_execute_server_program, pg_checkpoint
- Follow-up Guidance: 预定义角色权限未来版本可能变化，需看 release notes。
- Classification Note: 列出 pg_read_all_data、pg_monitor、pg_signal_backend、server file/program 等预定义角色能力。

## Official Source Content

## Predefined Roles

PostgreSQL provides a set of predefined roles
that provide access to certain, commonly needed, privileged capabilities
and information.  Administrators (including roles that have the
`CREATEROLE` privilege) can `GRANT` these
roles to users and/or other roles in their environment, providing those
users with access to the specified capabilities and information.

The predefined roles are described in [predefined-roles-table](#predefined-roles-table).
Note that the specific permissions for each of the roles may change in
the future as additional capabilities are added.  Administrators
should monitor the release notes for changes.

| Role | Allowed Access |
| --- | --- |
| pg_read_all_data | Read all data (tables, views, sequences), as if having        `SELECT` rights on those objects, and USAGE rights on        all schemas, even without having it explicitly.  This role does not have        the role attribute `BYPASSRLS` set.  If RLS is being        used, an administrator may wish to set `BYPASSRLS` on        roles which this role is GRANTed to. |
| pg_write_all_data | Write all data (tables, views, sequences), as if having        `INSERT`, `UPDATE`, and        `DELETE` rights on those objects, and USAGE rights on        all schemas, even without having it explicitly.  This role does not have        the role attribute `BYPASSRLS` set.  If RLS is being        used, an administrator may wish to set `BYPASSRLS` on        roles which this role is GRANTed to. |
| pg_read_all_settings | Read all configuration variables, even those normally visible only to        superusers. |
| pg_read_all_stats | Read all pg_stat_* views and use various statistics related extensions,        even those normally visible only to superusers. |
| pg_stat_scan_tables | Execute monitoring functions that may take `ACCESS SHARE` locks on tables,        potentially for a long time. |
| pg_monitor | Read/execute various monitoring views and functions.        This role is a member of `pg_read_all_settings`,        `pg_read_all_stats` and        `pg_stat_scan_tables`. |
| pg_database_owner | None.  Membership consists, implicitly, of the current database owner. |
| pg_signal_backend | Signal another backend to cancel a query or terminate its session. |
| pg_read_server_files | Allow reading files from any location the database can access on the server with COPY and        other file-access functions. |
| pg_write_server_files | Allow writing to files in any location the database can access on the server with COPY and        other file-access functions. |
| pg_execute_server_program | Allow executing programs on the database server as the user the database runs as with        COPY and other functions which allow executing a server-side program. |
| pg_checkpoint | Allow executing        the [`CHECKPOINT`](#sql-checkpoint)        command. |
| pg_use_reserved_connections | Allow use of connection slots reserved via        [guc-reserved-connections](#guc-reserved-connections). |
| pg_create_subscription | Allow users with `CREATE` permission on the        database to issue        [`CREATE SUBSCRIPTION`](#sql-createsubscription). |

The `pg_monitor`, `pg_read_all_settings`,
`pg_read_all_stats` and `pg_stat_scan_tables`
roles are intended to allow administrators to easily configure a role for the
purpose of monitoring the database server. They grant a set of common privileges
allowing the role to read various useful configuration settings, statistics and
other system information normally restricted to superusers.

The `pg_database_owner` role has one implicit,
situation-dependent member, namely the owner of the current database.  Like
any role, it can own objects or receive grants of access privileges.
Consequently, once `pg_database_owner` has rights within a
template database, each owner of a database instantiated from that template
will exercise those rights.  `pg_database_owner` cannot be
a member of any role, and it cannot have non-implicit members.  Initially,
this role owns the `public` schema, so each database owner
governs local use of the schema.

The `pg_signal_backend` role is intended to allow
administrators to enable trusted, but non-superuser, roles to send signals
to other backends. Currently this role enables sending of signals for
canceling a query on another backend or terminating its session. A user
granted this role cannot however send signals to a backend owned by a
superuser.  See [functions-admin-signal](#functions-admin-signal).

The `pg_read_server_files`, `pg_write_server_files` and
`pg_execute_server_program` roles are intended to allow administrators to have
trusted, but non-superuser, roles which are able to access files and run programs on the
database server as the user the database runs as.  As these roles are able to access any file on
the server file system, they bypass all database-level permission checks when accessing files
directly and they could be used to gain superuser-level access, therefore
great care should be taken when granting these roles to users.

Care should be taken when granting these roles to ensure they are only used where
needed and with the understanding that these roles grant access to privileged
information.

Administrators can grant access to these roles to users using the
[`GRANT`](#sql-grant) command, for example:

```
GRANT pg_signal_backend TO admin_user;
```
