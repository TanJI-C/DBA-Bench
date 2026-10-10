# Prepare TiDB Cloud API key and install n8n with TiDB Cloud node

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-n8n.md`
- Source Title: `Integrate TiDB Cloud with n8n`
- Source Heading Path: `Integrate TiDB Cloud with n8n | Integrate TiDB Cloud with n8n > Prerequisites: Get TiDB Cloud API key | Integrate TiDB Cloud with n8n > Step 1: Install n8n | Integrate TiDB Cloud with n8n > Step 2: Install TiDB Cloud node in n8n`
- Source Line Ranges: `5-62`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `api-key`, `n8n`, `installation`, `community-node`, `workflow-setup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0235_a67de89b51`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-n8n.md#integrate-tidb-cloud-with-n8n`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `93fc7c62ed4c584e0bfd0f81d52aaab7c830540ee4d5f47229c29b521b103eed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-n8n#integrate-tidb-cloud-with-n8n
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-n8n.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to get a TiDB Cloud API key and manually install the TiDB Cloud community node in a self-hosted n8n setup.
- Retrieval Keywords: TiDB Cloud API key, Organization Settings > API Keys, Create API Key, npx n8n, docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n, localhost:5678, Community nodes, Install a community node, n8n-nodes-tidb-cloud, TiDB Cloud node
- Follow-up Guidance: After installation, the source says you can search the TiDB Cloud node in Workflow > search bar and drag it to a workspace.
- Classification Note: This is classified as configuration because the content covers obtaining credentials and installing n8n plus the n8n-nodes-tidb-cloud package.

## Official Source Content

# Integrate TiDB Cloud with n8n

[n8n](https://n8n.io/) is an extendable workflow automation tool. With a [fair-code](https://faircode.io/) distribution model, n8n will always have visible source code, be available to self-host, and allow you to add your custom functions, logic, and apps.

This document introduces how to build an auto-workflow: create a TiDB Cloud Serverless cluster, gather Hacker News RSS, store it to TiDB and send a briefing email.
## Prerequisites: Get TiDB Cloud API key

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Organization Settings** > **API Keys**.
3. On the **API Keys** page, click **Create API Key**.
4. Enter a description for the API key, and then click **Next**.
5. Copy the created API key for later use in n8n, and then click **Done**.

For more information, see [TiDB Cloud API Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/api-overview).
## Step 1: Install n8n

There are two ways to install your self-hosting n8n. Choose whichever works for you.

<div label="npm">

1. Install [node.js](https://nodejs.org/en/download/) on your workspace.
2. Download and start n8n by `npx`.

    ```shell
    npx n8n
    ```

</div>
<div label="Docker">

1. Install [Docker](https://www.docker.com/products/docker-desktop) on your workspace.
2. Download and start n8n by `docker`.

    ```shell
    docker run -it --rm --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n
    ```

</div>

After starting n8n, you can visit [localhost:5678](http://localhost:5678) to try out n8n.
## Step 2: Install TiDB Cloud node in n8n

TiDB Cloud node is named `n8n-nodes-tidb-cloud` in the npm repository. You need to install this node manually to control TiDB Cloud with n8n.

1. In the [localhost:5678](http://localhost:5678) page, create an owner account for self-hosting n8n.
2. Go to **Settings** > **Community nodes**.
3. Click **Install a community node**.
4. In the **npm Package Name** field, enter `n8n-nodes-tidb-cloud`.
5. Click **Install**.

Then you can search the **TiDB Cloud** node in **Workflow** > search bar and use the TiDB Cloud node by dragging it to a workspace.
