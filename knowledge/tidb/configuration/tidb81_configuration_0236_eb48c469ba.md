# Prerequisites and get TiDB Cloud connection string for Netlify example

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-netlify.md`
- Source Title: `Integrate TiDB Cloud with Netlify`
- Source Heading Path: `Integrate TiDB Cloud with Netlify | Integrate TiDB Cloud with Netlify > Prerequisites | Integrate TiDB Cloud with Netlify > Prerequisites > A Netlify account and CLI | Integrate TiDB Cloud with Netlify > Prerequisites > A TiDB Cloud account and a TiDB cluster | Integrate TiDB Cloud with Netlify > Prerequisites > All IP addresses allowed for traffic filter in TiDB Cloud | Integrate TiDB Cloud with Netlify > Step 1. Get the example project and the connection string | Integrate TiDB Cloud with Netlify > Step 1. Get the example project and the connection string > Fork the example project and clone it to your own space | Integrate TiDB Cloud with Netlify > Step 1. Get the example project and the connection string > Get the TiDB Cloud connection string`
- Source Line Ranges: `5-124`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `prerequisites`, `netlify`, `account-setup`, `traffic-filter`, `connection-string`, `cloud-cli`, `console`, `prisma`, `example-project`, `git-clone`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0236_eb48c469ba`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-netlify.md#integrate-tidb-cloud-with-netlify`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2dfb75872bbd7b7af3ecfe4c0283eea1b70649e5b9fc2644eb43dae5317d2c91`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-netlify#integrate-tidb-cloud-with-netlify
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-netlify.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the prerequisites for integrating TiDB Cloud with Netlify or needs to obtain the TiDB Cloud connection string for the Next.js Prisma example project.
- Retrieval Keywords: Netlify account, Netlify CLI, TiDB Cloud account, TiDB Cloud Serverless cluster, TiDB Cloud Dedicated cluster, traffic filter, 0.0.0.0/0, dynamic IP addresses, Fullstack Example with Next.js and Prisma, nextjs-prisma-example, git clone, TiDB Cloud connection string, ticloud cluster connect-info, Prisma, mysql://<User>:<Password>@<Endpoint>:<Port>/<Database>?sslaccept=strict, Connect
- Follow-up Guidance: The chunk continues with how to authenticate with Netlify CLI, run `netlify init`, set `DATABASE_URL`, and deploy the example app.
- Classification Note: This is classified as configuration because the content lists required accounts, traffic filter settings, example project setup, and exact connection string retrieval details for Netlify integration.

## Official Source Content

# Integrate TiDB Cloud with Netlify

[Netlify](https://netlify.com/) is an all-in-one platform for automating modern web projects. It replaces your hosting infrastructure, continuous integration, and deployment pipeline with a single workflow and integrates dynamic functionality like serverless functions, user authentication, and form handling as your projects grow.

This document describes how to deploy a fullstack app on Netlify with TiDB Cloud as the database backend. You can also learn how to use Netlify edge function with our TiDB Cloud serverless driver.
## Prerequisites

Before the deployment, make sure the following prerequisites are met.
### A Netlify account and CLI

You are expected to have a Netlify account and CLI. If you do not have any, refer to the following links to create one:

* [Sign up for a Netlify account](https://app.netlify.com/signup).
* [Get Netlify CLI](https://docs.netlify.com/cli/get-started/).
### A TiDB Cloud account and a TiDB cluster

You are expected to have an account and a cluster in TiDB Cloud. If you do not have any, refer to the following to create one:

- [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless)
- [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster)

One TiDB Cloud cluster can connect to multiple Netlify sites.
### All IP addresses allowed for traffic filter in TiDB Cloud

For TiDB Cloud Dedicated clusters, make sure that the traffic filter of the cluster allows all IP addresses (set to `0.0.0.0/0`) for connection. This is because Netlify deployments use dynamic IP addresses.

TiDB Cloud Serverless clusters allow all IP addresses for connection by default, so you do not need to configure any traffic filter.
## Step 1. Get the example project and the connection string

To help you get started quickly, TiDB Cloud provides a fullstack example app in TypeScript with Next.js using React and Prisma Client. It is a simple blog site where you can post and delete your own blogs. All the content is stored in TiDB Cloud through Prisma.
### Fork the example project and clone it to your own space

1. Fork the [Fullstack Example with Next.js and Prisma](https://github.com/tidbcloud/nextjs-prisma-example) repository to your own GitHub repository.

2. Clone the forked repository to your own space:

    ```shell
    git clone https://github.com/${your_username}/nextjs-prisma-example.git
    cd nextjs-prisma-example/
    ```
### Get the TiDB Cloud connection string

For a TiDB Cloud Serverless cluster, you can get the connection string either from [TiDB Cloud CLI](https://docs.pingcap.com/tidb/stable/tidb-cloud/cli-reference) or from [TiDB Cloud console](https://tidbcloud.com/).

For a TiDB Cloud Dedicated cluster, you can get the connection string only from the TiDB Cloud console.

<div label="TiDB Cloud CLI">

> **Tip:**
>
> If you have not installed Cloud CLI, refer to [TiDB Cloud CLI Quick Start](https://docs.pingcap.com/tidb/stable/tidb-cloud/get-started-with-cli) for quick installation before taking the following steps.

1. Get the connection string of a cluster in interactive mode:

    ```shell
    ticloud cluster connect-info
    ```

2. Follow the prompts to select your cluster, client, and operating system. Note that the client used in this document is `Prisma`.

    ```
    Choose the cluster
    > [x] Cluster0(13796194496)
    Choose the client
    > [x] Prisma
    Choose the operating system
    > [x] macOS/Alpine (Detected)
    ```

    The output is as follows, where you can find the connection string for Prisma in the `url` value.

    ```shell
    datasource db {
    provider = "mysql"
    url      = "mysql://<User>:<Password>@<Endpoint>:<Port>/<Database>?sslaccept=strict"
    }
    ```

    > **Note:**
    >
    > When you use the connection string later, note the following:
    >
    > - Replace the parameters in the connection string with actual values.
    > - The example app in this document requires a new database, so you need to replace `<Database>` with a unique new name.

</div>
<div label="TiDB Cloud console">

1. In the [TiDB Cloud console](https://tidbcloud.com/), go to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page, and then click **Connect** in the upper-right corner. In the displayed dialog, you can get the following connection parameters from the connection string.

    - `${host}`
    - `${port}`
    - `${user}`
    - `${password}`

2. Fill the connection parameters in the following connection string:

    ```shell
    mysql://<User>:<Password>@<Host>:<Port>/<Database>?sslaccept=strict
    ```

    > **Note:**
    >
    > When you use the connection string later, note the following:
    >
    > - Replace the parameters in the connection string with actual values.
    > - The example app in this document requires a new database, so you need to replace `<Database>` with a unique new name.

</div>
