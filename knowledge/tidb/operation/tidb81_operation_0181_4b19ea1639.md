# Password expiration configuration, checks, and expired-password handling

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/password-management.md`
- Source Title: `TiDB Password Management`
- Source Heading Path: `TiDB Password Management > Password expiration policy > Automatic expiration | TiDB Password Management > Password expiration policy > Password expiration check mechanism | TiDB Password Management > Password expiration policy > Handle an expired password`
- Source Line Ranges: `210-284`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `password-expiration`, `password-lifetime`, `account-policy`, `global-policy`, `sandbox-mode`, `authentication`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0181_4b19ea1639`
- Source ID: `tidb-docs-8.1:password-management.md#automatic-expiration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `14c69e594707812cd946ec2ae9115b0ddf83a6123aa99b6da4e12e179263da79`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/password-management#automatic-expiration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/password-management.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB password expiration policies, how expiration is checked, or what happens when an expired password connects.
- Retrieval Keywords: default_password_lifetime, PASSWORD EXPIRE, PASSWORD EXPIRE INTERVAL 90 DAY, PASSWORD EXPIRE NEVER, PASSWORD EXPIRE DEFAULT, mysql.user, password age, password lifetime, password expiration check mechanism, security.disconnect-on-expired-password, disconnect-on-expired-password, sandbox mode, skip-grant-table, Forgot password process
- Follow-up Guidance: If the question is about manually expiring passwords or changing passwords for expired accounts, also look for the related user account management and forgot password content referenced here.
- Classification Note: This is classified as an operation chunk because the official content explains configuration, checking order, and runtime handling for expired passwords in TiDB.

## Official Source Content

### Automatic expiration

Automatic password expiration is based on the **password age** and the **password lifetime**.

- Password age: the time interval from the last password change date to the current date. The time of the last password change is recorded in the `mysql.user` system table.
- Password lifetime: the number of days the password can be used to log in to TiDB.

If a password is used for a longer period than it is allowed to live, the server automatically treats the password as expired.

TiDB supports automatic password expiration at the global level and at the account level.

- The global level

    You can set the system variable [`default_password_lifetime`](https://docs.pingcap.com/tidb/stable/system-variables#default_password_lifetime-new-in-v650) to control the password lifetime. The default value `0` indicates that the password never expires. If this system variable is set to a positive integer `N`, it means that the password lifetime is `N` days, and you must change your password every `N` days.

    The global automatic password expiration policy applies to all accounts that do not have an account-level override.

    The following example establishes a global automatic password expiration policy with a password lifetime of 180 days:

    ```sql
    SET GLOBAL default_password_lifetime = 180;
    ```

- The account level

    To establish an automatic password expiration policy for an individual account, use the `PASSWORD EXPIRE` option in the `CREATE USER` or `ALTER USER` statement.

    The following examples require that the user password is changed every 90 days:

    ```sql
    CREATE USER 'test'@'localhost' PASSWORD EXPIRE INTERVAL 90 DAY;
    ALTER USER 'test'@'localhost' PASSWORD EXPIRE INTERVAL 90 DAY;
    ```

    The following examples disable the automatic password expiration policy for an individual account:

    ```sql
    CREATE USER 'test'@'localhost' PASSWORD EXPIRE NEVER;
    ALTER USER 'test'@'localhost' PASSWORD EXPIRE NEVER;
    ```

    Remove the account-level automatic password expiration policy for a specified account so that it follows the global automatic password expiration policy:

    ```sql
    CREATE USER 'test'@'localhost' PASSWORD EXPIRE DEFAULT;
    ALTER USER 'test'@'localhost' PASSWORD EXPIRE DEFAULT;
    ```
### Password expiration check mechanism

When a client connects to the TiDB server, the server checks whether the password is expired in the following order:

1. The server checks whether the password has been set as expired manually.
2. If the password is not manually expired, the server checks whether the password age is longer than its configured lifetime. If so, the server treats the password as expired.
### Handle an expired password

You can control the behavior of the TiDB server for password expiration. When a password is expired, the server either disconnects the client or restricts the client to the "sandbox mode". In a "sandbox mode", the TiDB server allows connections from the expired account. However, in such connections, the user is only allowed to reset the password.

The TiDB server can control whether to restrict the user with an expired password in the "sandbox mode". To control the behavior of the TiDB server when a password is expired, configure the [`security.disconnect-on-expired-password`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#disconnect-on-expired-password-new-in-v650) parameter in the TiDB configuration file:

```toml
[security]
disconnect-on-expired-password = true
```

- If `disconnect-on-expired-password` is set to `true` (default), the server disconnects the client when the password is expired.
- If `disconnect-on-expired-password` is set to `false`, the server enables the "sandbox mode" and allows the user to connect to the server. However, the user can only reset the password. After the password is reset, the user can execute SQL statements normally.

When `disconnect-on-expired-password` is enabled, if an account password is expired, TiDB rejects the connection from the account. In such cases, you can modify the password in the following ways:

- If the password for a normal account is expired, the administrator can change the password for the account by using SQL statements.
- If the password for an administrator account is expired, another administrator can change the password for the account by using SQL statements.
- If the password for an administrator account is expired and no other administrator is available to help change the password, you can use the `skip-grant-table` mechanism to change the password for the account. For details, see [Forgot password process](https://docs.pingcap.com/tidb/stable/user-account-management#forget-the-root-password).
