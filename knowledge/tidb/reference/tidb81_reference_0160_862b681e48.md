# TypeORM connection code snippet and TLS notes

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-nodejs-typeorm.md`
- Source Title: `Connect to TiDB with TypeORM`
- Source Heading Path: `Connect to TiDB with TypeORM > Sample code snippets | Connect to TiDB with TypeORM > Sample code snippets > Connect with connection options`
- Source Line Ranges: `243-282`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `code-snippet`, `datasource`, `connection-options`, `dotenv`, `ssl`, `tls`, `environment-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0160_862b681e48`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-nodejs-typeorm.md#sample-code-snippets`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b9da8123bf5709abdcc8a8145deb8c6f9ca9732c8dedc04fed24d3d2fdd8114a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-nodejs-typeorm#sample-code-snippets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-nodejs-typeorm.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TypeORM `DataSource` example for TiDB, including environment-variable-based connection options and SSL configuration in `src/dataSource.ts`.
- Retrieval Keywords: src/dataSource.ts, DataSource, require('dotenv').config(), type: "mysql", process.env.TIDB_HOST, process.env.TIDB_PORT, process.env.TIDB_USER, process.env.TIDB_PASSWORD, process.env.TIDB_DATABASE, process.env.TIDB_ENABLE_SSL, minVersion: 'TLSv1.2', process.env.TIDB_CA_PATH, fs.readFileSync, entities: [Player, Profile], migrations: [__dirname + "/migrations/**/*{.ts,.js}"], Mozilla CA certificate
- Follow-up Guidance: The note in the source explains that for Starter and Essential public endpoints, `TIDB_ENABLE_SSL` must be set to `true`, and `TIDB_CA_PATH` is not required because Node.js uses the built-in Mozilla CA certificate by default.
- Classification Note: This is classified as a reference chunk because it provides a concrete code snippet and notes describing connection options rather than a full procedure.

## Official Source Content

## Sample code snippets

You can refer to the following sample code snippets to complete your own application development.

For complete sample code and how to run it, check out the [tidb-samples/tidb-nodejs-typeorm-quickstart](https://github.com/tidb-samples/tidb-nodejs-typeorm-quickstart) repository.
### Connect with connection options

The following code establishes a connection to TiDB with options defined in the environment variables:

```typescript
// src/dataSource.ts

// Load environment variables from .env file to process.env.
require('dotenv').config();

export const AppDataSource = new DataSource({
  type: "mysql",
  host: process.env.TIDB_HOST || '127.0.0.1',
  port: process.env.TIDB_PORT ? Number(process.env.TIDB_PORT) : 4000,
  username: process.env.TIDB_USER || 'root',
  password: process.env.TIDB_PASSWORD || '',
  database: process.env.TIDB_DATABASE || 'test',
  ssl: process.env.TIDB_ENABLE_SSL === 'true' ? {
    minVersion: 'TLSv1.2',
    ca: process.env.TIDB_CA_PATH ? fs.readFileSync(process.env.TIDB_CA_PATH) : undefined
  } : null,
  synchronize: process.env.NODE_ENV === 'development',
  logging: false,
  entities: [Player, Profile],
  migrations: [__dirname + "/migrations/**/*{.ts,.js}"],
});
```

> **Note**
>
> For {{{ .starter }}} and {{{ .essential }}}, you MUST enable TLS connection when using public endpoint. In this sample code, please set up the environment variable `TIDB_ENABLE_SSL` in the `.env` file to `true`.
>
> However, you **don't** have to specify an SSL CA certificate via `TIDB_CA_PATH`, because Node.js uses the built-in [Mozilla CA certificate](https://wiki.mozilla.org/CA/Included_Certificates) by default, which is trusted by {{{ .starter }}} and {{{ .essential }}}.
