# AWS Lambda mysql2 sample code and follow-up resources

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-aws-lambda.md`
- Source Title: `Connect to TiDB with mysql2 in AWS Lambda Function`
- Source Heading Path: `Connect to TiDB with mysql2 in AWS Lambda Function > Sample code snippets > Connect to TiDB | Connect to TiDB with mysql2 in AWS Lambda Function > Sample code snippets > Insert data | Connect to TiDB with mysql2 in AWS Lambda Function > Sample code snippets > Query data | Connect to TiDB with mysql2 in AWS Lambda Function > Sample code snippets > Update data | Connect to TiDB with mysql2 in AWS Lambda Function > Sample code snippets > Delete data | Connect to TiDB with mysql2 in AWS Lambda Function > Useful notes | Connect to TiDB with mysql2 in AWS Lambda Function > Next steps | Connect to TiDB with mysql2 in AWS Lambda Function > Need help?`
- Source Line Ranges: `270-380`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `cloud`, `ecosystem`, `sql`
- Topic Tags: `aws-lambda`, `mysql2`, `connection-pool`, `tls`, `crud`, `prepared-statements`, `sql-injection`, `orm`, `api-gateway`, `developer-guide`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0133_27f631a5a2`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-aws-lambda.md#connect-to-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c87ac29be3349d00fe96cf524c1cda9d44a2d20820f74069a197a87aa1ff8eb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-aws-lambda#connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-aws-lambda.md

## Retrieval Guidance

- Use When: Use this chunk when looking for mysql2 sample code to connect an AWS Lambda function to TiDB and perform basic CRUD with environment variables, TLS, and a connection pool.
- Retrieval Keywords: AWS Lambda mysql2, Connect to TiDB, mysql.createPool, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE, TLSv1.2, rejectUnauthorized, connectionLimit: 1, maxIdle: 1, enableKeepAlive, getPool, INSERT INTO players (coins, goods) VALUES (?, ?), SELECT id, coins, goods FROM players WHERE id = ?, UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?, DELETE FROM players WHERE id = ?, ResultSetHeader, prepared statements, SQL injection, API Gateway, TiDB-Lambda-integration/aws-lambda-bookstore Demo, mysql2 documentation, AWS developer guide of Lambda, Discord, Slack, support ticket
- Follow-up Guidance: The source links to mysql2 documentation, the AWS Lambda developer guide, the TiDB-Lambda-integration/aws-lambda-bookstore Demo, TiDB developer guide chapters such as Insert data, Update data, Delete data, Single table reading, Transactions, and SQL performance optimization, plus Discord, Slack, and support ticket channels.
- Classification Note: This is reference content because it provides exact mysql2 connection and CRUD code snippets, connection pool and TLS settings, and direct links for next steps and help.

## Official Source Content

### Connect to TiDB

The following code establish a connection to TiDB with options defined in the environment variables:

```typescript
// lib/tidb.ts
import mysql from 'mysql2';

let pool: mysql.Pool | null = null;

function connect() {
  return mysql.createPool({
    host: process.env.TIDB_HOST, // TiDB host, for example: {gateway-region}.aws.tidbcloud.com
    port: process.env.TIDB_PORT ? Number(process.env.TIDB_PORT) : 4000, // TiDB port, default: 4000
    user: process.env.TIDB_USER, // TiDB user, for example: {prefix}.root
    password: process.env.TIDB_PASSWORD, // TiDB password
    database: process.env.TIDB_DATABASE || 'test', // TiDB database name, default: test
    ssl: {
      minVersion: 'TLSv1.2',
      rejectUnauthorized: true,
    },
    connectionLimit: 1, // Setting connectionLimit to "1" in a serverless function environment optimizes resource usage, reduces costs, ensures connection stability, and enables seamless scalability.
    maxIdle: 1, // max idle connections, the default value is the same as `connectionLimit`
    enableKeepAlive: true,
  });
}

export function getPool(): mysql.Pool {
  if (!pool) {
    pool = connect();
  }
  return pool;
}
```
### Insert data

The following query creates a single `Player` record and returns a `ResultSetHeader` object:

```typescript
const [rsh] = await pool.query('INSERT INTO players (coins, goods) VALUES (?, ?);', [100, 100]);
console.log(rsh.insertId);
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

The following query returns a single `Player` record by ID `1`:

```typescript
const [rows] = await pool.query('SELECT id, coins, goods FROM players WHERE id = ?;', [1]);
console.log(rows[0]);
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

The following query adds `50` coins and `50` goods to the `Player` with ID `1`:

```typescript
const [rsh] = await pool.query(
    'UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?;',
    [50, 50, 1]
);
console.log(rsh.affectedRows);
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

The following query deletes the `Player` record with ID `1`:

```typescript
const [rsh] = await pool.query('DELETE FROM players WHERE id = ?;', [1]);
console.log(rsh.affectedRows);
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Useful notes

- Using [connection pools](https://github.com/sidorares/node-mysql2#using-connection-pools) to manage database connections can reduce the performance overhead caused by frequently establishing and destroying connections.
- To avoid SQL injection, it is recommended to use [prepared statements](https://github.com/sidorares/node-mysql2#using-prepared-statements).
- In scenarios where there are not many complex SQL statements involved, using ORM frameworks like [Sequelize](https://sequelize.org/), [TypeORM](https://typeorm.io/), or [Prisma](https://www.prisma.io/) can greatly improve development efficiency.
- For building a RESTful API for your application, it is recommended to [use AWS Lambda with API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html).
- For designing high-performance applications using {{{ .starter }}} and AWS Lambda, refer to [this blog](https://aws.amazon.com/blogs/apn/designing-high-performance-applications-using-serverless-tidb-cloud-and-aws-lambda/).
## Next steps

- For more details on how to use TiDB in AWS Lambda Function, see our [TiDB-Lambda-integration/aws-lambda-bookstore Demo](https://github.com/pingcap/TiDB-Lambda-integration/blob/main/aws-lambda-bookstore/README.md). You can also use AWS API Gateway to build a RESTful API for your application.
- Learn more usage of `mysql2` from [the documentation of `mysql2`](https://sidorares.github.io/node-mysql2/docs/documentation).
- Learn more usage of AWS Lambda from [the AWS developer guide of `Lambda`](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
