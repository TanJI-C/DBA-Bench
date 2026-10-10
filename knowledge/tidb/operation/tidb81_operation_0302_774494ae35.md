# Create a TiDB Cloud Serverless cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/create-tidb-cluster-serverless.md`
- Source Title: `Create a TiDB Cloud Serverless Cluster`
- Source Heading Path: `Create a TiDB Cloud Serverless Cluster | Create a TiDB Cloud Serverless Cluster > Before you begin | Create a TiDB Cloud Serverless Cluster > Steps | Create a TiDB Cloud Serverless Cluster > What's next`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cluster-creation`, `serverless`, `account-signup`, `organization-roles`, `aws-region`, `cluster-plan`, `billing`, `password-setup`, `public-endpoint`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0302_774494ae35`
- Source ID: `tidb-docs-8.1:tidb-cloud/create-tidb-cluster-serverless.md#create-a-tidb-cloud-serverless-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c4cce874f175be42d7ee702c073957f27c5418afce94b33d6f00d27aa007f228`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless#create-a-tidb-cloud-serverless-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/create-tidb-cluster-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the documented steps, prerequisites, or role requirements for creating a TiDB Cloud Serverless cluster in the TiDB Cloud console.
- Retrieval Keywords: Create a TiDB Cloud Serverless cluster, TiDB Cloud console, Organization Owner, Project Owner, Create Cluster, Serverless, AWS region, Free Cluster, Scalable Cluster, Monthly Spending Limit, credit card, maximum of five free clusters, approximately 30 seconds, Connect to TiDB Cloud Serverless via Public Endpoint, create a password, public endpoint
- Follow-up Guidance: After the cluster is created, the document points to Connect to TiDB Cloud Serverless via Public Endpoint to create a password, and notes that without setting a password you cannot connect to the cluster.
- Classification Note: This chunk is classified as an operation because it provides prerequisite information and step-by-step console actions for creating a TiDB Cloud Serverless cluster.

## Official Source Content

# Create a TiDB Cloud Serverless Cluster

This document describes how to create a TiDB Cloud Serverless cluster in the [TiDB Cloud console](https://tidbcloud.com/).

> **Tip:**
>
> To learn how to create a TiDB Cloud Dedicated cluster, see [Create a TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster).
## Before you begin

If you do not have a TiDB Cloud account, click [here](https://tidbcloud.com/signup) to sign up for an account.

- You can either sign up with email and password so that you can manage your password using TiDB Cloud, or sign up with your Google, GitHub, or Microsoft account.
- For AWS Marketplace users, you can also sign up through AWS Marketplace. To do that, search for `TiDB Cloud` in [AWS Marketplace](https://aws.amazon.com/marketplace), subscribe to TiDB Cloud, and then follow the onscreen instructions to set up your TiDB Cloud account.
- For Azure Marketplace users, you can also sign up through Azure Marketplace. To do that, search for `TiDB Cloud` in [Azure Marketplace](https://azuremarketplace.microsoft.com), subscribe to TiDB Cloud, and then follow the onscreen instructions to set up your TiDB Cloud account.
- For Google Cloud Marketplace users, you can also sign up through Google Cloud Marketplace. To do that, search for `TiDB Cloud` in [Google Cloud Marketplace](https://console.cloud.google.com/marketplace), subscribe to TiDB Cloud, and then follow the onscreen instructions to set up your TiDB Cloud account.
## Steps

If you are in the `Organization Owner` or the `Project Owner` role, you can create a TiDB Cloud Serverless cluster as follows:

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/), and then navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page.

2. Click **Create Cluster**.

3. On the **Create Cluster** page, **Serverless** is selected by default.

4. The cloud provider of TiDB Cloud Serverless is AWS. You can select an AWS region where you want to host your cluster.

5. Update the default cluster name if necessary.

6. Select a cluster plan. TiDB Cloud Serverless provides two [cluster plans](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#cluster-plans): **Free Cluster** and **Scalable Cluster**. You can start with a free cluster and later upgrade to a scalable cluster as your needs grow. To create a scalable cluster, you need to specify a **Monthly Spending Limit** and add a credit card.

    > **Note:**
    >
    > For each organization in TiDB Cloud, you can create a maximum of five [free clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#free-cluster-plan) by default. To create more TiDB Cloud Serverless clusters, you need to add a credit card and create [scalable clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#scalable-cluster-plan) for the usage.

7. Click **Create**.

    The cluster creation process starts and your TiDB Cloud cluster will be created in approximately 30 seconds.
## What's next

After your cluster is created, follow the instructions in [Connect to TiDB Cloud Serverless via Public Endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection-serverless) to create a password for your cluster.

> **Note:**
>
> If you do not set a password, you cannot connect to the cluster.
