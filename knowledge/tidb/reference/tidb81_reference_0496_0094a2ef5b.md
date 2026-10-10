# Security feature compatibility and MySQL differences

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/security-compatibility-with-mysql.md`
- Source Title: `Security Compatibility with MySQL`
- Source Heading Path: `Security Compatibility with MySQL | Security Compatibility with MySQL > Unsupported security features | Security Compatibility with MySQL > Differences with MySQL | Security Compatibility with MySQL > Differences with MySQL > Password expiration policy | Security Compatibility with MySQL > Differences with MySQL > Password complexity policy | Security Compatibility with MySQL > Differences with MySQL > Password failure tracking | Security Compatibility with MySQL > Differences with MySQL > Password reuse policy`
- Source Line Ranges: `5-107`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `security`, `mysql-compatibility`, `password-policy`, `password-expiration`, `password-complexity`, `password-failure-tracking`, `password-reuse`, `unsupported-features`, `authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0496_0094a2ef5b`
- Source ID: `tidb-docs-8.1:security-compatibility-with-mysql.md#security-compatibility-with-mysql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ce5320b86bebcd39a26e7c62fb6f6fa0d4357d85b0c1dee41efbe2c87e17459`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#security-compatibility-with-mysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/security-compatibility-with-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB and MySQL security compatibility for unsupported security features or for differences in password expiration, password complexity, password failure tracking, and password reuse behavior.
- Retrieval Keywords: Security Compatibility with MySQL, Unsupported security features, Column level permissions, max_questions, max_updated, max_user_connections, Password verification policy, Dual password policy, Random password generation, Multi-factor authentication, security.disconnect-on-expired-password, validate_password.enable, validate_password.dictionary, validate_password_dictionary_file, validate_password.dictionary_file, ALTER USER ... ACCOUNT UNLOCK, FLUSH PRIVILEGES, mysql.password_history, DROP USER IF EXISTS user01
- Follow-up Guidance: The content points to the configuration item `security.disconnect-on-expired-password`, the system variables `validate_password.enable` and `validate_password.dictionary`, and the related SQL statements `ALTER USER ... ACCOUNT UNLOCK`, `FLUSH PRIVILEGES`, `DROP USER`, and `DROP USER IF EXISTS`.
- Classification Note: This is a reference chunk because it catalogs compatibility gaps and implementation differences between TiDB and MySQL security features using exact feature names, variables, tables, and SQL statements.

## Official Source Content

# Security Compatibility with MySQL

TiDB supports security features similar to MySQL 5.7, and also supports some security features of MySQL 8.0. The security features of TiDB are different from MySQL in implementation.
## Unsupported security features

- Column level permissions.
- These permission attributes: `max_questions`, `max_updated`, and `max_user_connections`.
- Password verification policy, which requires you to verify the current password when you change it.
- Dual password policy.
- Random password generation.
- Multi-factor authentication.
## Differences with MySQL
### Password expiration policy

The password expiration policies of TiDB and MySQL have the following differences:

- MySQL supports password expiration policy in v5.7 and v8.0.
- TiDB supports password expiration policy starting from v6.5.0.

The expiration mechanism of TiDB is different from MySQL in the following aspects:

- In MySQL v5.7 and v8.0, the configuration of the client and the server combined together determines whether to enable "sandbox mode" for the client connection.
- In TiDB, the [`security.disconnect-on-expired-password`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#disconnect-on-expired-password-new-in-v650) configuration item alone determines whether to enable "sandbox mode" for the client connection.
### Password complexity policy

The password complexity policies of TiDB and MySQL have the following differences:

- MySQL v5.7 implements the password complexity policy by using the `validate_password` plugin.
- MySQL v8.0 re-implements the password complexity policy by using the `validate_password` component.
- TiDB introduces a built-in password complexity management feature starting from v6.5.0.

The feature implementation has the following differences:

- Enable the feature:

    - In MySQL v5.7, the feature is implemented by using the `validate_password` plugin. You can enable the feature by installing the plugin.
    - In MySQL v8.0, the feature is implemented by using the `validate_password` component. You can enable the feature by installing the component.
    - For TiDB, this feature is built-in. You can enable the feature using the system variable [`validate_password.enable`](https://docs.pingcap.com/tidb/stable/system-variables#validate_passwordenable-new-in-v650).

- Dictionary check:

    - In MySQL v5.7, you can specify a file path using the `validate_password_dictionary_file` variable. The file contains a list of words that are not allowed to exist in passwords.
    - In MySQL v8.0, you can specify a file path using the `validate_password.dictionary_file` variable. The file contains a list of words that are not allowed to exist in passwords.
    - In TiDB, you can specify a string using the [`validate_password.dictionary`](https://docs.pingcap.com/tidb/stable/system-variables#validate_passworddictionary-new-in-v650) system variable. The string contains a list of words that are not allowed to exist in passwords.
### Password failure tracking

The password failure tracking policies of TiDB and MySQL have the following differences:

- MySQL v5.7 does not support password failure tracking.
- MySQL v8.0 supports password failure tracking.
- TiDB supports password failure tracking starting from v6.5.0.

Because the number of failed attempts and lock status of accounts need to be globally consistent, and as a distributed database, TiDB cannot record the number of failed attempts and lock status in the server memory like MySQL, so the implementation mechanisms are different between TiDB and MySQL.

- For users that are not locked automatically, the count of failed attempts is reset in the following scenarios:

    + MySQL 8.0:

        - When the server is restarted, the count of failed attempts for all accounts is reset.
        - When `FLUSH PRIVILEGES` is executed, the count of failed attempts for all accounts is reset.
        - When you run `ALTER USER ... ACCOUNT UNLOCK` to unlock an account, the count is reset.
        - When an account logs in successfully, the count is reset.

    + TiDB:

        - When you run `ALTER USER ... ACCOUNT UNLOCK` to unlock an account, the count is reset.
        - When an account logs in successfully, the count is reset.

- For users that are locked automatically, the count of failed attempts is reset in the following scenarios:

    + MySQL 8.0:

        - When the server is restarted, the temporary locking for all accounts is reset.
        - When `FLUSH PRIVILEGES` is executed, the temporary locking for all accounts is reset.
        - If the lock time of an account ends, the temporary locking for the account is reset on the next login attempt.
        - When you run `ALTER USER ... ACCOUNT UNLOCK` to unlock an account, the temporary locking for the account is reset.

    + TiDB:

        - If the lock time of an account ends, the temporary locking for the account is reset on the next login attempt.
        - When you run `ALTER USER ... ACCOUNT UNLOCK` to unlock an account, the temporary locking for the account is reset.
### Password reuse policy

The password reuse policies of TiDB and MySQL have the following differences:

- MySQL v5.7 does not support password reuse management.
- MySQL v8.0 supports password reuse management.
- TiDB supports password reuse management starting from v6.5.0.

The implementation mechanisms are consistent between TiDB and MySQL. Both use the `mysql.password_history` system table to implement the password reuse management feature. However, when deleting a user that does not exist in the `mysql.user` system table, TiDB and MySQL have different behaviors:

- Scenario: A user (`user01`) is not created in a normal way; instead, it is created by using the `INSERT INTO mysql.password_history VALUES (...)` statement to append a record of `user01` to the `mysql.password_history` system table. In such cases, because the record of `user01` does not exist in the `mysql.user` system table, when you run `DROP USER` on `user01`, TiDB and MySQL have different behaviors.

    - MySQL: When you run `DROP USER user01`, MySQL tries to find `user01` in `mysql.user` and `mysql.password_history`. If either system table contains `user01`, the `DROP USER` statement is executed successfully and no error is reported.
    - TiDB: When you run `DROP USER user01`, TiDB tries to find `user01` only in `mysql.user`. If no related record is found, the `DROP USER` statement fails and an error is reported. If you want to execute the statement successfully and delete the `user01` record from `mysql.password_history`, use `DROP USER IF EXISTS user01` instead.
