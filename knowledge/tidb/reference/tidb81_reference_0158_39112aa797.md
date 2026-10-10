# Sequelize connection and CRUD code snippets

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-sequelize.md`
- Source Title: `Connect to TiDB with Sequelize`
- Source Heading Path: `Connect to TiDB with Sequelize > Sample code snippets | Connect to TiDB with Sequelize > Sample code snippets > Connect to TiDB | Connect to TiDB with Sequelize > Sample code snippets > Insert data | Connect to TiDB with Sequelize > Sample code snippets > Query data | Connect to TiDB with Sequelize > Sample code snippets > Update data`
- Source Line Ranges: `205-305`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `sequelize`, `nodejs`, `typescript`, `connection`, `environment-variables`, `ssl`, `crud`, `insert`, `query`, `update`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0158_39112aa797`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-sequelize.md#sample-code-snippets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8fa5ebde2aa7fba886dbdca63209639be46a348dc7d4651ba5555577effcaab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-sequelize#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-sequelize.md

## Retrieval Guidance

- Use When: Use this chunk when you need Sequelize sample code for initializing a TiDB connection from environment variables or for basic create, query, and update operations on the Players model.
- Retrieval Keywords: Sample code snippets, Connect to TiDB, src/lib/tidb.ts, new Sequelize, dialect: 'mysql', process.env.TIDB_HOST, process.env.TIDB_PORT, process.env.TIDB_USER, process.env.TIDB_PASSWORD, process.env.TIDB_DB_NAME, process.env.TIDB_ENABLE_SSL, process.env.TIDB_CA_PATH, minVersion: 'TLSv1.2', rejectUnauthorized: true, sequelize.authenticate(), Connection has been established successfully., Unable to connect to the database:, playersModel.create, findAll, Op.gt, coins > 300, newPlayer.update, Insert data, Query data, Update data
- Follow-up Guidance: The source links to separate TiDB documentation pages for Insert data, Query data, and Update data, and to the tidb-samples/tidb-nodejs-sequelize-quickstart repository for complete runnable code.
- Classification Note: This is classified as a reference chunk because it provides reusable code snippets and exact identifiers for connection setup and CRUD operations rather than a full procedural workflow.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-nodejs-sequelize-quickstart](https://github.com/tidb-samples/tidb-nodejs-sequelize-quickstart) repository.
### Connect to TiDB

The following code establish a connection to TiDB with options defined in the environment variables:

```typescript
// src/lib/tidb.ts
import { Sequelize } from 'sequelize';

export function initSequelize() {
  return new Sequelize({
    dialect: 'mysql',
    host: process.env.TIDB_HOST || 'localhost',     // TiDB host, for example: {gateway-region}.aws.tidbcloud.com
    port: Number(process.env.TIDB_PORT) || 4000,    // TiDB port, default: 4000
    username: process.env.TIDB_USER || 'root',      // TiDB user, for example: {prefix}.root
    password: process.env.TIDB_PASSWORD || 'root',  // TiDB password
    database: process.env.TIDB_DB_NAME || 'test',   // TiDB database name, default: test
    dialectOptions: {
      ssl:
        process.env?.TIDB_ENABLE_SSL === 'true'     // (Optional) Enable SSL
          ? {
              minVersion: 'TLSv1.2',
              rejectUnauthorized: true,
              ca: process.env.TIDB_CA_PATH          // (Optional) Path to the custom CA certificate
                ? readFileSync(process.env.TIDB_CA_PATH)
                : undefined,
            }
          : null,
    },
}

export async function getSequelize() {
  if (!sequelize) {
    sequelize = initSequelize();
    try {
      await sequelize.authenticate();
      logger.info('Connection has been established successfully.');
    } catch (error) {
      logger.error('Unable to connect to the database:');
      logger.error(error);
      throw error;
    }
  }
  return sequelize;
}
```
### Insert data

The following query creates a single `Players` record and returns a `Players` object:

```typescript
logger.info('Creating a new player...');
const newPlayer = await playersModel.create({
  id: 6,
  coins: 600,
  goods: 600,
});
logger.info('Created a new player.');
logger.info(newPlayer.toJSON());
```

For more information, refer to [Insert data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-insert-data).
### Query data

The following query returns a single `Players` record those coins are greater than `300`:

```typescript
logger.info('Reading all players with coins > 300...');
const allPlayersWithCoinsGreaterThan300 = await playersModel.findAll({
  where: {
    coins: {
      [Op.gt]: 300,
    },
  },
});
logger.info('Read all players with coins > 300.');
logger.info(allPlayersWithCoinsGreaterThan300.map((p) => p.toJSON()));
```

For more information, refer to [Query data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-get-data-from-single-table).
### Update data

The following query set `700` coins and `700` goods to the `Players` with ID `6` that was created in the [Insert data](#insert-data) section:

```typescript
logger.info('Updating the new player...');
await newPlayer.update({ coins: 700, goods: 700 });
logger.info('Updated the new player.');
logger.info(newPlayer.toJSON());
```

For more information, refer to [Update data](https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data).
