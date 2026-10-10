# TiDB Cloud Vercel integration workflow and connection management

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-vercel.md`
- Source Title: `Integrate TiDB Cloud with Vercel`
- Source Heading Path: `Integrate TiDB Cloud with Vercel > Connect via the TiDB Cloud Vercel integration | Integrate TiDB Cloud with Vercel > Connect via the TiDB Cloud Vercel integration > Integration workflow | Integrate TiDB Cloud with Vercel > Connect via the TiDB Cloud Vercel integration > Configure connections`
- Source Line Ranges: `68-169`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `vercel`, `integration`, `workflow`, `serverless`, `data-app`, `environment-variables`, `branching`, `project-settings`, `connection-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0239_8b98808a2d`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-vercel.md#connect-via-the-tidb-cloud-vercel-integration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `237fb59b980c536440f1379c729cb150da554cfb03faca9493d2cc6968f5b102`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-vercel#connect-via-the-tidb-cloud-vercel-integration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-vercel.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to connect a Vercel project to TiDB Cloud through the TiDB Cloud Vercel integration, which environment variables are added, or how to add and remove integration links later.
- Retrieval Keywords: Connect via the TiDB Cloud Vercel integration, TiDB Cloud integration, Vercel's Integrations Marketplace, Add Integration, Integration workflow, Cluster, Data App, TiDB Cloud Serverless clusters, manual method, Branching, Settings > Environment Variables, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE, DATABASE_URL, DATA_APP_BASE_URL, DATA_APP_PUBLIC_KEY, DATA_APP_PRIVATE_KEY, Integrations, Manage, Configure, Add Link, Remove
- Follow-up Guidance: The content notes that removing a connection also removes the environment variables created by the integration workflow from the Vercel project, but does not affect the data of the TiDB Cloud Serverless cluster.
- Classification Note: This is classified as configuration because the content provides the integration workflow, connection type selection, framework-based environment variable setup, optional Branching, and later connection management in Vercel.

## Official Source Content

## Connect via the TiDB Cloud Vercel integration

To connect via the TiDB Cloud Vercel integration, go to the [TiDB Cloud integration](https://vercel.com/integrations/tidb-cloud) page from the [Vercel's Integrations Marketplace](https://vercel.com/integrations). Using this method, you can choose which cluster to connect to, and TiDB Cloud will automatically generate all the necessary environment variables for your Vercel projects.

> **Note:**
>
> This method is only available for TiDB Cloud Serverless clusters. If you want to connect to a TiDB Cloud Dedicated cluster, use the [manual method](#connect-via-manually-setting-environment-variables).
### Integration workflow

The detailed steps are as follows:

<div label="Cluster">

1. Click **Add Integration** in the upper-right area of the [TiDB Cloud Vercel integration](https://vercel.com/integrations/tidb-cloud) page. The **Add TiDB Cloud** dialog is displayed.
2. Select the scope of your integration in the drop-down list and click **Continue**.
3. Select the Vercel projects to which the integration will be added and click **Continue**.
4. Confirm the required permissions for integration and click **Add Integration**. Then you are directed to an integration page of the TiDB Cloud console.
5. On the integration page, do the following:

    1. Select your target Vercel projects and click **Next**.
    2. Select your target TiDB Cloud organization and project.
    3. Select **Cluster** as your connection type.
    4. Select your target TiDB Cloud cluster. If the **Cluster** drop-down list is empty or you want to select a new TiDB Cloud Serverless cluster, click **+ Create Cluster** in the list to create one.
    5. Select the database that you want to connect to. If the **Database** drop-down list is empty or you want to select a new Database, click **+ Create Database** in the list to create one.
    6. Select the framework that your Vercel projects are using. If the target framework is not listed, select **General**. Different frameworks determine different environment variables.
    7. Choose whether to enable **Branching** to create new branches for preview environments.
    8. Click **Add Integration and Return to Vercel**.

![Vercel Integration Page](/media/tidb-cloud/vercel/integration-link-cluster-page.png)

6. Get back to your Vercel dashboard, go to your Vercel project, click **Settings** > **Environment Variables**, and check whether the environment variables for your target TiDB cluster have been automatically added.

    If the following variables have been added, the integration is completed.

    **General**

    ```shell
    TIDB_HOST
    TIDB_PORT
    TIDB_USER
    TIDB_PASSWORD
    TIDB_DATABASE
    ```

    **Prisma**

    ```
    DATABASE_URL
    ```

    **TiDB Cloud Serverless Driver**

    ```
    DATABASE_URL
    ```

</div>

<div label="Data App">

1. Click **Add Integration** in the upper-right area of the [TiDB Cloud Vercel integration](https://vercel.com/integrations/tidb-cloud) page. The **Add TiDB Cloud** dialog is displayed.
2. Select the scope of your integration in the drop-down list and click **Continue**.
3. Select the Vercel projects to which the integration will be added and click **Continue**.
4. Confirm the required permissions for integration and click **Add Integration**. Then you are directed to an integration page of the TiDB Cloud console.
5. On the integration page, do the following:

    1. Select your target Vercel projects and click **Next**.
    2. Select your target TiDB Cloud organization and project.
    3. Select **Data App** as your connection type.
    4. Select your target TiDB Data App.
    6. Click **Add Integration and Return to Vercel**.

![Vercel Integration Page](/media/tidb-cloud/vercel/integration-link-data-app-page.png)

6. Get back to your Vercel dashboard, go to your Vercel project, click **Settings** > **Environment Variables**, and check whether the environment variables for your target Data App have been automatically added.

    If the following variables have been added, the integration is completed.

    ```shell
    DATA_APP_BASE_URL
    DATA_APP_PUBLIC_KEY
    DATA_APP_PRIVATE_KEY
    ```

</div>
### Configure connections

If you have installed [TiDB Cloud Vercel integration](https://vercel.com/integrations/tidb-cloud), you can add or remove connections inside the integration.

1. In your Vercel dashboard, click **Integrations**.
2. Click **Manage** in the TiDB Cloud entry.
3. Click **Configure**.
4. Click **Add Link** or **Remove** to add or remove connections.

    ![Vercel Integration Configuration Page](/media/tidb-cloud/vercel/integration-vercel-configuration-page.png)

    When you remove a connection, the environment variables set by the integration workflow are removed from the Vercel project, too. However, this action does not affect the data of the TiDB Cloud Serverless cluster.
