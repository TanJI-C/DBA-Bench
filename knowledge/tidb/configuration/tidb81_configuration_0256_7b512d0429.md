# Serverless driver connection configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver.md`
- Source Title: `TiDB Cloud Serverless Driver (Beta)`
- Source Heading Path: `TiDB Cloud Serverless Driver (Beta) > Configure the serverless driver | TiDB Cloud Serverless Driver (Beta) > Configure the serverless driver > Connection level configurations`
- Source Line Ranges: `147-195`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `configuration`, `connection-options`, `database-url`, `credentials`, `fetch`, `arraymode`, `fullresult`, `decoders`, `percent-encoding`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0256_7b512d0429`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver.md#configure-the-serverless-driver`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2e12ba345e82de8dd1059bd78f08459dd1cc29a37edc2f8e25b8d78937a0d315`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver#configure-the-serverless-driver
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver.md

## Retrieval Guidance

- Use When: Use this chunk when searching for connection-level configuration options of the TiDB Cloud serverless driver, including `url`, credentials fields, `fetch`, `arrayMode`, `fullResult`, `decoders`, and database URL encoding rules.
- Retrieval Keywords: Configure the serverless driver, Connection level configurations, username, password, host, database, url, mysql://[username]:[password]@[host]/[database], fetch, global fetch, undici fetch, arrayMode, fullResult, decoders, Database URL, percentage-encode, percent-encoding, DATABASE_URL, connect(config)
- Follow-up Guidance: The source states that when `url` is configured, you do not need to configure `host`, `username`, `password`, and `database` separately, and it shows equivalent `connect(config)` examples.
- Classification Note: This is classified as configuration because the content is a reference for serverless driver connection options and how to express them in a database URL or config object.

## Official Source Content

## Configure the serverless driver

You can configure TiDB Cloud serverless driver at both the connection level and the SQL level.
### Connection level configurations

At the connection level, you can make the following configurations:

| Name         | Type     | Default value | Description                                                                                                                                                                                                                                                                                                                                                  |
|--------------|----------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `username`   | string   | N/A           | Username of TiDB Cloud Serverless                                                                                                                                                                                                                                                                                                                                  |
| `password`   | string   | N/A           | Password of TiDB Cloud Serverless                                                                                                                                                                                                                                                                                                                                  |
| `host`       | string   | N/A           | Hostname of TiDB Cloud Serverless                                                                                                                                                                                                                                                                                                                                  |
| `database`   | string   | `test`        | Database of TiDB Cloud Serverless                                                                                                                                                                                                                                                                                                                                  |
| `url`        | string   | N/A           | The URL for the database, in the `mysql://[username]:[password]@[host]/[database]` format, where `database` can be skipped if you intend to connect to the default database.                                                                                                                                                                                 |
| `fetch`      | function | global fetch  | Custom fetch function. For example, you can use the `undici` fetch in node.js.                                                                                                                                                                                                                                                                               |
| `arrayMode`  | bool     | `false`       | Whether to return results as arrays instead of objects. To get better performance, set it to `true`.                                                                                                                                                                                                                                                         |
| `fullResult` | bool     | `false`       | Whether to return full result object instead of just rows. To get more detailed results, set it to `true`.                                                                                                                                                                                                                                                   |
| `decoders`   | object   | `{}`          | A collection of key-value pairs, which enables you to customize the decoding process for different column types. In each pair, you can specify a column type as the key and specify a corresponding function as the value. This function takes the raw string value received from TiDB Cloud serverless driver as an argument and returns the decoded value. |

**Database URL**

> **Note:**
>
> If your username, password, or database name contains special characters, you must [percentage-encode](https://en.wikipedia.org/wiki/Percent-encoding) these characters when passing them by the URL. For example, the password `password1@//?` needs to be encoded as `password1%40%2F%2F%3F` in the URL.

When `url` is configured, there is no need to configure `host`, `username`, `password`, and `database` separately. The following codes are equivalent:

```ts
const config = {
  host: '<host>',
  username: '<user>',
  password: '<password>',
  database: '<database>',
  arrayMode: true,
}

const conn = connect(config)
```

```ts
const config = {
  url: process.env['DATABASE_URL'] || 'mysql://[username]:[password]@[host]/[database]',
  arrayMode: true
}

const conn = connect(config)
```
