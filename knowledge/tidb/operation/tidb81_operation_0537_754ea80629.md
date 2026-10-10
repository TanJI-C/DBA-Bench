# Manage TiDB user accounts, passwords, and basic account operations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/user-account-management.md`
- Source Title: `TiDB User Account Management`
- Source Heading Path: `TiDB User Account Management | TiDB User Account Management > User names and passwords | TiDB User Account Management > Add user accounts | TiDB User Account Management > Remove user accounts | TiDB User Account Management > Reserved user accounts | TiDB User Account Management > Set account resource limits | TiDB User Account Management > Assign account passwords`
- Source Line Ranges: `5-182`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `user-accounts`, `authentication`, `passwords`, `create-user`, `grant`, `drop-user`, `resource-limits`, `root-account`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0537_754ea80629`
- Source ID: `tidb-docs-8.1:user-account-management.md#tidb-user-account-management`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1643102ab9d4ed0cc6e26b5a289f7d48948230e31016da598c36455347b8db59`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/user-account-management#tidb-user-account-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/user-account-management.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB stores and manages user accounts, including account naming, password assignment, privilege inspection, account deletion, reserved accounts, and related SQL statements.
- Retrieval Keywords: mysql.user, CREATE USER, GRANT, SHOW GRANTS, DROP USER, SET PASSWORD FOR, ALTER USER, 'user_name'@'host_name', NO_AUTO_CREATE_USER, 'root'@'%', IDENTIFIED BY, resource groups
- Follow-up Guidance: It also notes that direct `INSERT`, `UPDATE`, or `DELETE` on privilege tables can lead to incomplete updates and that `SHOW GRANTS FOR 'admin'@'localhost'` displays granted privileges.
- Classification Note: This is classified as operation because the content describes routine TiDB user account administration through SQL statements and account settings.

## Official Source Content

# TiDB User Account Management

This document describes how to manage a TiDB user account.
## User names and passwords

TiDB stores the user accounts in the table of the [`mysql.user`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema-user) system table. Each account is identified by a user name and the client host. Each account may have a password.

You can connect to the TiDB server using the MySQL client, and use the specified account and password to login. For each user name, make sure that it contains no more than 32 characters.

```shell
mysql --port 4000 --user xxx --password
```

Or use the abbreviation of command line parameters:

```shell
mysql -P 4000 -u xxx -p
```
## Add user accounts

You can create TiDB accounts in two ways:

- By using the standard account-management SQL statements intended for creating accounts and establishing their privileges, such as `CREATE USER` and `GRANT`.
- By manipulating the privilege tables directly with statements such as `INSERT`, `UPDATE`, or `DELETE`. It is not recommended to use this method to create accounts, because it might lead to incomplete updates.

You can also create accounts by using third party GUI tools.

```sql
CREATE USER [IF NOT EXISTS] user [IDENTIFIED BY 'auth_string'];
```

After you assign the password, TiDB hashes and stores the `auth_string` in the [`mysql.user`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema-user) table.

```sql
CREATE USER 'test'@'127.0.0.1' IDENTIFIED BY 'xxx';
```

The name of a TiDB account consists of a user name and a hostname. The syntax of the account name is 'user_name'@'host_name'.

- `user_name` is case sensitive.

- `host_name` is a hostname or IP address, which supports the wild card `%` or `_`. For example, the hostname `'%'` matches all hosts, and the hostname `'192.168.1.%'` matches all hosts in the subnet.

The host supports fuzzy matching:

```sql
CREATE USER 'test'@'192.168.10.%';
```

The `test` user is allowed to log in from any hosts on the `192.168.10` subnet.

If the host is not specified, the user is allowed to log in from any IP. If no password is specified, the default is empty password:

```sql
CREATE USER 'test';
```

Equivalent to:

```sql
CREATE USER 'test'@'%' IDENTIFIED BY '';
```

If the specified user does not exist, the behavior of automatically creating users depends on `sql_mode`. If the `sql_mode` includes `NO_AUTO_CREATE_USER`, the `GRANT` statement will not create users with an error returned.

For example, assume that the `sql_mode` does not include `NO_AUTO_CREATE_USER`, and you use the following `CREATE USER` and `GRANT` statements to create four accounts:

```sql
CREATE USER 'finley'@'localhost' IDENTIFIED BY 'some_pass';
```

```sql
GRANT ALL PRIVILEGES ON *.* TO 'finley'@'localhost' WITH GRANT OPTION;
```

```sql
CREATE USER 'finley'@'%' IDENTIFIED BY 'some_pass';
```

```sql
GRANT ALL PRIVILEGES ON *.* TO 'finley'@'%' WITH GRANT OPTION;
```

```sql
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'admin_pass';
```

```sql
GRANT RELOAD,PROCESS ON *.* TO 'admin'@'localhost';
```

```sql
CREATE USER 'dummy'@'localhost';
```

To see the privileges granted for an account, use the `SHOW GRANTS` statement:

```sql
SHOW GRANTS FOR 'admin'@'localhost';
```

```
+-----------------------------------------------------+
| Grants for admin@localhost                          |
+-----------------------------------------------------+
| GRANT RELOAD, PROCESS ON *.* TO 'admin'@'localhost' |
+-----------------------------------------------------+
```
## Remove user accounts

To remove a user account, use the `DROP USER` statement:

```sql
DROP USER 'test'@'localhost';
```

This operation clears the user's records in the [`mysql.user`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema-user) table and the related records in the privilege table.
## Reserved user accounts

TiDB creates the `'root'@'%'` default account during the database initialization.
## Set account resource limits

TiDB can limit the resources consumed by users using resource groups. For more information, see [Use resource control to achieve resource isolation](https://docs.pingcap.com/tidb/stable/tidb-resource-control).
## Assign account passwords

TiDB stores passwords in the [`mysql.user`](https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema-user) system table. Operations that assign or update passwords are permitted only to users with the `CREATE USER` privilege, or, alternatively, privileges for the `mysql` database (`INSERT` privilege to create new accounts, `UPDATE` privilege to update existing accounts).

- To assign a password when you create a new account, use `CREATE USER` and include an `IDENTIFIED BY` clause:

    ```sql
    CREATE USER 'test'@'localhost' IDENTIFIED BY 'mypass';
    ```

- To assign or change a password for an existing account, use `SET PASSWORD FOR` or `ALTER USER`:

    ```sql
    SET PASSWORD FOR 'root'@'%' = 'xxx';
    ```

    Or:

    ```sql
    ALTER USER 'test'@'localhost' IDENTIFIED BY 'mypass';
    ```
