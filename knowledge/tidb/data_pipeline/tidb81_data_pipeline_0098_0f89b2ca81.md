# Full data export from TiDB Self-Managed to Amazon S3 with Dumpling

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-op-tidb.md`
- Source Title: `Migrate from TiDB Self-Managed to TiDB Cloud`
- Source Heading Path: `Migrate from TiDB Self-Managed to TiDB Cloud > Migrate full data | Migrate from TiDB Self-Managed to TiDB Cloud > Migrate full data > Migrate data from the TiDB Self-Managed cluster to Amazon S3 | Migrate from TiDB Self-Managed to TiDB Cloud > Migrate full data > Migrate data from the TiDB Self-Managed cluster to Amazon S3 > Step 1. Disable the GC mechanism of the upstream TiDB Self-Managed cluster temporarily | Migrate from TiDB Self-Managed to TiDB Cloud > Migrate full data > Migrate data from the TiDB Self-Managed cluster to Amazon S3 > Step 2. Configure access permissions to the Amazon S3 bucket for Dumpling | Migrate from TiDB Self-Managed to TiDB Cloud > Migrate full data > Migrate data from the TiDB Self-Managed cluster to Amazon S3 > Step 3. Export data from the upstream TiDB cluster to Amazon S3 using Dumpling`
- Source Line Ranges: `103-199`
- Source Scope: `cloud`
- Primary Component: `dumpling`
- Related Components: `cloud`, `tidb`, `sql`
- Topic Tags: `full-migration`, `export`, `s3`, `aws`, `gc`, `permissions`, `environment-variables`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0098_0f89b2ca81`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-op-tidb.md#migrate-full-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c8fe87f39506f48e7c63a369ebe9b602cf70f8dedd8da7304223ec807ad29773`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-op-tidb#migrate-full-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-op-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the documented full export procedure from a TiDB Self-Managed cluster to Amazon S3 with Dumpling before importing into TiDB Cloud.
- Retrieval Keywords: Migrate full data, Migrate data from the TiDB Self-Managed cluster to Amazon S3, Disable the GC mechanism of the upstream TiDB Self-Managed cluster temporarily, SET GLOBAL tidb_gc_enable = FALSE;, SELECT @@global.tidb_gc_enable;, Configure access permissions to the Amazon S3 bucket for Dumpling, Create access key, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3 bucket URI, region information, dumpling -u root -P 4000 -h 127.0.0.1 -r 20000 --filetype {sql|csv} -F 256MiB -t 8 -o "${S3 URI}" --s3.region "${s3.region}", -t option specifies the number of threads, export to Amazon S3 bucket, metadata, {schema}-schema-create.sql, {schema}.{table}-schema.sql, {schema}.{table}.{0001}.{sql|csv}, *-schema-view.sql, *-schema-trigger.sql, *-schema-post.sql
- Follow-up Guidance: The source also notes that if the Dumpling server and Amazon S3 are not connected, you can export files to local storage first and upload them to Amazon S3 later.
- Classification Note: This is classified as data_pipeline because the content describes the full data export flow, including temporary GC disabling, S3 access configuration, Dumpling export parameters, and exported file artifacts.

## Official Source Content

## Migrate full data

To migrate data from the TiDB Self-Managed cluster to TiDB Cloud, perform a full data migration as follows:

1. Migrate data from the TiDB Self-Managed cluster to Amazon S3.
2. Migrate data from Amazon S3 to TiDB Cloud.
### Migrate data from the TiDB Self-Managed cluster to Amazon S3

You need to migrate data from the TiDB Self-Managed cluster to Amazon S3 using Dumpling.

If your TiDB cluster is in a local IDC, or the network between the Dumpling server and Amazon S3 is not connected, you can export the files to the local storage first, and then upload them to Amazon S3 later.
#### Step 1. Disable the GC mechanism of the upstream TiDB Self-Managed cluster temporarily

To ensure that newly written data is not lost during incremental migration, you need to disable the upstream cluster's garbage collection (GC) mechanism before starting the migration to prevent the system from cleaning up historical data.

Run the following command to verify whether the setting is successful.

```sql
SET GLOBAL tidb_gc_enable = FALSE;
```

The following is an example output, in which `0` indicates that it is disabled.

```sql
SELECT @@global.tidb_gc_enable;
+-------------------------+
| @@global.tidb_gc_enable |
+-------------------------+
|                       0 |
+-------------------------+
1 row in set (0.01 sec)
```
#### Step 2. Configure access permissions to the Amazon S3 bucket for Dumpling

Create an access key in the AWS console. See [Create an access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey) for details.

1. Use your AWS account ID or account alias, your IAM user name, and your password to sign in to [the IAM console](https://console.aws.amazon.com/iam/home#/security_credentials).

2. In the navigation bar on the upper right, choose your user name, and then click **My Security Credentials**.

3. To create an access key, click **Create access key**. Then choose **Download .csv file** to save the access key ID and secret access key to a CSV file on your computer. Store the file in a secure location. You will not have access to the secret access key again after this dialog box closes. After you download the CSV file, choose **Close**. When you create an access key, the key pair is active by default, and you can use the pair right away.

    ![Create access key](/media/tidb-cloud/op-to-cloud-create-access-key01.png)

    ![Download CSV file](/media/tidb-cloud/op-to-cloud-create-access-key02.png)
#### Step 3. Export data from the upstream TiDB cluster to Amazon S3 using Dumpling

Do the following to export data from the upstream TiDB cluster to Amazon S3 using Dumpling:

1. Configure the environment variables for Dumpling.

    ```shell
    export AWS_ACCESS_KEY_ID=${AccessKey}
    export AWS_SECRET_ACCESS_KEY=${SecretKey}
    ```

2. Get the S3 bucket URI and region information from the AWS console. See [Create a bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) for details.

    The following screenshot shows how to get the S3 bucket URI information:

    ![Get the S3 URI](/media/tidb-cloud/op-to-cloud-copy-s3-uri.png)

    The following screenshot shows how to get the region information:

    ![Get the region information](/media/tidb-cloud/op-to-cloud-copy-region-info.png)

3. Run Dumpling to export data to the Amazon S3 bucket.

    ```shell
    dumpling \
    -u root \
    -P 4000 \
    -h 127.0.0.1 \
    -r 20000 \
    --filetype {sql|csv}  \
    -F 256MiB  \
    -t 8 \
    -o "${S3 URI}" \
    --s3.region "${s3.region}"
    ```

    The `-t` option specifies the number of threads for the export. Increasing the number of threads improves the concurrency of Dumpling and the export speed, and also increases the database's memory consumption. Therefore, do not set a too large number for this parameter.

    For more information, see [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-to-sql-files).

4. Check the export data. Usually the exported data includes the following:

    - `metadata`: this file contains the start time of the export, and the location of the master binary log.
    - `{schema}-schema-create.sql`: the SQL file for creating the schema
    - `{schema}.{table}-schema.sql`: the SQL file for creating the table
    - `{schema}.{table}.{0001}.{sql|csv}`: data files
    - `*-schema-view.sql`, `*-schema-trigger.sql`, `*-schema-post.sql`: other exported SQL files
