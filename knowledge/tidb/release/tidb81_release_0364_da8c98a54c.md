# New security features in TiDB 6.5.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > New features > Security`
- Source Line Ranges: `95-122`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `security`, `password-policy`, `password-complexity`, `password-expiration`, `password-reuse`, `failed-login`, `account-locking`, `authentication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0364_da8c98a54c`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#security`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `72f7569af3e5b0972554c33fc05696b6d7ae418273f5a692c1d0d2b42bbfc1b8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.5.0 security additions related to password management policies and failed-login account locking.
- Retrieval Keywords: TiDB 6.5.0 security features, password complexity policy, VALIDATE_PASSWORD_STRENGTH(), password expiration policy, password reuse policy, failed-login tracking, temporary account locking policy, password management
- Follow-up Guidance: The content links to password management documentation for password complexity, password expiration, password reuse, and failed-login tracking with temporary account locking.
- Classification Note: This is classified as a TiDB release security feature summary because the official content lists new password and authentication-related policies introduced in TiDB 6.5.0.

## Official Source Content

### Security

* Support the password complexity policy [#38928](https://github.com/pingcap/tidb/issues/38928) @[CbcWestwolf](https://github.com/CbcWestwolf)

    After this policy is enabled, when you set a password, TiDB checks the password length, whether uppercase and lowercase letters, numbers, and special characters in the password are sufficient, whether the password matches the dictionary, and whether the password matches the username. This ensures that you set a secure password.

    TiDB provides the SQL function [`VALIDATE_PASSWORD_STRENGTH()`](https://dev.mysql.com/doc/refman/5.7/en/encryption-functions.html#function_validate-password-strength) to validate the password strength.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/password-management#password-complexity-policy).

* Support the password expiration policy [#38936](https://github.com/pingcap/tidb/issues/38936) @[CbcWestwolf](https://github.com/CbcWestwolf)

    TiDB supports configuring the password expiration policy, including manual expiration, global-level automatic expiration, and account-level automatic expiration. After this policy is enabled, you must change your passwords periodically. This reduces the risk of password leakage due to long-term use and improves password security.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/password-management#password-expiration-policy).

* Support the password reuse policy [#38937](https://github.com/pingcap/tidb/issues/38937) @[keeplearning20221](https://github.com/keeplearning20221)

    TiDB supports configuring the password reuse policy, including global-level password reuse policy and account-level password reuse policy. After this policy is enabled, you cannot use the passwords that you have used within a specified period or the most recent several passwords that you have used. This reduces the risk of password leakage due to repeated use of passwords and improves password security.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/password-management#password-reuse-policy).

* Support failed-login tracking and temporary account locking policy [#38938](https://github.com/pingcap/tidb/issues/38938) @[lastincisor](https://github.com/lastincisor)

    After this policy is enabled, if you log in to TiDB with incorrect passwords multiple times consecutively, the account is temporarily locked. After the lock time ends, the account is automatically unlocked.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/password-management#failed-login-tracking-and-temporary-account-locking-policy).
