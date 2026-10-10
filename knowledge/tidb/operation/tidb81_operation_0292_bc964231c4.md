# Connect to a TiDB cluster with Web SQL Shell

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/connect-via-sql-shell.md`
- Source Title: `Connect via SQL Shell`
- Source Heading Path: `Connect via SQL Shell`
- Source Line Ranges: `5-24`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `sql-shell`, `cluster-connection`, `web-console`, `networking`, `authentication`, `serverless-limitation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0292_bc964231c4`
- Source ID: `tidb-docs-8.1:tidb-cloud/connect-via-sql-shell.md#connect-via-sql-shell`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `72c0ad3894c8ab5fbda25f0a42bc9b82d5aabb8e462b2819cd73e1bb3925d012`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-sql-shell#connect-via-sql-shell
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/connect-via-sql-shell.md

## Retrieval Guidance

- Use When: Use this when looking for how to open Web SQL Shell in the TiDB Cloud console and connect to a TiDB cluster with the root password.
- Retrieval Keywords: Connect via SQL Shell, TiDB Cloud SQL Shell, Web SQL Shell, Clusters page, Settings > Networking, Enter password, root password, connect to a TiDB cluster, test out TiDB's compatibility with MySQL, administer database user privileges, cannot connect to TiDB Cloud Serverless clusters using SQL Shell
- Follow-up Guidance: The content notes that SQL Shell cannot connect to TiDB Cloud Serverless clusters and points to Connect to TiDB Cloud Serverless clusters for that case.
- Classification Note: The classification is operation for the cloud component because the content gives console navigation and connection steps for using Web SQL Shell with a TiDB cluster in TiDB Cloud.

## Official Source Content

# Connect via SQL Shell

In TiDB Cloud SQL Shell, you can try TiDB SQL, test out TiDB's compatibility with MySQL quickly, and administer database user privileges.

> **Note:**
>
> You cannot connect to [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless) using SQL Shell. To connect to your TiDB Cloud Serverless cluster, see [Connect to TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-to-tidb-cluster-serverless).

To connect to your TiDB cluster using SQL shell, perform the following steps:

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its cluster overview page, and then click **Settings** > **Networking** in the left navigation pane.
3. On the **Networking** page, click **Web SQL Shell** in the upper-right corner.
4. On the prompted **Enter password** line, enter the root password of the current cluster. Then your application is connected to the TiDB cluster.
