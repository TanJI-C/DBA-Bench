# Serverless driver SQL-level options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver.md`
- Source Title: `TiDB Cloud Serverless Driver (Beta)`
- Source Heading Path: `TiDB Cloud Serverless Driver (Beta) > Configure the serverless driver > SQL level options`
- Source Line Ranges: `196-261`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`
- Topic Tags: `sql-options`, `arraymode`, `fullresult`, `isolation`, `decoders`, `configuration-precedence`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0257_f075fffa10`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver.md#sql-level-options`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `da50b692f8fa615d00b8d1165cbb777571e4f987ad9066b3177f53ed54cdf5d7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver#sql-level-options
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL level options for the TiDB Cloud serverless driver, their defaults, precedence over connection level configurations, or examples for arrayMode, fullResult, isolation, and decoders.
- Retrieval Keywords: SQL level options, arrayMode, fullResult, isolation, decoders, higher priority over connection level configurations, REPEATABLE READ, READ COMMITTED, begin function, connect(), conn.execute, ColumnType.BIGINT, ColumnType.DATETIME, decoder option, serverless driver configuration changes v0.0.7 v0.0.10
- Follow-up Guidance: The source includes examples showing conn.execute with {arrayMode:true,fullResult:true}, conn.begin with {isolation:"READ COMMITTED"}, and decoders configured in connect() and overridden at the SQL level.
- Classification Note: This is classified as configuration because the content defines SQL level and connection level driver options, default values, precedence, and supported settings.

## Official Source Content

### SQL level options

> **Note:**
>
> The SQL level options have a higher priority over connection level configurations.

At the SQL level, you can configure the following options:

| Option       | Type   | Default value     | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|--------------|--------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `arrayMode`  | bool   | `false`           | Whether to return results as arrays instead of objects. To get better performance, set it to `true`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `fullResult` | bool   | `false`           | Whether to return the full result object instead of just rows. To get more detailed results, set it to `true`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `isolation`  | string | `REPEATABLE READ` | The transaction isolation level, which can be set to `READ COMMITTED` or `REPEATABLE READ`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `decoders`   | object | `{}`              | A collection of key-value pairs, which enables you to customize the decoding process for different column types. In each pair, you can specify a column type as the key and specify a corresponding function as the value. This function takes the raw string value received from TiDB Cloud serverless driver as an argument and returns the decoded value. If you have configured `decoders` at both the connection and SQL levels, the key-value pairs with different keys configured at the connection level will be merged to the SQL level to take effect. If the same key (this is, column type) is specified at both levels, the value at the SQL level takes precedence. |

**arrayMode and fullResult**

To return the full result object as arrays, you can configure the `arrayMode` and `fullResult` options as follows:

```ts
const conn = connect({url: process.env['DATABASE_URL'] || 'mysql://[username]:[password]@[host]/[database]'})
const results = await conn.execute('select * from test',null,{arrayMode:true,fullResult:true})
```

**isolation**

The `isolation` option can only be used in the `begin` function.

```ts
const conn = connect({url: 'mysql://[username]:[password]@[host]/[database]'})
const tx = await conn.begin({isolation:"READ COMMITTED"})
```

**decoders**

To customize the format of returned column values, you can configure the `decoder` option in the `connect()` method as follows:

```ts
import { connect, ColumnType } from '@tidbcloud/serverless';

const conn = connect({
  url: 'mysql://[username]:[password]@[host]/[database]',
  decoders: {
    // By default, TiDB Cloud serverless driver returns the BIGINT type as text value. This decoder converts BIGINT to the JavaScript built-in BigInt type.
    [ColumnType.BIGINT]: (rawValue: string) => BigInt(rawValue),
    
    // By default, TiDB Cloud serverless driver returns the DATETIME type as the text value in the 'yyyy-MM-dd HH:mm:ss' format. This decoder converts the DATETIME text to the JavaScript native Date object.
    [ColumnType.DATETIME]: (rawValue: string) => new Date(rawValue),
  }
})

// You can also configure the decoder option at the SQL level to override the decoders with the same keys at the connection level.
conn.execute(`select ...`, [], {
  decoders: {
    // ...
  }
})
```

> **Note:**
>
> TiDB Cloud serverless driver configuration changes:
> 
> - v0.0.7: add the SQL level option `isolation`.
> - v0.0.10: add the connection level configuration `decoders` and the SQL level option `decoders`.
