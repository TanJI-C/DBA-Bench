# Manage Data Service API keys for a Data App

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-api-key.md`
- Source Title: `API Keys in Data Service`
- Source Heading Path: `API Keys in Data Service > Manage API keys > Create an API key | API Keys in Data Service > Manage API keys > Edit an API key | API Keys in Data Service > Manage API keys > Delete an API key | API Keys in Data Service > Manage API keys > Expire an API key | API Keys in Data Service > Manage API keys > Expire all API keys`
- Source Line Ranges: `84-162`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `api-keys`, `data-apps`, `create`, `edit`, `delete`, `expire`, `roles`, `rate-limits`, `expiration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0304_ee87a4fd89`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-api-key.md#create-an-api-key`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a862a42e2e14c0e660eef8e9009a7acbe97d9b44963f0f735edf6e9afab9fd42`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key#create-an-api-key
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-api-key.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the documented TiDB Cloud Data Service steps to create, edit, delete, or expire API keys for a Data App, including role, rate limit, and expiration settings.
- Retrieval Keywords: Create API Key, Edit an API key, Delete an API key, Expire an API key, Expire all API keys, Data Service page, Authentication area, Action column, Expire Now, Expire All, ReadOnly, ReadAndWrite, SELECT, SHOW, USE, DESC, EXPLAIN, DML, DDL, private key is only displayed upon key creation, cannot edit an expired key, cannot expire an expired key
- Follow-up Guidance: The source includes step-by-step UI navigation from the Data Service page to the target Data App and the Authentication area for each API key management task.
- Classification Note: This is operation content because it provides procedural steps in TiDB Cloud to manage Data Service API keys for a Data App.

## Official Source Content

### Create an API key

To create an API key for a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the **Authentication** area, click **Create API Key**.
4. In the **Create API Key** dialog box, do the following:

    1. (Optional) Enter a description for your API key.
    2. Select a role for your API key.

        The role is used to control whether the API key can read or write data to the clusters linked to the Data App. You can select the `ReadOnly` or `ReadAndWrite` role:

        - `ReadOnly`: only allows the API key to read data, such as `SELECT`, `SHOW`, `USE`, `DESC`, and `EXPLAIN` statements.
        - `ReadAndWrite`: allows the API key to read and write data. You can use this API key to execute all SQL statements, such as DML and DDL statements.

    3. (Optional) Set a desired rate limit for your API key.

       If your requests per minute exceed the rate limit, the API returns a `429` error. To get a quota of more than 1000 requests per minute (rpm) per API key, you can [submit a request](https://tidb.support.pingcap.com/) to our support team.

    4. (Optional) Set a desired expiration time for your API key.

        By default, an API key never expires. If you prefer to specify an expiration time for the API key, click **Expires in**, select a time unit (`Minutes`, `Days`, or `Months`), and then fill in a desired number for the time unit. 

5. Click **Next**. The public key and private key are displayed.

    Make sure that you have copied and saved the private key in a secure location. After leaving this page, you will not be able to get the full private key again.

6. Click **Done**.
### Edit an API key

> **Note**:
>
> You cannot edit an expired key.

To edit the description or rate limit of an API key, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the **Authentication** area, locate the **Action** column, and then click **...** > **Edit** in the API key row that you want to change.
4. Update the description, role, rate limit, or expiration time of the API key.
5. Click **Update**.
### Delete an API key

> **Note:**
>
> Before you delete an API key, make sure that the API key is not used by any Data App.

To delete an API key for a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the **API Key** area, locate the **Action** column, and then click **...** > **Delete** in the API key row that you want to delete.
4. In the displayed dialog box, confirm the deletion.
### Expire an API key

> **Note**:
>
> You cannot expire an expired key.

To expire an API key for a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the **Authentication** area, locate the **Action** column, and then click **...** > **Expire Now** in the API key row that you want to expire.
4. In the displayed dialog box, confirm the expiration.
### Expire all API keys

To expire all API keys for a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the **Authentication** area, click **Expire All**.
4. In the displayed dialog box, confirm the expiration.
