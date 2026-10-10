# Create TiDB Cloud DMS endpoints

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-connect-aws-dms.md`
- Source Title: `Connect AWS DMS to TiDB Cloud clusters`
- Source Heading Path: `Connect AWS DMS to TiDB Cloud clusters > Create TiDB Cloud DMS endpoints`
- Source Line Ranges: `95-140`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`
- Topic Tags: `endpoint`, `mysql source`, `mysql target`, `ssl mode`, `ca certificate`, `foreign_key_checks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0415_9b131ba69d`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-connect-aws-dms.md#create-tidb-cloud-dms-endpoints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3a32346fca383843893f4bd1c2df2716039618c15d8e23c5eb658672ce9af42d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms#create-tidb-cloud-dms-endpoints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-connect-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when creating AWS DMS endpoints for TiDB Cloud and needing the exact endpoint fields, MySQL engine selection, SSL mode, CA certificate references, or target endpoint connection attributes.
- Retrieval Keywords: Create TiDB Cloud DMS endpoints, Endpoints, Create endpoint, Source endpoint, Target endpoint, MySQL as a source, MySQL as a target, Provide access information manually, Server name, Port, User name, Password, Secure Socket Layer (SSL) mode, verify-full, none, CA certificate, ISRG Root X1 certificate, Extra connection attributes, Initstmt=SET FOREIGN_KEY_CHECKS=0;, Migrate existing data, TiDB does not support MySQL binlog
- Follow-up Guidance: The source states that when using a TiDB Cloud cluster as a source, you can only Migrate existing data because TiDB does not support MySQL binlog.
- Classification Note: This is classified as operation because the content provides the endpoint creation procedure and the exact source and target database settings required in AWS DMS.

## Official Source Content

## Create TiDB Cloud DMS endpoints

For connectivity, the steps for using TiDB Cloud clusters as a source or as a target are similar, but DMS does have some different database setting requirements for source and target. For more information, see [Using MySQL as a source](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MySQL.html) or [Using MySQL as a target](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.MySQL.html). When using a TiDB Cloud cluster as a source, you can only **Migrate existing data** because TiDB does not support MySQL binlog.

1. In the AWS DMS console, go to the [**Endpoints**](https://console.aws.amazon.com/dms/v2/home#endpointList) page and switch to the corresponding region.

    ![Create endpoint](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-connect-create-endpoint.png)

2. Click **Create endpoint** to create the target database endpoint.

3. In the **Endpoint type** section, select **Source endpoint** or **Target endpoint**.

4. In the **Endpoint configuration** section, fill in the **Endpoint identifier** and ARN fields. Then, select **MySQL** as **Source engine** or **Target engine**.

5. For the **Access to endpoint database** field, select the **Provide access information manually** checkbox and fill in cluster information as follows:

    <div label="TiDB Cloud Serverless">

    - **Server name**: `HOST` of TiDB Cloud Serverless cluster.
    - **Port**: `PORT` of TiDB Cloud Serverless cluster.
    - **User name**: User of TiDB Cloud Serverless cluster for migration. Make sure it meets DMS requirements.
    - **Password**: Password of the TiDB Cloud Serverless cluster user.
    - **Secure Socket Layer (SSL) mode**: If you are connecting via public endpoint, it is highly recommended to set the mode to **verify-full** to ensure transport security. If you are connecting via private endpoint, you can set the mode to **none**.
    - (Optional) **CA certificate**: Use the [ISRG Root X1 certificate](https://letsencrypt.org/certs/isrgrootx1.pem). For more information, see [TLS Connections to TiDB Cloud Serverless](https://docs.pingcap.com/tidb/stable/tidb-cloud/secure-connections-to-serverless-clusters).

    </div>

    <div label="TiDB Cloud Dedicated">

    - **Server name**: `HOST` of TiDB Cloud Dedicated cluster.
    - **Port**: `PORT` of TiDB Cloud Dedicated cluster.
    - **User name**: User of TiDB Cloud Dedicated cluster for migration. Make sure it meets DMS requirements.
    - **Password**: Password of TiDB Cloud Dedicated cluster user.
    - **Secure Socket Layer (SSL) mode**: If you are connecting via public endpoint, it is highly recommended to set the mode to **verify-full** to ensure transport security. If you are connecting via private endpoint, you can set it to **none**.
    - (Optional) **CA certificate**: Get the CA certificate according to [TLS connections to TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-tls-connect-to-dedicated).

    </div>

     ![Provide access information manually](/media/tidb-cloud/aws-dms-tidb-cloud/aws-dms-connect-configure-endpoint.png)

6. If you want to create the endpoint as a **Target endpoint**, expand the **Endpoint settings** section, select the **Use endpoint connection attributes** checkbox, and then set **Extra connection attributes** to `Initstmt=SET FOREIGN_KEY_CHECKS=0;`.

7. Configure the **KMS Key** and **Tags** sections if needed. Click **Create endpoint** to finish the instance creation.
