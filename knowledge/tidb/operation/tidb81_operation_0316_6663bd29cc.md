# Connect a Data App to GitHub and synchronize configuration files

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-github-connection.md`
- Source Title: `Deploy Data App Automatically with GitHub`
- Source Heading Path: `Deploy Data App Automatically with GitHub | Deploy Data App Automatically with GitHub > Before you begin | Deploy Data App Automatically with GitHub > Step 1. Connect your Data App to GitHub | Deploy Data App Automatically with GitHub > Step 2. Synchronize Data App configurations with GitHub`
- Source Line Ranges: `5-75`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `data-app`, `github-connection`, `auto-sync`, `deployment`, `configuration-files`, `prerequisites`, `repository`, `branch`, `directory`, `synchronization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0316_6663bd29cc`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-github-connection.md#deploy-data-app-automatically-with-github`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3b90b7da460b435e3d25c8bd198796ca35ebb2d6cc925881619aa4123615adfd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection#deploy-data-app-automatically-with-github
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-github-connection.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented prerequisites, connection steps, Auto Sync & Deployment behavior, or initial synchronization flow for connecting a Data App to GitHub in TiDB Cloud.
- Retrieval Keywords: Deploy Data App Automatically with GitHub, Connect your Data App to GitHub, Auto Sync & Deployment, Configure Auto Sync & Deployment, Install on GitHub, TiDB Cloud Data Service, Confirm Connect, repository branch directory, configuration files, Data App configuration files, deployment history, tidb-cloud-data-service, data_sources/cluster.json, dataapp_config.json, http_endpoints/config.json, http_endpoints/sql
- Follow-up Guidance: After GitHub connection is enabled after App creation, a deployment operation such as re-deploying on the Deployments tab is needed to synchronize the Data App configurations with GitHub.
- Classification Note: This is classified as an operation chunk because the content gives step-by-step procedures and conditions for connecting a Data App to GitHub and synchronizing its configuration files.

## Official Source Content

# Deploy Data App Automatically with GitHub

TiDB Cloud provides a Configuration as Code (CaC) approach to represent your entire Data App configurations as code using the JSON syntax.

By connecting your Data App to GitHub, TiDB Cloud can use the CaC approach and push your Data App configurations as [configuration files](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files) to your preferred GitHub repository and branch.

If **Auto Sync & Deployment** is enabled for your GitHub connection, you can also modify your Data App by updating its configuration files on GitHub. After you push the configuration file changes to GitHub, the new configurations will be deployed in TiDB Cloud automatically.

This document introduces how to deploy your Data App automatically with GitHub and how to manage the GitHub connection.
## Before you begin

Before you connect a Data App to GitHub, make sure that you have the following:

- A GitHub account.
- A GitHub repository with your target branch.

> **Note:**
>
> The GitHub repository is used to store [Data App configuration files](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files) after you connect a Data App to it. If the information (such as the cluster ID and endpoint URL) in the configuration files is sensitive, make sure to use a private repository instead of a public one.
## Step 1. Connect your Data App to GitHub

You can connect your Data App to GitHub when you create the App. For more information, see [Create a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app).

If you did not enable the GitHub connection during the App creation, you can still enable it as follows:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. On the **Settings** tab, click **Connect** in the **Connect to GitHub** area. A dialog box for connection settings is displayed.
4. In the dialog box, perform the following steps:

    1. Click **Install on GitHub**, and then follow the on-screen instructions to install **TiDB Cloud Data Service** as an application on your target repository.
    2. Click **Authorize** to authorize access to the application on GitHub.
    3. Specify the target repository, branch, and directory where you want to store the configuration files of your Data App.

        > **Note:**
        >
        > - The directory must start with a slash (`/`). For example, `/mydata`. If the directory you specified does not exist in the target repository and branch, it will be created automatically.
        > - The combination of repository, branch, and directory identifies the path of the configuration files, which must be unique among Data Apps. If your specified path is already used by another Data App, you need to specify a new path instead. Otherwise, the endpoints configured in the TiDB Cloud console for the current Data App will overwrite the files in your specified path.
        > - If your specified path contains configuration files copied from another Data App and you want to import these files to the current Data App, see [Import configurations of an existing Data App](#import-configurations-of-an-existing-data-app).

    4. To allow Data App changes made in either TiDB Cloud console or GitHub are synchronized with each other, enable **Configure Auto Sync & Deployment**.

        - When it is enabled, the changes made in your specified GitHub directory can be automatically deployed in TiDB Cloud, and the changes made in the TiDB Cloud console can be pushed to GitHub as well. You can find the corresponding deployment and commit information in the Data App deployment history.
        - When it is disabled, the changes made in your specified GitHub directory will **NOT** be deployed in TiDB Cloud, and the changes made in the TiDB Cloud console will **NOT** be pushed to GitHub either.

5. Click **Confirm Connect**.
## Step 2. Synchronize Data App configurations with GitHub

If GitHub connection is enabled when you [create a Data App](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app), TiDB Cloud pushes the configuration files of this Data App to GitHub immediately after the App creation.

If GitHub connection is enabled after the App creation, you need to perform a deployment operation to synchronize the Data App configurations with GitHub. For example, you can click the **Deployments** tab, and then re-deploy a deployment for this Data App.

After the deployment operation, check your specified GitHub directory. You will find that the Data App configuration files have been committed to the directory by `tidb-cloud-data-service`, which means that your Data App is connected to GitHub successfully. The directory structure is as follows:

```
├── <Your Data App directory on GitHub>
│   ├── data_sources
│   │   └── cluster.json  # specifies the linked clusters.
│   ├── dataapp_config.json # specifies the Data APP ID, name, type, version, and description.
│   ├── http_endpoints
│   │   ├── config.json # specifies the endpoints.
│   │   └── sql # contains SQL files of the endpoints.
│   │       ├── <method>-<endpoint-path1>.sql
│   │       ├── <method>-<endpoint-path2>.sql
│   │       └── <method>-<endpoint-path3>.sql
```
