# Password expiration policy and manual expiration

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/password-management.md`
- Source Title: `TiDB Password Management`
- Source Heading Path: `TiDB Password Management > Password expiration policy | TiDB Password Management > Password expiration policy > Manual expiration`
- Source Line Ranges: `173-209`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `passwords`, `password-expiration`, `manual-expiration`, `account-policy`, `privileges`, `roles`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0180_28e195208b`
- Source ID: `tidb-docs-8.1:password-management.md#password-expiration-policy`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `181ef235321e7439dd624ad9bcbe59ab04a51d862ddd78b87aae1062e85cbaa8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/password-management#password-expiration-policy
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/password-management.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB password expiration policy, manual password expiration, relevant privileges, or how password_expired is recorded for roles in mysql.user.
- Retrieval Keywords: password expiration policy, manual expiration, ALTER USER 'test'@'localhost' PASSWORD EXPIRE, CREATE USER, ALTER USER, SUPER, CREATE USER privilege, SYSTEM_VARIABLES_ADMINR, account-level password expiration policy, global-level password expiration policy, CREATE ROLE testrole, password_expired, Account_locked, SELECT user,password_expired,Account_locked FROM mysql.user WHERE user = 'testrole', ALTER USER ... ACCOUNT UNLOCK, role password is empty
- Follow-up Guidance: The source explains that manual expiration cannot be revoked and that roles created by CREATE ROLE are marked with password_expired = 'Y' to prevent login with an empty password after unlocking.
- Classification Note: This is classified as operation because the content focuses on applying and observing password expiration behavior through privileges and SQL statements such as ALTER USER and CREATE ROLE.

## Official Source Content

## Password expiration policy

TiDB supports configuring a password expiration policy so that users must change their passwords periodically to improve password security. You can manually make account passwords expire or establish a policy for automatic password expiration.

The automatic password expiration policy can be set at the global level and at the account level. As a database administrator, you can establish an automatic password expiration policy at the global level, and also use an account-level policy to override the global policy.

The privileges for setting the password expiration policy are as follows:

- Database administrator with `SUPER` or `CREATE USER` privileges can manually make passwords expire.
- Database administrator with `SUPER` or `CREATE USER` privileges can set the account-level password expiration policy.
- Database administrator with `SUPER` or `SYSTEM_VARIABLES_ADMINR` privileges can set the global-level password expiration policy.
### Manual expiration

To manually make an account password expire, use the `CREATE USER` or `ALTER USER` statements.

```sql
ALTER USER 'test'@'localhost' PASSWORD EXPIRE;
```

When the account password is set to expire by a database administrator, you must change the password before you can log in to TiDB. The manual expiration cannot be revoked.

For roles created using the `CREATE ROLE` statement, since the role does not require a password, the password field for the role is empty. In such case, TiDB sets the `password_expired` attribute to `'Y'`, which means that the role's password is manually expired. The purpose of this design is to prevent the role from being unlocked and logged into TiDB with an empty password. When the role is unlocked by the `ALTER USER ... ACCOUNT UNLOCK` statement, you can log in with this account even though the password is empty. Therefore, TiDB makes the password manually expired using the `password_expired` attribute so that the user must set a valid password for the account.

```sql
mysql> CREATE ROLE testrole;
Query OK, 0 rows affected (0.01 sec)

mysql> SELECT user,password_expired,Account_locked FROM mysql.user WHERE user = 'testrole';
+----------+------------------+----------------+
| user     | password_expired | Account_locked |
+----------+------------------+----------------+
| testrole | Y                | Y              |
+----------+------------------+----------------+
1 row in set (0.02 sec)
```
