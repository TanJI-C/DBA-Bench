# TiDB Cloud Serverless driver Node.js local setup and usage

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-driver-node-example.md`
- Source Title: `TiDB Cloud Serverless Driver Node.js Tutorial`
- Source Heading Path: `TiDB Cloud Serverless Driver Node.js Tutorial | TiDB Cloud Serverless Driver Node.js Tutorial > Before you begin | TiDB Cloud Serverless Driver Node.js Tutorial > Step 1. Create a local Node.js project | TiDB Cloud Serverless Driver Node.js Tutorial > Step 2. Use the serverless driver | TiDB Cloud Serverless Driver Node.js Tutorial > Compatibility with earlier versions of Node.js`
- Source Line Ranges: `5-95`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `nodejs`, `serverless-driver`, `local-project`, `installation`, `connection-string`, `es-modules`, `commonjs`, `fetch-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0362_efc67860a9`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-driver-node-example.md#tidb-cloud-serverless-driver-node-js-tutorial`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43128196d6acde6554efd735917fde132b7d6483ee0859306cf020cc4444bc0d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver-node-example#tidb-cloud-serverless-driver-node-js-tutorial
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-driver-node-example.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the local Node.js setup, package installation, connection string format, module usage, or fetch compatibility details for the TiDB Cloud serverless driver.
- Retrieval Keywords: TiDB Cloud Serverless Driver Node.js Tutorial, @tidbcloud/serverless, npm install @tidbcloud/serverless, mysql://[username]:[password]@[host]/[database], connect({url: 'mysql://[username]:[password]@[host]/[database]'}), show tables, package.json, type: "module", ES modules, CommonJS, node index.js, Node.js >= 18.0.0, global fetch, undici, npm install undici, import { fetch } from 'undici'
- Follow-up Guidance: The source also includes the earlier-Node.js compatibility example that passes `fetch` from `undici` to `connect`.
- Classification Note: This is classified as an operation chunk because the content is a step-by-step tutorial for creating a local Node.js project and using the TiDB Cloud serverless driver.

## Official Source Content

# TiDB Cloud Serverless Driver Node.js Tutorial

This tutorial describes how to use TiDB Cloud serverless driver in a local Node.js project.

> **Note:**
>
> - This tutorial is applicable to TiDB Cloud Serverless clusters only. 
> - To learn how to use TiDB Cloud serverless driver with Cloudflare Workers, Vercel Edge Functions, and Netlify Edge Functions, check out our [Insights into Automotive Sales](https://car-sales-insight.vercel.app/) and the [sample repository](https://github.com/tidbcloud/car-sales-insight).
## Before you begin

To complete this step-by-step tutorial, you need the following:

- [Node.js](https://nodejs.org/en) >= 18.0.0.
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) or your preferred package manager.
- A TiDB Cloud Serverless cluster. If you don't have any, you can [create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
## Step 1. Create a local Node.js project

1. Create a project named `node-example`:

    ```shell
    mkdir node-example
    cd node-example
    ```

2. Install the TiDB Cloud serverless driver using npm or your preferred package manager.

    The following command takes installation with npm as an example. Executing this command will create a `node_modules` directory and a `package.json` file in your project directory.

    ```
    npm install @tidbcloud/serverless
    ```
## Step 2. Use the serverless driver

The serverless driver supports both CommonJS and ES modules. The following steps take the usage of the ES module as an example.

1. On the overview page of your TiDB Cloud Serverless cluster, click **Connect** in the upper-right corner, and then get the connection string for your database from the displayed dialog. The connection string looks like this:

    ```
   mysql://[username]:[password]@[host]/[database]
    ```
   
2. In the `package.json` file, specify the ES module by adding `type: "module"`. 

    For example:

    ```json
    {
      "type": "module",
      "dependencies": {
        "@tidbcloud/serverless": "^0.0.7",
      }
    }
    ```

3. Create a file named `index.js` in your project directory and add the following code:

    ```js
    import { connect } from '@tidbcloud/serverless'
    
    const conn = connect({url: 'mysql://[username]:[password]@[host]/[database]'}) // replace with your TiDB Cloud Serverless cluster information
    console.log(await conn.execute("show tables"))
    ```

4. Run your project with the following command:

    ```
    node index.js
    ```
## Compatibility with earlier versions of Node.js

If you are using Node.js earlier than 18.0.0, which does not have a global `fetch` function, you can take the following steps to get `fetch`:

1. Install a package that provides `fetch`, such as `undici`:

    ```
    npm install undici
    ``` 

2. Pass the `fetch` function to the `connect` function:

    ```js
    import { connect } from '@tidbcloud/serverless'
    import { fetch } from 'undici'
    
    const conn = connect({url: 'mysql://[username]:[password]@[host]/[database]',fetch})
    ```
