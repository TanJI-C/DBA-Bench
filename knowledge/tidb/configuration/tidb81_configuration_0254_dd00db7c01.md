# Prisma adapter installation and client initialization

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver-prisma-example.md`
- Source Title: `TiDB Cloud Serverless Driver Prisma Tutorial`
- Source Heading Path: `TiDB Cloud Serverless Driver Prisma Tutorial | TiDB Cloud Serverless Driver Prisma Tutorial > Install | TiDB Cloud Serverless Driver Prisma Tutorial > Enable `driverAdapters` | TiDB Cloud Serverless Driver Prisma Tutorial > Initialize Prisma Client`
- Source Line Ranges: `5-71`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `shared`
- Topic Tags: `prisma`, `serverless-driver`, `installation`, `driveradapters`, `schema`, `client-initialization`, `https`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0254_dd00db7c01`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver-prisma-example.md#tidb-cloud-serverless-driver-prisma-tutorial`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf85009a9bb3f9795eb789c374c24d411cd0e700bc3d370d1770229296600177`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver-prisma-example#tidb-cloud-serverless-driver-prisma-tutorial
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver-prisma-example.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to install @tidbcloud/prisma-adapter and @tidbcloud/serverless, enable the driverAdapters preview feature in schema.prisma, or initialize PrismaClient with PrismaTiDBCloud over HTTPS.
- Retrieval Keywords: @tidbcloud/prisma-adapter, @tidbcloud/serverless, driverAdapters, schema.prisma, previewFeatures = ["driverAdapters"], PrismaTiDBCloud, PrismaClient, connect({ url: ${DATABASE_URL} }), const adapter = new PrismaTiDBCloud({ url: ${DATABASE_URL} }), Prisma Client over HTTPS, serverless environments, edge environments
- Follow-up Guidance: The chunk also distinguishes initialization for @tidbcloud/prisma-adapter earlier than v6.6.0 versus v6.6.0 or later.
- Classification Note: This is classified as configuration because the content covers package installation, schema.prisma settings, and Prisma Client initialization code.

## Official Source Content

# TiDB Cloud Serverless Driver Prisma Tutorial

[Prisma](https://www.prisma.io/docs) is an open source next-generation ORM (Object-Relational Mapping) that helps developers interact with their database in an intuitive, efficient, and safe way. TiDB Cloud offers [@tidbcloud/prisma-adapter](https://github.com/tidbcloud/prisma-adapter), enabling you to use [Prisma Client](https://www.prisma.io/docs/concepts/components/prisma-client) over HTTPS with [TiDB Cloud serverless driver](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver). Compared with the traditional TCP way, [@tidbcloud/prisma-adapter](https://github.com/tidbcloud/prisma-adapter) brings the following benefits:

- Better performance of Prisma Client in serverless environments
- Ability to use Prisma Client in edge environments

This tutorial describes how to use [@tidbcloud/prisma-adapter](https://github.com/tidbcloud/prisma-adapter) in serverless environments and edge environments.
## Install

You need to install both [@tidbcloud/prisma-adapter](https://github.com/tidbcloud/prisma-adapter) and [TiDB Cloud serverless driver](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver). You can install them using [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.

Taking npm as an example, you can run the following commands for installation:

```shell
npm install @tidbcloud/prisma-adapter
npm install @tidbcloud/serverless
```
## Enable `driverAdapters`

To use the Prisma adapter, you need to enable the `driverAdapters` feature in the `schema.prisma` file. For example:

```prisma
generator client {
  provider        = "prisma-client-js"
  previewFeatures = ["driverAdapters"]
}

datasource db {
  provider     = "mysql"
  url          = env("DATABASE_URL")
}
```
## Initialize Prisma Client

Before using Prisma Client, you need to initialize it with `@tidbcloud/prisma-adapter`. 

For `@tidbcloud/prisma-adapter` earlier than v6.6.0: 

```js
import { connect } from '@tidbcloud/serverless';
import { PrismaTiDBCloud } from '@tidbcloud/prisma-adapter';
import { PrismaClient } from '@prisma/client';

// Initialize Prisma Client
const connection = connect({ url: ${DATABASE_URL} });
const adapter = new PrismaTiDBCloud(connection);
const prisma = new PrismaClient({ adapter });
```

For `@tidbcloud/prisma-adapter` v6.6.0 or a later version: 

```js
import { PrismaTiDBCloud } from '@tidbcloud/prisma-adapter';
import { PrismaClient } from '@prisma/client';

// Initialize Prisma Client
const adapter = new PrismaTiDBCloud({ url: ${DATABASE_URL} });
const prisma = new PrismaClient({ adapter });
```

Then, queries from Prisma Client can be sent to the TiDB Cloud serverless driver for processing.
