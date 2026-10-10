# Deploy Cloudflare Workers with the TiDB Cloud serverless driver

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-cloudflare.md`
- Source Title: `Integrate TiDB Cloud with Cloudflare`
- Source Heading Path: `Integrate TiDB Cloud with Cloudflare Workers | Integrate TiDB Cloud with Cloudflare Workers > Before you begin | Integrate TiDB Cloud with Cloudflare Workers > Step 1: Set up Wrangler | Integrate TiDB Cloud with Cloudflare Workers > Step 2: Install the serverless driver | Integrate TiDB Cloud with Cloudflare Workers > Step 3: Develop the Cloudflare Worker function | Integrate TiDB Cloud with Cloudflare Workers > Step 4: Set the DATABASE_URL in your environment | Integrate TiDB Cloud with Cloudflare Workers > Step 5: Publish to Cloudflare Workers | Integrate TiDB Cloud with Cloudflare Workers > Step 6: Try your Cloudflare Workers | Integrate TiDB Cloud with Cloudflare Workers > Examples`
- Source Line Ranges: `5-117`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `cloudflare-workers`, `serverless-driver`, `wrangler`, `deployment`, `environment-variables`, `http-connection`, `worker-function`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0233_a1d82a1a7a`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-cloudflare.md#integrate-tidb-cloud-with-cloudflare-workers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `addfa475adcf6ca796c4588334c4aff1e823cc09c92b1f349db3d2f7c96565d4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-cloudflare#integrate-tidb-cloud-with-cloudflare-workers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-cloudflare.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about connecting Cloudflare Workers to TiDB Cloud Serverless with the TiDB Cloud serverless driver over HTTP, including Wrangler setup, DATABASE_URL configuration, and publishing the worker.
- Retrieval Keywords: Cloudflare Workers, TiDB Cloud serverless driver, @tidbcloud/serverless, Wrangler, wrangler init tidb-cloud-cloudflare, wrangler login, npm install wrangler, npm install @tidbcloud/serverless, DATABASE_URL, mysql://username:password@host/database, wrangler secret put <DATABASE_URL>, npx wrangler publish, show databases, src/index.ts, connect({url:env.DATABASE_URL}), HTTP connection, V8 engine cannot make direct TCP connections, TiDB Cloud Serverless
- Follow-up Guidance: The source also includes an example Worker function in src/index.ts that executes "show databases" and notes a Cloudflare Workers example repository.
- Classification Note: This is classified as configuration because the content provides the setup flow and required settings to deploy a Cloudflare Worker that uses the TiDB Cloud serverless driver, including environment variables and publish commands.

## Official Source Content

# Integrate TiDB Cloud with Cloudflare Workers

[Cloudflare Workers](https://workers.cloudflare.com/) is a platform that allows you to run code in response to specific events, such as HTTP requests or changes to a database. Cloudflare Workers is easy to use and can be used to build a variety of applications, including custom APIs, serverless functions, and microservices. It is particularly useful for applications that require low-latency performance or need to scale quickly.

You may find it hard to connect to TiDB Cloud from Cloudflare Workers because Cloudflare Workers runs on the V8 engine which cannot make direct TCP connections. You can use [TiDB Cloud serverless driver](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver) to help you connect to Cloudflare Workers over HTTP connection.

This document shows how to connect to Cloudflare Workers with TiDB Cloud serverless driver step by step.

> **Note:**
>
> TiDB Cloud serverless driver can only be used in TiDB Cloud Serverless.
## Before you begin

Before you try the steps in this article, you need to prepare the following things:

- A TiDB Cloud account and a TiDB Cloud Serverless cluster on TiDB Cloud. For more details, see [TiDB Cloud Quick Start](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart#step-1-create-a-tidb-cluster).
- A [Cloudflare Workers account](https://dash.cloudflare.com/login).
- [npm](https://docs.npmjs.com/about-npm) is installed.
## Step 1: Set up Wrangler

[Wrangler](https://developers.cloudflare.com/workers/wrangler/) is the official Cloudflare Worker CLI. You can use it to generate, build, preview, and publish your Workers.

1. Install Wrangler:

   ```
   npm install wrangler
   ```

2. To authenticate Wrangler, run wrangler login:

    ```
    wrangler login
    ```

3. Use Wrangler to create a worker project:

    ```
    wrangler init tidb-cloud-cloudflare
    ```

4. In your terminal, you will be asked a series of questions related to your project. Choose the default values for all questions.
## Step 2: Install the serverless driver

1. Enter your project directory:

    ```
    cd tidb-cloud-cloudflare
    ```

2. Install the serverless driver with npm:

    ```
    npm install @tidbcloud/serverless
    ```

   This adds the serverless driver dependency in `package.json`.
## Step 3: Develop the Cloudflare Worker function

You need to modify the `src/index.ts` according to your needs.

For example, if you want to show all the databases, you can use the following code:

```ts
import { connect } from '@tidbcloud/serverless'


export interface Env {
   DATABASE_URL: string;
}

export default {
   async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
      const conn = connect({url:env.DATABASE_URL})
      const resp = await conn.execute("show databases")
      return new Response(JSON.stringify(resp));
   },
};
```
## Step 4: Set the DATABASE_URL in your environment

The `DATABASE_URL` follows the `mysql://username:password@host/database` format. You can set the environment variable with wrangler cli:

```
wrangler secret put <DATABASE_URL>
```

You can also edit the `DATABASE_URL` secret via the Cloudflare Workers dashboard.
## Step 5: Publish to Cloudflare Workers

You're now ready to deploy to Cloudflare Workers.

In your project directory, run the following command:

```
npx wrangler publish
```
## Step 6: Try your Cloudflare Workers

1. Go to [Cloudflare dashboard](https://dash.cloudflare.com) to find your worker. You can find the URL of your worker on the overview page.

2. Visit the URL and you will get the result.
## Examples

See the [Cloudflare Workers example](https://github.com/tidbcloud/car-sales-insight/tree/main/examples/cloudflare-workers).
