# Serverless driver features, pricing, and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver.md`
- Source Title: `TiDB Cloud Serverless Driver (Beta)`
- Source Heading Path: `TiDB Cloud Serverless Driver (Beta) > Features | TiDB Cloud Serverless Driver (Beta) > Features > Supported SQL statements | TiDB Cloud Serverless Driver (Beta) > Features > Data type mapping | TiDB Cloud Serverless Driver (Beta) > Features > ORM integrations | TiDB Cloud Serverless Driver (Beta) > Pricing | TiDB Cloud Serverless Driver (Beta) > Limitations | TiDB Cloud Serverless Driver (Beta) > What's next`
- Source Line Ranges: `262-342`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `supported-sql`, `data-type-mapping`, `javascript-types`, `orm-integrations`, `pricing`, `limitations`, `private-endpoints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0826_695e4382a3`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver.md#features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f4fe058622057a3f951d82ea8e5bfa1de68949597853b976452c3bcae8db3ec5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver#features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver.md

## Retrieval Guidance

- Use When: Use this chunk when you need a reference for TiDB Cloud serverless driver supported SQL statements, JavaScript data type mapping, ORM integrations, pricing, or documented limitations.
- Retrieval Keywords: Supported SQL statements, SELECT, SHOW, EXPLAIN, USE, INSERT, UPDATE, DELETE, BEGIN, COMMIT, ROLLBACK, SET, Data type mapping, Javascript type, BIGINT string, DECIMAL string, BINARY Uint8Array, VARBINARY Uint8Array, BIT Uint8Array, JSON object, utf8mb4 character set, v0.1.0 data type mapping changes, ORM integrations, Kysely dialect, Prisma adapter, Pricing, Request Units (RUs), TiDB Cloud Serverless pricing, Limitations, Up to 10,000 rows, single SQL statement at a time, private endpoints not supported
- Follow-up Guidance: The source points to using TiDB Cloud serverless driver in a local Node.js project in the What's next section.
- Classification Note: This is classified as reference because the content summarizes supported statements, type mappings, integrations, pricing behavior, and limitations without defining configuration steps.

## Official Source Content

## Features
### Supported SQL statements

DDL is supported and the following SQL statements are supported:  `SELECT`, `SHOW`, `EXPLAIN`, `USE`, `INSERT`, `UPDATE`, `DELETE`, `BEGIN`, `COMMIT`, `ROLLBACK`, and `SET`.
### Data type mapping

The type mapping between TiDB Cloud Serverless and Javascript is as follows:

| TiDB Cloud Serverless type | Javascript type |
|----------------------|-----------------|
| TINYINT              | number          |
| UNSIGNED TINYINT     | number          |
| BOOL                 | number          |
| SMALLINT             | number          |
| UNSIGNED SMALLINT    | number          |
| MEDIUMINT            | number          |
| INT                  | number          |
| UNSIGNED INT         | number          |
| YEAR                 | number          |
| FLOAT                | number          |
| DOUBLE               | number          |
| BIGINT               | string          |
| UNSIGNED BIGINT      | string          |
| DECIMAL              | string          |
| CHAR                 | string          |
| VARCHAR              | string          |
| BINARY               | Uint8Array      |
| VARBINARY            | Uint8Array      |
| TINYTEXT             | string          |
| TEXT                 | string          |
| MEDIUMTEXT           | string          |
| LONGTEXT             | string          |
| TINYBLOB             | Uint8Array      |
| BLOB                 | Uint8Array      |
| MEDIUMBLOB           | Uint8Array      |
| LONGBLOB             | Uint8Array      |
| DATE                 | string          |
| TIME                 | string          |
| DATETIME             | string          |
| TIMESTAMP            | string          |
| ENUM                 | string          |
| SET                  | string          |
| BIT                  | Uint8Array      |
| JSON                 | object          |
| NULL                 | null            |
| Others               | string          |

> **Note:**
>
> Make sure to use the default `utf8mb4` character set in TiDB Cloud Serverless for the type conversion to JavaScript strings, because TiDB Cloud serverless driver uses the UTF-8 encoding to decode them to strings. 

> **Note:**
>
> TiDB Cloud serverless driver data type mapping changes:
> 
> - v0.1.0: the `BINARY`, `VARBINARY`, `TINYBLOB`, `BLOB`, `MEDIUMBLOB`, `LONGBLOB`, and `BIT` types are now returned as a `Uint8Array` instead of a `string`.
### ORM integrations

TiDB Cloud serverless driver has been integrated with the following ORMs:

- [TiDB Cloud serverless driver Kysely dialect](https://github.com/tidbcloud/kysely).
- [TiDB Cloud serverless driver Prisma adapter](https://github.com/tidbcloud/prisma-adapter).
## Pricing

The serverless driver itself is free, but accessing data with the driver generates [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit) and storage usage. The pricing follows the [TiDB Cloud Serverless pricing](https://www.pingcap.com/tidb-serverless-pricing-details/) model.
## Limitations

Currently, using serverless driver has the following limitations:

- Up to 10,000 rows can be fetched in a single query.
- You can execute only a single SQL statement at a time. Multiple SQL statements in one query are not supported yet.
- Connection with [private endpoints](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless) is not supported yet.
## What's next

- Learn how to [use TiDB Cloud serverless driver in a local Node.js project](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver-node-example).
