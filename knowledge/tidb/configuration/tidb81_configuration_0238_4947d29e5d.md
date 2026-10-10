# Vercel integration overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-vercel.md`
- Source Title: `Integrate TiDB Cloud with Vercel`
- Source Heading Path: `Integrate TiDB Cloud with Vercel | Integrate TiDB Cloud with Vercel > Prerequisites | Integrate TiDB Cloud with Vercel > Prerequisites > A Vercel account and a Vercel project | Integrate TiDB Cloud with Vercel > Prerequisites > A TiDB Cloud account and a TiDB cluster | Integrate TiDB Cloud with Vercel > Prerequisites > A Data App and endpoints`
- Source Line Ranges: `5-67`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `vercel`, `integration`, `prerequisites`, `serverless`, `dedicated`, `traffic-filter`, `data-app`, `endpoints`, `roles`, `environment-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0238_4947d29e5d`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-vercel.md#integrate-tidb-cloud-with-vercel`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `616777bff1839e6500a6fd9a118d16c68d3becc617d70ba81840326aedd881ca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel#integrate-tidb-cloud-with-vercel
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-vercel.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about prerequisites, supported connection options, account or role requirements, Data App preparation, or one-to-one versus one-to-many connection limits for integrating TiDB Cloud with Vercel.
- Retrieval Keywords: Integrate TiDB Cloud with Vercel, prerequisites, Vercel account, Vercel project, TiDB Cloud account, TiDB Cloud cluster, TiDB Cloud Serverless cluster, TiDB Cloud Dedicated cluster, traffic filter, 0.0.0.0/0, dynamic IP addresses, Organization Owner, Project Owner, User roles, Data App, Data Service, endpoints, serverless driver, environment variables, one Vercel project can only connect to one TiDB Cloud cluster, one TiDB Cloud cluster can connect to multiple Vercel projects, one Vercel project can only connect to one TiDB Cloud Data App
- Follow-up Guidance: The page also describes two connection methods: the TiDB Cloud Vercel integration and manually setting environment variables.
- Classification Note: This is classified as configuration because the content defines setup prerequisites, connection options, required roles, traffic filter settings, and Data App endpoint preparation for a cloud integration.

## Official Source Content

# Integrate TiDB Cloud with Vercel

[Vercel](https://vercel.com/) is a platform for frontend developers, providing the speed and reliability innovators need to create at the moment of inspiration.

Using TiDB Cloud with Vercel enables you to build new frontend applications faster with a MySQL-compatible relational model and grow your app with confidence with a platform built for resilience, scale, and the highest levels of data privacy and security.

This guide describes how to connect your TiDB Cloud clusters to Vercel projects using one of the following methods:

* [Connect via the TiDB Cloud Vercel integration](#connect-via-the-tidb-cloud-vercel-integration)
* [Connect via manually configuring environment variables](#connect-via-manually-setting-environment-variables)

For both of the preceding methods, TiDB Cloud provides the following options for programmatically connecting to your database:

- Cluster: connect your TiDB Cloud cluster to your Vercel project with direct connections or [serverless driver](https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-driver).
- [Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app): access data of your TiDB Cloud cluster through a collection of HTTP endpoints.
## Prerequisites

Before connection, make sure the following prerequisites are met.
### A Vercel account and a Vercel project

You are expected to have an account and a project in Vercel. If you do not have any, refer to the following Vercel documents to create one:

* [Creating a new personal account](https://vercel.com/docs/teams-and-accounts#creating-a-personal-account) or [Creating a new team](https://vercel.com/docs/teams-and-accounts/create-or-join-a-team#creating-a-team).
* [Creating a project](https://vercel.com/docs/concepts/projects/overview#creating-a-project) in Vercel, or if you do not have an application to deploy, you can use the [TiDB Cloud Starter Template](https://vercel.com/templates/next.js/tidb-cloud-starter) to have a try.

One Vercel project can only connect to one TiDB Cloud cluster. To change the integration, you need to first disconnect the current cluster and then connect to a new cluster.
### A TiDB Cloud account and a TiDB cluster

You are expected to have an account and a cluster in TiDB Cloud. If you do not have any, refer to the following to create one:

- [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless)

    > **Note:**
    >
    > The TiDB Cloud Vercel integration supports creating TiDB Cloud Serverless clusters. You can also create one later during the integration process.

- [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster)

    > **Note:**
    >
    > For TiDB Cloud Dedicated clusters, make sure that the traffic filter of the cluster allows all IP addresses (set to `0.0.0.0/0`) for connection, because Vercel deployments use [dynamic IP addresses](https://vercel.com/guides/how-to-allowlist-deployment-ip-address).

To [integrate with Vercel via the TiDB Cloud Vercel Integration](#connect-via-the-tidb-cloud-vercel-integration), you are expected to be in the `Organization Owner` role of your organization or the `Project Owner` role of the target project in TiDB Cloud. For more information, see [User roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles).

One TiDB Cloud cluster can connect to multiple Vercel projects.
### A Data App and endpoints

If you want to connect to your TiDB Cloud cluster via a [Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app), you are expected to have the target Data App and endpoints in TiDB Cloud in advance. If you do not have any, refer to the following to create one:

1. In the [TiDB Cloud console](https://tidbcloud.com), go to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. [Create a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#create-a-data-app) for your project.
3. [Link the Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#manage-linked-data-sources) to the target TiDB Cloud cluster.
4. [Manage endpoints](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint) so that you can customize them to execute SQL statements.

One Vercel project can only connect to one TiDB Cloud Data App. To change the Data App for your Vercel project, you need to first disconnect the current App and then connect to a new App.
