# Configure cluster root password settings in TiDB Cloud Dedicated

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/configure-security-settings.md`
- Source Title: `Configure Cluster Password Settings`
- Source Heading Path: `Configure Cluster Password Settings`
- Source Line Ranges: `5-27`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `password`, `root-user`, `allowed-ip-addresses`, `console`, `dedicated-cluster`, `serverless-note`, `access-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0215_b83001fc9e`
- Source ID: `tidb-docs-8.1:tidb-cloud/configure-security-settings.md#configure-cluster-password-settings`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `14910d960f3d1110c1125969b15e01b6d251fe70ab66d0e82ed8ee7bde23d215`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/configure-security-settings#configure-cluster-password-settings
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/configure-security-settings.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about where in the TiDB Cloud console to configure the root password or allowed IP addresses for a TiDB Cloud Dedicated cluster.
- Retrieval Keywords: Configure Cluster Password Settings, TiDB Cloud Dedicated, root password, allowed IP addresses, Password Settings, Clusters page, Auto-generate Password, TiDB Cloud Serverless inapplicable, TLS Connection to TiDB Cloud Serverless
- Follow-up Guidance: It notes that for TiDB Cloud Serverless clusters this document is inapplicable and refers readers to TLS Connection to TiDB Cloud Serverless instead.
- Classification Note: The official content is configuration guidance because it describes console steps to set the root password and allowed IP addresses for a Dedicated cluster.

## Official Source Content

# Configure Cluster Password Settings

For TiDB Cloud Dedicated clusters, you can configure the root password and allowed IP addresses to connect to your cluster.

> **Note:**
>
> For TiDB Cloud Serverless clusters, this document is inapplicable and you can refer to [TLS Connection to TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters) instead.

1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the row of your target cluster, click **...** and select **Password Settings**.
3. Set the root password to connect to your cluster, and then click **Save**.

    You can click **Auto-generate Password** to generate a random password. The generated password will not show again, so save your password in a secure location.

> **Tip:**
>
> If you are viewing the overview page of your cluster, you can click the **...** in the upper-right corner of the page, select **Password Settings**, and configure these settings, too.
