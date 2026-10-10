# Inspect, enable, revoke, and delete RBAC roles

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/role-based-access-control.md`
- Source Title: `Role-Based Access Control`
- Source Heading Path: `Role-Based Access Control > RBAC operations > Check a role's privileges | Role-Based Access Control > RBAC operations > Set the default role | Role-Based Access Control > RBAC operations > Enable a role in the current session | Role-Based Access Control > RBAC operations > Check the current enabled role | Role-Based Access Control > RBAC operations > Revoke a role | Role-Based Access Control > RBAC operations > Revoke a privilege | Role-Based Access Control > RBAC operations > Delete a role`
- Source Line Ranges: `107-370`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `show-grants`, `default-roles`, `set-role`, `current-role`, `revoke-role`, `revoke-privileges`, `drop-role`, `session-roles`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0212_205fe5b318`
- Source ID: `tidb-docs-8.1:role-based-access-control.md#check-a-role-s-privileges`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b6886e90ecae81cbfe586a0a6bd854c0a93c492c31beb1761b44c00a078c72b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/role-based-access-control#check-a-role-s-privileges
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/role-based-access-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to inspect RBAC grants, set or enable default and session roles, check CURRENT_ROLE(), revoke roles or privileges, or drop roles in TiDB.
- Retrieval Keywords: SHOW GRANTS, SHOW GRANTS FOR CURRENT_USER(), SHOW GRANTS FOR 'dev1'@'localhost' USING 'app_developer';, SHOW GRANTS FOR 'rw_user1'@'localhost' USING 'app_read', 'app_write';, SET DEFAULT ROLE, SET ROLE, CURRENT_ROLE(), REVOKE 'app_read' FROM 'read_user1'@'localhost', 'read_user2'@'localhost';, REVOKE INSERT, UPDATE, DELETE ON app_db.* FROM 'app_write';, DROP ROLE 'app_read', 'app_write';, ALL EXCEPT, mysql.user, DROP ROLE privilege, DROP USER privilege
- Follow-up Guidance: The content also states that setting a default role requires the role to have been granted first, and that SET ROLE only affects the current session.
- Classification Note: This is classified as an operation chunk because the official content provides SQL statements and behavior for checking grants, managing enabled and default roles, revoking roles or privileges, and deleting roles.

## Official Source Content

### Check a role's privileges

You can use the `SHOW GRANTS` statement to check what privileges have been granted to the user.

To check privilege-related information of another user, you need the `SELECT` privilege on the `mysql` database.

```sql
SHOW GRANTS FOR 'dev1'@'localhost';
```

```
+-------------------------------------------------+
| Grants for dev1@localhost                       |
+-------------------------------------------------+
| GRANT USAGE ON *.* TO `dev1`@`localhost`        |
| GRANT `app_developer`@`%` TO `dev1`@`localhost` |
+-------------------------------------------------+
```

You can use the `USING` option in `SHOW GRANTS` to check a role's privileges:

```sql
SHOW GRANTS FOR 'dev1'@'localhost' USING 'app_developer';
```

```sql
+----------------------------------------------------------+
| Grants for dev1@localhost                                |
+----------------------------------------------------------+
| GRANT USAGE ON *.* TO `dev1`@`localhost`                 |
| GRANT ALL PRIVILEGES ON `app_db`.* TO `dev1`@`localhost` |
| GRANT `app_developer`@`%` TO `dev1`@`localhost`          |
+----------------------------------------------------------+
```

```sql
SHOW GRANTS FOR 'rw_user1'@'localhost' USING 'app_read', 'app_write';
```

```
+------------------------------------------------------------------------------+
| Grants for rw_user1@localhost                                                |
+------------------------------------------------------------------------------+
| GRANT USAGE ON *.* TO `rw_user1`@`localhost`                                 |
| GRANT SELECT, INSERT, UPDATE, DELETE ON `app_db`.* TO `rw_user1`@`localhost` |
| GRANT `app_read`@`%`,`app_write`@`%` TO `rw_user1`@`localhost`               |
+------------------------------------------------------------------------------+
```

```sql
SHOW GRANTS FOR 'read_user1'@'localhost' USING 'app_read';
```

```
+--------------------------------------------------------+
| Grants for read_user1@localhost                        |
+--------------------------------------------------------+
| GRANT USAGE ON *.* TO `read_user1`@`localhost`         |
| GRANT SELECT ON `app_db`.* TO `read_user1`@`localhost` |
| GRANT `app_read`@`%` TO `read_user1`@`localhost`       |
+--------------------------------------------------------+
```

You can use `SHOW GRANTS` or `SHOW GRANTS FOR CURRENT_USER()` to check the current user's privileges. `SHOW GRANTS` and `SHOW GRANTS FOR CURRENT_USER()` are different in the following aspects:

- `SHOW GRANTS` shows the privilege of the enabled role for the current user.
- `SHOW GRANTS FOR CURRENT_USER()` does not show the enabled role's privilege.
### Set the default role

After a role is granted to a user, it does not take effect immediately. Only after the user enables this role, he can use the privilege the role owns.

You can set default roles for a user. When the user logs in, the default roles are automatically enabled.

```sql
SET DEFAULT ROLE
    {NONE | ALL | role [, role ] ...}
    TO user [, user ]
```

For example, you can use the following statement to set default roles of `rw_user1@localhost` to `app_read` and `app_write`:

```sql
SET DEFAULT ROLE app_read, app_write TO 'rw_user1'@'localhost';
```

You can use the following statement to set default roles of `dev1@localhost` to all roles:

```sql
SET DEFAULT ROLE ALL TO 'dev1'@'localhost';
```

You can use the following statement to disable all default roles of `dev1@localhost`:

```sql
SET DEFAULT ROLE NONE TO 'dev1'@'localhost';
```

> **Note:**
>
> You need to grant the role to the user before you set the default role to this role.
### Enable a role in the current session

You can enable some role(s) in the current session.

```sql
SET ROLE {
    DEFAULT
  | NONE
  | ALL
  | ALL EXCEPT role [, role ] ...
  | role [, role ] ...
}
```

For example, after `rw_user1` logs in, you can use the following statement to enable roles `app_read` and `app_write` that are valid only in the current session:

```sql
SET ROLE 'app_read', 'app_write';
```

You can use the following statement to enable the default role of the current user:

```sql
SET ROLE DEFAULT
```

You can use the following statement to enable all roles granted to the current user:

```sql
SET ROLE ALL
```

You can use the following statement to disable all roles:

```sql
SET ROLE NONE
```

You can use the following statement to enable roles except `app_read`:

```sql
SET ROLE ALL EXCEPT 'app_read'
```

> **Note:**
>
> If you use `SET ROLE` to enable a role, this role is valid only in the current session.
### Check the current enabled role

The current user can use the `CURRENT_ROLE()` function to check which role has been enabled by the current user.

For example, you can grant default roles to `rw_user1'@'localhost`:

```sql
SET DEFAULT ROLE ALL TO 'rw_user1'@'localhost';
```

After `rw_user1@localhost` logs in, you can execute the following statement:

```sql
SELECT CURRENT_ROLE();
```

```
+--------------------------------+
| CURRENT_ROLE()                 |
+--------------------------------+
| `app_read`@`%`,`app_write`@`%` |
+--------------------------------+
```

```sql
SET ROLE 'app_read'; SELECT CURRENT_ROLE();
```

```
+----------------+
| CURRENT_ROLE() |
+----------------+
| `app_read`@`%` |
+----------------+
```
### Revoke a role

You can use the following statement to revoke the `app_read` role granted to the users `read_user1@localhost` and `read_user2@localhost`:

```sql
REVOKE 'app_read' FROM 'read_user1'@'localhost', 'read_user2'@'localhost';
```

You can use the following statement to revoke the roles `app_read` and `app_write` granted to the `rw_user1@localhost` user:

```sql
REVOKE 'app_read', 'app_write' FROM 'rw_user1'@'localhost';
```

The operation of revoking a role from a user is atomic. If you fail to revoke a role, this operation rolls back.
### Revoke a privilege

The `REVOKE` statement is reverse to `GRANT`. You can use `REVOKE` to revoke the privileges of `app_write`.

```sql
REVOKE INSERT, UPDATE, DELETE ON app_db.* FROM 'app_write';
```

For details, see [TiDB Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management).
### Delete a role

You can use the following statement to delete roles `app_read` and `app_write`:

```sql
DROP ROLE 'app_read', 'app_write';
```

This operation deletes the role records of `app_read` and `app_write` in the `mysql.user` table and related records in the authorization table, and terminates the authorization related to the two roles.

To delete a role, you need the `DROP ROLE` or `DROP USER` privilege.
