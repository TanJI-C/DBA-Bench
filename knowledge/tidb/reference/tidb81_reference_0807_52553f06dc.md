# Zapier triggers, actions, templates, and account setup FAQ

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-zapier.md`
- Source Title: `Integrate TiDB Cloud with Zapier`
- Source Heading Path: `Integrate TiDB Cloud with Zapier > Triggers & Actions | Integrate TiDB Cloud with Zapier > Triggers & Actions > Triggers | Integrate TiDB Cloud with Zapier > Triggers & Actions > Actions | Integrate TiDB Cloud with Zapier > TiDB Cloud App templates | Integrate TiDB Cloud with Zapier > FAQ | Integrate TiDB Cloud with Zapier > FAQ > How can I set up the TiDB Cloud account in Zapier?`
- Source Line Ranges: `140-193`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `zapier`, `triggers`, `actions`, `templates`, `faq`, `api-key`, `serverless`, `custom-query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0807_52553f06dc`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-zapier.md#triggers-actions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1412a77dfc16607f3f742f13a72124d1f56229a311fcfb90ee05b67f8dafb2a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-zapier#triggers-actions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-zapier.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs a reference list of TiDB Cloud Zapier triggers, actions, templates, or the FAQ about setting up a TiDB Cloud account in Zapier with an API key.
- Retrieval Keywords: Triggers & Actions, New Cluster, New Table, New Row, New Row (Custom Query), Find Cluster, Create Cluster, Find Database, Create Database, Find Table, Create Table, Create Row, Update Row, Find Row, Find Row (Custom Query), TiDB Cloud App templates, TiDB Cloud API key, How can I set up the TiDB Cloud account in Zapier?
- Follow-up Guidance: It also lists example Zapier templates such as Duplicate new TiDB Cloud rows in Google Sheets and Send emails via Gmail from new custom TiDB queries.
- Classification Note: This is classified as reference because the content enumerates supported Zapier triggers, actions, required resources, example templates, and an account setup FAQ rather than providing a single procedure.

## Official Source Content

## Triggers & Actions

[Triggers and actions](https://zapier.com/how-it-works) are the key concepts in Zapier. By combining different triggers and actions, you can create various automation workflows.

This section introduces the triggers and actions provided by TiDB Cloud App on Zapier.
### Triggers

The following table lists the triggers supported by TiDB Cloud App.

| Trigger                | Description                                                                 |
| ---------------------- |-----------------------------------------------------------------------------|
| New Cluster            | Triggers when a new cluster is created.                                     |
| New Table              | Triggers when a new table is created.                                       |
| New Row                | Triggers when new rows are created. Only fetches the recent 10000 new rows. |
| New Row (Custom Query) | Triggers when new rows are returned from a custom query that you provide.   |
### Actions

The following table lists the actions supported by TiDB Cloud App. Note that some actions need extra resources, and you need to prepare the corresponding resources before using the action.

| Action | Description | Resource |
|---|---|---|
| Find Cluster | Finds an existing TiDB Cloud Serverless or TiDB Cloud Dedicated cluster. | None |
| Create Cluster | Creates a new cluster. Only supports creating a TiDB Cloud Serverless cluster. | None |
| Find Database | Finds an existing database. | A TiDB Cloud Serverless cluster |
| Create Database | Creates a new database. | A TiDB Cloud Serverless cluster |
| Find Table | Finds an existing Table. | A TiDB Cloud Serverless cluster and a database |
| Create Table | Creates a new table. | A TiDB Cloud Serverless cluster and a database |
| Create Row | Creates a new row. | A TiDB Cloud Serverless cluster, a database, and a table |
| Update Row | Updates an existing row. | A TiDB Cloud Serverless cluster, a database, and a table |
| Find Row | Finds a row in a table via a lookup column. | A TiDB Cloud Serverless cluster, a database, and a table |
| Find Row (Custom Query) | Finds a row in a table via a custom query the you provide. | A TiDB Cloud Serverless cluster, a database, and a table |
## TiDB Cloud App templates

TiDB Cloud provides some templates for you to use in Zapier directly. You can find all the templates in the [TiDB Cloud App](https://zapier.com/apps/tidb-cloud/integrations) page.

Here are some examples:

- [Duplicate new TiDB Cloud rows in Google Sheets](https://zapier.com/apps/google-sheets/integrations/tidb-cloud/1134881/duplicate-new-tidb-cloud-rows-in-google-sheets).
- [Send emails via Gmail from new custom TiDB queries](https://zapier.com/apps/gmail/integrations/tidb-cloud/1134903/send-emails-via-gmail-from-new-custom-tidb-queries).
- [Add rows to TiDB Cloud from newly caught webhooks](https://zapier.com/apps/tidb-cloud/integrations/webhook/1134955/add-rows-to-tidb-cloud-from-newly-caught-webhooks).
- [Store new Salesforce contacts on TiDB rows](https://zapier.com/apps/salesforce/integrations/tidb-cloud/1134923/store-new-salesforce-contacts-on-tidb-rows).
- [Create TiDB rows for new Gmail emails with resumes and send direct Slack notifications](https://zapier.com/apps/gmail/integrations/slack/1135456/create-tidb-rows-for-new-gmail-emails-with-resumes-and-send-direct-slack-notifications)
## FAQ
### How can I set up the TiDB Cloud account in Zapier?

Zapier requires your **TiDB Cloud API key** to connect with your TiDB Cloud account. Zapier does not need your login account for TiDB Cloud.

To get your TiDB Cloud API key, follow the [TiDB Cloud API documentation](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-Key-Management).
