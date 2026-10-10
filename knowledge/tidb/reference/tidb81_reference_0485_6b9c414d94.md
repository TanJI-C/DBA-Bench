# Required privileges for TiDB SQL operations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/privilege-management.md`
- Source Title: `Privilege Management`
- Source Heading Path: `Privilege Management > Privileges required for TiDB operations | Privilege Management > Privileges required for TiDB operations > ALTER | Privilege Management > Privileges required for TiDB operations > BACKUP | Privilege Management > Privileges required for TiDB operations > CANCEL IMPORT JOB | Privilege Management > Privileges required for TiDB operations > CREATE DATABASE | Privilege Management > Privileges required for TiDB operations > CREATE INDEX | Privilege Management > Privileges required for TiDB operations > CREATE TABLE | Privilege Management > Privileges required for TiDB operations > CREATE VIEW | Privilege Management > Privileges required for TiDB operations > DROP DATABASE | Privilege Management > Privileges required for TiDB operations > DROP INDEX | Privilege Management > Privileges required for TiDB operations > DROP TABLES | Privilege Management > Privileges required for TiDB operations > IMPORT INTO | Privilege Management > Privileges required for TiDB operations > LOAD DATA | Privilege Management > Privileges required for TiDB operations > TRUNCATE TABLE | Privilege Management > Privileges required for TiDB operations > RENAME TABLE | Privilege Management > Privileges required for TiDB operations > ANALYZE TABLE | Privilege Management > Privileges required for TiDB operations > LOCK STATS | Privilege Management > Privileges required for TiDB operations > UNLOCK STATS | Privilege Management > Privileges required for TiDB operations > SHOW | Privilege Management > Privileges required for TiDB operations > CREATE ROLE/USER | Privilege Management > Privileges required for TiDB operations > DROP ROLE/USER | Privilege Management > Privileges required for TiDB operations > ALTER USER | Privilege Management > Privileges required for TiDB operations > GRANT | Privilege Management > Privileges required for TiDB operations > REVOKE | Privilege Management > Privileges required for TiDB operations > SET GLOBAL | Privilege Management > Privileges required for TiDB operations > ADMIN | Privilege Management > Privileges required for TiDB operations > SET DEFAULT ROLE | Privilege Management > Privileges required for TiDB operations > KILL | Privilege Management > Privileges required for TiDB operations > CREATE RESOURCE GROUP | Privilege Management > Privileges required for TiDB operations > ALTER RESOURCE GROUP | Privilege Management > Privileges required for TiDB operations > DROP RESOURCE GROUP | Privilege Management > Privileges required for TiDB operations > CALIBRATE RESOURCE`
- Source Line Ranges: `214-414`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `br`
- Topic Tags: `privileges`, `grant`, `revoke`, `show`, `backup`, `import`, `load-data`, `resource-groups`, `user-management`, `role-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0485_6b9c414d94`
- Source ID: `tidb-docs-8.1:privilege-management.md#privileges-required-for-tidb-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `17b57b4a6489cbca17e027523d358efb877a6d7164c87940befdb700350b508b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/privilege-management#privileges-required-for-tidb-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/privilege-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact privileges required for a specific TiDB SQL operation, user or role statement, SHOW statement, import or backup command, or resource group statement.
- Retrieval Keywords: INFORMATION_SCHEMA.USER_PRIVILEGES, ALTER privilege, BACKUP_ADMIN, CANCEL IMPORT JOB, CREATE DATABASE privilege, CREATE INDEX privilege, CREATE TABLE LIKE SELECT privilege, CREATE VIEW, SUPER privilege, IMPORT INTO FILE privilege, LOAD DATA, REPLACE INTO DELETE privilege, TRUNCATE TABLE DROP privilege, RENAME TABLE privileges, ANALYZE TABLE, LOCK STATS, UNLOCK STATS, SHOW CREATE TABLE, SHOW GRANTS, SHOW PROCESSLIST, SHOW IMPORT JOB, SHOW STATS_LOCKED, CREATE ROLE, CREATE USER, DROP ROLE, DROP USER, ALTER USER, GRANT ROLE, ROLE_ADMIN, REVOKE ROLE, SYSTEM_VARIABLES_ADMIN, CONNECTION_ADMIN, RESOURCE_GROUP_ADMIN, CALIBRATE RESOURCE
- Follow-up Guidance: The source also shows that you can check a user's granted privileges in the INFORMATION_SCHEMA.USER_PRIVILEGES table with a SELECT query filtered by grantee.
- Classification Note: This is classified as reference content because it enumerates required privileges for many named TiDB operations and statements.

## Official Source Content

## Privileges required for TiDB operations

You can check privileges of TiDB users in the `INFORMATION_SCHEMA.USER_PRIVILEGES` table. For example:

```sql
mysql> SELECT * FROM INFORMATION_SCHEMA.USER_PRIVILEGES WHERE grantee = "'root'@'%'";
+------------+---------------+-------------------------+--------------+
| GRANTEE    | TABLE_CATALOG | PRIVILEGE_TYPE          | IS_GRANTABLE |
+------------+---------------+-------------------------+--------------+
| 'root'@'%' | def           | Select                  | YES          |
| 'root'@'%' | def           | Insert                  | YES          |
| 'root'@'%' | def           | Update                  | YES          |
| 'root'@'%' | def           | Delete                  | YES          |
| 'root'@'%' | def           | Create                  | YES          |
| 'root'@'%' | def           | Drop                    | YES          |
| 'root'@'%' | def           | Process                 | YES          |
| 'root'@'%' | def           | References              | YES          |
| 'root'@'%' | def           | Alter                   | YES          |
| 'root'@'%' | def           | Show Databases          | YES          |
| 'root'@'%' | def           | Super                   | YES          |
| 'root'@'%' | def           | Execute                 | YES          |
| 'root'@'%' | def           | Index                   | YES          |
| 'root'@'%' | def           | Create User             | YES          |
| 'root'@'%' | def           | Create Tablespace       | YES          |
| 'root'@'%' | def           | Trigger                 | YES          |
| 'root'@'%' | def           | Create View             | YES          |
| 'root'@'%' | def           | Show View               | YES          |
| 'root'@'%' | def           | Create Role             | YES          |
| 'root'@'%' | def           | Drop Role               | YES          |
| 'root'@'%' | def           | CREATE TEMPORARY TABLES | YES          |
| 'root'@'%' | def           | LOCK TABLES             | YES          |
| 'root'@'%' | def           | CREATE ROUTINE          | YES          |
| 'root'@'%' | def           | ALTER ROUTINE           | YES          |
| 'root'@'%' | def           | EVENT                   | YES          |
| 'root'@'%' | def           | SHUTDOWN                | YES          |
| 'root'@'%' | def           | RELOAD                  | YES          |
| 'root'@'%' | def           | FILE                    | YES          |
| 'root'@'%' | def           | CONFIG                  | YES          |
| 'root'@'%' | def           | REPLICATION CLIENT      | YES          |
| 'root'@'%' | def           | REPLICATION SLAVE       | YES          |
+------------+---------------+-------------------------+--------------+
31 rows in set (0.00 sec)
```
### ALTER

- For all `ALTER` statements, users must have the `ALTER` privilege for the corresponding table.
- For statements except `ALTER...DROP` and `ALTER...RENAME TO`, users must have the `INSERT` and `CREATE` privileges for the corresponding table.
- For the `ALTER...DROP` statement, users must have the `DROP` privilege for the corresponding table.
- For the `ALTER...RENAME TO` statement, users must have the `DROP` privilege for the table before renaming, and the `CREATE` and `INSERT` privileges for the table after renaming.

> **Note:**
>
> In MySQL 5.7 documentation, users need `INSERT` and `CREATE` privileges to perform the `ALTER` operation on a table. But in reality for MySQL 5.7.25, only the `ALTER` privilege is required in this case. Currently, the `ALTER` privilege in TiDB is consistent with the actual behavior in MySQL.
### BACKUP

Requires the `SUPER` or `BACKUP_ADMIN` privilege.
### CANCEL IMPORT JOB

Requires the `SUPER` privilege to cancel jobs created by other users. Otherwise, only jobs created by the current user can be canceled.
### CREATE DATABASE

Requires the `CREATE` privilege for the database.
### CREATE INDEX

Requires the `INDEX` privilege for the table.
### CREATE TABLE

Requires the `CREATE` privilege for the table.

To execute the `CREATE TABLE...LIKE...` statement, the `SELECT` privilege for the table is required.
### CREATE VIEW

Requires the `CREATE VIEW` privilege.

> **Note:**
>
> If the current user is not the user that creates the View, both the `CREATE VIEW` and `SUPER` privileges are required.
### DROP DATABASE

Requires the `DROP` privilege for the database.
### DROP INDEX

Requires the `INDEX` privilege for the table.
### DROP TABLES

Requires the `DROP` privilege for the table.
### IMPORT INTO

Requires the `SELECT`, `UPDATE`, `INSERT`, `DELETE`, and `ALTER` privileges for the target table. To import files stored locally in TiDB, the `FILE` privilege is also required.
### LOAD DATA

Requires the `INSERT` privilege for the table. When you use `REPLACE INTO`, the `DELETE` privilege is also required.
### TRUNCATE TABLE

Requires the `DROP` privilege for the table.
### RENAME TABLE

Requires the `ALTER` and `DROP` privileges for the table before renaming and the `CREATE` and `INSERT` privileges for the table after renaming.
### ANALYZE TABLE

Requires the `INSERT` and `SELECT` privileges for the table.
### LOCK STATS

Requires the `INSERT` and `SELECT` privileges for the table.
### UNLOCK STATS

Requires the `INSERT` and `SELECT` privileges for the table.
### SHOW

`SHOW CREATE TABLE` requires any single privilege to the table.

`SHOW CREATE VIEW` requires the `SHOW VIEW` privilege.

`SHOW GRANTS` requires the `SELECT` privilege to the `mysql` database. If the target user is current user, `SHOW GRANTS` does not require any privilege.

`SHOW PROCESSLIST` requires the `PROCESS` privilege to show connections belonging to other users.

`SHOW IMPORT JOB` requires the `SUPER` privilege to show connections belonging to other users. Otherwise, it only shows jobs created by the current user.

`SHOW STATS_LOCKED` requires the `SELECT` privilege to the `mysql.stats_table_locked` table.
### CREATE ROLE/USER

`CREATE ROLE` requires the `CREATE ROLE` privilege.

`CREATE USER` requires the `CREATE USER` privilege.
### DROP ROLE/USER

`DROP ROLE` requires the `DROP ROLE` privilege.

`DROP USER` requires the `CREATE USER` privilege.
### ALTER USER

Requires the `CREATE USER` privilege.
### GRANT

Requires the `GRANT` privilege with the privileges granted by `GRANT`.

Requires additional `CREATE USER` privilege to create a user implicitly.

`GRANT ROLE` requires `SUPER` or `ROLE_ADMIN` privilege.
### REVOKE

Requires the `GRANT` privilege and those privileges targeted by the `REVOKE` statement.

`REVOKE ROLE` requires `SUPER` or `ROLE_ADMIN` privilege.
### SET GLOBAL

Requires `SUPER` or `SYSTEM_VARIABLES_ADMIN` privilege to set global variables.
### ADMIN

Requires `SUPER` privilege.
### SET DEFAULT ROLE

Requires `SUPER` privilege.
### KILL

Requires `SUPER` or `CONNECTION_ADMIN` privilege to kill other user sessions.
### CREATE RESOURCE GROUP

Requires `SUPER` or `RESOURCE_GROUP_ADMIN` privilege.
### ALTER RESOURCE GROUP

Requires `SUPER` or `RESOURCE_GROUP_ADMIN` privilege.
### DROP RESOURCE GROUP

Requires `SUPER` or `RESOURCE_GROUP_ADMIN` privilege.
### CALIBRATE RESOURCE

Requires `SUPER` or `RESOURCE_GROUP_ADMIN` privilege.
