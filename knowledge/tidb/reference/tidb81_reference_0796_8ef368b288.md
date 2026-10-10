# Data Service HTTP status codes and error responses

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-response-and-status-code.md`
- Source Title: `Response and HTTP Status Codes of Data Service`
- Source Heading Path: `Response and HTTP Status Codes of Data Service > Status code | Response and HTTP Status Codes of Data Service > Status code > 200 | Response and HTTP Status Codes of Data Service > Status code > 400 | Response and HTTP Status Codes of Data Service > Status code > 401 | Response and HTTP Status Codes of Data Service > Status code > 404 | Response and HTTP Status Codes of Data Service > Status code > 405 | Response and HTTP Status Codes of Data Service > Status code > 408 | Response and HTTP Status Codes of Data Service > Status code > 429 | Response and HTTP Status Codes of Data Service > Status code > 500`
- Source Line Ranges: `118-380`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `http-status-codes`, `success`, `parameter-validation`, `authentication`, `endpoint-not-found`, `method-not-allowed`, `timeout`, `rate-limit`, `internal-error`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0796_8ef368b288`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-response-and-status-code.md#status-code`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `24021a6120ff9fc6345c2f48ff022259d8d2c26cee6cd0695a9bf7634ae27ffa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-response-and-status-code#status-code
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-response-and-status-code.md

## Retrieval Guidance

- Use When: Use this chunk when you need to interpret Data Service HTTP status codes and error response bodies such as 200, 400, 401, 404, 405, 408, 429, and 500.
- Retrieval Keywords: Data Service HTTP status codes, 200 data.result.code 200, 400 param check failed, 401 auth failed, 404 endpoint not found, 405 method not allowed, GET and POST only, 408 request timeout, 429 rate limit API key, 49900007, Chat2Data 429, 500 internal error, defaultPermissionHelper rpc error DeadlineExceeded, context deadline exceeded, refer to the message for troubleshooting
- Follow-up Guidance: The content says to check the `code` and `message` fields for detailed information, and for `500` errors it says to refer to the `message` for troubleshooting.
- Classification Note: This is reference content because it maps specific HTTP status codes and example `result.code` and `message` values to their meanings in Data Service responses.

## Official Source Content

## Status code
### 200

If the HTTP status code is `200` and the `data.result.code` field also shows `200`, this indicated that the SQL statement is executed successfully. Otherwise, TiDB Cloud fails to execute the SQL statement defined in your endpoint. You can check the `code` and `message` fields for detailed information.

An example response is as follows:

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 1146,
            "message": "table not found",
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
### 400

This status code indicates that the parameter check failed.

An example response is as follows:

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 400,
            "message": "param check failed! {detailed error}",
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
### 401

This status code indicates that the authentication failed due to lack of permission.

An example response is as follows:

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 401,
            "message": "auth failed",
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
### 404

This status code indicates that the authentication failed due to the inability to find the specified endpoint.

An example response is as follows:

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 404,
            "message": "endpoint not found",
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
### 405

This status code indicates that the request used a method that is not allowed. Note that Data Service only supports `GET` and `POST`.

An example response is as follows:

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 405,
            "message": "method not allowed",
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
### 408

This status code indicates that the request exceeds the timeout duration of the endpoint. To modify the timeout of an endpoint, refer to [Configure properties](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#configure-properties).

An example response is as follows:

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 408,
            "message": "request timeout.",
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
### 429

This status code indicates that the request exceeds the rate limit of the API key. For more quota, you can [submit a request](https://tidb.support.pingcap.com/) to our support team.

An example response is as follows:

<div label="SQL Endpoint">

```json
{
  "type": "",
  "data": {
    "columns": [],
    "rows": [],
    "result": {
      "code": 49900007,
      "message": "The request exceeded the limit of 100 times per apikey per minute. For more quota, please contact us: https://tidb.support.pingcap.com/",
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

</div>

<div label="Chat2Data Endpoint">

```json
{
  "type": "chat2data_endpoint",
  "data": {
    "columns": [],
    "rows": [],
    "result": {
      "code": 429,
      "message": "The AI request exceeded the limit of 100 times per day. For more quota, please contact us: https://tidb.support.pingcap.com/",
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

</div>
### 500

This status code indicates that the request met an internal error. There might be various causes for this error.

One possible cause is that the authentication failed due to the inability to connect to the authentication server.

An example response is as follows:

```json
{
    "type": "sql_endpoint",
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

This might also be related to the inability to connect the TiDB Cloud cluster. You need to refer to the `message` for troubleshooting.

```json
{
    "type": "sql_endpoint",
    "data": {
        "columns": [],
        "rows": [],
        "result": {
            "code": 500,
            "message": "internal error! {detailed error}",
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
