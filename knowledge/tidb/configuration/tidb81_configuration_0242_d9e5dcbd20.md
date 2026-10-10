# Zapier quick start template setup for TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-zapier.md`
- Source Title: `Integrate TiDB Cloud with Zapier`
- Source Heading Path: `Integrate TiDB Cloud with Zapier | Integrate TiDB Cloud with Zapier > Quick start with template | Integrate TiDB Cloud with Zapier > Quick start with template > Prerequisites | Integrate TiDB Cloud with Zapier > Quick start with template > Step 1: Get the template | Integrate TiDB Cloud with Zapier > Quick start with template > Step 2: Set up the trigger | Integrate TiDB Cloud with Zapier > Quick start with template > Step 3: Set up the `Find Table in TiDB Cloud` action | Integrate TiDB Cloud with Zapier > Quick start with template > Step 4: Set up the `Create Row in TiDB Cloud` action | Integrate TiDB Cloud with Zapier > Quick start with template > Step 5: Publish your zap`
- Source Line Ranges: `5-139`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `dashboard`, `sql`
- Topic Tags: `zapier`, `quickstart`, `template`, `github`, `trigger`, `action`, `api-key`, `table-creation`, `row-insert`, `workflow-publishing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0242_d9e5dcbd20`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-zapier.md#integrate-tidb-cloud-with-zapier`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce5977e0c4c574a32975780a3946e8976d0e6a88f6883b8420afd80279764afe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-zapier#integrate-tidb-cloud-with-zapier
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-zapier.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the quick start steps for the Zapier template that adds new GitHub global events to TiDB Cloud rows, including account setup, table creation, trigger testing, row insertion, and publishing the zap.
- Retrieval Keywords: Add new Github global events to TiDB rows, Find Table in TiDB Cloud, Create Row in TiDB Cloud, github_global_event, public key and private key, TiDB Cloud API key, Test trigger, Test action, Publish your zap, SELECT * FROM test.github_global_event
- Follow-up Guidance: It also shows that Zapier can create the github_global_event table during the Find Table test or on the first workflow run and includes a sample SELECT * FROM test.github_global_event result after Create Row succeeds.
- Classification Note: This is classified as configuration because the content is a step-by-step setup workflow in Zapier for connecting GitHub and TiDB Cloud, configuring actions, and publishing a zap.

## Official Source Content

# Integrate TiDB Cloud with Zapier

[Zapier](https://zapier.com) is a no-code automation tool that lets you easily create workflows that involve thousands of apps and services.

Using the [TiDB Cloud app](https://zapier.com/apps/tidb-cloud/integrations) on Zapier enables you to:

- Use TiDB, a MySQL-compatible HTAP database. No need to build locally.
- Make it easier to manage your TiDB Cloud.
- Connect TiDB Cloud to 5000+ apps and automate your workflows.

This guide gives a high-level introduction to the TiDB Cloud app on Zapier and an example of how to use it.
## Quick start with template

[Zap Templates](https://platform.zapier.com/partners/zap-templates) are ready made integrations or Zaps with the apps and core fields pre-selected, for publicly available Zapier integrations.

In this section, we will use the **Add new Github global events to TiDB rows** template as an example to create a workflow. In this workflow, every time a new global event (any [GitHub event](https://docs.github.com/en/developers/webhooks-and-events/events/github-event-types) happens from or to you, on any repo) is created from your GitHub account, Zapier adds a new row to your TiDB Cloud cluster.
### Prerequisites

Before you start, you need:

- A [Zapier account](https://zapier.com/app/login).
- A [GitHub account](https://github.com/login).
- A [TiDB Cloud account](https://tidbcloud.com/signup) and a TiDB Cloud Serverless cluster on TiDB Cloud. For more details, see [TiDB Cloud Quick Start](https://docs.pingcap.com/tidbcloud/tidb-cloud-quickstart#step-1-create-a-tidb-cluster).
### Step 1: Get the template

Go to [TiDB Cloud App on Zapier](https://zapier.com/apps/tidb-cloud/integrations). Choose the **Add new Github global events to TiDB rows** template and click **Try it**. Then you will enter the editor page.
### Step 2: Set up the trigger

In the editor page, you can see the trigger and action. Click the trigger to set it up.

1. Choose app & event

    The template has set the app and the event by default, so you don't need to do anything here. Click **Continue**.

2. Choose account

    Choose a GitHub account that you want to connect with TiDB Cloud. You can either connect a new account or select an existing account. After you set up, click **Continue**.

3. Set up trigger

    The template has set the trigger by default. Click **Continue**.

4. Test trigger

    Click **Test trigger**. If the trigger is successfully set up, you can see the data of a new global event from the GitHub account. Click **Continue**.
### Step 3: Set up the `Find Table in TiDB Cloud` action

1. Choose app & event

    Keep the default value `Find Table` set by the template. Click **Continue**.

2. Choose account

    1. Click the **Sign in** button, and you will be redirected to a new login page.
    2. On the login page, fill in your public key and private key. To get the TiDB Cloud API key, follow the instructions in [TiDB Cloud API documentation](https://docs.pingcap.com/tidbcloud/api/v1beta#section/Authentication/API-Key-Management).
    3. Click **Continue**.

    ![Account](/media/tidb-cloud/zapier/zapier-tidbcloud-account.png)

3. Set up action

    In this step, you need to specify a table in your TiDB Cloud cluster to store the event data. If you do not already have a table, you can create one through this step.

    1. From the drop-down list, choose the project name and cluster name. The connection information of your cluster will be displayed automatically.

        ![Set up project name and cluster name](/media/tidb-cloud/zapier/zapier-set-up-tidbcloud-project-and-cluster.png)

    2. Enter your password.

    3. From the drop-down list, choose the database.

        ![Set up database name](/media/tidb-cloud/zapier/zapier-set-up-tidbcloud-databse.png)

        Zapier queries the databases from TiDB Cloud using the password you entered. If no database is found in your cluster, re-enter your password and refresh the page.

    4. In **The table you want to search** box, fill in `github_global_event`. If the table does not exist, the template uses the following DDL to create the table. Click **Continue**.

        ![The create table DDL](/media/tidb-cloud/zapier/zapier-tidbcloud-create-table-ddl.png)

4. Test action

    Click **Test action**, and Zapier will create the table. You can also skip the test, and the table will be created when this workflow is running for the first time.
### Step 4: Set up the `Create Row in TiDB Cloud` action

1. Choose app & event

    Keep the default value set by the template. Click **Continue**.

2. Choose account

    Select the account you have chosen when you set up the `Find Table in TiDB Cloud` action. Click **Continue**.

    ![Choose account](/media/tidb-cloud/zapier/zapier-tidbcloud-choose-account.png)

3. Set up action

    1. Fill in the **Project Name**, **Cluster Name**, **TiDB Password**, and **Database Name** as in the previous step.

    2. In the **Table Name**, choose the **github_global_event** table from the drop-down list. The columns of the table are displayed.

        ![Table columns](/media/tidb-cloud/zapier/zapier-set-up-tidbcloud-columns.png)

    3. In the **Columns** box, choose the corresponding data from the trigger. Fill in all the columns, and click **Continue**.

        ![Fill in Columns](/media/tidb-cloud/zapier/zapier-fill-in-tidbcloud-triggers-data.png)

4. Test action

    Click **Test action** to create a new row in the table. If you check your TiDB Cloud cluster, you can find the data is written successfully.

   ```sql
   mysql> SELECT * FROM test.github_global_event;
   +-------------+-------------+------------+-----------------+----------------------------------------------+--------+---------------------+
   | id          | type        | actor      | repo_name       | repo_url                                     | public | created_at          |
   +-------------+-------------+------------+-----------------+----------------------------------------------+--------+---------------------+
   | 25324462424 | CreateEvent | shiyuhang0 | shiyuhang0/docs | https://api.github.com/repos/shiyuhang0/docs | True   | 2022-11-18 08:03:14 |
   +-------------+-------------+------------+-----------------+----------------------------------------------+--------+---------------------+
   1 row in set (0.17 sec)
   ```
### Step 5: Publish your zap

Click **Publish** to publish your zap. You can see the zap is running in the [home page](https://zapier.com/app/zaps).

![Publish the zap](/media/tidb-cloud/zapier/zapier-tidbcloud-publish.png)

Now, this zap will automatically record all the global events from your GitHub account into TiDB Cloud.
