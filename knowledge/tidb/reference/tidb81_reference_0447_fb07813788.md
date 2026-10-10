# mysql.user table fields and privileges

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/mysql-schema/mysql-schema-user.md`
- Source Title: `mysql.user`
- Source Heading Path: ``mysql.user``
- Source Line Ranges: `5-110`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `mysql.user`, `privileges`, `authentication`, `password policy`, `account lock`, `user attributes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0447_fb07813788`
- Source ID: `tidb-docs-8.1:mysql-schema/mysql-schema-user.md#mysql-user`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ee0e9eb0cf9c47a69b4b0f2a2a99f4547b2adc3c4fb96dbbb93c58b0cdc2509`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/mysql-schema/mysql-schema-user#mysql-user
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/mysql-schema/mysql-schema-user.md

## Retrieval Guidance

- Use When: Use this chunk when you need the schema of `mysql.user` or the meaning of its account scope, privilege, and security-related fields.
- Retrieval Keywords: mysql.user, DESC mysql.user;, Host, User, authentication_string, plugin, Select_priv, Create_user_priv, Account_locked, Password_reuse_history, Password_reuse_time, User_attributes, Token_issuer, Password_expired, Password_last_changed, Password_lifetime, tidb_auth_token, mysql.user table fields and privileges
- Follow-up Guidance: The source also notes that fields ending with `_priv` or `_Priv` define granted permissions and that `Token_issuer` is specific to TiDB.
- Classification Note: This is reference content because it enumerates the `mysql.user` table structure and explains the purpose of its fields without describing a procedure.

## Official Source Content

# `mysql.user`

The `mysql.user` table provides information about user accounts and their privileges.

To view the structure of `mysql.user`, use the following SQL statement:

```sql
DESC mysql.user;
```

The output is as follows:

```
+------------------------+----------------------+------+------+-------------------+-------+
| Field                  | Type                 | Null | Key  | Default           | Extra |
+------------------------+----------------------+------+------+-------------------+-------+
| Host                   | char(255)            | NO   | PRI  | NULL              |       |
| User                   | char(32)             | NO   | PRI  | NULL              |       |
| authentication_string  | text                 | YES  |      | NULL              |       |
| plugin                 | char(64)             | YES  |      | NULL              |       |
| Select_priv            | enum('N','Y')        | NO   |      | N                 |       |
| Insert_priv            | enum('N','Y')        | NO   |      | N                 |       |
| Update_priv            | enum('N','Y')        | NO   |      | N                 |       |
| Delete_priv            | enum('N','Y')        | NO   |      | N                 |       |
| Create_priv            | enum('N','Y')        | NO   |      | N                 |       |
| Drop_priv              | enum('N','Y')        | NO   |      | N                 |       |
| Process_priv           | enum('N','Y')        | NO   |      | N                 |       |
| Grant_priv             | enum('N','Y')        | NO   |      | N                 |       |
| References_priv        | enum('N','Y')        | NO   |      | N                 |       |
| Alter_priv             | enum('N','Y')        | NO   |      | N                 |       |
| Show_db_priv           | enum('N','Y')        | NO   |      | N                 |       |
| Super_priv             | enum('N','Y')        | NO   |      | N                 |       |
| Create_tmp_table_priv  | enum('N','Y')        | NO   |      | N                 |       |
| Lock_tables_priv       | enum('N','Y')        | NO   |      | N                 |       |
| Execute_priv           | enum('N','Y')        | NO   |      | N                 |       |
| Create_view_priv       | enum('N','Y')        | NO   |      | N                 |       |
| Show_view_priv         | enum('N','Y')        | NO   |      | N                 |       |
| Create_routine_priv    | enum('N','Y')        | NO   |      | N                 |       |
| Alter_routine_priv     | enum('N','Y')        | NO   |      | N                 |       |
| Index_priv             | enum('N','Y')        | NO   |      | N                 |       |
| Create_user_priv       | enum('N','Y')        | NO   |      | N                 |       |
| Event_priv             | enum('N','Y')        | NO   |      | N                 |       |
| Repl_slave_priv        | enum('N','Y')        | NO   |      | N                 |       |
| Repl_client_priv       | enum('N','Y')        | NO   |      | N                 |       |
| Trigger_priv           | enum('N','Y')        | NO   |      | N                 |       |
| Create_role_priv       | enum('N','Y')        | NO   |      | N                 |       |
| Drop_role_priv         | enum('N','Y')        | NO   |      | N                 |       |
| Account_locked         | enum('N','Y')        | NO   |      | N                 |       |
| Shutdown_priv          | enum('N','Y')        | NO   |      | N                 |       |
| Reload_priv            | enum('N','Y')        | NO   |      | N                 |       |
| FILE_priv              | enum('N','Y')        | NO   |      | N                 |       |
| Config_priv            | enum('N','Y')        | NO   |      | N                 |       |
| Create_Tablespace_Priv | enum('N','Y')        | NO   |      | N                 |       |
| Password_reuse_history | smallint(5) unsigned | YES  |      | NULL              |       |
| Password_reuse_time    | smallint(5) unsigned | YES  |      | NULL              |       |
| User_attributes        | json                 | YES  |      | NULL              |       |
| Token_issuer           | varchar(255)         | YES  |      | NULL              |       |
| Password_expired       | enum('N','Y')        | NO   |      | N                 |       |
| Password_last_changed  | timestamp            | YES  |      | CURRENT_TIMESTAMP |       |
| Password_lifetime      | smallint(5) unsigned | YES  |      | NULL              |       |
+------------------------+----------------------+------+------+-------------------+-------+
44 rows in set (0.00 sec)
```

The `mysql.user` table contains several fields that can be categorized into three groups:

* Scope:
    * `Host`: specifies the hostname of a TiDB account.
    * `User`: specifies the username of a TiDB account.
* Privilege:

    The fields ending with `_priv` or `_Priv` define the permissions granted to a user account. For example, `Select_priv` means that the user has global `Select` privilege. For more information, see [Privileges required for TiDB operations](https://docs.pingcap.com/tidb/stable/privilege-management#privileges-required-for-tidb-operations).

* Security:
    * `authentication_string` and `plugin`: `authentication_string` stores the credentials for the user account. The credentials are interpreted based on the authentication plugin specified in the `plugin` field.
    * `Account_locked`: indicates whether the user account is locked.
    * `Password_reuse_history` and `Password_reuse_time`: used for [Password reuse policy](https://docs.pingcap.com/tidb/stable/password-management#password-reuse-policy).
    * `User_attributes`: provides information about user comments and user attributes.
    * `Token_issuer`: used for the [`tidb_auth_token`](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#tidb_auth_token) authentication plugin.
    * `Password_expired`, `Password_last_changed`, and `Password_lifetime`: used for [Password expiration policy](https://docs.pingcap.com/tidb/stable/password-management#password-expiration-policy).

* Scope:
    * `Host`: specifies the hostname of a TiDB account.
    * `User`: specifies the username of a TiDB account.
* Privilege:

    The fields ending with `_priv` or `_Priv` define the permissions granted to a user account. For example, `Select_priv` means that the user has global `Select` privilege. For more information, see [Privileges required for TiDB operations](https://docs.pingcap.com/tidb/stable/privilege-management#privileges-required-for-tidb-operations).
* Security:
    * `authentication_string` and `plugin`: `authentication_string` stores the credentials for the user account. The credentials are interpreted based on the authentication plugin specified in the `plugin` field.
    * `Account_locked`: indicates whether the user account is locked.
    * `Password_reuse_history` and `Password_reuse_time`: used for [Password reuse policy](https://docs.pingcap.com/tidb/stable/password-management#password-reuse-policy).
    * `User_attributes`: provides information about user comments and user attributes.
    * `Token_issuer`: used for the [`tidb_auth_token`](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#tidb_auth_token) authentication plugin.
    * `Password_expired`, `Password_last_changed`, and `Password_lifetime`: used for [Password expiration policy](https://docs.pingcap.com/tidb/stable/password-management#password-expiration-policy).

Although most of the fields in the TiDB `mysql.user` table also exist in the MySQL `mysql.user` table, the `Token_issuer` field is specific to TiDB.
