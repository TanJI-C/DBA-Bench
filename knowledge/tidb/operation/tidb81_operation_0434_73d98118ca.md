# Calling Chat2Query endpoints and generating a data summary

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-chat2query-api.md`
- Source Title: `Get Started with Chat2Query API`
- Source Heading Path: `Get Started with Chat2Query API > Call Chat2Query endpoints | Get Started with Chat2Query API > Call Chat2Query endpoints > Get the code example of an endpoint | Get Started with Chat2Query API > Call Chat2Query endpoints > Call Chat2Query v3 endpoints or v2 endpoints | Get Started with Chat2Query API > Call Chat2Query endpoints > Call Chat2Query v3 endpoints or v2 endpoints > 1. Generate a data summary by calling `/v3/dataSummaries``
- Source Line Ranges: `64-170`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `chat2query`, `endpoints`, `rate-limit`, `code-examples`, `v1`, `v2`, `v3`, `data-summaries`, `jobs`, `curl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0434_73d98118ca`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-chat2query-api.md#call-chat2query-endpoints`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a7daed6854dae605b530e8066364ae42b98d3cd8c20fae40af08c5d665ce404f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api#call-chat2query-endpoints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-chat2query-api.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs endpoint names, rate limits, code example access, or the workflow for calling Chat2Query v3 or v2 endpoints and generating a data summary before `/v3/chat2data`.
- Retrieval Keywords: 100 requests per day, 429 error, submit a request, Chat2Query Data App, /v3/dataSummaries, /v3/chat2data, /v2/dataSummaries, /v2/chat2data, /v1/chat2data, deprecated, recommended, Show Code Example, endpoint URL, request method, ${PUBLIC_KEY}, ${PRIVATE_KEY}, /v2/jobs/{job_id}, /v3/knowledgeBases, /v3/sessions, /v3/refineSql, /v3/suggestQuestions, generate a data summary, cluster_id, database, description, reuse, data_summary_id, job_id, curl --digest
- Follow-up Guidance: The source provides a concrete `/v3/dataSummaries` curl example with request body fields `cluster_id`, `database`, `description`, and `reuse`, plus a response containing `data_summary_id` and `job_id`.
- Classification Note: This is classified as an operation chunk because the content enumerates callable Chat2Query endpoints, request flow, quota behavior, and a concrete API invocation example.

## Official Source Content

## Call Chat2Query endpoints

> **Note:**
>
> Each Chat2Query Data App has a rate limit of 100 requests per day. If you exceed the rate limit, the API returns a `429` error. For more quota, you can [submit a request](https://tidb.support.pingcap.com/) to our support team.

In each Chat2Query Data App, you can find the following endpoints:

- Chat2Query v3 endpoints: the endpoints whose names starting with `/v3`, such as `/v3/dataSummaries` and `/v3/chat2data`(recommended)
- Chat2Query v2 endpoints: the endpoints whose names starting with `/v2`, such as `/v2/dataSummaries` and `/v2/chat2data`
- Chat2Query v1 endpoint: `/v1/chat2data`(deprecated)

> **Tip:**
>
> Compared with `/v1/chat2data`, `/v3/chat2data` and `/v2/chat2data` requires you to analyze your database first by calling `/v3/dataSummaries` or `/v2/dataSummaries`. Consequently, the results returned by `/v3/chat2data` and `/v2/chat2data` are generally more accurate.
### Get the code example of an endpoint

TiDB Cloud provides code examples to help you quickly call Chat2Query endpoints. To get the code example of a Chat2Query endpoint, perform the following steps:

1. In the left pane of the [**Data Service**](https://tidbcloud.com/project/data-service) page, click the name of a Chat2Query endpoint.

    The information for calling this endpoint is displayed on the right side, such as endpoint URL, code example, and request method.

2. Click **Show Code Example**.

3. In the displayed dialog box, select the cluster, database, and authentication method that you want to use to call the endpoint, and then copy the code example.

    > **Note:**
    >
    > For some of the endpoints such as `/v2/jobs/{job_id}`, you only need to select the authentication method.

4. To call the endpoint, you can paste the example in your application, replace the parameters in the example with your own (such as replacing the `${PUBLIC_KEY}` and `${PRIVATE_KEY}` placeholders with your API key), and then run it.
### Call Chat2Query v3 endpoints or v2 endpoints

TiDB Cloud Data Service provides the following Chat2Query v3 endpoints and v2 endpoints:

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST   | `/v3/dataSummaries` | This endpoint generates a data summary for your database schema, table schema, and column schema by using artificial intelligence for analysis. |
| GET    | `/v3/dataSummaries` | This endpoint retrieves all data summaries of your database. |
| GET    | `/v3/dataSummaries/{data_summary_id}` | This endpoint retrieves a specific data summary. |
| PUT    | `/v3/dataSummaries/{data_summary_id}` | This endpoint updates a specific data summary. |
| PUT    | `/v3/dataSummaries/{data_summary_id}/tables/{table_name}` | This endpoint updates the description of a specific table in a specific data summary. |
| PUT    | `/v3/dataSummaries/{data_summary_id}/tables/{table_name}/columns` | This endpoint updates the description of columns for a specific table in a specific data summary. |
| POST   | `/v3/knowledgeBases` | This endpoint creates a new knowledge base. For more information about the usage of knowledge base related endpoints, see [Use knowledge bases](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-knowledge).  |
| GET    | `/v3/knowledgeBases` | This endpoint retrieves all knowledge bases. |
| GET    | `/v3/knowledgeBases/{knowledge_base_id}` | This endpoint retrieves a specific knowledge base. |
| PUT    | `/v3/knowledgeBases/{knowledge_base_id}` | This endpoint updates a specific knowledge base. |
| POST   | `/v3/knowledgeBases/{knowledge_base_id}/data` | This endpoint adds data to a specific knowledge base. |
| GET    | `/v3/knowledgeBases/{knowledge_base_id}/data` | This endpoint retrieves data from a specific knowledge base. |
| PUT    | `/v3/knowledgeBases/{knowledge_base_id}/data/{knowledge_data_id}` | This endpoint updates specific data in a knowledge base. |
| DEL    | `/v3/knowledgeBases/{knowledge_base_id}/data/{knowledge_data_id}` | This endpoint deletes specific data from a knowledge base. |
| POST   | `/v3/sessions` | This endpoint creates a new session. For more information about the usage of session-related endpoints, see [Start multi-round Chat2Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-sessions). |
| GET    | `/v3/sessions` | This endpoint retrieves a list of all sessions. |
| GET    | `/v3/sessions/{session_id}` | This endpoint retrieves the details of a specific session. |
| PUT    | `/v3/sessions/{session_id}` | This endpoint updates a specific session. |
| PUT    | `/v3/sessions/{session_id}/reset` | This endpoint resets a specific session. |
| POST   | `/v3/sessions/{session_id}/chat2data` | This endpoint generates and executes SQL statements within a specific session using artificial intelligence. For more information, see [Start multi-round Chat2Query by using sessions](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-sessions). |
| POST   | `/v3/chat2data` | This endpoint enables you to generate and execute SQL statements using artificial intelligence by providing the data summary ID and instructions. |
| POST   | `/v3/refineSql` | This endpoint refines existing SQL queries using artificial intelligence. |
| POST   | `/v3/suggestQuestions` | This endpoint suggests questions based on the provided data summary. |
| POST   | `/v2/dataSummaries` | This endpoint generates a data summary for your database schema, table schema, and column schema using artificial intelligence. |
| GET    | `/v2/dataSummaries` | This endpoint retrieves all data summaries. |
| POST   | `/v2/chat2data` | This endpoint enables you to generate and execute SQL statements using artificial intelligence by providing the data summary ID and instructions. |
| GET    | `/v2/jobs/{job_id}` | This endpoint enables you to query the status of a specific data summary generation job. |

The steps to call `/v3/chat2data` and `/v2/chat2data` are the same. The following sections take `/v3/chat2data` as an example to show how to call it.
#### 1. Generate a data summary by calling `/v3/dataSummaries`

Before calling `/v3/chat2data`, let AI analyze the database and generate a data summary first by calling `/v3/dataSummaries`, so `/v3/chat2data` can get a better performance in SQL generation later.

The following is a code example of calling `/v3/dataSummaries` to analyze the `sp500insight` database and generate a data summary for the database:

```bash
curl --digest --user ${PUBLIC_KEY}:${PRIVATE_KEY} --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/chat2query-<ID>/endpoint/v3/dataSummaries'\
 --header 'content-type: application/json'\
 --data-raw '{
    "cluster_id": "10140100115280519574",
    "database": "sp500insight",
    "description": "Data summary for SP500 Insight",
    "reuse": false
}'
```

In the preceding example, the request body is a JSON object with the following properties:

- `cluster_id`: _string_. A unique identifier of the TiDB cluster.
- `database`: _string_. The name of the database.
- `description`: _string_. A description of the data summary.
- `reuse`: _boolean_. Specifies whether to reuse an existing data summary. If you set it to `true`, the API will reuse an existing data summary. If you set it to `false`, the API will generate a new data summary.

An example response is as follows:

```js
{
  "code": 200,
  "msg": "",
  "result": {
    "data_summary_id": 304823,
    "job_id": "fb99ef785da640ab87bf69afed60903d"
  }
}
```
