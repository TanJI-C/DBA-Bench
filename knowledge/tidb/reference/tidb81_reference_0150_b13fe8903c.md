# mysql2 code snippets and developer notes for TiDB in Next.js

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nextjs.md`
- Source Title: `Connect to TiDB with mysql2 in Next.js`
- Source Heading Path: `Connect to TiDB with mysql2 in Next.js > Sample code snippets | Connect to TiDB with mysql2 in Next.js > Sample code snippets > Connect to TiDB | Connect to TiDB with mysql2 in Next.js > Sample code snippets > Insert data | Connect to TiDB with mysql2 in Next.js > Sample code snippets > Query data | Connect to TiDB with mysql2 in Next.js > Sample code snippets > Update data | Connect to TiDB with mysql2 in Next.js > Sample code snippets > Delete data | Connect to TiDB with mysql2 in Next.js > Useful notes | Connect to TiDB with mysql2 in Next.js > Next steps | Connect to TiDB with mysql2 in Next.js > Need help?`
- Source Line Ranges: `183-296`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`, `shared`
- Topic Tags: `code-snippets`, `connection-pool`, `crud`, `insert`, `select`, `update`, `delete`, `prepared-statements`, `orm`, `developer-guide`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0150_b13fe8903c`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nextjs.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7763f5bb4dc8b54dad352d51b1a93712f06b692ea8dc13662463b8d3492aa9dc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nextjs#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nextjs.md

## Retrieval Guidance

- Use When: Use this chunk when you need official mysql2 code examples for Next.js with TiDB, including pool creation, TLS options, CRUD SQL statements, and developer notes about connection pools or prepared statements.
- Retrieval Keywords: Sample code snippets, Connect to TiDB, src/lib/tidb.js, mysql.createPool, ssl minVersion TLSv1.2, rejectUnauthorized true, connectionLimit: 1, maxIdle: 1, enableKeepAlive: true, INSERT INTO players (coins, goods) VALUES (?, ?), SELECT id, coins, goods FROM players WHERE id = ?, UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?, DELETE FROM players WHERE id = ?, ResultSetHeader, connection pools, prepared statements, Sequelize, TypeORM, Prisma, Bookshop Demo, node-mysql2 documentation
- Follow-up Guidance: The source points to next steps including the Bookshop Demo, node-mysql2 documentation, the TiDB Developer guide, and community help through Discord, Slack, or a support ticket.
- Classification Note: This is classified as reference because the content mainly provides reusable code snippets, SQL examples, and related notes and links rather than a procedural setup workflow.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-nextjs-vercel-quickstart](https://github.com/tidb-samples/tidb-nextjs-vercel-quickstart) repository.
### Connect to TiDB

The following code establish a connection to TiDB with options defined in the environment variables:

```javascript
// src/lib/tidb.js
import mysql from 'mysql2';

let pool = null;

export function connect() {
  return mysql.createPool({
    host: process.env.TIDB_HOST, // TiDB host, for example: {gateway-region}.aws.tidbcloud.com
    port: process.env.TIDB_PORT || 4000, // TiDB port, default: 4000
    user: process.env.TIDB_USER, // TiDB user, for example: {prefix}.root
    password: process.env.TIDB_PASSWORD, // The password of TiDB user.
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

export function getPool() {
  if (!pool) {
    pool = createPool();
  }
  return pool;
}
```
### Insert data

The following query creates a single `Player` record and returns a `ResultSetHeader` object:

```javascript
const [rsh] = await pool.query('INSERT INTO players (coins, goods) VALUES (?, ?);', [100, 100]);
console.log(rsh.insertId);
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

The following query returns a single `Player` record by ID `1`:

```javascript
const [rows] = await pool.query('SELECT id, coins, goods FROM players WHERE id = ?;', [1]);
console.log(rows[0]);
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

The following query adds `50` coins and `50` goods to the `Player` with ID `1`:

```javascript
const [rsh] = await pool.query(
    'UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?;',
    [50, 50, 1]
);
console.log(rsh.affectedRows);
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

The following query deletes the `Player` record with ID `1`:

```javascript
const [rsh] = await pool.query('DELETE FROM players WHERE id = ?;', [1]);
console.log(rsh.affectedRows);
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
## Useful notes

- Using [connection pools](https://github.com/sidorares/node-mysql2#using-connection-pools) to manage database connections can reduce the performance overhead caused by frequently establishing and destroying connections.
- To avoid SQL injection, it is recommended to use [prepared statements](https://github.com/sidorares/node-mysql2#using-prepared-statements).
- In scenarios where there are not many complex SQL statements involved, using ORM frameworks like [Sequelize](https://sequelize.org/), [TypeORM](https://typeorm.io/), or [Prisma](https://www.prisma.io/) can greatly improve development efficiency.
## Next steps

- For more details on how to build a complex application with ORM and Next.js, see [our Bookshop Demo](https://github.com/pingcap/tidb-prisma-vercel-demo).
- Learn more usage of node-mysql2 driver from [the documentation of node-mysql2](https://sidorares.github.io/node-mysql2/docs/documentation).
- Learn the best practices for TiDB application development with the chapters in the [Developer guide](https://docs.pingcap.com/tidb/stable/develop/dev-guide-overview), such as [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data), [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data), [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data), [Single table reading](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table), [Transactions](https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview), and [SQL performance optimization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-optimize-sql-overview).
- Learn through the professional [TiDB developer courses](https://www.pingcap.com/education/) and earn [TiDB certifications](https://www.pingcap.com/education/certification/) after passing the exam.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
