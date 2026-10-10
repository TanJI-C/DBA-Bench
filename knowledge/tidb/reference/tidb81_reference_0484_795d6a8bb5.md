# Privilege operations, dynamic privileges, and SUPER privilege

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/privilege-management.md`
- Source Title: `Privilege Management`
- Source Heading Path: `Privilege Management | Privilege Management > Privilege-related operations | Privilege Management > Privilege-related operations > Grant privileges | Privilege Management > Privilege-related operations > Revoke privileges | Privilege Management > Privilege-related operations > Check privileges granted to users | Privilege Management > Privilege-related operations > Dynamic privileges | Privilege Management > `SUPER` privilege`
- Source Line Ranges: `5-213`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`, `dashboard`
- Topic Tags: `privilege-management`, `grant`, `revoke`, `show-grants`, `dynamic-privileges`, `super-privilege`, `sql-mode`, `roles`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0484_795d6a8bb5`
- Source ID: `tidb-docs-8.1:privilege-management.md#privilege-management`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3be4430b5e99baecfe45858f86609df4dd99d17ad2b84fb53762f890d4bb09c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/privilege-management#privilege-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/privilege-management.md

## Retrieval Guidance

- Use When: Use this content when looking for TiDB privilege management details around GRANT, REVOKE, SHOW GRANTS, dynamic privileges, SQL Mode effects on GRANT, or the meaning of the SUPER privilege.
- Retrieval Keywords: GRANT SELECT ON test.* TO 'xxx'@'%', GRANT ALL PRIVILEGES ON *.*, REVOKE ALL PRIVILEGES ON `test`.*, SHOW GRANTS, SHOW GRANTS FOR 'root'@'%', SHOW PRIVILEGES, NO_AUTO_CREATE_USER, You are not allowed to create a user with GRANT, ERROR 1141 (42000): There is no such grant defined for user, fuzzy matching in GRANT, `te%`.*, `te\\%`.*, mysql.user, mysql.db, dynamic privileges, BACKUP_ADMIN, RESTORE_ADMIN, SYSTEM_USER, SYSTEM_VARIABLES_ADMIN, ROLE_ADMIN, CONNECTION_ADMIN, PLACEMENT_ADMIN, DASHBOARD_CLIENT, RESTRICTED_TABLES_ADMIN, RESTRICTED_STATUS_ADMIN, RESTRICTED_VARIABLES_ADMIN, RESTRICTED_USER_ADMIN, RESTRICTED_CONNECTION_ADMIN, RESTRICTED_REPLICA_WRITER_ADMIN, SUPER privilege, KILL, KILL TIDB, tidb_restricted_read_only
- Follow-up Guidance: The source also points to SHOW PRIVILEGES for the full dynamic privilege set and notes that dynamic privileges can replace SUPER with more fine-grained access control.
- Classification Note: This chunk is reference content because it defines privilege-related SQL operations, error behaviors, supported dynamic privileges, and the documented meaning of the SUPER privilege in TiDB.

## Official Source Content

# Privilege Management

TiDB supports MySQL 5.7's privilege management system, including the syntax and privilege types. The following features from MySQL 8.0 are also supported:

* SQL Roles, starting with TiDB 3.0.
* Dynamic privileges, starting with TiDB 5.1.

This document introduces privilege-related TiDB operations, privileges required for TiDB operations and implementation of the privilege system.
## Privilege-related operations
### Grant privileges

The `GRANT` statement grants privileges to the user accounts.

For example, use the following statement to grant the `xxx` user the privilege to read the `test` database.

```sql
GRANT SELECT ON test.* TO 'xxx'@'%';
```

Use the following statement to grant the `xxx` user all privileges on all databases:

```sql
GRANT ALL PRIVILEGES ON *.* TO 'xxx'@'%';
```

By default, `GRANT` statements will return an error if the user specified does not exist. This behavior depends on if the SQL Mode `NO_AUTO_CREATE_USER` is specified:

```sql
mysql> SET sql_mode=DEFAULT;
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT @@sql_mode;
+-------------------------------------------------------------------------------------------------------------------------------------------+
| @@sql_mode                                                                                                                                |
+-------------------------------------------------------------------------------------------------------------------------------------------+
| ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION |
+-------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SELECT * FROM mysql.user WHERE user='idontexist';
Empty set (0.00 sec)

mysql> GRANT ALL PRIVILEGES ON test.* TO 'idontexist';
ERROR 1105 (HY000): You are not allowed to create a user with GRANT

mysql> SELECT user,host,authentication_string FROM mysql.user WHERE user='idontexist';
Empty set (0.00 sec)
```

In the following example, the user `idontexist` is automatically created with an empty password because the SQL Mode `NO_AUTO_CREATE_USER` was not set. This is **not recommended** since it presents a security risk: miss-spelling a username will result in a new user created with an empty password:

```sql
mysql> SET @@sql_mode='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT @@sql_mode;
+-----------------------------------------------------------------------------------------------------------------------+
| @@sql_mode                                                                                                            |
+-----------------------------------------------------------------------------------------------------------------------+
| ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION |
+-----------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

mysql> SELECT * FROM mysql.user WHERE user='idontexist';
Empty set (0.00 sec)

mysql> GRANT ALL PRIVILEGES ON test.* TO 'idontexist';
Query OK, 1 row affected (0.05 sec)

mysql> SELECT user,host,authentication_string FROM mysql.user WHERE user='idontexist';
+------------+------+-----------------------+
| user       | host | authentication_string |
+------------+------+-----------------------+
| idontexist | %    |                       |
+------------+------+-----------------------+
1 row in set (0.01 sec)
```

You can use fuzzy matching in `GRANT` to grant privileges to databases.

```sql
mysql> GRANT ALL PRIVILEGES ON `te%`.* TO genius;
Query OK, 0 rows affected (0.00 sec)

mysql> SELECT user,host,db FROM mysql.db WHERE user='genius';
+--------|------|-----+
| user   | host | db  |
+--------|------|-----+
| genius | %    | te% |
+--------|------|-----+
1 row in set (0.00 sec)
```

In this example, because of the `%` in `te%`, all the databases starting with `te` are granted the privilege.
### Revoke privileges

The `REVOKE` statement enables system administrators to revoke privileges from the user accounts.

The `REVOKE` statement corresponds with the `REVOKE` statement:

```sql
REVOKE ALL PRIVILEGES ON `test`.* FROM 'genius'@'localhost';
```

> **Note:**
>
> To revoke privileges, you need the exact match. If the matching result cannot be found, an error will be displayed:

```sql
mysql> REVOKE ALL PRIVILEGES ON `te%`.* FROM 'genius'@'%';
ERROR 1141 (42000): There is no such grant defined for user 'genius' on host '%'
```

About fuzzy matching, escape, string and identifier:

```sql
mysql> GRANT ALL PRIVILEGES ON `te\%`.* TO 'genius'@'localhost';
Query OK, 0 rows affected (0.00 sec)
```

This example uses exact match to find the database named `te%`. Note that the `%` uses the `\` escape character so that `%` is not considered as a wildcard.

A string is enclosed in single quotation marks(''), while an identifier is enclosed in backticks (``). See the differences below:

```sql
mysql> GRANT ALL PRIVILEGES ON 'test'.* TO 'genius'@'localhost';
ERROR 1064 (42000): You have an error in your SQL syntax; check the
manual that corresponds to your MySQL server version for the right
syntax to use near ''test'.* to 'genius'@'localhost'' at line 1

mysql> GRANT ALL PRIVILEGES ON `test`.* TO 'genius'@'localhost';
Query OK, 0 rows affected (0.00 sec)
```

If you want to use special keywords as table names, enclose them in backticks (``). For example:

```sql
mysql> CREATE TABLE `select` (id int);
Query OK, 0 rows affected (0.27 sec)
```
### Check privileges granted to users

You can use the `SHOW GRANTS` statement to see what privileges are granted to a user. For example:

```sql
SHOW GRANTS; -- show grants for the current user

+-------------------------------------------------------------+
| Grants for User                                             |
+-------------------------------------------------------------+
| GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION |
+-------------------------------------------------------------+
SHOW GRANTS FOR 'root'@'%'; -- show grants for a specific user
```

For example, create a user `rw_user@192.168.%` and grant the user with write privilege on the `test.write_table` table and global read privilege.

```sql
CREATE USER `rw_user`@`192.168.%`;
GRANT SELECT ON *.* TO `rw_user`@`192.168.%`;
GRANT INSERT, UPDATE ON `test`.`write_table` TO `rw_user`@`192.168.%`;
```

Show granted privileges of the `rw_user@192.168.%` user:

```sql
SHOW GRANTS FOR `rw_user`@`192.168.%`;

+------------------------------------------------------------------+
| Grants for rw_user@192.168.%                                     |
+------------------------------------------------------------------+
| GRANT Select ON *.* TO 'rw_user'@'192.168.%'                     |
| GRANT Insert,Update ON test.write_table TO 'rw_user'@'192.168.%' |
+------------------------------------------------------------------+
```
### Dynamic privileges

Since v5.1, TiDB features support dynamic privileges, a feature borrowed from MySQL 8.0. Dynamic privileges are intended to replace the `SUPER` privilege by implementing more fine-grained access to certain operations. For example, using dynamic privileges, system administrators can create a user account that can only perform `BACKUP` and `RESTORE` operations.

Dynamic privileges include:

* `BACKUP_ADMIN`
* `RESTORE_ADMIN`
* `SYSTEM_USER`
* `SYSTEM_VARIABLES_ADMIN`
* `ROLE_ADMIN`
* `CONNECTION_ADMIN`
* `PLACEMENT_ADMIN` allows privilege owners to create, modify, and remove placement policies.
* `DASHBOARD_CLIENT` allows privilege owners to log in to TiDB Dashboard.
* `RESTRICTED_TABLES_ADMIN` allows privilege owners to view system tables when SEM is enabled.
* `RESTRICTED_STATUS_ADMIN` allows privilege owners to view all status variables in [`SHOW [GLOBAL|SESSION] STATUS`](/sql-statements/sql-statement-show-status.md) when SEM is enabled.
* `RESTRICTED_VARIABLES_ADMIN` allows privilege owners to view all system variables when SEM is enabled.
* `RESTRICTED_USER_ADMIN` prohibits privilege owners to have their access revoked by SUPER users when SEM is enabled.
* `RESTRICTED_CONNECTION_ADMIN` allows privilege owners to kill connections of `RESTRICTED_USER_ADMIN` users. This privilege affects `KILL` and `KILL TIDB` statements.
* `RESTRICTED_REPLICA_WRITER_ADMIN` allows privilege owners to perform write or update operations without being affected when the read-only mode is enabled in the TiDB cluster. For details, see [`tidb_restricted_read_only`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_restricted_read_only-new-in-v520).

To see the full set of dynamic privileges, execute the `SHOW PRIVILEGES` statement. Because plugins are permitted to add new privileges, the list of privileges that are assignable might differ based on your TiDB installation.
## `SUPER` privilege

- The `SUPER` privilege allows the user to perform almost any operation. By default, only the `root` user is granted with this privilege. Be careful when granting this privilege to other users.
- The `SUPER` privilege is considered [deprecated in MySQL 8.0](https://dev.mysql.com/doc/refman/8.0/en/privileges-provided.html#dynamic-privileges-migration-from-super) and can be replaced by [dynamic privileges](#dynamic-privileges) to provide more fine-grained access control.
