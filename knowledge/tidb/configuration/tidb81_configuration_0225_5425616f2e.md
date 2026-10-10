# Configure Data App properties, links, and deployments

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/data-service-manage-data-app.md`
- Source Title: `Manage a Data App`
- Source Heading Path: `Manage a Data App > Configure a Data App | Manage a Data App > Configure a Data App > Edit Data App properties | Manage a Data App > Configure a Data App > Manage GitHub connection | Manage a Data App > Configure a Data App > Manage linked data sources | Manage a Data App > Configure a Data App > Manage an API key | Manage a Data App > Configure a Data App > Manage an endpoint | Manage a Data App > Configure a Data App > Manage a custom domain | Manage a Data App > Configure a Data App > Manage deployments`
- Source Line Ranges: `48-117`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `data app`, `properties`, `github integration`, `linked clusters`, `api keys`, `endpoints`, `custom domain`, `deployment settings`, `auto sync`, `review draft`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0225_5425616f2e`
- Source ID: `tidb-docs-8.1:tidb-cloud/data-service-manage-data-app.md#configure-a-data-app`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `99259ce6257211624af791041333cb06a1a17fd9d2592583946eadc55b8102d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-data-app#configure-a-data-app
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/data-service-manage-data-app.md

## Retrieval Guidance

- Use When: Use this chunk when you need to configure an existing Data App in TiDB Cloud, such as editing properties, linking or removing clusters, or managing deployment settings like Auto Sync & Deployment and Review Draft.
- Retrieval Keywords: Configure a Data App, Data App Properties, App name, version, description, Linked Data Sources, Add Cluster, Delete, existing endpoints in the Data App cannot access it, Deployment Configuration, Config, Auto Sync & Deployment, Review Draft, deployment history, Manage GitHub connection, Manage an API key, Manage an endpoint, Manage a custom domain
- Follow-up Guidance: The content links to separate documents for GitHub connection, API key management, endpoint management, and custom domain management.
- Classification Note: This is classified as configuration because the content focuses on changing Data App settings, linked data sources, and deployment behavior for an existing Data App.

## Official Source Content

## Configure a Data App

You can edit the name, version, or description of a Data App, and manage its GitHub connection, linked data sources, API keys, endpoints, and deployments.
### Edit Data App properties

You can edit the name, version, and description of a Data App. To edit Data App properties, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, click the name of your target Data App to view its details.
3. In the **Data App Properties** area, click <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" color="gray.1"><path d="M11 3.99998H6.8C5.11984 3.99998 4.27976 3.99998 3.63803 4.32696C3.07354 4.61458 2.6146 5.07353 2.32698 5.63801C2 6.27975 2 7.11983 2 8.79998V17.2C2 18.8801 2 19.7202 2.32698 20.362C2.6146 20.9264 3.07354 21.3854 3.63803 21.673C4.27976 22 5.11984 22 6.8 22H15.2C16.8802 22 17.7202 22 18.362 21.673C18.9265 21.3854 19.3854 20.9264 19.673 20.362C20 19.7202 20 18.8801 20 17.2V13M7.99997 16H9.67452C10.1637 16 10.4083 16 10.6385 15.9447C10.8425 15.8957 11.0376 15.8149 11.2166 15.7053C11.4184 15.5816 11.5914 15.4086 11.9373 15.0627L21.5 5.49998C22.3284 4.67156 22.3284 3.32841 21.5 2.49998C20.6716 1.67156 19.3284 1.67155 18.5 2.49998L8.93723 12.0627C8.59133 12.4086 8.41838 12.5816 8.29469 12.7834C8.18504 12.9624 8.10423 13.1574 8.05523 13.3615C7.99997 13.5917 7.99997 13.8363 7.99997 14.3255V16Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>, modify the App name, version, or description, and then click **Confirm**.
### Manage GitHub connection

For more information, see [Deploy automatically with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).
### Manage linked data sources

You can add or remove linked clusters for a Data App.

To link a cluster to a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App and click the name of your target Data App to view its details.
3. In the **Linked Data Sources** area, click **Add Cluster**.
4. In the displayed dialog box, select a cluster from the list and click **Add**.

To remove a linked cluster from a Data App, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App and click the name of your target Data App to view its details.
3. In the **Linked Data Sources** area, locate the target linked cluster you want to remove from the Data App, and click **Delete** in the **Action** column.
4. In the displayed dialog box, confirm the removal.

    After you remove a linked cluster, the cluster is not deleted, but the existing endpoints in the Data App cannot access it.
### Manage an API key

For more information, see [Manage an API key](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-api-key).
### Manage an endpoint

For more information, see [Manage an endpoint](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-endpoint).
### Manage a custom domain

For more information, see [Manage a custom domain](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-custom-domain).
### Manage deployments

To manage deployments, perform the following steps:

1. Navigate to the [**Data Service**](https://tidbcloud.com/project/data-service) page of your project.
2. In the left pane, locate your target Data App and click the name of your target Data App to view its details.
3. In the **Deployment Configuration** area, click **Config**. The dialog for deployment configuration is displayed.
4. In the dialog, choose your desired setting of **Auto Sync & Deployment** and **Review Draft**.

    - **Auto Sync & Deployment**

        - This option can be enabled only when your Data App is connected to GitHub. For more information, see [Deploy automatically with GitHub](https://docs.pingcap.com/tidb/stable/tidb-cloud/data-service-manage-github-connection).
        - When it is enabled, the changes made in your specified GitHub directory can be automatically deployed in TiDB Cloud, and the changes made in the TiDB Cloud console can be pushed to GitHub as well. You can find the corresponding deployment and commit information in the Data App deployment history.
        - When it is disabled, the changes made in your specified GitHub directory will **NOT** be deployed in TiDB Cloud, and the changes made in the TiDB Cloud console will **NOT** be pushed to GitHub either.

    - **Review Draft**

        - When it is enabled, you can review the Data App changes you made in the TiDB Cloud console before the deployment. Based on the review, you can either deploy or discard the changes.
        - When it is disabled, the Data App changes you made in the TiDB Cloud console are deployed directly.

5. In the **Action** column, you can edit or re-deploy your changes according to your needs.
