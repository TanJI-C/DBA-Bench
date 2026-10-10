# Drizzle with TiDB Cloud serverless driver in edge environments

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver-drizzle-example.md`
- Source Title: `TiDB Cloud Serverless Driver Drizzle Tutorial`
- Source Heading Path: `TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in edge environments | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in edge environments > Before you begin | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in edge environments > Step 1. Create a project | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in edge environments > Step 2. Set the environment | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in edge environments > Step 3. Create an edge function | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in edge environments > Step 4. Deploy your code to Vercel | TiDB Cloud Serverless Driver Drizzle Tutorial > What's next`
- Source Line Ranges: `148-272`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `drizzle`, `serverless-driver`, `edge-functions`, `vercel`, `nextjs`, `typescript`, `deployment`, `environment-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0359_c9b89b0beb`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver-drizzle-example.md#use-drizzle-and-tidb-cloud-serverless-driver-in-edge-environments`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d3e5882cc1a4279e2ceca63ba73ab3f986eac1f0e84fd81ba9e696e3eeddcb0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver-drizzle-example#use-drizzle-and-tidb-cloud-serverless-driver-in-edge-environments
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver-drizzle-example.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an edge environment example that uses Drizzle ORM with the TiDB Cloud serverless driver in a Vercel Edge Function and deploys a Next.js route with DATABASE_URL.
- Retrieval Keywords: edge environments, Vercel Edge Function, Next.js, drizzle-example, npm i -g vercel@latest, npx create-next-app@latest drizzle-example --ts --no-eslint --tailwind --no-src-dir --app --import-alias "@/*", drizzle-orm/tidb-serverless, @tidbcloud/serverless, DATABASE_URL, mysql://[username]:[password]@[host]/[database], /api/edge-function-example/route.ts, export const runtime = 'edge', NextResponse, NextRequest, CREATE TABLE `test`.`users`, next dev, http://localhost:3000/api/edge-function-example, vercel -e DATABASE_URL='mysql://[username]:[password]@[host]/[database]' --prod
- Follow-up Guidance: The source points to learning more about Drizzle, drizzle-orm/tidb-serverless, and integrating TiDB Cloud with Vercel.
- Classification Note: This chunk is classified as an operation for the cloud component because it documents procedural setup, local testing, and deployment steps for an edge-function-based integration.

## Official Source Content

## Use Drizzle and TiDB Cloud serverless driver in edge environments

This section takes the Vercel Edge Function as an example.
### Before you begin

To complete this tutorial, you need the following:

- A [Vercel](https://vercel.com/docs) account that provides edge environment.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A TiDB Cloud Serverless cluster. If you don't have any, you can [create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
### Step 1. Create a project

1. Install the Vercel CLI:

    ```shell
    npm i -g vercel@latest
    ```

2. Create a [Next.js](https://nextjs.org/) project called `drizzle-example` using the following terminal command:

   ```shell
   npx create-next-app@latest drizzle-example --ts --no-eslint --tailwind --no-src-dir --app --import-alias "@/*"
   ```

3. Navigate to the `drizzle-example` directory:

   ```shell
   cd drizzle-example
   ```

4. Install the `drizzle-orm` and `@tidbcloud/serverless` packages:

   ```shell
   npm install drizzle-orm @tidbcloud/serverless --force
   ```
### Step 2. Set the environment

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.

2. On the overview page, click **Connect** in the upper-right corner, select `Serverless Driver` in the **Connect With** drop-down list, and then click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, you can either use the original password or click **Reset Password** to generate a new one.

    The connection string looks like this:

    ```
    mysql://[username]:[password]@[host]/[database]
    ```
### Step 3. Create an edge function

1. Create a table in your TiDB Cloud Serverless cluster.

   You can use [SQL Editor in the TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query) to execute SQL statements. Here is an example:

   ```sql
   CREATE TABLE `test`.`users` (
    `id` BIGINT PRIMARY KEY auto_increment,
    `full_name` TEXT,
    `phone` VARCHAR(256)
   );
   ```

2. In the `app` directory of your project, create a file `/api/edge-function-example/route.ts` and add the following code:

   ```ts
   import { NextResponse } from 'next/server';
   import type { NextRequest } from 'next/server';
   import { connect } from '@tidbcloud/serverless';
   import { drizzle } from 'drizzle-orm/tidb-serverless';
   import { mysqlTable, serial, text, varchar } from 'drizzle-orm/mysql-core';
   export const runtime = 'edge';

   // Initialize
   const client = connect({ url: process.env.DATABASE_URL });
   const db = drizzle(client);

   // Define schema
   export const users = mysqlTable('users', {
     id: serial("id").primaryKey(),
     fullName: text('full_name'),
     phone: varchar('phone', { length: 256 }),
   });
   export type User = typeof users.$inferSelect; // return type when queried
   export type NewUser = typeof users.$inferInsert; // insert type

   export async function GET(request: NextRequest) {
     // Insert and select data
     const user: NewUser = { fullName: 'John Doe', phone: '123-456-7890' };
     await db.insert(users).values(user)
     const result: User[] = await db.select().from(users);
     return NextResponse.json(result);
   }
   ```

3. Test your code locally:

   ```shell
   export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
   next dev
   ```

4. Navigate to `http://localhost:3000/api/edge-function-example` to get the response from your route.
### Step 4. Deploy your code to Vercel

1. Deploy your code to Vercel with the `DATABASE_URL` environment variable:

   ```shell
   vercel -e DATABASE_URL='mysql://[username]:[password]@[host]/[database]' --prod
   ```

   After the deployment is complete, you will get the URL of your project.

2. Navigate to the `${Your-URL}/api/edge-function-example` page to get the response from your route.
## What's next

- Learn more about [Drizzle](https://orm.drizzle.team/docs/overview) and [drizzle-orm/tidb-serverless](https://orm.drizzle.team/docs/get-started-mysql#tidb-serverless).
- Learn how to [integrate TiDB Cloud with Vercel](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel).
