# Serverless driver overview, installation, usage, and edge examples

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver.md`
- Source Title: `TiDB Cloud Serverless Driver (Beta)`
- Source Heading Path: `TiDB Cloud Serverless Driver (Beta) | TiDB Cloud Serverless Driver (Beta) > Why use TiDB Cloud Serverless Driver (Beta) | TiDB Cloud Serverless Driver (Beta) > Install the serverless driver | TiDB Cloud Serverless Driver (Beta) > Use the serverless driver | TiDB Cloud Serverless Driver (Beta) > Use the serverless driver > Query | TiDB Cloud Serverless Driver (Beta) > Use the serverless driver > Transaction (experimental) | TiDB Cloud Serverless Driver (Beta) > Edge examples`
- Source Line Ranges: `6-146`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `serverless`, `edge`, `http-connection`, `installation`, `query`, `transaction`, `javascript`, `vercel`, `cloudflare`, `netlify`, `deno`, `bun`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0255_2950afb73a`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver.md#tidb-cloud-serverless-driver-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cedcf57756e10ec1ccec89943ac00f2d04c008d666d878a7150e4a71f7647b78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver#tidb-cloud-serverless-driver-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver.md

## Retrieval Guidance

- Use When: Use this chunk when looking for what TiDB Cloud Serverless Driver (Beta) is for, how to install `@tidbcloud/serverless`, how to run a query or interactive transaction with `connect`, or how to use it in edge environments such as Vercel Edge Functions and Cloudflare Workers.
- Retrieval Keywords: TiDB Cloud Serverless Driver (Beta), @tidbcloud/serverless, npm install @tidbcloud/serverless, connect({url: 'mysql://[username]:[password]@[host]/[database]'}), conn.execute, begin(), commit(), rollback(), interactive transactions, Transaction (experimental), HTTP connection, serverless functions, edge environments, Vercel Edge Functions, Cloudflare Workers, Netlify Edge Function, Deno, Bun, show tables, Data Service (beta)
- Follow-up Guidance: The source also provides edge code examples for Vercel, Cloudflare Workers, Netlify Edge Function, Deno, and Bun, and links to Vercel, Cloudflare, Netlify, and a live demo.
- Classification Note: This is classified as configuration because the content explains installation and usage patterns for configuring and using the serverless driver connection and runtime examples in TiDB Cloud.

## Official Source Content

# TiDB Cloud Serverless Driver (Beta)
## Why use TiDB Cloud Serverless Driver (Beta)

Traditional TCP-based MySQL drivers are not suitable for serverless functions due to their expectation of long-lived, persistent TCP connections, which contradict the short-lived nature of serverless functions. Moreover, in edge environments such as [Vercel Edge Functions](https://vercel.com/docs/functions/edge-functions) and [Cloudflare Workers](https://workers.cloudflare.com/), where comprehensive TCP support and full Node.js compatibility may be lacking, these drivers may not work at all.

[TiDB Cloud serverless driver (Beta)](https://github.com/tidbcloud/serverless-js) for JavaScript allows you to connect to your TiDB Cloud Serverless cluster over HTTP, which is generally supported by serverless environments. With it, it is now possible to connect to TiDB Cloud Serverless clusters from edge environments and reduce connection overhead with TCP while keeping the similar development experience of traditional TCP-based MySQL drivers. 

> **Note:**
>
> If you prefer programming with RESTful API rather than SQL or ORM, you can use [Data Service (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview).
## Install the serverless driver

You can install the driver with npm:

```bash
npm install @tidbcloud/serverless
```
## Use the serverless driver

You can use the serverless driver to query data of a TiDB Cloud Serverless cluster or perform interactive transactions.
### Query

To query data from a TiDB Cloud Serverless cluster, you need to create a connection first. Then you can use the connection to execute raw SQL queries. For example:

```ts
import { connect } from '@tidbcloud/serverless'

const conn = connect({url: 'mysql://[username]:[password]@[host]/[database]'})
const results = await conn.execute('select * from test where id = ?',[1])
```
### Transaction (experimental)

You can also perform interactive transactions with the serverless driver. For example:

```ts
import { connect } from '@tidbcloud/serverless'

const conn = connect({url: 'mysql://[username]:[password]@[host]/[database]'})
const tx = await conn.begin()

try {
  await tx.execute('insert into test values (1)')
  await tx.execute('select * from test')
  await tx.commit()
} catch (err) {
  await tx.rollback()
  throw err
}
```
## Edge examples

Here are some examples of using the serverless driver in edge environments. For a complete example, you can also try this [live demo](https://github.com/tidbcloud/car-sales-insight).

<div label="Vercel Edge Function">

```ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { connect } from '@tidbcloud/serverless'
export const runtime = 'edge'

export async function GET(request: NextRequest) {
  const conn = connect({url: process.env.DATABASE_URL})
  const result = await conn.execute('show tables')
  return NextResponse.json({result});
}
```

Learn more about [using TiDB Cloud serverless driver in Vercel](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel).

</div>

<div label="Cloudflare Workers">

```ts
import { connect } from '@tidbcloud/serverless'
export interface Env {
  DATABASE_URL: string;
}
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const conn = connect({url: env.DATABASE_URL})
    const result = await conn.execute('show tables')
    return new Response(JSON.stringify(result));
  },
};
```

Learn more about [using TiDB Cloud serverless driver in Cloudflare Workers](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-cloudflare).

</div>

<div label="Netlify Edge Function">

```ts
import { connect } from 'https://esm.sh/@tidbcloud/serverless'

export default async () => {
  const conn = connect({url: Netlify.env.get('DATABASE_URL')})
  const result = await conn.execute('show tables')
  return new Response(JSON.stringify(result));
}
```

Learn more about [using TiDB Cloud serverless driver in Netlify](https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-netlify#use-the-edge-function).

</div>

<div label="Deno">

```ts
import { connect } from "npm:@tidbcloud/serverless"

const conn = connect({url: Deno.env.get('DATABASE_URL')})
const result = await conn.execute('show tables')
```

</div>

<div label="Bun">

```ts
import { connect } from "@tidbcloud/serverless"

const conn = connect({url: Bun.env.DATABASE_URL})
const result = await conn.execute('show tables')
```

</div>
