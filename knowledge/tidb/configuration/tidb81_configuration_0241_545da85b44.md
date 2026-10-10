# Manually set Vercel environment variables for cluster or Data App

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-vercel.md`
- Source Title: `Integrate TiDB Cloud with Vercel`
- Source Heading Path: `Integrate TiDB Cloud with Vercel > Connect via manually setting environment variables`
- Source Line Ranges: `216-266`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `shared`
- Topic Tags: `vercel`, `environment-variables`, `cluster-connection`, `data-app`, `prisma`, `database-url`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0241_545da85b44`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-vercel.md#connect-via-manually-setting-environment-variables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ae599581da225e8e3842f480b858e8f63210d161f12f912eaeb54575d1e060f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel#connect-via-manually-setting-environment-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-vercel.md

## Retrieval Guidance

- Use When: Use this when looking for the manual Vercel environment variable setup for connecting either a TiDB cluster or a Data App from a Vercel project.
- Retrieval Keywords: Connect via manually setting environment variables, Vercel project Settings Environment Variables, declare each environment variable value, TiDB cluster connection information, Clusters page, Connect, Prisma schema, datasource db, provider = "mysql", url = env("DATABASE_URL"), DATABASE_URL, mysql://<User>:<Password>@<Endpoint>:<Port>/<Database>?sslaccept=strict, Data App, DATA_APP_BASE_URL, DATA_APP_PUBLIC_KEY, DATA_APP_PRIVATE_KEY, Data Service page, Manage a Data APP, Manage an Endpoint
- Follow-up Guidance: For the Data App path, the content says to create a Data App and its endpoints by following Manage a Data APP and Manage an Endpoint if you have not done that.
- Classification Note: This is classified as configuration because the content specifies the exact environment variables and connection values to declare in Vercel for cluster and Data App connections.

## Official Source Content

## Connect via manually setting environment variables

<div label="Cluster">

1. Get the connection information of your TiDB cluster.

    You can get the connection information from the connection dialog of your cluster. To open the dialog, go to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page, and then click **Connect** in the upper-right corner.

2. Go to your Vercel dashboard > Vercel project > **Settings** > **Environment Variables**, and then [declare each environment variable value](https://vercel.com/docs/concepts/projects/environment-variables#declare-an-environment-variable) according to the connection information of your TiDB cluster.

    ![Vercel Environment Variables](/media/tidb-cloud/vercel/integration-vercel-environment-variables.png)

Here we use a Prisma application as an example. The following is a datasource setting in the Prisma schema file for a TiDB Cloud Serverless cluster:

```
datasource db {
    provider = "mysql"
    url      = env("DATABASE_URL")
}
```

In Vercel, you can declare the environment variables as follows:

- **Key** = `DATABASE_URL`
- **Value** = `mysql://<User>:<Password>@<Endpoint>:<Port>/<Database>?sslaccept=strict`

You can get the information of `<User>`, `<Password>`, `<Endpoint>`, `<Port>`, and `<Database>` in the TiDB Cloud console.

</div>
<div label="Data App">

1. Follow the steps in [Manage a Data APP](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app) and [Manage an Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint) to create a Data App and its endpoints if you have not done that.

2. Go to your Vercel dashboard > Vercel project > **Settings** > **Environment Variables**, and then [declare each environment variable value](https://vercel.com/docs/concepts/projects/environment-variables#declare-an-environment-variable) according to the connection information of your Data App.

    ![Vercel Environment Variables](/media/tidb-cloud/vercel/integration-vercel-environment-variables.png)

    In Vercel, you can declare the environment variables as follows.

    - **Key** = `DATA_APP_BASE_URL`
    - **Value** = `<DATA_APP_BASE_URL>`
    - **Key** = `DATA_APP_PUBLIC_KEY`
    - **Value** = `<DATA_APP_PUBLIC_KEY>`
    - **Key** = `DATA_APP_PRIVATE_KEY`
    - **Value** = `<DATA_APP_PRIVATE_KEY>`

    You can get the information of `<DATA_APP_BASE_URL>`, `<DATA_APP_PUBLIC_KEY>`, `<DATA_APP_PRIVATE_KEY>` from your [Data Service](https://tidbcloud.com/project/data-service) page of the TiDB Cloud console.

</div>
