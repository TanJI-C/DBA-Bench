# Deprecated Chat2Data v1 endpoint and related references

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-chat2query-api.md`
- Source Title: `Get Started with Chat2Query API`
- Source Heading Path: `Get Started with Chat2Query API > Call Chat2Query endpoints > Call the Chat2Data v1 endpoint (deprecated) | Get Started with Chat2Query API > Learn more`
- Source Line Ranges: `340-447`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `chat2query`, `deprecated`, `v1-endpoint`, `rate-limit`, `api-key`, `curl`, `status-codes`, `links`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0915_fdd6ea29cb`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-chat2query-api.md#call-the-chat2data-v1-endpoint-deprecated`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf6d3dd48b7c41f5933ce741306b7f312c0c80d4ff7e4cd78bc43bc2a39fbb0f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api#call-the-chat2data-v1-endpoint-deprecated
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-chat2query-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the deprecated Chat2Data v1 endpoint details, including the `/v1/chat2data` request format, rate limit note, API key restriction, and example success or failure responses.
- Retrieval Keywords: Chat2Data v1 endpoint is deprecated, /v1/chat2data, /endpoint/chat2data, faster response but lower performance, 100 requests per day, 429 error, Chat2Query Data Summary Management Role, instruction, tables, cluster_id, database, COUNT(`user_id`), internal error! defaultPermissionHelper: rpc error: code = DeadlineExceeded desc = context deadline exceeded, Manage an API key, Start Multi-round Chat2Query, Use Knowledge Bases, Response and Status Codes of Data Service
- Follow-up Guidance: The Learn more section links to Manage an API key, Start Multi-round Chat2Query, Use Knowledge Bases, and Response and Status Codes of Data Service.
- Classification Note: This is classified as a reference chunk because it documents a deprecated endpoint, its parameters, notes, and example responses rather than a current step-by-step workflow.

## Official Source Content

### Call the Chat2Data v1 endpoint (deprecated)

> **Note:**
>
> The Chat2Data v1 endpoint is deprecated. It is recommended that you call Chat2Data v3 endpoints instead.

TiDB Cloud Data Service provides the following Chat2Query v1 endpoint:

|  Method | Endpoint| Description |
|  ----  | ----  |----  |
|  POST | `/v1/chat2data`  | This endpoint allows you to generate and execute SQL statements using artificial intelligence by providing the target database name and instructions.  |

You can call the `/v1/chat2data` endpoint directly to generate and execute SQL statements. Compared with `/v2/chat2data`, `/v1/chat2data` provides a faster response but lower performance.

TiDB Cloud generates code examples to help you call an endpoint. To get the examples and run the code, see [Get the code example of an endpoint](#get-the-code-example-of-an-endpoint).

When calling `/v1/chat2data`, you need to replace the following parameters:

- Replace the `${PUBLIC_KEY}` and `${PRIVATE_KEY}` placeholders with your API key.
- Replace the `<your table name, optional>` placeholder with the table name you want to query. If you do not specify a table name, AI will query all tables in the database.
- Replace the `<your instruction>` placeholder with the instruction you want AI to generate and execute SQL statements.

> **Note:**
>
> - Each Chat2Query Data App has a rate limit of 100 requests per day. If you exceed the rate limit, the API returns a `429` error. For more quota, you can [submit a request](https://tidb.support.pingcap.com/) to our support team.
> - An API Key with the role `Chat2Query Data Summary Management Role` cannot call the Chat2Data v1 endpoint.
The following code example is used to count how many users are in the `sp500insight.users` table:

```bash
curl --digest --user ${PUBLIC_KEY}:${PRIVATE_KEY} --request POST 'https://<region>.data.dev.tidbcloud.com/api/v1beta/app/chat2query-<ID>/endpoint/chat2data'\
 --header 'content-type: application/json'\
 --data-raw '{
    "cluster_id": "10939961583884005252",
    "database": "sp500insight",
    "tables": ["users"],
    "instruction": "count the users"
}'
```

In the preceding example, the request body is a JSON object with the following properties:

- `cluster_id`: _string_. A unique identifier of the TiDB cluster.
- `database`: _string_. The name of the database.
- `tables`: _array_. (optional) A list of table names to be queried.
- `instruction`: _string_. An instruction in natural language describing the query you want.

The response is as follows:

```json
{
  "type": "chat2data_endpoint",
  "data": {
    "columns": [
      {
        "col": "COUNT(`user_id`)",
        "data_type": "BIGINT",
        "nullable": false
      }
    ],
    "rows": [
      {
        "COUNT(`user_id`)": "1"
      }
    ],
    "result": {
      "code": 200,
      "message": "Query OK!",
      "start_ms": 1699529488292,
      "end_ms": 1699529491901,
      "latency": "3.609656403s",
      "row_count": 1,
      "row_affect": 0,
      "limit": 1000,
      "sql": "SELECT COUNT(`user_id`) FROM `users`;",
      "ai_latency": "3.054822491s"
    }
  }
}
```

If your API call is not successful, you will receive a status code other than `200`. The following is an example of the `500` status code:

```json
{
  "type": "chat2data_endpoint",
  "data": {
    "columns": [],
    "rows": [],
    "result": {
      "code": 500,
      "message": "internal error! defaultPermissionHelper: rpc error: code = DeadlineExceeded desc = context deadline exceeded",
      "start_ms": "",
      "end_ms": "",
      "latency": "",
      "row_count": 0,
      "row_affect": 0,
      "limit": 0
    }
  }
}
```
## Learn more

- [Manage an API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key)
- [Start Multi-round Chat2Query](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-sessions)
- [Use Knowledge Bases](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-knowledge)
- [Response and Status Codes of Data Service](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-response-and-status-code)
