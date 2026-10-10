# TiDB Cloud node fields and limitations in n8n

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-n8n.md`
- Source Title: `Integrate TiDB Cloud with n8n`
- Source Heading Path: `Integrate TiDB Cloud with n8n > TiDB Cloud node core > Fields | Integrate TiDB Cloud with n8n > TiDB Cloud node core > Limitations`
- Source Line Ranges: `222-295`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `api-key`, `fields`, `supported-operations`, `serverless-cluster`, `execute-sql`, `delete`, `insert`, `update`, `limitations`, `multi-statement`, `workflow-items`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0806_dc4b8d5d61`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-n8n.md#fields`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7761c5fcd205fd706643e6880f0fab7ae1063c5a1de94fc5ada0dbaef536b87b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-n8n#fields
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-n8n.md

## Retrieval Guidance

- Use When: Use this chunk when identifying the required TiDB Cloud node fields in n8n for Create Serverless Cluster, Execute SQL, Delete, Insert, or Update, or when checking documented limitations of Execute SQL, Delete, Insert, and Update.
- Retrieval Keywords: TiDB Cloud node fields, n8n TiDB Cloud API key, Create Serverless Cluster fields, Execute SQL fields, Delete fields, Insert fields, Update fields, Credential for TiDB Cloud API, Project, Operation, Cluster, Region, Password, User, Database, SQL, Table, Delete Key, Update Key, Columns, From list mode, Name mode, workflow items, n8n items, tidb_multi_statement_mode, only one SQL statement is allowed, Delete and Update only support specifying one key, comma-separated list in the Columns field
- Follow-up Guidance: The source also points to Get TiDB Cloud API Key for creating the API credential and notes that n8n items are the incoming data each node acts on.
- Classification Note: This is reference content because it enumerates operation-specific field definitions and explicit limitations for the TiDB Cloud node in n8n.

## Official Source Content

### Fields

To use different operations, you need to fill in the different required fields. The following shows the respective field descriptions for the corresponding operation.

<div label="Create Serverless Cluster">

- **Credential for TiDB Cloud API**: only supports TiDB Cloud API key. For how to create an API key, refer to [Get TiDB Cloud API Key](#prerequisites-get-tidb-cloud-api-key).
- **Project**: the TiDB Cloud project name.
- **Operation**: the operation of this node. For all supported operations, refer to [Supported operations](#supported-operations).
- **Cluster**: the TiDB Cloud cluster name. Enter the name for your new cluster.
- **Region**: the region name. Choose a region where your cluster will be deployed. Usually, choose the region closest to your application deployment.
- **Password**: the root password. Set a password for your new cluster.

</div>
<div label="Execute SQL">

- **Credential for TiDB Cloud API**: only supports TiDB Cloud API key. For how to create an API key, refer to [Get TiDB Cloud API Key](#prerequisites-get-tidb-cloud-api-key).
- **Project**: the TiDB Cloud project name.
- **Operation**: the operation of this node. For all supported operations, refer to [Supported operations](#supported-operations).
- **Cluster**: the TiDB Cloud cluster name. You should choose one existing cluster.
- **Password**: the password of the TiDB Cloud cluster.
- **User**: the username of the TiDB Cloud cluster.
- **Database**: the database name.
- **SQL**: the SQL statement to be executed.

</div>
<div label="Delete">

- **Credential for TiDB Cloud API**: only supports TiDB Cloud API key. For how to create an API key, refer to [Get TiDB Cloud API Key](#prerequisites-get-tidb-cloud-api-key).
- **Project**: the TiDB Cloud project name.
- **Operation**: the operation of this node. For all supported operations, refer to [Support Operation](#supported-operations).
- **Cluster**: the TiDB Cloud cluster name. You should choose one existing cluster.
- **Password**: the password of the TiDB Cloud cluster.
- **User**: the username of the TiDB Cloud cluster.
- **Database**: the database name.
- **Table**: the table name. You can use the `From list` mode to choose one or use the `Name` mode to type the table name manually.
- **Delete Key**: the name of the item's property that decides which rows in the database are deleted. An item is the data sent from one node to another. A node performs its action on each item of the incoming data. For more information about items in n8n, see [n8n documentation](https://docs.n8n.io/workflows/items/).

</div>
<div label="Insert">

- **Credential for TiDB Cloud API**: only supports TiDB Cloud API key. For how to create an API key, refer to [Get TiDB Cloud API Key](#prerequisites-get-tidb-cloud-api-key).
- **Project**: the TiDB Cloud project name.
- **Operation**: the operation of this node. For all supported operations, refer to [Support Operation](#supported-operations).
- **Cluster**: the TiDB Cloud cluster name. You should choose one existing cluster.
- **Password**: the password of the TiDB Cloud cluster.
- **User**: the username of the TiDB Cloud cluster.
- **Database**: the database name.
- **Table**: the table name. You can use the `From list` mode to choose one or use the `Name` mode to type the table name manually.
- **Columns**: The comma-separated list of the input item's properties, which are used as columns for the new rows. An item is the data sent from one node to another. A node performs its action on each item of the incoming data. For more information about items in n8n, see [n8n documentation](https://docs.n8n.io/workflows/items/).

</div>
<div label="Update">

- **Credential for TiDB Cloud API**: only supports TiDB Cloud API key. For how to create an API key, refer to [Get TiDB Cloud API Key](#prerequisites-get-tidb-cloud-api-key).
- **Project**: the TiDB Cloud project name.
- **Operation**: the operation of this node. For all supported operations, refer to [Support Operation](#supported-operations).
- **Cluster**: the TiDB Cloud cluster name. You should choose one existing cluster.
- **Password**: the password of the TiDB Cloud cluster.
- **User**: the username of the TiDB Cloud cluster.
- **Database**: the database name.
- **Table**: the table name. You can use the `From list` mode to choose one or use the `Name` mode to type the table name manually.
- **Update Key**: the name of the item's property that decides which rows in the database are updated. An item is the data sent from one node to another. A node performs its action on each item of the incoming data. For more information about items in n8n, see [n8n documentation](https://docs.n8n.io/workflows/items/).
- **Columns**: The comma-separated list of the input item's properties, which are used as columns for the rows to be updated.

</div>
### Limitations

- Normally only one SQL statement is allowed in the **Execute SQL** operation. If you want to execute more than one statement in a single operation, you need to manually enable [`tidb_multi_statement_mode`](https://docs.pingcap.com/tidbcloud/system-variables#tidb_multi_statement_mode-new-in-v4011).
- For the **Delete** and **Update** operations, you need to specify one field as a key. For example, the `Delete Key` is set to `id`, which is equivalent to executing `DELETE FROM table WHERE id = ${item.id}`. Currently, the **Delete** and **Update** operations only support specifying one key.
- For the **Insert** and **Update** operations, you need to specify the comma-separated list in the **Columns** field, and the field name must be the same as the input item's property.
