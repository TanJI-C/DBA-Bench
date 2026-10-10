# Password reuse rules and failed-login account locking

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/password-management.md`
- Source Title: `TiDB Password Management`
- Source Heading Path: `TiDB Password Management > Password reuse policy | TiDB Password Management > Password reuse policy > Global-level password reuse policy | TiDB Password Management > Password reuse policy > Account-level password reuse policy | TiDB Password Management > Failed-login tracking and temporary account locking policy | TiDB Password Management > Failed-login tracking and temporary account locking policy > Configure the login failure tracking policy`
- Source Line Ranges: `285-404`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `password-reuse`, `password-history`, `reuse-interval`, `failed-login`, `account-locking`, `user-management`, `security-policy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0182_834ec64c4b`
- Source ID: `tidb-docs-8.1:password-management.md#password-reuse-policy`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2f9f9e15bd5d6de88b6eebd7ac9b180f284efe10e56c6f45e0d4be3a1c0bf5cd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/password-management#password-reuse-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/password-management.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB password reuse restrictions or account locking after failed login attempts.
- Retrieval Keywords: password_history, password_reuse_interval, PASSWORD HISTORY, PASSWORD REUSE INTERVAL, mysql.password_history, password reuse policy, global-level password reuse policy, account-level password reuse policy, FAILED_LOGIN_ATTEMPTS, PASSWORD_LOCK_TIME, UNBOUNDED, failed-login tracking, temporary account locking, consecutive login failures
- Follow-up Guidance: If the question is about exact SQL syntax for configuring per-user policies, check the CREATE USER and ALTER USER examples included in this content.
- Classification Note: This is classified as an operation chunk because the official content describes policy configuration and behavior for password reuse and failed-login account locking.

## Official Source Content

## Password reuse policy

TiDB can limit the reuse of previous passwords. The password reuse policy can be based on the number of password changes or time elapsed, or both.

The password reuse policy can be set at the global level and at the account level. You can establish a password reuse policy at the global level, and also use an account-level policy to override the global policy.

TiDB records the password history for an account and limits the selection of a new password from the history:

- If a password reuse policy is based on the number of password changes, a new password must not be the same as any of the specified number of most recent passwords. For example, if the minimum number of password changes is set to `3`, the new password cannot be the same as any of the previous 3 passwords.
- If a password reuse policy is based on time elapsed, a new password must not be the same as any of the passwords used within the specified number of days. For example, if the password reuse interval is set to `60`, the new password cannot be the same as any of the passwords used within the last 60 days.

> **Note:**
>
> Empty passwords are not recorded in the password history and can be reused at any time.
### Global-level password reuse policy

To establish a global password reuse policy, use the [`password_history`](https://docs.pingcap.com/tidb/stable/system-variables#password_history-new-in-v650) and [`password_reuse_interval`](https://docs.pingcap.com/tidb/stable/system-variables#password_reuse_interval-new-in-v650) system variables.

For example, to establish a global password reuse policy that prohibits the reuse of the last 6 passwords and passwords used within the last 365 days:

```sql
SET GLOBAL password_history = 6;
SET GLOBAL password_reuse_interval = 365;
```

The global password reuse policy applies to all accounts that do not have an account-level override.
### Account-level password reuse policy

To establish an account-level password reuse policy, use the `PASSWORD HISTORY` and `PASSWORD REUSE INTERVAL` options in the `CREATE USER` or `ALTER USER` statement.

For example:

To prohibit the reuse of the last 5 passwords:

```sql
CREATE USER 'test'@'localhost' PASSWORD HISTORY 5;
ALTER USER 'test'@'localhost' PASSWORD HISTORY 5;
```

To prohibit the reuse of passwords used within the last 365 days:

```sql
CREATE USER 'test'@'localhost' PASSWORD REUSE INTERVAL 365 DAY;
ALTER USER 'test'@'localhost' PASSWORD REUSE INTERVAL 365 DAY;
```

To combine the two types of reuse policies, use both `PASSWORD HISTORY` and `PASSWORD REUSE INTERVAL`:

```sql
CREATE USER 'test'@'localhost'
  PASSWORD HISTORY 5
  PASSWORD REUSE INTERVAL 365 DAY;
ALTER USER 'test'@'localhost'
  PASSWORD HISTORY 5
  PASSWORD REUSE INTERVAL 365 DAY;
```

To remove the account-level password reuse policy for a specified account so that it follows the global password reuse policy:

```sql
CREATE USER 'test'@'localhost'
  PASSWORD HISTORY DEFAULT
  PASSWORD REUSE INTERVAL DEFAULT;
ALTER USER 'test'@'localhost'
  PASSWORD HISTORY DEFAULT
  PASSWORD REUSE INTERVAL DEFAULT;
```

> **Note:**
>
> - If you set the password reuse policy multiple times, the last set value takes effect.
> - The default value of the `PASSWORD HISTORY` and `PASSWORD REUSE INTERVAL` options is 0, which means that the reuse policy is disabled.
> - When you modify a username, TiDB migrates the corresponding password history in the `mysql.password_history` system table from the original username to the new username.
## Failed-login tracking and temporary account locking policy

TiDB can track the number of failed login attempts for an account. To prevent the password from being cracked by brute force, TiDB can lock the account after a specified number of failed login attempts.

> **Note:**
>
> - TiDB only supports failed-login tracking and temporary account locking at the account level, but not at the global level.
> - Failed-login means that the client fails to provide the correct password during the connection attempt, and does not include connection failures due to unknown users or network issues.
> - When you enable the failed-login tracking and temporary account locking for an account, the account is subject to additional checks when the account attempts to log in. This affects the performance of the login operation, especially in high-concurrency login scenarios.
### Configure the login failure tracking policy

You can configure the number of failed login attempts and the lock time for each account by using the `FAILED_LOGIN_ATTEMPTS` and `PASSWORD_LOCK_TIME` options in the `CREATE USER` or `ALTER USER` statement. The available value options are as follows:

- `FAILED_LOGIN_ATTEMPTS`: N. The account is temporarily locked after `N` consecutive login failures. The value of N ranges from 0 to 32767.
- `PASSWORD_LOCK_TIME`: N | UNBOUNDED.
    - N means that the account will be temporarily locked for `N` days after consecutive failed login attempts. The value of N ranges from 0 to 32767.
    - `UNBOUNDED` means that the lock time is unlimited and the account must be manually unlocked. The value of N ranges from 0 to 32767.

> **Note:**
>
> - You can configure only `FAILED_LOGIN_ATTEMPTS` or `PASSWORD_LOCK_TIME` in a single SQL statement. In this case, the account locking does not take effect.
> - The account locking takes effect only when both `FAILED_LOGIN_ATTEMPTS` and `PASSWORD_LOCK_TIME` are not 0.

You can configure the account locking policy as follows:

Create a user and configure the account locking policy. When the password is entered incorrectly for 3 consecutive times, the account will be temporarily locked for 3 days:

```sql
CREATE USER 'test1'@'localhost' IDENTIFIED BY 'password' FAILED_LOGIN_ATTEMPTS 3 PASSWORD_LOCK_TIME 3;
```

Modify the account locking policy for an existing user. When the password is entered incorrectly for 4 consecutive times, the account will be locked indefinitely until it is manually unlocked:

```sql
ALTER USER 'test2'@'localhost' FAILED_LOGIN_ATTEMPTS 4 PASSWORD_LOCK_TIME UNBOUNDED;
```

Disable the account locking policy for an existing user:

```sql
ALTER USER 'test3'@'localhost' FAILED_LOGIN_ATTEMPTS 0 PASSWORD_LOCK_TIME 0;
```
