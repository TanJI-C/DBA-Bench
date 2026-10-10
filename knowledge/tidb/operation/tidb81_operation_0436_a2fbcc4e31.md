# Create a Chat2Query knowledge base for a linked database

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-chat2query-knowledge.md`
- Source Title: `Use Knowledge Bases`
- Source Heading Path: `Use Knowledge Bases | Use Knowledge Bases > Before you begin | Use Knowledge Bases > Step 1. Create a knowledge base for the linked database`
- Source Line Ranges: `5-63`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `chat2query`, `knowledge-base`, `api`, `prerequisites`, `database-linking`, `endpoint`, `creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0436_a2fbcc4e31`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-chat2query-knowledge.md#use-knowledge-bases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9abbb29ac7e4ad9c90220dfe59d37b12f4949fe857182318b2be511062d5e808`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-knowledge#use-knowledge-bases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-chat2query-knowledge.md

## Retrieval Guidance

- Use When: Use this chunk when you need the prerequisites and API endpoint for creating a Chat2Query knowledge base for a linked database and obtaining the returned identifier.
- Retrieval Keywords: Chat2Query knowledge base, create knowledge base, linked database, /v3/knowledgeBases, knowledge_base_id, Chat2Query Data App, API key, cluster_id, database, description, TiDB Cloud Serverless, TiDB Cloud Dedicated, knowledge base related endpoints
- Follow-up Guidance: After the response is returned, record the `knowledge_base_id` value for later knowledge management.
- Classification Note: This is classified as an operation because it provides prerequisites, an endpoint call, request fields, and the response field used when creating a knowledge base.

## Official Source Content

# Use Knowledge Bases

A knowledge base is a collection of structured data that can be used to enhance the SQL generation capabilities of Chat2Query.

Starting from v3, the Chat2Query API enables you to add or modify knowledge bases by calling knowledge base related endpoints of your Chat2Query Data App.

> **Note:**
>
> Knowledge base related endpoints are available for [TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) clusters by default. To use knowledge base related endpoints on [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters, contact [TiDB Cloud support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
## Before you begin

Before creating a knowledge base for your database, make sure that you have the following:

- A [Chat2Query Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api#create-a-chat2query-data-app)
- An [API key for the Chat2Query Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api#create-an-api-key)
## Step 1. Create a knowledge base for the linked database

> **Note:**
>
> The knowledge used by Chat2Query is **structured according to the database dimension**. You can connect multiple Chat2Query Data Apps to the same database, but each Chat2Query Data App can only use knowledge from a specific database it is linked to.

In your Chat2Query Data App, you can create a knowledge base for a specific database by calling the `/v3/knowledgeBases` endpoint. After creation, you will get a `knowledge_base_id` for future knowledge management.

The following is a general code example for calling this endpoint.

> **Tip:**
>
> To get a specific code example for your endpoint, click the endpoint name in the left pane of your Data App, and then click **Show Code Example**. For more information, see [Get the example code of an endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api#get-the-code-example-of-an-endpoint).

```bash
curl --digest --user ${PUBLIC_KEY}:${PRIVATE_KEY} --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/chat2query-<ID>/endpoint/v3/knowledgeBases'\
 --header 'content-type: application/json'\
 --data-raw '{
    "cluster_id": "<The ID of the cluster to which the database belongs>",
    "database": "<The name of the target database>",
    "description": "<Your knowledge base description>"
}'
```

An example response is as follows:

```json
{
    "code":200,
    "msg":"",
    "result":
        {
            "default":true,
            "description":"",
            "knowledge_base_id":2
        }
}
```

After getting the response, record the `knowledge_base_id` value in your response for later use.
