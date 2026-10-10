# Kysely serverless driver tutorial for edge environments

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver-kysely-example.md`
- Source Title: `TiDB Cloud Serverless Driver Kysely Tutorial`
- Source Heading Path: `TiDB Cloud Serverless Driver Kysely Tutorial > Use TiDB Cloud Kysely dialect in edge environments | TiDB Cloud Serverless Driver Kysely Tutorial > Use TiDB Cloud Kysely dialect in edge environments > Before you begin | TiDB Cloud Serverless Driver Kysely Tutorial > Use TiDB Cloud Kysely dialect in edge environments > Step 1. Create a project | TiDB Cloud Serverless Driver Kysely Tutorial > Use TiDB Cloud Kysely dialect in edge environments > Step 2. Set the environment | TiDB Cloud Serverless Driver Kysely Tutorial > Use TiDB Cloud Kysely dialect in edge environments > Step 3. Create an edge function | TiDB Cloud Serverless Driver Kysely Tutorial > Use TiDB Cloud Kysely dialect in edge environments > Step 4. Deploy your code to Vercel | TiDB Cloud Serverless Driver Kysely Tutorial > What's next`
- Source Line Ranges: `159-299`
- Source Scope: `developer`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `kysely`, `serverless-driver`, `edge-functions`, `vercel`, `next.js`, `typescript`, `environment-variables`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0361_ebe6867ebb`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver-kysely-example.md#use-tidb-cloud-kysely-dialect-in-edge-environments`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d64df712bd1d6ec01c82f123711eca4a32818185e07c425afa0e43b3191ab060`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver-kysely-example#use-tidb-cloud-kysely-dialect-in-edge-environments
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver-kysely-example.md

## Retrieval Guidance

- Use When: Use this chunk when you need the edge environment tutorial for using the TiDB Cloud Kysely dialect in a Vercel Edge Function with Next.js, including local testing and deployment.
- Retrieval Keywords: Use TiDB Cloud Kysely dialect in edge environments, Vercel Edge Function, Next.js, vercel@latest, npx create-next-app@latest kysely-example --ts --no-eslint --tailwind --no-src-dir --app --import-alias "@/*", npm install kysely @tidbcloud/kysely @tidbcloud/serverless, DATABASE_URL, mysql://[username]:[password]@[host]/[database], /api/edge-function-example/route.ts, export const runtime = 'edge', NextResponse, NextRequest, TiDBServerlessDialect, process.env.DATABASE_URL, query parameter `query`, next dev, http://localhost:3000/api/edge-function-example, vercel -e DATABASE_URL='mysql://[username]:[password]@[host]/[database]' --prod, ${Your-URL}/api/edge-function-example
- Follow-up Guidance: The source also points to Kysely, @tidbcloud/kysely, and integrating TiDB Cloud with Vercel in the What's next section.
- Classification Note: The content is classified as an operation chunk because it provides a procedural example for creating, testing, and deploying an edge function that queries TiDB Cloud with Kysely.

## Official Source Content

## Use TiDB Cloud Kysely dialect in edge environments

This section takes the TiDB Cloud Kysely dialect in Vercel Edge Function as an example.
### Before you begin

To complete this tutorial, you need the following:

- A [Vercel](https://vercel.com/docs) account that provides edge environment.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A TiDB Cloud Serverless cluster. If you don't have any, you can [create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
### Step 1. Create a project

1. Install the Vercel CLI:

    ```
    npm i -g vercel@latest
    ```

2. Create a [Next.js](https://nextjs.org/) project called `kysely-example` using the following terminal commands:

   ```
   npx create-next-app@latest kysely-example --ts --no-eslint --tailwind --no-src-dir --app --import-alias "@/*"
   cd kysely-example
   ```
   
3. Install the `kysely`, `@tidbcloud/kysely`, and `@tidbcloud/serverless` packages:

   ```
   npm install kysely @tidbcloud/kysely @tidbcloud/serverless
   ```
### Step 2. Set the environment

On the overview page of your TiDB Cloud Serverless cluster, click **Connect** in the upper-right corner, and then get the connection string for your database from the displayed dialog. The connection string looks like this:

```
mysql://[username]:[password]@[host]/[database]
```
### Step 3. Create an edge function

1. Create a table in your TiDB Cloud Serverless cluster and insert some data.

    You can use [SQL Editor in the TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query) to execute SQL statements. Here is an example:

   ```sql
   CREATE TABLE `test`.`person`  (
     `id` int(11) NOT NULL AUTO_INCREMENT,
     `name` varchar(255) NULL DEFAULT NULL,
     `gender` enum('male','female') NULL DEFAULT NULL,
     PRIMARY KEY (`id`) USING BTREE
   );
   
   insert into test.person values (1,'pingcap','male')
   ```

2. In the `app` directory of your project, create a file `/api/edge-function-example/route.ts` and add the following code:

   ```ts
   import { NextResponse } from 'next/server';
   import type { NextRequest } from 'next/server';
   import { Kysely,GeneratedAlways,Selectable } from 'kysely'
   import { TiDBServerlessDialect } from '@tidbcloud/kysely'
   
   export const runtime = 'edge';
   
   // Types
   interface Database {
     person: PersonTable
   }
   
   interface PersonTable {
     id: GeneratedAlways<number>
     name: string
     gender: "male" | "female" | "other"
   }
   
   // Dialect
   const db = new Kysely<Database>({
     dialect: new TiDBServerlessDialect({
       url: process.env.DATABASE_URL
     }),
   })
   
   // Query
   type Person = Selectable<PersonTable>
   async function findPeople(criteria: Partial<Person> = {}) {
     let query = db.selectFrom('person')
   
     if (criteria.name){
       query = query.where('name', '=', criteria.name)
     }
   
     return await query.selectAll().execute()
   }
   
   export async function GET(request: NextRequest) {
   
     const searchParams = request.nextUrl.searchParams
     const query = searchParams.get('query')
   
     let response = null;
     if (query) {
       response = await findPeople({name: query})
     } else {
       response = await findPeople()
     }
   
     return NextResponse.json(response);
   }
   ```
   
   The preceding code accepts a query parameter `query` and returns the result of the query. If the query parameter is not provided, it returns all records in the `person` table.

3. Test your code locally:

   ```
   export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
   next dev
   ```
   
4. Navigate to `http://localhost:3000/api/edge-function-example` to get the response from your route.
### Step 4. Deploy your code to Vercel

1. Deploy your code to Vercel with the `DATABASE_URL` environment variable:

   ```
   vercel -e DATABASE_URL='mysql://[username]:[password]@[host]/[database]' --prod
   ```

    After the deployment is complete, you will get the URL of your project. 

2. Navigate to the `${Your-URL}/api/edge-function-example` page to get the response from your route.
## What's next

- Learn more about [Kysely](https://kysely.dev/docs/intro) and [@tidbcloud/kysely](https://github.com/tidbcloud/kysely)
- Learn how to [integrate TiDB Cloud with Vercel](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel)
