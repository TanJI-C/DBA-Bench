# TiDB Cloud quick start and create a serverless cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-quickstart.md`
- Source Title: `TiDB Cloud Quick Start`
- Source Heading Path: `TiDB Cloud Quick Start | TiDB Cloud Quick Start > Step 1: Create a TiDB cluster`
- Source Line Ranges: `6-34`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `quickstart`, `signup`, `login`, `serverless`, `cluster-creation`, `region`, `cluster-plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0423_306f6c319c`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-quickstart.md#tidb-cloud-quick-start`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5f8c6476f990e937e0d60fa765a1112ec3879f94ceee0dacf49d9c13eb0523c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart#tidb-cloud-quick-start
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-quickstart.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the TiDB Cloud quick start steps to sign up, log in, and create a TiDB Cloud Serverless cluster or understand the default cluster for new sign-up users.
- Retrieval Keywords: TiDB Cloud Quick Start, Step 1: Create a TiDB cluster, TiDB Cloud Serverless, sign up, log in, Clusters page, default cluster Cluster0, Create Cluster, Create Cluster page, Serverless, target region, cluster name, cluster plan
- Follow-up Guidance: It points new sign-up users with the default cluster `Cluster0` to Step 2: Try AI-assisted SQL Editor.
- Classification Note: This is classified as an operation chunk because it gives console steps for account access and TiDB Cloud Serverless cluster creation.

## Official Source Content

# TiDB Cloud Quick Start

*Estimated completion time: 20 minutes*

This tutorial guides you through an easy way to get started with TiDB Cloud. You can also follow the step-by-step tutorials on the [**Getting Started**](https://tidbcloud.com/getting-started) page in the TiDB Cloud console.

Additionally, you can try out TiDB features on [TiDB Playground](https://play.tidbcloud.com/?utm_source=docs&utm_medium=tidb_cloud_quick_start).
## Step 1: Create a TiDB cluster

[TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) is the best way to get started with TiDB Cloud. To create a TiDB Cloud Serverless cluster, follow these steps:

1. If you do not have a TiDB Cloud account, click [here](https://tidbcloud.com/free-trial) to sign up.

    You can sign up with your email and password to manage your password using TiDB Cloud, or choose to sign in with your Google, GitHub, or Microsoft account for single sign-on (SSO) to TiDB Cloud.

2. [Log in](https://tidbcloud.com/) to your TiDB Cloud account.

    The [**Clusters**](https://tidbcloud.com/project/clusters) page is displayed by default.

3. For new sign-up users, TiDB Cloud automatically creates a default TiDB Cloud Serverless cluster named `Cluster0` for you.

    - To instantly try out TiDB Cloud features with this default cluster, proceed to [Step 2: Try AI-assisted SQL Editor](#step-2-try-ai-assisted-sql-editor).
    - To create a new TiDB Cloud Serverless cluster on your own, follow these steps:

        1. Click **Create Cluster**.
        2. On the **Create Cluster** page, **Serverless** is selected by default. Select the target region for your cluster, update the default cluster name if necessary, select your [cluster plan](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#cluster-plans), and then click **Create**. Your TiDB Cloud Serverless cluster will be created in approximately 30 seconds.
