# PITR prerequisites, S3 storage setup, and backup policy

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-use-cases.md`
- Source Title: `TiDB Backup and Restore Use Cases`
- Source Heading Path: `TiDB Backup and Restore Use Cases | TiDB Backup and Restore Use Cases > Deploy the TiDB cluster and BR | TiDB Backup and Restore Use Cases > Configure backup storage (Amazon S3) | TiDB Backup and Restore Use Cases > Determine the backup policy`
- Source Line Ranges: `5-87`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tikv`, `tiup`, `cloud`, `tidb`
- Topic Tags: `pitr`, `deployment`, `versioning`, `s3`, `iam`, `backup-policy`, `snapshot-backup`, `log-backup`, `retention`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0014_849da88f86`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-use-cases.md#tidb-backup-and-restore-use-cases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ba4ce31691a4942d292e538735cfa1853dcc64be7a477d98e4dfc96bfb1e49a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases#tidb-backup-and-restore-use-cases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-use-cases.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PITR prerequisites, BR and TiDB version alignment, Amazon S3 backup storage layout, required IAM permissions, or the example backup retention policy.
- Retrieval Keywords: PITR, TiDB cluster >= v6.2.0, BR same version as the TiDB cluster, v8.1.2, tiup install br:v8.1.2, tiup update br:v8.1.2, BR can connect to all PD and TiKV nodes, BR and PD servers must use the same time zone, Amazon S3, s3://tidb-pitr-bucket/backup-data, IAM, s3:ListBucket, s3:GetObject, s3:DeleteObject, s3:PutObject, s3:AbortMultipartUpload, snapshot-${date}, log-backup, Run the log backup to continuously back up the data change, snapshot backup at 00:00 AM every two days, retain within 30 days
- Follow-up Guidance: The source continues with commands to start log backup, run scheduled snapshot backups, restore to a point in time, and clean up outdated backup data.
- Classification Note: This is classified as operation because the content describes deployment prerequisites, storage preparation, permission setup, and backup policy planning for BR and PITR.

## Official Source Content

# TiDB Backup and Restore Use Cases

[TiDB Snapshot Backup and Restore Guide](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide) and [TiDB Log Backup and PITR Guide](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) introduce the backup and restore solutions provided by TiDB, namely, snapshot (full) backup and restore, log backup and point-in-time recovery (PITR). This document helps you to quickly get started with the backup and restore solutions of TiDB in specific use cases.

Assume that you have deployed a TiDB production cluster on AWS and the business team requests the following requirements:

- Back up the data changes in a timely manner. When the database encounters a disaster, you can quickly recover the application with minimal data loss (only a few minutes of data loss is tolerable).
- Perform business audits every month at no specific time. When an audit request is received, you must provide a database to query the data at a certain time point of the past month as requested.

With PITR, you can satisfy the preceding requirements.
## Deploy the TiDB cluster and BR

To use PITR, you need to deploy a TiDB cluster >= v6.2.0 and update BR to the same version as the TiDB cluster. This document uses v8.1.2 as an example.

The following table shows the recommended hardware resources for using PITR in a TiDB cluster.

| Component | CPU | Memory | Disk | AWS instance  | Number of instances |
| --- | --- | --- | --- | --- | --- |
| TiDB | 8 core+ | 16 GB+ | SAS | c5.2xlarge | 2 |
| PD | 8 core+ | 16 GB+ | SSD | c5.2xlarge | 3 |
| TiKV | 8 core+ | 32 GB+ | SSD | m5.2xlarge | 3 |
| BR | 8 core+ | 16 GB+ | SAS | c5.2xlarge | 1 |
| Monitor | 8 core+ | 16 GB+ | SAS | c5.2xlarge | 1 |

> **Note:**
>
> - When BR runs backup and restore tasks, it needs to access PD and TiKV. Make sure that BR can connect to all PD and TiKV nodes.
> - BR and PD servers must use the same time zone.

Deploy or upgrade a TiDB cluster using TiUP:

- To deploy a new TiDB cluster, refer to [Deploy a TiDB cluster](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).
- If the TiDB cluster is earlier than v6.2.0, upgrade it by referring to [Upgrade a TiDB cluster](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup).

Install or upgrade BR using TiUP:

- Install:

    ```shell
    tiup install br:v8.1.2
    ```

- Upgrade:

    ```shell
    tiup update br:v8.1.2
    ```
## Configure backup storage (Amazon S3)

Before you start a backup task, prepare the backup storage, including the following aspects:

1. Prepare the S3 bucket and directory that stores the backup data.
2. Configure the permissions to access the S3 bucket.
3. Plan the subdirectory that stores each backup data.

The detailed steps are as follows:

1. Create a directory in S3 to store the backup data. The directory in this example is `s3://tidb-pitr-bucket/backup-data`.

    1. Create a bucket. You can choose an existing S3 to store the backup data. If there is none, refer to [AWS documentation: Creating a bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) and create an S3 bucket. In this example, the bucket name is `tidb-pitr-bucket`.
    2. Create a directory for your backup data. In the bucket (`tidb-pitr-bucket`), create a directory named `backup-data`. For detailed steps, refer to [AWS documentation: Organizing objects in the Amazon S3 console using folders](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-folders.html).

2. Configure permissions for BR and TiKV to access the S3 directory. It is recommended to grant permissions using the IAM method, which is the most secure way to access the S3 bucket. For detailed steps, refer to [AWS documentation: Controlling access to a bucket with user policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/walkthrough1.html). The required permissions are as follows:

    - TiKV and BR in the backup cluster need `s3:ListBucket`, `s3:GetObject`, `s3:DeleteObject`, `s3:PutObject`, and `s3:AbortMultipartUpload` permissions of the `s3://tidb-pitr-bucket/backup-data` directory.
    - TiKV and BR in the restore cluster need `s3:ListBucket`, `s3:GetObject`, `s3:DeleteObject`, and `s3:PutObject` permissions of the `s3://tidb-pitr-bucket/backup-data` directory.

3. Plan the directory structure that stores the backup data, including the snapshot (full) backup and the log backup.

    - All snapshot backup data are stored in the `s3://tidb-pitr-bucket/backup-data/snapshot-${date}` directory. `${date}` is the start time of the snapshot backup. For example, a snapshot backup starting at 2022/05/12 00:01:30 is stored in `s3://tidb-pitr-bucket/backup-data/snapshot-20220512000130`.
    - Log backup data are stored in the `s3://tidb-pitr-bucket/backup-data/log-backup/` directory.
## Determine the backup policy

To meet the requirements of minimum data loss, quick recovery, and business audits within a month, you can set the backup policy as follows:

- Run the log backup to continuously back up the data change in the database.
- Run a snapshot backup at 00:00 AM every two days.
- Retain the snapshot backup data and log backup data within 30 days and clean up backup data older than 30 days.
