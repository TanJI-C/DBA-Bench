# Create a TiDB Cloud starter cluster

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-build-cluster-in-cloud.md`
- Source Title: `Build a {{{ .starter }}} Cluster`
- Source Heading Path: `Build a {{{ .starter }}} Cluster | Build a {{{ .starter }}} Cluster > Step 1. Create a {{{ .starter }}} cluster {#step-1-create-a-tidb-cloud-cluster}`
- Source Line Ranges: `5-59`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cluster-creation`, `account-login`, `region-selection`, `connection-setup`, `password-generation`, `username-prefix`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0049_e7930101d1`
- Source ID: `tidb-docs-8.1:develop/dev-guide-build-cluster-in-cloud.md#build-a-starter-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c072162800a7f3828feb365ee7729a9c2ddcdd70afc755fb0358beccbb2d831`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud#build-a-starter-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-build-cluster-in-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented TiDB Cloud Starter cluster creation flow, including account login, cluster creation, region selection, Connect dialog access, and password generation details.
- Retrieval Keywords: TiDB Cloud Starter cluster, Create Cluster, Clusters page, Create a Starter cluster, region selection, Connect, Generate Password, root password, user name prefix, wrap the name with quotation marks, cluster overview page
- Follow-up Guidance: It continues with selecting a connection method and operating system, getting the connection string, and notes that Starter connections require the cluster prefix in the user name.
- Classification Note: This is an operation chunk because the official content gives step-by-step TiDB Cloud procedures to create a Starter cluster and prepare connection credentials.

## Official Source Content

# Build a {{{ .starter }}} Cluster

This document walks you through the quickest way to get started with TiDB. You will use [TiDB Cloud](https://www.pingcap.com/tidb-cloud) to create a {{{ .starter }}} cluster, connect to it, and run a sample application on it.

If you need to run TiDB on your local machine, see [Starting TiDB Locally](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb).

This document walks you through the quickest way to get started with TiDB Cloud. You will create a TiDB cluster, connect to it, and run a sample application on it.
## Step 1. Create a {{{ .starter }}} cluster {#step-1-create-a-tidb-cloud-cluster}

1. If you do not have a TiDB Cloud account, click [here](https://tidbcloud.com/free-trial) to sign up for an account.

2. [Log in](https://tidbcloud.com/) to your TiDB Cloud account.

3. On the [**Clusters**](https://tidbcloud.com/project/clusters) page, click **Create Cluster**.

4. On the **Create Cluster** page, **Starter** is selected by default. Update the default cluster name if necessary, and then select the region where you want to create your cluster.

5. Click **Create** to create a {{{ .starter }}} cluster.

    Your TiDB Cloud cluster will be created in approximately 30 seconds.

6. After your TiDB Cloud cluster is created, click your cluster name to go to the cluster overview page, and then click **Connect** in the upper-right corner. A connection dialog box is displayed.

7. In the dialog, select your preferred connection method and operating system to get the corresponding connection string. This document uses MySQL client as an example.

8. Click **Generate Password** to generate a random password. The generated password will not show again, so save your password in a secure location. If you do not set a root password, you cannot connect to the cluster.

> **Note:**
>
> For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) clusters, when you connect to your cluster, you must include the prefix for your cluster in the user name and wrap the name with quotation marks. For more information, see [User name prefix](https://docs.pingcap.com/tidbcloud/select-cluster-tier#user-name-prefix).

> **Note:**
>
> For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) clusters, when you connect to your cluster, you must include the prefix for your cluster in the user name and wrap the name with quotation marks. For more information, see [User name prefix](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#user-name-prefix).
