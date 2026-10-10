# Modify a Data App through GitHub or console and import existing configurations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-github-connection.md`
- Source Title: `Deploy Data App Automatically with GitHub`
- Source Heading Path: `Deploy Data App Automatically with GitHub > Step 3. Modify your Data App | Deploy Data App Automatically with GitHub > Step 3. Modify your Data App > Option 1: Modify your Data App by updating files on GitHub | Deploy Data App Automatically with GitHub > Step 3. Modify your Data App > Option 2: Modify your Data App in the TiDB Cloud console | Deploy Data App Automatically with GitHub > Import configurations of an existing Data App`
- Source Line Ranges: `76-130`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `data-app`, `github`, `console`, `auto-sync`, `deployment-history`, `configuration-files`, `endpoints`, `import`, `app-id`, `conflict-resolution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0317_345e65ca46`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-github-connection.md#step-3-modify-your-data-app`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `30714288aba620a56d22e17916ab051a05dfc313f2bb1b2a39310e676cc90a30`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection#step-3-modify-your-data-app
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-github-connection.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented ways to modify a GitHub-connected Data App from GitHub or the TiDB Cloud console, handle conflicts, or import configuration files from an existing Data App.
- Retrieval Keywords: Step 3. Modify your Data App, Option 1: Modify your Data App by updating files on GitHub, Option 2: Modify your Data App in the TiDB Cloud console, Auto Sync & Deployment, deployment history, Discard Draft, Deploy and Push to GitHub, data_source/cluster.json, http_endpoints/config.json, http_endpoints/sql/method-<endpoint-path>.sql, datapp_config.json, app_id, app_name, Import configurations of an existing Data App, copied configuration files, refresh the webpage
- Follow-up Guidance: After GitHub file changes are pushed or console changes are deployed, you can view deployment status and commit information in the deployment history.
- Classification Note: This is classified as an operation chunk because the content describes modification workflows, file-specific constraints, conflict handling choices, and the import procedure for an existing Data App configuration.

## Official Source Content

## Step 3. Modify your Data App

When **Auto Sync & Deployment** is enabled, you can modify your Data App using either GitHub or the TiDB Cloud console.

- [Option 1: Modify your Data App by updating files on GitHub](#option-1-modify-your-data-app-by-updating-files-on-github)
- [Option 2: Modify your Data App in the TiDB Cloud console](#option-2-modify-your-data-app-in-the-tidb-cloud-console)

> **Note:**
>
> If you have modified your Data App on GitHub and TiDB Cloud console at the same time, to resolve conflicts, you can choose either discard the changes made in the console or let the console changes overwrite the GitHub changes.
### Option 1: Modify your Data App by updating files on GitHub

When updating the configuration files, pay attention to the following:

| File directory  | Notes |
| ---------|---------|
| `data_source/cluster.json`     | When updating this file, make sure that you have access to the linked clusters. You can get the cluster ID from the cluster URL. For example, if the cluster URL is `https://tidbcloud.com/clusters/1234567891234567890/overview`, the cluster ID is `1234567891234567890`. |
| `http_endpoints/config.json`     | When modifying the endpoints, make sure that you follow the rules described in [HTTP endpoint configuration](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files#http-endpoint-configuration).   |
| `http_endpoints/sql/method-<endpoint-path>.sql`| To add or remove SQL files in the `http_endpoints/sql` directory, you need to update the corresponding endpoint configurations as well. |
| `datapp_config.json` | Do not change the `app_id` field in this file unless your `dataapp_config.json` file is copied from another Data App and you want to update it to the ID of your current Data App. Otherwise, the deployment triggered by this modification will fail. |

For more information about the field configuration in these files, see [Data App configuration files](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files).

After the file changes are committed and pushed, TiDB Cloud will automatically deploy the Data App with the latest changes on GitHub. You can view the deployment status and commit information in the deployment history.
### Option 2: Modify your Data App in the TiDB Cloud console

After [modifying your Data App endpoints](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint) in the TiDB Cloud console (such as modifying endpoints), you can review and deploy the changes to GitHub as follows:

1. Click **Deploy** in the upper-right corner. A dialog is displayed for you to review the changes you made.
2. Depending on your review, do one of the following:

    - If you still want to make further changes based on the current draft, close this dialog and make the changes.
    - If you want to revert the current changes to the last deployment, click **Discard Draft**.
    - If the current changes look fine, write a change description (optional), and then click **Deploy and Push to GitHub**. The deployment status will be displayed in the top banner.

If the deployment is successful, the changes made in the TiDB Cloud console will be pushed to GitHub automatically.
## Import configurations of an existing Data App

To import configurations of an existing Data App to a new Data App, take the following steps:

1. Copy configuration files of the existing Data App to a new branch or directory on GitHub.
2. On the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project, [create a new Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#create-a-data-app) without connecting to GitHub.
3. [Connect your new Data App to GitHub](#step-1-connect-your-data-app-to-github) with **Auto Sync & Deployment** enabled. When you specify the target repository, branch, and directory for your new Data App, use your new path with the copied configuration files.
4. Get the ID and name of your new Data App. You can click the name of your new Data App in the left pane and get the App ID and name in the **Data App Properties** area of the right pane.
5. In your new path on GitHub, update the `app_id` and `app_name` in the `datapp_config.json` file to the ID and name you get, and then push the changes.

    After the file changes are pushed to GitHub, TiDB Cloud will automatically deploy your new Data App with the latest changes.

6. To view the imported configurations from GitHub, refresh the webpage of the TiDB Cloud console.

    You can also view the deployment status and commit information in the deployment history.
