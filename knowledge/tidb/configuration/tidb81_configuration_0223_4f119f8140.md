# Create your own Data App and configure an endpoint

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-get-started.md`
- Source Title: `Get Started with Data Service`
- Source Heading Path: `Get Started with Data Service > Get started with your own Data App | Get Started with Data Service > Get started with your own Data App > Step 1. Create a Data App | Get Started with Data Service > Get started with your own Data App > Step 2. Develop an endpoint | Get Started with Data Service > Get started with your own Data App > Step 2. Develop an endpoint > Configure properties`
- Source Line Ranges: `42-98`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `data app`, `endpoint`, `github integration`, `auto sync`, `deployment review`, `path`, `request method`, `endpoint url`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0223_4f119f8140`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-get-started.md#get-started-with-your-own-data-app`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `24836d1b28bfb38e0daac9e2d230eef99ae91aea876b36fecd8e5e8751231a47`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-get-started#get-started-with-your-own-data-app
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-get-started.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to create your own Data App in TiDB Cloud Data Service and configure endpoint properties such as Path, Endpoint URL, Request Method, and optional GitHub connection settings.
- Retrieval Keywords: Create Data App, Create DataApp, Connect to GitHub, Install on GitHub, Authorize, target repository, branch, directory must start with a slash, Auto Sync & Deployment, Review Draft, Create Endpoint, Properties, Path, Endpoint URL, Request Method, GET, POST, PUT, DELETE, https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/
- Follow-up Guidance: The source also states that the repository, branch, and directory combination must be unique among Data Apps and that connected Data Apps have Auto Sync & Deployment and Review Draft enabled by default.
- Classification Note: This is classified as a configuration chunk because the content focuses on setting up a Data App and defining endpoint and GitHub integration properties in the TiDB Cloud console.

## Official Source Content

## Get started with your own Data App

To get started with Data Service, you can also create your own Data App, and then develop, test, deploy, and call endpoints according to the following steps.
### Step 1. Create a Data App

 To create a Data App, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), click <MDSvgIcon name="icon-left-data-service" /> **Data Service** in the left navigation pane.

2. On the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project, click <MDSvgIcon name="icon-create-data-app" /> **Create DataApp** in the left pane.

    > **Tip:**
    >
    > If this is the first Data App in your project, click **Create Data App** in the middle of the page.

3. In the **Create Data App** dialog, enter a name, a description, and select clusters that you want the Data App to access.

    > **Note:**
    >
    > By default, the Data App type is **Standard Data App**. If you want to create a **Chat2Query Data App**, refer to [Get Started with Chat2Query API](https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-api) instead of this document.

4. (Optional) To automatically deploy endpoints of the Data App to your preferred GitHub repository and branch, enable **Connect to GitHub**, and then do the following:

    1. Click **Install on GitHub**, and then follow the on-screen instructions to install **TiDB Cloud Data Service** as an application on your target repository.
    2. Go back to the TiDB Cloud console, and then click **Authorize** to authorize access to the application on GitHub.
    3. Specify the target repository, branch, and directory where you want to save the configuration files of your Data App.

    > **Note:**
    >
    > - The directory must start with a slash (`/`). For example, `/mydata`. If the directory you specified does not exist in the target repository and branch, it will be created automatically.
    > - The combination of repository, branch, and directory identifies the path of the configuration files, which must be unique among Data Apps. If your specified path is already used by another Data App, you need to specify a new path instead. Otherwise, the endpoints configured in the TiDB Cloud console for the current Data App will overwrite the files in your specified path.

5. Click **Create Data App**. The [**Data Service**](https://tidbcloud.com/project/data-service) details page is displayed.

6. If you have configured to connect your Data App to GitHub, check your specified GitHub directory. You will find that the [Data App configuration files](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-app-config-files) have been committed to the directory by `tidb-cloud-data-service`, which means that your Data App is connected to GitHub successfully.

    For your new Data App, **Auto Sync & Deployment** and **Review Draft** are enabled by default so you can easily synchronize Data App changes between TiDB Cloud console and GitHub and review changes before the deployment. For more information about the GitHub integration, see [Deploy your Data App changes with GitHub automatically](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).
### Step 2. Develop an endpoint

An endpoint is a web API that you can customize to execute SQL statements.

To create a new endpoint, locate the newly created Data App and click **+** **Create Endpoint** to the right of the App name.
#### Configure properties

On the right pane, click the **Properties** tab and set properties for the endpoint, such as:

- **Path**: the path that users use to access the endpoint. The combination of the request method and the path must be unique within a Data App.

- **Endpoint URL**: (read-only) the URL is automatically generated based on the region where the corresponding cluster is located, the service URL of the Data App, and the path of the endpoint. For example, if the path of the endpoint is `/my_endpoint/get_id`, the endpoint URL is `https://<region>.data.tidbcloud.com/api/v1beta/app/<App ID>/endpoint/my_endpoint/get_id`.

- **Request Method**: the HTTP method of the endpoint. You can use `GET` to retrieve data, use `POST` to create or insert data, use `PUT` to update or modify data, and use `DELETE` to delete data.

For more information about endpoint properties, see [Configure properties](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint#configure-properties).
