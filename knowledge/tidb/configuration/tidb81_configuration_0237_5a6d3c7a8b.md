# Use Netlify edge function with TiDB Cloud serverless driver

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-netlify.md`
- Source Title: `Integrate TiDB Cloud with Netlify`
- Source Heading Path: `Integrate TiDB Cloud with Netlify > Use the edge function`
- Source Line Ranges: `227-261`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`
- Topic Tags: `edge-function`, `serverless-driver`, `database-url`, `netlify-env`, `typescript`, `api-endpoint`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0237_5a6d3c7a8b`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-netlify.md#use-the-edge-function`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66faee70dc56391fafa826ecba7a760805c3707c8f8b21a3a8a5ad04c10ae58f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-netlify#use-the-edge-function
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-netlify.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the example for running a Netlify edge function with the TiDB Cloud serverless driver and setting `DATABASE_URL` for the edge function.
- Retrieval Keywords: Use the edge function, Netlify edge function, TiDB Cloud serverless driver, netlify/edge-functions, hello.ts, @tidbcloud/serverless, connect({url: Netlify.env.get('DATABASE_URL')}), show databases, export const config = { path: "/api/hello" }, netlify env:set DATABASE_URL, netlify deploy --prod --trigger, https://<netlify-host>/api/hello
- Follow-up Guidance: After deployment, the chunk says the edge function can be accessed through the `https://<netlify-host>/api/hello` URL.
- Classification Note: This is classified as configuration because the content provides the file path, TypeScript code, environment variable, and route configuration needed to use a Netlify edge function with the TiDB Cloud serverless driver.

## Official Source Content

## Use the edge function

The example app mentioned in the section above runs on the Netlify serverless function. This section shows you how to use the edge function with [TiDB Cloud serverless driver](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver). The edge function is a feature provided by Netlify, which allows you to run serverless functions on the edge of the Netlify CDN.

To use the edge function, take the following steps:

1. Create a directory named `netlify/edge-functions` in the root directory of your project. 

2. Create a file named `hello.ts` in the directory and add the following code:

    ```typescript
    import { connect } from 'https://esm.sh/@tidbcloud/serverless'
    
    export default async () => {
      const conn = connect({url: Netlify.env.get('DATABASE_URL')})
      const result = await conn.execute('show databases')
      return new Response(JSON.stringify(result));
    }
   
    export const config = { path: "/api/hello" };
    ```

3. Set the `DATABASE_URL` environment variables. You can get the connection information from the [TiDB Cloud console](https://tidbcloud.com/).

    ```shell
    netlify env:set DATABASE_URL 'mysql://<username>:<password>@<host>/<database>'
    ```

4. Deploy the edge function to Netlify.

    ```shell
    netlify deploy --prod --trigger
    ```

Then you can go to your Netlify console to check the state of the deployment. After the deployment is done, you can access the edge function through the `https://<netlify-host>/api/hello` URL.
