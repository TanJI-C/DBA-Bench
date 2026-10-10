# RBAC overview and role creation and grants

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/role-based-access-control.md`
- Source Title: `Role-Based Access Control`
- Source Heading Path: `Role-Based Access Control | Role-Based Access Control > RBAC operations | Role-Based Access Control > RBAC operations > Create a role | Role-Based Access Control > RBAC operations > Grant a privilege to a role | Role-Based Access Control > RBAC operations > Grant a role to a user`
- Source Line Ranges: `5-106`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `rbac`, `roles`, `create-role`, `grant-privileges`, `grant-role`, `user-management`, `privilege-inheritance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0211_fa2f651e62`
- Source ID: `tidb-docs-8.1:role-based-access-control.md#role-based-access-control`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf6f10070dbad3e667fa8aab2aab05048a2ba0ff11a67dee69f9acb6c512e878`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/role-based-access-control#role-based-access-control
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/role-based-access-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how TiDB RBAC roles are created, how privileges are granted to roles, how roles are granted to users, and what privileges are required for these grant operations.
- Retrieval Keywords: Role-Based Access Control, RBAC operations, CREATE ROLE, GRANT SELECT ON app_db.* TO 'app_read'@'%';, GRANT INSERT, UPDATE, DELETE ON app_db.* TO 'app_write'@'%';, GRANT ALL ON app_db.* TO 'app_developer';, GRANT 'app_developer' TO 'dev1'@'localhost';, GRANT 'app_read', 'app_write' TO 'rw_user1'@'localhost';, CREATE USER, CREATE ROLE privilege, CREATE USER privilege, SUPER privilege, mysql.user, privilege inheritance, relation loop
- Follow-up Guidance: The content also notes that granting a role to a user does not enable the role immediately, because enabling a role is a separate operation.
- Classification Note: This is classified as an operation chunk because the official content gives SQL procedures and required privileges for creating roles, granting privileges to roles, and granting roles to users.

## Official Source Content

# Role-Based Access Control

The implementation of TiDB's role-based access control (RBAC) system is similar to that of MySQL 8.0. TiDB is compatible with most RBAC syntax of MySQL.

This document introduces TiDB RBAC-related operations and implementation.
## RBAC operations

A role is a collection of a series of privileges. You can do the following operations:

- Create a role.
- Delete a role.
- Grant a privilege to a role.
- Grant a role to another user. That user can obtain the privileges involved in the role, after enabling the role.
### Create a role

For example, you can use the following statement to create the roles `app_developer`, `app_read`, and `app_write`:

```sql
CREATE ROLE 'app_developer', 'app_read', 'app_write';
```

For the role naming format and rule, see [TiDB User Account Management](https://docs.pingcap.com/tidb/stable/user-account-management).

Roles are stored in the `mysql.user` table and the host name part of the role name (if omitted) defaults to `'%'`. The name of the role you are trying to create must be unique; otherwise, an error is reported.

To create a role, you need the `CREATE ROLE` or `CREATE USER` privilege.
### Grant a privilege to a role

The operation of granting a privilege to a role is the same with that of granting a privilege to a user. For details, see [TiDB Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management).

For example, you can use the following statement to grant the `app_read` role the privilege to read the `app_db` database:

```sql
GRANT SELECT ON app_db.* TO 'app_read'@'%';
```

You can use the following statement to grant the `app_write` role the privilege to write data to the `app_db` database:

```sql
GRANT INSERT, UPDATE, DELETE ON app_db.* TO 'app_write'@'%';
```

You can use the following statement to grant the `app_developer` role all privileges on the `app_db` database:

```sql
GRANT ALL ON app_db.* TO 'app_developer';
```
### Grant a role to a user

Assume that a user `dev1` has the developer role with all the privileges on `app_db`; two users `read_user1` and `read_user2` have the read-only privilege on `app_db`; and a user `rw_user1` has read and write privileges on `app_db`.

Use `CREATE USER` to create the users:

```sql
CREATE USER 'dev1'@'localhost' IDENTIFIED BY 'dev1pass';
CREATE USER 'read_user1'@'localhost' IDENTIFIED BY 'read_user1pass';
CREATE USER 'read_user2'@'localhost' IDENTIFIED BY 'read_user2pass';
CREATE USER 'rw_user1'@'localhost' IDENTIFIED BY 'rw_user1pass';
```

Then use `GRANT` to grant roles to users

```sql
GRANT 'app_developer' TO 'dev1'@'localhost';
GRANT 'app_read' TO 'read_user1'@'localhost', 'read_user2'@'localhost';
GRANT 'app_read', 'app_write' TO 'rw_user1'@'localhost';
```

To grant a role to another user or revoke a role, you need the `SUPER` privilege.

Granting a role to a user does not mean enabling the role immediately. Enabling a role is another operation.

The following operations might form a "relation loop:"

```sql
CREATE USER 'u1', 'u2';
CREATE ROLE 'r1', 'r2';

GRANT 'u1' TO 'u1';
GRANT 'r1' TO 'r1';

GRANT 'r2' TO 'u2';
GRANT 'u2' TO 'r2';
```

TiDB supports this multi-level authorization relationship. You can use it to implement privilege inheritance.
