# TiDB Cloud Serverless connection methods and network options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connect-to-tidb-cluster-serverless.md`
- Source Title: `Connect to Your TiDB Cloud Serverless Cluster`
- Source Heading Path: `Connect to Your TiDB Cloud Serverless Cluster | Connect to Your TiDB Cloud Serverless Cluster > Connection methods | Connect to Your TiDB Cloud Serverless Cluster > Network | Connect to Your TiDB Cloud Serverless Cluster > What's next`
- Source Line Ranges: `5-62`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `connection-methods`, `direct-connections`, `data-service`, `serverless-driver`, `network`, `private-endpoint`, `public-endpoint`, `tls`, `sql-clients`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0217_e34e793050`
- Source ID: `tidb-docs-8.1:tidb-cloud/connect-to-tidb-cluster-serverless.md#connect-to-your-tidb-cloud-serverless-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cd555df0250715f700e7b86290ff9e394f957fb5d18f2bc287a5f948d5c56dbe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster-serverless#connect-to-your-tidb-cloud-serverless-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connect-to-tidb-cluster-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to connect to a TiDB Cloud Serverless cluster, compare direct connections, Data Service, and Serverless Driver, or determine whether to use a public endpoint or private endpoint.
- Retrieval Keywords: TiDB Cloud Serverless, Connect to Your TiDB Cloud Serverless Cluster, connection methods, Direct connections, Data Service (beta), Serverless Driver (beta), MySQL native connection system over TCP, RESTful API, custom API endpoint, JavaScript, edge environments, SQL/ORM, public endpoint, private endpoint, AWS PrivateLink, TLS connections, standard connection, VPC, MySQL client, Vercel Edge Functions, Cloudflare Workers
- Follow-up Guidance: After successfully connecting to your TiDB cluster, you can explore SQL statements with TiDB.
- Classification Note: The content is classified as configuration because it describes available connection methods and network connection types for TiDB Cloud Serverless, including direct connections, Data Service, Serverless Driver, and public or private endpoints.

## Official Source Content

# Connect to Your TiDB Cloud Serverless Cluster

This document describes how to connect to your TiDB Cloud Serverless cluster.

> **Tip:**
>
> To learn how to connect to a TiDB Cloud Dedicated cluster, see [Connect to Your TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster).
## Connection methods

After your TiDB Cloud Serverless cluster is created on TiDB Cloud, you can connect to it via one of the following methods:

- Direct connections

  Direct connections mean the MySQL native connection system over TCP. You can connect to your TiDB Cloud Serverless cluster using any tool that supports MySQL connection, such as [MySQL client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html).

- [Data Service (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-overview)

  TiDB Cloud provides a Data Service feature that enables you to connect to your TiDB Cloud Serverless cluster via an HTTPS request using a custom API endpoint. Unlike direct connections, Data Service accesses TiDB Cloud Serverless data via a RESTful API rather than raw SQL.

- [Serverless Driver (beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver)

  TiDB Cloud provides a serverless driver for JavaScript, which allows you to connect to your TiDB Cloud Serverless cluster in edge environments with the same experience as direct connections.

In the preceding connection methods, you can choose your desired one based on your needs:

| Connection method  | User interface     | Scenario                                                                                                                                                       |
|--------------------|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Direct connections | SQL/ORM            | Long-running environment, such as Java, Node.js, and Python.                                                                                                   |
| Data Service       | RESTful API        | All browser and application interactions.                                                                                                                      |
| Serverless Driver  | SQL/ORM            | Serverless and edge environments such as [Vercel Edge Functions](https://vercel.com/docs/functions/edge-functions) and [Cloudflare Workers](https://workers.cloudflare.com/). |
## Network

There are two network connection types for TiDB Cloud Serverless:

- [Private endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections-serverless) (recommended)

    Private endpoint connection provides a private endpoint to allow SQL clients in your VPC to securely access services over AWS PrivateLink, which provides highly secure and one-way access to database services with simplified network management.

- [Public endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless)

  The standard connection exposes a public endpoint, so you can connect to your TiDB cluster via a SQL client from your laptop.

  TiDB Cloud Serverless requires [TLS connections](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters), which ensures the security of data transmission from your applications to TiDB clusters.

The following table shows the network you can use in different connection methods:

| Connection method          | Network                      | Description                                                                                                       |
|----------------------------|------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Direct connections         | Public or private endpoint   | Direct connections can be made via both public and private endpoints.                                             |
| Data Service (beta)        | /                            | Accessing TiDB Cloud Serverless via Data Service (beta) does not need to specify the network type.                      |
| Serverless Driver (beta)   | Public endpoint              | Serverless Driver only supports connections via public endpoint.                                                  |
## What's next

After you have successfully connected to your TiDB cluster, you can [explore SQL statements with TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations).
