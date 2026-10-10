# Disable or re-enable a Serverless public endpoint

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connect-via-standard-connection-serverless.md`
- Source Title: `Connect to TiDB Cloud Serverless via Public Endpoint`
- Source Heading Path: `Connect to TiDB Cloud Serverless via Public Endpoint > Disable a public endpoint | Connect to TiDB Cloud Serverless via Public Endpoint > What's next`
- Source Line Ranges: `40-68`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `public-endpoint`, `disable`, `enable`, `networking`, `access-control`, `existing-connections`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0294_bcdf6523d8`
- Source ID: `tidb-docs-8.1:tidb-cloud/connect-via-standard-connection-serverless.md#disable-a-public-endpoint`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1b47a7052768d678dea31e2eec4858d060c58626452121b0c0e5770f9dc6bc8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless#disable-a-public-endpoint
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connect-via-standard-connection-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about disabling or re-enabling a TiDB Cloud Serverless public endpoint and what happens to existing and new internet connections afterward.
- Retrieval Keywords: Disable a public endpoint, re-enable the public endpoint, TiDB Cloud Serverless public endpoint, Settings > Networking, Networking page, Disable, Enable, Connection Type drop-down list, Public entry is disabled, existing connections, new connections from the internet, users will get an error
- Follow-up Guidance: After you have successfully connected to your TiDB cluster, you can explore SQL statements with TiDB.
- Classification Note: The official content is an operation guide for changing public-endpoint availability in TiDB Cloud Serverless and explains that disabling only prevents new internet connections while not affecting existing connections.

## Official Source Content

## Disable a public endpoint

If you do not need to use a public endpoint of a TiDB Cloud Serverless cluster, you can disable it to prevent connections from the internet:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. In the left navigation pane, click **Settings** > **Networking**.

3. On the **Networking** page, click **Disable**. A confirmation dialog is displayed.

4. Click **Disable** in the confirmation dialog.

After disabling the public endpoint, the `Public` entry in the **Connection Type** drop-down list of the connect dialog is disabled. If users are still trying to access the cluster from the public endpoint, they will get an error.

> **Note:**
>
> Disabling the public endpoint does not affect existing connections. It only prevents new connections from the internet.

You can re-enable the public endpoint after disabling it:

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. In the left navigation pane, click **Settings** > **Networking**.

3. On the **Networking** page, click **Enable**.
## What's next

After you have successfully connected to your TiDB cluster, you can [explore SQL statements with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations).
