# Password storage and complexity policy

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/password-management.md`
- Source Title: `TiDB Password Management`
- Source Heading Path: `TiDB Password Management | TiDB Password Management > TiDB authentication credential storage | TiDB Password Management > Password complexity policy | TiDB Password Management > Password complexity policy > Configure password complexity policy | TiDB Password Management > Password complexity policy > Password complexity check examples | TiDB Password Management > Password complexity policy > Password strength validation function`
- Source Line Ranges: `5-172`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `passwords`, `authentication`, `credential-storage`, `password-complexity`, `system-variables`, `validate-password`, `password-strength`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0123_51f0d742b5`
- Source ID: `tidb-docs-8.1:password-management.md#tidb-password-management`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fb1d976497c600a25a54a56ef6795c551abc42d5684573dd3b9913f5f9b84802`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/password-management#tidb-password-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/password-management.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB password credential storage, enabling or tuning password complexity checks, password validation behavior for plaintext versus hashed passwords, or the VALIDATE_PASSWORD_STRENGTH() function.
- Retrieval Keywords: mysql.user, mysql_native_password, caching_sha2_password, tidb_sm3_password, validate_password.enable, validate_password.check_user_name, validate_password.dictionary, validate_password.length, validate_password.mixed_case_count, validate_password.number_count, validate_password.policy, validate_password.special_char_count, SHOW VARIABLES LIKE 'validate_password.%', SET GLOBAL validate_password.enable = ON, SET GLOBAL validate_password.policy = LOW, SET GLOBAL validate_password.length = 10, VALIDATE_PASSWORD_STRENGTH(), ALTER USER 'test'@'localhost' IDENTIFIED BY 'abc', ALTER USER 'test'@'localhost' IDENTIFIED WITH mysql_native_password AS, CREATE USER 'user02'@'localhost' ACCOUNT LOCK, ERROR 1819 (HY000): Require Password Length: 8, password complexity check, hashed password is not checked, plaintext password is checked
- Follow-up Guidance: The source also states that changes to the password complexity policy affect only newly set passwords and that VALIDATE_PASSWORD_STRENGTH() evaluates passwords according to the current policy.
- Classification Note: This is classified as configuration because the content centers on system variables and SQL settings that control password complexity behavior in TiDB.

## Official Source Content

# TiDB Password Management

To protect the security of user passwords, TiDB supports the following password management policies starting from v6.5.0:

- Password complexity policy: require users to set strong passwords to prevent empty and weak passwords.
- Password expiration policy: require users to change their passwords periodically.
- Password reuse policy: prevent users from reusing old passwords.
- Failed-login tracking and temporary account locking policy: temporarily lock a user account to prevent the same user from trying to log in after multiple login failures caused by wrong passwords.
## TiDB authentication credential storage

To ensure the authenticity of user identity, TiDB uses passwords as credentials to authenticate users when they log in to the TiDB server.

The *password* described in this document refers to the internal credentials generated, stored, and verified by TiDB. TiDB stores user passwords in the `mysql.user` system table.

The following authentication plugins are related to TiDB password management:

- `mysql_native_password`
- `caching_sha2_password`
- `tidb_sm3_password`

For more information about TiDB authentication plugins, see [Authentication plugin status](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#authentication-plugin-status).
## Password complexity policy

Password complexity check is disabled by default in TiDB. By configuring system variables related to password complexity, you can enable the password complexity check and make sure the user passwords comply with the password complexity policy.

The password complexity policy has the following features:

- For SQL statements that set user passwords in plaintext (including `CREATE USER`, `ALTER USER`, and `SET PASSWORD`), TiDB checks the passwords against the password complexity policy. If a password does not meet the requirements, the password is rejected.
- You can use the SQL function [`VALIDATE_PASSWORD_STRENGTH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#validate_password_strength) to validate the password strength.

> **Note:**
>
> - For the `CREATE USER` statement, even if you can lock the account upon creation, you must set an acceptable password. Otherwise, when the account is unlocked, this account can log in to TiDB using a password that does not comply with the password complexity policy.
> - The modification to the password complexity policy does not affect the passwords that already exist and only affects the newly set passwords.

You can view all system variables related to the password complexity policy by executing the following SQL statement:

```sql
mysql> SHOW VARIABLES LIKE 'validate_password.%';

+--------------------------------------+--------+
| Variable_name                        | Value  |
+--------------------------------------+--------+
| validate_password.check_user_name    | ON     |
| validate_password.dictionary         |        |
| validate_password.enable             | OFF    |
| validate_password.length             | 8      |
| validate_password.mixed_case_count   | 1      |
| validate_password.number_count       | 1      |
| validate_password.policy             | MEDIUM |
| validate_password.special_char_count | 1      |
+--------------------------------------+--------+
8 rows in set (0.00 sec)
```

For a detailed description of each system variable, see [System Variables](https://docs.pingcap.com/tidb/stable/system-variables#validate_passwordcheck_user_name-new-in-v650).
### Configure password complexity policy

This section shows examples of configuring system variables related to the password complexity policy.

Enable the password complexity check:

```sql
SET GLOBAL validate_password.enable = ON;
```

Do not allow users to use a password that is the same as the user name:

```sql
SET GLOBAL validate_password.check_user_name = ON;
```

Set the password complexity level to `LOW`:

```sql
SET GLOBAL validate_password.policy = LOW;
```

Set the minimum password length to `10`:

```sql
SET GLOBAL validate_password.length = 10;
```

Require a password to contain at least two numbers, one uppercase letter, one lowercase letter, and one special character:

```sql
SET GLOBAL validate_password.number_count = 2;
SET GLOBAL validate_password.mixed_case_count = 1;
SET GLOBAL validate_password.special_char_count = 1;
```

Enable the dictionary check that prevents a password from containing words like `mysql` or `abcd`:

```sql
SET GLOBAL validate_password.dictionary = 'mysql;abcd';
```

> **Note:**
>
> - The value of `validate_password.dictionary` is a string, no longer than 1024 characters. It contains a list of words that must not exist in the password. Each word is separated by semicolon (`;`).
> - The dictionary check is case-insensitive.
### Password complexity check examples

When the system variable `validate_password.enable` is set to `ON`, TiDB enables the password complexity check. The following are examples of the check results:

TiDB checks the user's plaintext password against the default password complexity policy. If the set password does not meet the policy, the password is rejected.

```sql
mysql> ALTER USER 'test'@'localhost' IDENTIFIED BY 'abc';
ERROR 1819 (HY000): Require Password Length: 8
```

TiDB does not check the hashed password against the password complexity policy.

```sql
mysql> ALTER USER 'test'@'localhost' IDENTIFIED WITH mysql_native_password AS '*0D3CED9BEC10A777AEC23CCC353A8C08A633045E';
Query OK, 0 rows affected (0.01 sec)
```

When creating an account initially locked, you must also set a password that matches the password complexity policy, or the creation will fail.

```sql
mysql> CREATE USER 'user02'@'localhost' ACCOUNT LOCK;
ERROR 1819 (HY000): Require Password Length: 8
```
### Password strength validation function

To check the password strength, you can use the [`VALIDATE_PASSWORD_STRENGTH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#validate_password_strength) function. This function accepts a password argument and returns an integer from 0 (weak) to 100 (strong).

> **Note:**
>
> This function evaluates the password strength based on the current password complexity policy. If the password complexity policy is changed, the same password might get different evaluation results.

The following example shows how to use the [`VALIDATE_PASSWORD_STRENGTH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions#validate_password_strength) function:

```sql
mysql> SELECT VALIDATE_PASSWORD_STRENGTH('weak');
+------------------------------------+
| VALIDATE_PASSWORD_STRENGTH('weak') |
+------------------------------------+
|                                 25 |
+------------------------------------+
1 row in set (0.01 sec)

mysql> SELECT VALIDATE_PASSWORD_STRENGTH('lessweak$_@123');
+----------------------------------------------+
| VALIDATE_PASSWORD_STRENGTH('lessweak$_@123') |
+----------------------------------------------+
|                                           50 |
+----------------------------------------------+
1 row in set (0.01 sec)

mysql> SELECT VALIDATE_PASSWORD_STRENGTH('N0Tweak$_@123!');
+----------------------------------------------+
| VALIDATE_PASSWORD_STRENGTH('N0Tweak$_@123!') |
+----------------------------------------------+
|                                          100 |
+----------------------------------------------+
1 row in set (0.01 sec)
```
