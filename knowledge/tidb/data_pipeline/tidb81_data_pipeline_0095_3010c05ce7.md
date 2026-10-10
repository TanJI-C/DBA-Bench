# Build and run an n8n workflow with TiDB Cloud, RSS, code, and Gmail

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-n8n.md`
- Source Title: `Integrate TiDB Cloud with n8n`
- Source Heading Path: `Integrate TiDB Cloud with n8n > Step 3: Build your workflow | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > (Optional) Create a TiDB Cloud Serverless cluster | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow > Use a manual trigger as the workflow's starter | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow > Create a table used to insert data | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow > Get the Hacker News RSS | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow > Insert data to TiDB | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow > Build message | Integrate TiDB Cloud with n8n > Step 3: Build your workflow > Create a workflow > Send message by Gmail | Integrate TiDB Cloud with n8n > Step 4: Run your workflow`
- Source Line Ranges: `63-209`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`
- Topic Tags: `workflow`, `serverless-cluster`, `schedule-trigger`, `execute-sql`, `rss`, `insert`, `javascript`, `gmail`, `automation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0095_3010c05ce7`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-n8n.md#step-3-build-your-workflow`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `15f33a45b03b10d3fe5ddfc0bf52cd945ad9f70604b81475d434d6237f926e92`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-n8n#step-3-build-your-workflow
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-n8n.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the example n8n workflow that creates or uses a TiDB Cloud Serverless cluster, reads Hacker News RSS, inserts rows into TiDB, builds an HTML message, and sends it with Gmail.
- Retrieval Keywords: Create Serverless Cluster, Schedule Trigger, RSS Read, Code, Gmail, Execute SQL, Insert, https://hnrss.org/frontpage, CREATE TABLE IF NOT EXISTS hacker_news_briefing, hacker_news_briefing, creator, title, link, pubdate, comments, content, guid, isodate, Run Once for All Items, Hacker News Briefing, {{ $json["response"] }}, Execute Workflow
- Follow-up Guidance: The source says that after testing with Execute Workflow, you can activate the workflow in the Workflows panel to get front-page Hacker News articles every day.
- Classification Note: This is classified as a data pipeline because the content defines a multi-node workflow that schedules ingestion, executes SQL, inserts RSS data into TiDB, transforms message content, and sends email output.

## Official Source Content

## Step 3: Build your workflow

In this step, you will create a new workflow to insert some data to TiDB when you click **Execute** button.

This example usage workflow would use the following nodes:

- [Schedule Trigger](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.scheduletrigger/)
- [RSS Read](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.rssfeedread/)
- [Code](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.code/)
- [Gmail](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.gmail/)
- [TiDB Cloud node](https://www.npmjs.com/package/n8n-nodes-tidb-cloud)

The final workflow should look like the following image.

![img](/media/tidb-cloud/integration-n8n-workflow-rss.jpg)
### (Optional) Create a TiDB Cloud Serverless cluster

If you don't have a TiDB Cloud Serverless cluster, you can use this node to create one. Otherwise, feel free to skip this operation.

1. Navigate to **Workflows** panel, and click **Add workflow**.
2. In new workflow workspace, click **+** in the top right corner and choose **All** field.
3. Search `TiDB Cloud` and drag it to the workspace.
4. Enter credentials, which is the TiDB Cloud API key, for the TiDB Cloud node.
5. In the **Project** list, select your project.
6. In the **Operation** list, select `Create Serverless Cluster`.
7. In the **Cluster Name** box, enter a cluster name.
8. In the **Region** list, select a region.
9. In the **Password** box, enter a password used to log in to your TiDB clusters.
10. Click **Execute Node** to run the node.

> **Note:**
>
> It takes several seconds to create a new TiDB Cloud Serverless cluster.
### Create a workflow
#### Use a manual trigger as the workflow's starter

1. If you don't have a workflow yet, navigate to the **Workflows** panel, and click **Start from scratch**. Otherwise, skip this step.
2. Click **+** in the top right corner and search `schedule trigger`.
3. Drag the manual trigger node to your workspace, and double-click the node. The **Parameters** dialog is displayed.
4. Configure the rule as follows:

    - **Trigger Interval**: `Days`
    - **Days Between Triggers**: `1`
    - **Trigger at Hour**: `8am`
    - **Trigger at Minute**: `0`

This trigger will execute your workflow every morning at 8 AM.
#### Create a table used to insert data

1. Click **+** to the right of the manual trigger node.
2. Search `TiDB Cloud` and add it to the workspace.
3. In the **Parameters** dialog, enter the credential for the TiDB Cloud node. The credential is your TiDB Cloud API key.
4. In the **Project** list, select your project.
5. In the **Operation** list, select `Execute SQL`.
6. Select the cluster. If you have not seen your new cluster in the list, you need to wait a few minutes until the cluster creation is completed.
7. In the **User** list, select a user. TiDB Cloud always creates a default user, so you don't have to manually create one.
8. In the **Database** box, enter `test`.
9. Enter your database password.
10. In the **SQL** box, enter the following SQL:

    ```sql
    CREATE TABLE IF NOT EXISTS hacker_news_briefing (creator VARCHAR (200), title TEXT,  link VARCHAR(200), pubdate VARCHAR(200), comments VARCHAR(200), content TEXT, guid VARCHAR (200), isodate VARCHAR(200));
    ```

11. Click **Execute node** to create the table.
#### Get the Hacker News RSS

1. Click **+** to the right of the TiDB Cloud node.
2. Search `RSS Read` and add it to the workspace.
3. In the **URL** box, enter `https://hnrss.org/frontpage`.
#### Insert data to TiDB

1. Click **+** to the right of the RSS Read node.
2. Search `TiDB Cloud` and add it to the workspace.
3. Select the credentials that you entered the previous TiDB Cloud node.
4. In the **Project** list, select your project.
5. In the **Operation** list, select `Insert`.
6. In **Cluster**, **User**, **Database** and **Password** boxes, enter the corresponding values.
7. In the **Table** box, enter the `hacker_news_briefing` table.
8. In the **Columns** box, enter `creator, title, link, pubdate, comments, content, guid, isodate`.
#### Build message

1. Click **+** to the right of the RSS Feed Read node.
2. Search `code` and add it to the workspace.
3. Select the `Run Once for All Items` mode.
4. In the **JavaScript** box, copy and paste the following code.

    ```javascript
    let message = "";

    // Loop the input items
    for (item of items) {
      message += `
          <h3>${item.json.title}</h3>
          <br>
          ${item.json.content}
          <br>
          `
    }

    let response =
        `
          <!DOCTYPE html>
          <html>
          <head>
          <title>Hacker News Briefing</title>
        </head>
        <body>
            ${message}
        </body>
        </html>
        `
    // Return our message
    return [{json: {response}}];
    ```
#### Send message by Gmail

1. Click **+** to the right of the code node.
2. Search `gmail` and add it to the workspace.
3. Enter the credential for the Gmail node. For detailed instructions, refer to [n8n documentation](https://docs.n8n.io/integrations/builtin/credentials/google/oauth-single-service/).
4. In the **Resource** list, select `Message`.
5. In the **Operation** list, select `Send`.
6. In the **To** box, enter your email.
7. In the **Subject** box, enter `Hacker News Briefing`.
8. In the **Email Type** box, select `HTML`.
9. In the **Message** box, click `Expression` and enter `{{ $json["response"] }}`.

    > **Note:**
    >
    > You must hover over the **Message** box and select the **Expression** pattern.
## Step 4: Run your workflow

After building up the workflow, you can click **Execute Workflow** to test run it.

If the workflow runs as expected, you'll get Hacker News briefing emails. These news contents will be logged to your TiDB Cloud Serverless cluster, so you don't have to worry about losing them.

Now you can activate this workflow in the **Workflows** panel. This workflow will help you get the front-page articles on Hacker News every day.
