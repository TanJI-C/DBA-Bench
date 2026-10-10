# Index Insight FAQ for deactivation and troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/index-insight.md`
- Source Title: `Index Insight (Beta)`
- Source Heading Path: `Index Insight (Beta) > FAQ | Index Insight (Beta) > FAQ > How to deactivate Index Insight? | Index Insight (Beta) > FAQ > How to delete the SQL user after deactivating Index Insight? | Index Insight (Beta) > FAQ > Why does the `invalid user or password` message show up during activation or check-up? | Index Insight (Beta) > FAQ > Why does the `no sufficient privileges` message show up during activation or check-up? | Index Insight (Beta) > FAQ > Why does the `operations may be too frequent` message show up during using Index Insight? | Index Insight (Beta) > FAQ > Why does the `internal error` message show up during using Index Insight?`
- Source Line Ranges: `92-170`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `faq`, `deactivation`, `drop user`, `authentication errors`, `privilege errors`, `rate limiting`, `internal errors`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0087_f16626cec4`
- Source ID: `tidb-docs-8.1:tidb-cloud/index-insight.md#faq`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1f8abe601ab689ab4ee58d3fce427f9433a1c193e8174bddd6d2f86ca72fa67c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/index-insight#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/index-insight.md

## Retrieval Guidance

- Use When: Use this when the user asks about Index Insight FAQ items such as deactivation, deleting the SQL user, or troubleshooting messages like invalid user or password, no sufficient privileges, operations may be too frequent, and internal error.
- Retrieval Keywords: Index Insight FAQ, deactivate Index Insight, Index Insight settings, Deactivate, all index recommendations are removed, DROP USER 'username', invalid user or password, no sufficient privileges, operations may be too frequent, internal error, cannot authenticate the credentials, expired or locked user account, required privileges, read privilege for information_schema and mysql, PROCESS and REFERENCES privileges, contact PingCAP support team, refresh the page, retry the operation
- Follow-up Guidance: The source provides specific follow-up steps for each error, including verifying credentials or privileges, recreating the SQL user with the listed GRANT statements, slowing down operations, retrying, and contacting PingCAP support if the issue persists.
- Classification Note: This is classified as diagnosis because the official content is an FAQ focused on deactivation behavior and troubleshooting Index Insight activation and check-up errors.

## Official Source Content

## FAQ

This section lists some frequently asked questions about the Index Insight feature.
### How to deactivate Index Insight?

To deactivate the Index Insight feature, perform the following steps:

1. In the upper-right corner of the **Index Insight overview** page, click **Settings**. The **Index Insight settings** page is displayed.
2. Click **Deactivate**. A confirmation dialog box is displayed.
3. Click **OK** to confirm the deactivation.

    After you deactivate the Index Insight feature, all index recommendations are removed from the **Index Insight overview** page. However, the SQL user created for the feature is not deleted. You can delete the SQL user manually.
### How to delete the SQL user after deactivating Index Insight?

After you deactivate the Index Insight feature, you can execute the `DROP USER` statement to delete the SQL user created for the feature. The following is an example. Replace `'username'` with your value.

```sql
DROP USER 'username';
```
### Why does the `invalid user or password` message show up during activation or check-up?

The `invalid user or password` message typically prompts when the system cannot authenticate the credentials you provided. This issue might occur due to various reasons, such as incorrect username or password, or an expired or locked user account.

To resolve this issue, perform the following steps:

1. Verify your credentials: Make sure that the username and password you provided are correct. Pay attention to case sensitivity.
2. Check account status: Make sure that your user account is in active status and not expired or locked. You can confirm this by contacting the system administrator or the relevant support channel.
3. Create a new SQL user: If this issue is not resolved by the preceding steps, you can create a new SQL user using the following statements. Replace `'index_insight_user'` and `'random_password'` with your values.

    ```sql
    CREATE user 'index_insight_user'@'%' IDENTIFIED by 'random_password';
    GRANT SELECT ON information_schema.* TO 'index_insight_user'@'%';
    GRANT SELECT ON mysql.* TO 'index_insight_user'@'%';
    GRANT PROCESS, REFERENCES ON *.* TO 'index_insight_user'@'%';
    FLUSH PRIVILEGES;
    ```

If you are still facing the issue after following the preceding steps, it is recommended to contact [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### Why does the `no sufficient privileges` message show up during activation or check-up?

The `no sufficient privileges` message typically prompts when the SQL user you provided lacks the required privileges to request index recommendations from Index Insight.

To resolve this issue, perform the following steps:

1. Check the user privileges: Confirm if your user account has been granted the required privileges, including read privilege for `information_schema` and `mysql`, and `PROCESS` and `REFERENCES` privileges for all databases.

2. Create a new SQL user: If this issue is not resolved by the preceding steps, you can create a new SQL user using the following statements. Replace `'index_insight_user'` and `'random_password'` with your values.

    ```sql
    CREATE user 'index_insight_user'@'%' IDENTIFIED by 'random_password';
    GRANT SELECT ON information_schema.* TO 'index_insight_user'@'%';
    GRANT SELECT ON mysql.* TO 'index_insight_user'@'%';
    GRANT PROCESS, REFERENCES ON *.* TO 'index_insight_user'@'%';
    FLUSH PRIVILEGES;
    ```

If you are still facing the issue after following the preceding steps, it is recommended to contact [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
### Why does the `operations may be too frequent` message show up during using Index Insight?

The `operations may be too frequent` message typically prompts when you have exceeded the rate or usage limit set by Index Insight.

To resolve this issue, perform the following steps:

1. Slow down operations: If you receive this message, you need to decrease your operation frequency on Index Insight.
2. Contact support: If the issue persists, contact [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) and provide details of the error message, your actions, and any other relevant information.
### Why does the `internal error` message show up during using Index Insight?

The `internal error` message typically prompts when the system encounters an unexpected error or issue. This error message is general and does not provide details about the underlying cause.

To resolve this issue, perform the following steps:

1. Retry the operation: Refresh the page or try the operation again. The error might be temporary and can be resolved by a simple retry.
2. Contact support: If the issue persists, contact [PingCAP support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) and provide details of the error message, your actions, and any other relevant information.
