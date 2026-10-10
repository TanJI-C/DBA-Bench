# Drizzle with TiDB Cloud serverless driver in Node.js

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver-drizzle-example.md`
- Source Title: `TiDB Cloud Serverless Driver Drizzle Tutorial`
- Source Heading Path: `TiDB Cloud Serverless Driver Drizzle Tutorial | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in Node.js environments | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in Node.js environments > Before you begin | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in Node.js environments > Step 1. Create a project | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in Node.js environments > Step 2. Set the environment | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in Node.js environments > Step 3. Use Drizzle to query data | TiDB Cloud Serverless Driver Drizzle Tutorial > Use Drizzle and TiDB Cloud serverless driver in Node.js environments > Step 4. Run the Typescript code`
- Source Line Ranges: `5-147`
- Source Scope: `developer`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `drizzle`, `serverless-driver`, `nodejs`, `typescript`, `environment-variables`, `project-setup`, `sql-query`, `ts-node`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0358_87c83bde0f`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver-drizzle-example.md#tidb-cloud-serverless-driver-drizzle-tutorial`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd2b3eecc51b42e4026438963289b0c7d7f3a4077a84ff959e1d88a26e687cff`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver-drizzle-example#tidb-cloud-serverless-driver-drizzle-tutorial
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver-drizzle-example.md

## Retrieval Guidance

- Use When: Use this chunk when looking for a Node.js and TypeScript tutorial that connects Drizzle ORM to TiDB Cloud through the TiDB Cloud serverless driver, sets DATABASE_URL, creates a users table, and runs hello-world.ts with ts-node.
- Retrieval Keywords: Drizzle ORM, TiDB Cloud serverless driver, Node.js environments, drizzle-orm/tidb-serverless, @tidbcloud/serverless, DATABASE_URL, mysql://[username]:[password]@[host]/[database], drizzle-node-example, package.json, "type": "module", tsconfig.json, CREATE TABLE `test`.`users`, hello-world.ts, connect({ url: process.env.DATABASE_URL }), db.insert(users).values(user), db.select().from(users), ts-node --esm hello-world.ts, @types/node
- Follow-up Guidance: The source continues with a separate section for using Drizzle and the TiDB Cloud serverless driver in edge environments.
- Classification Note: This chunk is classified as an operation for the cloud component because it provides step-by-step project setup, environment configuration, SQL table creation, and query execution instructions in a developer workflow.

## Official Source Content

# TiDB Cloud Serverless Driver Drizzle Tutorial

[Drizzle ORM](https://orm.drizzle.team/) is a lightweight and performant TypeScript ORM with developer experience in mind. Starting from `drizzle-orm@0.31.2`, it supports [drizzle-orm/tidb-serverless](https://orm.drizzle.team/docs/get-started-mysql#tidb-serverless), enabling you to use Drizzle over HTTPS with [TiDB Cloud serverless driver](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver).

This tutorial describes how to use TiDB Cloud serverless driver with Drizzle in Node.js environments and edge environments.
## Use Drizzle and TiDB Cloud serverless driver in Node.js environments

This section describes how to use TiDB Cloud serverless driver with Drizzle in Node.js environments.
### Before you begin

To complete this tutorial, you need the following:

- [Node.js](https://nodejs.org/en) >= 18.0.0.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A TiDB Cloud Serverless cluster. If you don't have any, you can [create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
### Step 1. Create a project

1. Create a project named `drizzle-node-example`:

    ```shell
    mkdir drizzle-node-example
    cd drizzle-node-example
    ```

2. Install the `drizzle-orm` and `@tidbcloud/serverless` packages:

   ```shell
   npm install drizzle-orm @tidbcloud/serverless
   ```

3. In the root directory of your project, locate the `package.json` file, and then specify the ES module by adding `"type": "module"` to the file:

   ```json
   {
     "type": "module",
     "dependencies": {
       "@tidbcloud/serverless": "^0.1.1",
       "drizzle-orm": "^0.31.2"
     }
   }
   ```

4. In the root directory of your project, add a `tsconfig.json` file to define the TypeScript compiler options. Here is an example file:

   ```json
   {
     "compilerOptions": {
       "module": "ES2022",
       "target": "ES2022",
       "moduleResolution": "node",
       "strict": false,
       "declaration": true,
       "outDir": "dist",
       "removeComments": true,
       "allowJs": true,
       "esModuleInterop": true,
       "resolveJsonModule": true
     }
   }
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

3. Set the environment variable `DATABASE_URL` in your local environment. For example, in Linux or macOS, you can run the following command:

    ```shell
    export DATABASE_URL='mysql://[username]:[password]@[host]/[database]'
    ```
### Step 3. Use Drizzle to query data

1. Create a table in your TiDB Cloud Serverless cluster.

   You can use [SQL Editor in the TiDB Cloud console](https://docs.pingcap.com/tidb/stable/tidb-cloud/explore-data-with-chat2query) to execute SQL statements. Here is an example:

   ```sql
   CREATE TABLE `test`.`users` (
    `id` BIGINT PRIMARY KEY auto_increment,
    `full_name` TEXT,
    `phone` VARCHAR(256)
   );
   ```

2. In the root directory of your project, create a file named `hello-world.ts` and add the following code:

   ```ts
   import { connect } from '@tidbcloud/serverless';
   import { drizzle } from 'drizzle-orm/tidb-serverless';
   import { mysqlTable, serial, text, varchar } from 'drizzle-orm/mysql-core';

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

   // Insert and select data
   const user: NewUser = { fullName: 'John Doe', phone: '123-456-7890' };
   await db.insert(users).values(user)
   const result: User[] = await db.select().from(users);
   console.log(result);
   ```
### Step 4. Run the Typescript code

1. Install `ts-node` to transform TypeScript into JavaScript, and then install `@types/node` to provide TypeScript type definitions for Node.js.

   ```shell
   npm install -g ts-node
   npm i --save-dev @types/node
   ```

2. Run the Typescript code with the following command:

   ```shell
   ts-node --esm hello-world.ts
   ```
