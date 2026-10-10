# SQL proxy account overview, lifecycle, naming, roles, and access control

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/sql-proxy-account.md`
- Source Title: `SQL Proxy Account`
- Source Heading Path: `SQL Proxy Account | SQL Proxy Account > Identify the SQL proxy account | SQL Proxy Account > How the SQL proxy account is created | SQL Proxy Account > How the SQL proxy account is deleted | SQL Proxy Account > SQL proxy account username | SQL Proxy Account > SQL proxy account password | SQL Proxy Account > SQL proxy account roles | SQL Proxy Account > SQL proxy account access control`
- Source Line Ranges: `5-90`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `sql proxy account`, `jwt authentication`, `sql editor`, `data service`, `account identification`, `account creation`, `account deletion`, `username format`, `passwordless access`, `iam roles`, `access control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0840_7ce95376b8`
- Source ID: `tidb-docs-8.1:tidb-cloud/sql-proxy-account.md#sql-proxy-account`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c03a23f0de6b8d296bc68af56c7c2d958de97f7ec7300f5a6660c20a727f3256`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/sql-proxy-account#sql-proxy-account
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/sql-proxy-account.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what a TiDB Cloud SQL proxy account is, how to identify it, how its username is formed, which IAM roles map to proxy roles, or how access is limited for SQL Editor and Data Service.
- Retrieval Keywords: SQL proxy account, tidb_auth_token, mysql.user, SELECT user FROM user WHERE plugin = 'tidb_auth_token', SHOW GRANTS for 'username', role_admin, role_readonly, role_readwrite, SQL Editor, Data Service, JWT token-based, SQL proxy account username, TiDB Cloud Dedicated, TiDB Cloud Serverless, serverless_unique_prefix, No proxy account, automatically created, automatically deleted
- Follow-up Guidance: The source also states that a manually deleted SQL proxy account is automatically recreated when the user log in to the TiDB Cloud console next time.
- Classification Note: This is reference content because it defines SQL proxy account behavior, identification queries, username rules, role mappings, lifecycle conditions, and access control in TiDB Cloud.

## Official Source Content

# SQL Proxy Account

A SQL proxy account is a SQL user account that is automatically created by TiDB Cloud to access the database via [SQL Editor](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query) or [Data Service](https://docs.pingcap.com/tidbcloud/api/v1beta1/dataservice) on behalf of a TiDB Cloud user. For example, `testuser@pingcap.com` is a TiDB Cloud user account, while `3jhEcSimm7keKP8.testuser._41mqK6H4` is its corresponding SQL proxy account.

SQL proxy accounts provide a secure, token-based authentication mechanism for accessing the database in TiDB Cloud. By eliminating the need for traditional username and password credentials, SQL proxy accounts enhance security and simplify access management.

The key benefits of SQL proxy accounts are as follows:

- Enhanced security: mitigates risks associated with static credentials by using JWT tokens.
- Streamlined access: restricts access specifically to the SQL Editor and Data Service, ensuring precise control.
- Ease of management: simplifies authentication for developers and administrators working with TiDB Cloud.
## Identify the SQL proxy account

If you want to identify whether a specific SQL account is a SQL proxy account, take the following steps:

1. Examine the `mysql.user` table:

    ```sql
    USE mysql;
    SELECT user FROM user WHERE plugin = 'tidb_auth_token';
    ```

2. Check grants for the SQL account. If roles like `role_admin`, `role_readonly`, or `role_readwrite` are listed, then it is a SQL proxy account.

    ```sql
    SHOW GRANTS for 'username';
    ```
## How the SQL proxy account is created

The SQL proxy account is automatically created during TiDB Cloud cluster initialization for the TiDB Cloud user who is granted a role with permissions in the cluster.
## How the SQL proxy account is deleted

When a user is removed from [an organization](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#remove-an-organization-member) or [a project](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#remove-a-project-member), or their role changes to one that does not have access to the cluster, the SQL proxy account is automatically deleted.

Note that if a SQL proxy account is manually deleted, it will be automatically recreated when the user log in to the TiDB Cloud console next time.
## SQL proxy account username

In some cases, the SQL proxy account username is exactly the same as the TiDB Cloud username, but in other cases it is not exactly the same. The SQL proxy account username is determined by the length of the TiDB Cloud user's email address. The rules are as follows:

| Environment | Email length | Username format |
| ----------- | ------------ | --------------- |
| TiDB Cloud Dedicated | <= 32 characters | Full email address |
| TiDB Cloud Dedicated | > 32 characters | `prefix($email, 23)_prefix(base58(sha1($email)), 8)` |
| TiDB Cloud Serverless | <= 15 characters | `serverless_unique_prefix + "." + email` |
| TiDB Cloud Serverless | > 15 characters | `serverless_unique_prefix + "." + prefix($email, 6)_prefix(base58(sha1($email)), 8)` |

Examples:

| Environment | Email address | SQL proxy account username |
| ----------- | ----- | -------- |
| TiDB Cloud Dedicated | `user@pingcap.com` | `user@pingcap.com` |
| TiDB Cloud Dedicated | `longemailaddressexample@pingcap.com` | `longemailaddressexample_48k1jwL9` |
| TiDB Cloud Serverless | `u1@pingcap.com` | `{user_name_prefix}.u1@pingcap.com` |
| TiDB Cloud Serverless | `longemailaddressexample@pingcap.com` | `{user_name_prefix}.longem_48k1jwL9`|

> **Note:**
>
> In the preceding table, `{user_name_prefix}` is a unique prefix generated by TiDB Cloud to distinguish TiDB Cloud Serverless clusters. For details, see the [user name prefix](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#user-name-prefix) of TiDB Cloud Serverless clusters.
## SQL proxy account password

Since SQL proxy accounts are JWT token-based, it is not necessary to manage passwords for these accounts. The security token is automatically managed by the system.
## SQL proxy account roles

The SQL proxy account's role depends on the TiDB Cloud user's IAM role:

- Organization level:
    - Organization Owner: role_admin
    - Organization Billing Manager: No proxy account
    - Organization Viewer: No proxy account
    - Organization Console Audit Manager: No proxy account

- Project level:
    - Project Owner: role_admin
    - Project Data Access Read-Write: role_readwrite
    - Project Data Access Read-Only: role_readonly
## SQL proxy account access control

SQL proxy accounts are JWT token-based and only accessible to the Data Service and SQL Editor. It is impossible to access the TiDB Cloud cluster using a SQL proxy account with a username and password.
