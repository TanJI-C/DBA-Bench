# Manage TiDB Cloud Serverless branches in the console

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/branch-manage.md`
- Source Title: `Manage TiDB Cloud Serverless Branches`
- Source Heading Path: `Manage TiDB Cloud Serverless Branches | Manage TiDB Cloud Serverless Branches > Required access | Manage TiDB Cloud Serverless Branches > Create a branch | Manage TiDB Cloud Serverless Branches > View branches | Manage TiDB Cloud Serverless Branches > Connect to a branch | Manage TiDB Cloud Serverless Branches > Delete a branch | Manage TiDB Cloud Serverless Branches > Reset a branch | Manage TiDB Cloud Serverless Branches > What's next`
- Source Line Ranges: `5-99`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `serverless`, `branches`, `access-control`, `create-branch`, `view-branches`, `connect`, `delete`, `reset`, `console`, `password`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0285_3ff41ddfff`
- Source ID: `tidb-docs-8.1:tidb-cloud/branch-manage.md#manage-tidb-cloud-serverless-branches`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0af5a6776ddfcf7b765b5a4b2341087633ed133a8529639fca07674a09da14a7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-manage#manage-tidb-cloud-serverless-branches
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/branch-manage.md

## Retrieval Guidance

- Use When: Use this when someone needs console-based steps or access requirements to create, view, connect to, delete, or reset TiDB Cloud Serverless branches.
- Retrieval Keywords: Manage TiDB Cloud Serverless Branches, TiDB Cloud console, TiDB Cloud Serverless branches, Required access, Organization Owner, Project Owner, User roles, Create Branch, Branches, Parent branch, main, Include data up to, Current point in time, Specific date and time, View branches, Connect to a branch, Generate Password, Reset Password, Branch drop-down list, Delete a branch, Reset a branch, synchronizes it with the latest data from its parent, irreversible, GitHub CI/CD pipeline, ticloud branch
- Follow-up Guidance: The source also links to integrating TiDB Cloud Serverless branching into a GitHub CI/CD pipeline and to the `ticloud branch` CLI documentation.
- Classification Note: This is classified as a cloud operation document because it describes TiDB Cloud console procedures and role-based access for managing Serverless branches.

## Official Source Content

# Manage TiDB Cloud Serverless Branches

This document describes how to manage TiDB Cloud Serverless branches using the [TiDB Cloud console](https://tidbcloud.com). To manage it using the TiDB Cloud CLI, see [`ticloud branch`](https://docs.pingcap.com/tidb/stable/tidb-cloud/ticloud-branch-create).
## Required access

- To [create a branch](#create-a-branch) or [connect to a branch](#connect-to-a-branch), you must be in the `Organization Owner` role of your organization or the `Project Owner` role of the target project.
- To [view branches](#create-a-branch) for clusters in a project, you must belong to that project.

For more information about permissions, see [User roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles).
## Create a branch

> **Note:**
>
> You can only create branches for TiDB Cloud Serverless clusters that are created after July 5, 2023. See [Limitations and quotas](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-overview#limitations-and-quotas) for more limitations.

To create a branch, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.
2. Click **Branches** in the left navigation pane.
3. In the upper-right corner of the **Branches** page, click **Create Branch**. A dialog is displayed.

    Alternatively, to create a branch from an existing parent branch, locate the row of your target parent branch, and then click **...** > **Create Branch** in the **Action** column.

4. In the **Create Branch** dialog, configure the following options:

    - **Name**: enter a name for the branch.
    - **Parent branch**: select the original cluster or an existing branch. `main` represents the current cluster.
    - **Include data up to**: choose one of the following:
        - **Current point in time**: create a branch from the current state.
        - **Specific date and time**: create a branch from a specified time.

5. Click **Create**.

Depending on the data size in your cluster, the branch creation will be completed in a few minutes.
## View branches

To view branches for your cluster, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.
2. Click **Branches** in the left navigation pane.

    The branch list of the cluster is displayed in the right pane.
## Connect to a branch

To connect to a branch, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.
2. Click **Branches** in the left navigation pane.
3. In the row of your target branch to be connected, click **...** in the **Action** column.
4. Click **Connect** in the drop-down list. The dialog for the connection information is displayed.
5. Click **Generate Password** or **Reset Password** to create or reset the root password.
6. Connect to the branch using the connection information.

Alternatively, you can get the connection string from the cluster overview page:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.
2. Click **Connect** in the upper-right corner.
3. Select the branch you want to connect to in the `Branch` drop-down list.
4. Click **Generate Password** or **Reset Password** to create or reset the root password.
5. Connect to the branch using the connection information.
## Delete a branch

To delete a branch, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.
2. Click **Branches** in the left navigation pane.
3. In the row of your target branch to be deleted, click **...** in the **Action** column.
4. Click **Delete** in the drop-down list.
5. Confirm the deletion.
## Reset a branch

Resetting a branch synchronizes it with the latest data from its parent.

> **Note:**
> 
> This operation is irreversible. Before resetting a branch, make sure that you have backed up any important data.

To reset a branch, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, and then click the name of your target TiDB Cloud Serverless cluster to go to its overview page.
2. Click **Branches** in the left navigation pane.
3. In the row of your target branch to be reset, click **...** in the **Action** column.
4. Click **Reset** in the drop-down list.
5. Confirm the reset.
## What's next

- [Integrate TiDB Cloud Serverless branching into your GitHub CI/CD pipeline](https://docs.pingcap.com/tidb/stable/tidb-cloud/branch-github-integration)
