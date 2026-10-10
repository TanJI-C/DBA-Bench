# Create an Amazon AppFlow flow to move Salesforce data into TiDB

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-aws-appflow-integration.md`
- Source Title: `Integrate TiDB with Amazon AppFlow`
- Source Heading Path: `Integrate TiDB with Amazon AppFlow > Step 2. Create a flow | Integrate TiDB with Amazon AppFlow > Step 2. Create a flow > Set the flow name | Integrate TiDB with Amazon AppFlow > Step 2. Create a flow > Set the source and destination tables | Integrate TiDB with Amazon AppFlow > Step 2. Create a flow > Set mapping rules | Integrate TiDB with Amazon AppFlow > Step 2. Create a flow > (Optional) Set filters | Integrate TiDB with Amazon AppFlow > Step 2. Create a flow > Confirm and create the flow`
- Source Line Ranges: `94-209`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `flow creation`, `salesforce source`, `tidb destination`, `table creation`, `field mapping`, `filters`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0001_79ed8ae491`
- Source ID: `tidb-docs-8.1:develop/dev-guide-aws-appflow-integration.md#step-2-create-a-flow`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43105470cdb7ca9faf27882d6a3af3d0b895a6ea0415a5a70d597adb20592840`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-aws-appflow-integration#step-2-create-a-flow
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-aws-appflow-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact Amazon AppFlow flow setup to move Salesforce Account data into a TiDB table, including table schema, connection properties, mapping rules, filters, and trigger settings.
- Retrieval Keywords: Create flow, Amazon AppFlow > Flows, Salesforce, TiDB-Connector, sf_account, CREATE TABLE `sf_account`, Account object, Connect to Salesforce, Connect to TiDB-Connector, TLS option to `Yes`, Error handling, Stop the current flow run, Run on demand, Map fields, Account ID -> id, Account Name -> name, Account Type -> type, Billing State/Province -> billing_state, Account Rating -> rating, Industry -> industry, SELECT * FROM sf_account
- Follow-up Guidance: After confirming the source, destination, mappings, optional filters, and review information, the flow is created with Create flow.
- Classification Note: The chunk is classified as data_pipeline because it describes defining a source-to-destination AppFlow transfer from Salesforce to TiDB, including schema preparation and field mapping.

## Official Source Content

## Step 2. Create a flow

Navigate to [Amazon AppFlow > Flows](https://console.aws.amazon.com/appflow/home#/list) and click **Create flow**.

![create flow](/media/develop/aws-appflow-step-create-flow.png)
### Set the flow name

Enter the flow name, and then click **Next**.

![name flow](/media/develop/aws-appflow-step-name-flow.png)
### Set the source and destination tables

Choose the **Source details** and **Destination details**. TiDB connector can be used in both of them.

1. Choose the source name. This document uses **Salesforce** as an example source.

    ![salesforce source](/media/develop/aws-appflow-step-salesforce-source.png)

    After you register to Salesforce, Salesforce will add some example data to your platform. The following steps will use the **Account** object as an example source object.

    ![salesforce data](/media/develop/aws-appflow-step-salesforce-data.png)

2. Click **Connect**.

    1. In the **Connect to Salesforce** dialog, specify the name of this connection, and then click **Continue**.

        ![connect to salesforce](/media/develop/aws-appflow-step-connect-to-salesforce.png)

    2. Click **Allow** to confirm that AWS can read your Salesforce data.

        ![allow salesforce](/media/develop/aws-appflow-step-allow-salesforce.png)

    > **Note:**
    >
    > If your company has already used the Professional Edition of Salesforce, the REST API is not enabled by default. You might need to register a new Developer Edition to use the REST API. For more information, refer to [Salesforce Forum Topic](https://developer.salesforce.com/forums/?id=906F0000000D9Y2IAK).

3. In the **Destination details** area, choose **TiDB-Connector** as the destination. The **Connect** button is displayed.

    ![tidb dest](/media/develop/aws-appflow-step-tidb-dest.png)

4. Before clicking **Connect**, you need to create a `sf_account` table in TiDB for the Salesforce **Account** object. Note that this table schema is different from the sample data in [Tutorial of Amazon AppFlow](https://docs.aws.amazon.com/appflow/latest/userguide/flow-tutorial-set-up-source.html).

    ```sql
    CREATE TABLE `sf_account` (
        `id` varchar(255) NOT NULL,
        `name` varchar(150) NOT NULL DEFAULT '',
        `type` varchar(150) NOT NULL DEFAULT '',
        `billing_state` varchar(255) NOT NULL DEFAULT '',
        `rating` varchar(255) NOT NULL DEFAULT '',
        `industry` varchar(255) NOT NULL DEFAULT '',
        PRIMARY KEY (`id`)
    );
    ```

5. After the `sf_account` table is created, click **Connect**. A connection dialog is displayed.
6. In the **Connect to TiDB-Connector** dialog, enter the connection properties of the TiDB cluster. If you use a {{{ .starter }}} cluster, you need to set the **TLS** option to `Yes`, which lets the TiDB connector use the TLS connection. Then, click **Connect**.

    ![tidb connection message](/media/develop/aws-appflow-step-tidb-connection-message.png)

7. Now you can get all tables in the database that you specified for connection. Choose the **sf_account** table from the drop-down list.

    ![database](/media/develop/aws-appflow-step-database.png)

    The following screenshot shows the configurations to transfer data from the Salesforce **Account** object to the `sf_account` table in TiDB:

    ![complete flow](/media/develop/aws-appflow-step-complete-flow.png)

8. In the **Error handling** area, choose **Stop the current flow run**. In the **Flow trigger** area, choose the **Run on demand** trigger type, which means you need to run the flow manually. Then, click **Next**.

    ![complete step1](/media/develop/aws-appflow-step-complete-step1.png)
### Set mapping rules

Map the fields of the **Account** object in Salesforce to the `sf_account` table in TiDB, and then click **Next**.

- The `sf_account` table is newly created in TiDB and it is empty.

    ```sql
    test> SELECT * FROM sf_account;
    +----+------+------+---------------+--------+----------+
    | id | name | type | billing_state | rating | industry |
    +----+------+------+---------------+--------+----------+
    +----+------+------+---------------+--------+----------+
    ```

- To set a mapping rule, you can select a source field name on the left, and select a destination field name on the right. Then, click **Map fields**, and a rule is set.

    ![add mapping rule](/media/develop/aws-appflow-step-add-mapping-rule.png)

- The following mapping rules (Source field name -> Destination field name) are needed in this document:

    - Account ID -> id
    - Account Name -> name
    - Account Type -> type
    - Billing State/Province -> billing_state
    - Account Rating -> rating
    - Industry -> industry

    ![mapping a rule](/media/develop/aws-appflow-step-mapping-a-rule.png)

    ![show all mapping rules](/media/develop/aws-appflow-step-show-all-mapping-rules.png)
### (Optional) Set filters

If you want to add some filters to your data fields, you can set them here. Otherwise, skip this step and click **Next**.

![filters](/media/develop/aws-appflow-step-filters.png)
### Confirm and create the flow

Confirm the information of the flow to be created. If everything looks fine, click **Create flow**.

![review](/media/develop/aws-appflow-step-review.png)
