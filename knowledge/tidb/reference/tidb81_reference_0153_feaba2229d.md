# mysql.js connection and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-mysqljs.md`
- Source Title: `Connect to TiDB with mysql.js`
- Source Heading Path: `Connect to TiDB with mysql.js > Sample code snippets | Connect to TiDB with mysql.js > Sample code snippets > Connect with connection options | Connect to TiDB with mysql.js > Sample code snippets > Insert data | Connect to TiDB with mysql.js > Sample code snippets > Query data | Connect to TiDB with mysql.js > Sample code snippets > Update data | Connect to TiDB with mysql.js > Sample code snippets > Delete data`
- Source Line Ranges: `204-314`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `shared`
- Topic Tags: `nodejs`, `mysqljs`, `code-snippets`, `connection-options`, `dotenv`, `tls`, `crud`, `insert`, `query`, `update`, `delete`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0153_feaba2229d`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-mysqljs.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e5f2bfaac50ecde2df8692cc17b3af0fb3a468437fb269458a4b8f83ad20574`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-mysqljs#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-mysqljs.md

## Retrieval Guidance

- Use When: Use this chunk when you need mysql.js code examples for creating a TiDB connection from environment variables or basic CRUD SQL statements in Node.js.
- Retrieval Keywords: Sample code snippets, createConnection, dotenv.config(), process.env.TIDB_HOST, process.env.TIDB_PORT, process.env.TIDB_USER, process.env.TIDB_PASSWORD, process.env.TIDB_DATABASE, process.env.TIDB_ENABLE_SSL, minVersion: 'TLSv1.2', process.env.TIDB_CA_PATH, fs.readFileSync, conn.end(), INSERT INTO players (coins, goods) VALUES (?, ?), ok.insertId, SELECT id, coins, goods FROM players WHERE id = ?, UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?, ok.affectedRows, DELETE FROM players WHERE id = ?, Player
- Follow-up Guidance: The source also points to the `tidb-samples/tidb-nodejs-mysqljs-quickstart` repository and to separate Insert data, Query data, Update data, and Delete data documentation pages for more information.
- Classification Note: This is classified as reference content because it supplies reusable mysql.js connection options and CRUD code snippets with exact SQL statements and environment variable names.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-nodejs-mysqljs-quickstart](https://github.com/tidb-samples/tidb-nodejs-mysqljs-quickstart) repository.
### Connect with connection options

The following code establishes a connection to TiDB with options defined in the environment variables:

```javascript
// Step 1. Import the 'mysql' and 'dotenv' packages.
import { createConnection } from "mysql";
import dotenv from "dotenv";
import * as fs from "fs";

// Step 2. Load environment variables from .env file to process.env.
dotenv.config();

// Step 3. Create a connection to the TiDB cluster.
const options = {
    host: process.env.TIDB_HOST || '127.0.0.1',
    port: process.env.TIDB_PORT || 4000,
    user: process.env.TIDB_USER || 'root',
    password: process.env.TIDB_PASSWORD || '',
    database: process.env.TIDB_DATABASE || 'test',
    ssl: process.env.TIDB_ENABLE_SSL === 'true' ? {
        minVersion: 'TLSv1.2',
        ca: process.env.TIDB_CA_PATH ? fs.readFileSync(process.env.TIDB_CA_PATH) : undefined
    } : null,
}
const conn = createConnection(options);

// Step 4. Perform some SQL operations...

// Step 5. Close the connection.
conn.end();
```

> **Note**
>
> For {{{ .starter }}} and {{{ .essential }}}, you **MUST** enable TLS connection via `TIDB_ENABLE_SSL` when using public endpoint. However, you **don't** have to specify an SSL CA certificate via `TIDB_CA_PATH`, because Node.js uses the built-in [Mozilla CA certificate](https://wiki.mozilla.org/CA/Included_Certificates) by default, which is trusted by {{{ .starter }}}.
### Insert data

The following query creates a single `Player` record and returns the ID of the newly created record:

```javascript
conn.query('INSERT INTO players (coins, goods) VALUES (?, ?);', [100, 100], (err, ok) => {
   if (err) {
       console.error(err);
   } else {
       console.log(ok.insertId);
   }
});
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

The following query returns a single `Player` record by ID `1`:

```javascript
conn.query('SELECT id, coins, goods FROM players WHERE id = ?;', [1], (err, rows) => {
   if (err) {
      console.error(err);
   } else {
      console.log(rows[0]);
   }
});
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

The following query adds `50` coins and `50` goods to the `Player` with ID `1`:

```javascript
conn.query(
   'UPDATE players SET coins = coins + ?, goods = goods + ? WHERE id = ?;',
   [50, 50, 1],
   (err, ok) => {
      if (err) {
         console.error(err);
      } else {
          console.log(ok.affectedRows);
      }
   }
);
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
### Delete data

The following query deletes the `Player` record with ID `1`:

```javascript
conn.query('DELETE FROM players WHERE id = ?;', [1], (err, ok) => {
    if (err) {
        reject(err);
    } else {
        resolve(ok.affectedRows);
    }
});
```

For more information, refer to [Delete data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data).
