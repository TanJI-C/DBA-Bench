# Migration prerequisites and tool deployment for Dumpling and TiCDC

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-from-op-tidb.md`
- Source Title: `Migrate from TiDB Self-Managed to TiDB Cloud`
- Source Heading Path: `Migrate from TiDB Self-Managed to TiDB Cloud | Migrate from TiDB Self-Managed to TiDB Cloud > Prerequisites | Migrate from TiDB Self-Managed to TiDB Cloud > Prepare tools | Migrate from TiDB Self-Managed to TiDB Cloud > Prepare tools > Dumpling | Migrate from TiDB Self-Managed to TiDB Cloud > Prepare tools > Dumpling > Deploy Dumpling using TiUP | Migrate from TiDB Self-Managed to TiDB Cloud > Prepare tools > Dumpling > Deploy Dumpling using the installation package | Migrate from TiDB Self-Managed to TiDB Cloud > Prepare tools > Dumpling > Configure privileges for Dumpling | Migrate from TiDB Self-Managed to TiDB Cloud > Prepare tools > Deploy TiCDC`
- Source Line Ranges: `5-102`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dumpling`, `ticdc`, `tiup`, `tidb`
- Topic Tags: `migration`, `prerequisites`, `tooling`, `dumpling`, `ticdc`, `tiup`, `privileges`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0344_1e17186b37`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-from-op-tidb.md#migrate-from-tidb-self-managed-to-tidb-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fa91867e4946bc6505eb4f1508323beb2f43ce4929649c5220b1c0d2af344953`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-from-op-tidb#migrate-from-tidb-self-managed-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-from-op-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving prerequisites and tool preparation details for migrating from TiDB Self-Managed to TiDB Cloud (AWS) with Dumpling for full export and TiCDC for incremental replication.
- Retrieval Keywords: Migrate from TiDB Self-Managed to TiDB Cloud, Prerequisites, AWS account with administrator access, AWS S3 bucket, TiDB Cloud account, Project Data Access Read-Write, Prepare tools, Dumpling, TiCDC, Deploy Dumpling using TiUP, curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh, tiup install dumpling, tiup update --self && tiup update dumpling, Deploy Dumpling using the installation package, download toolkit package, Configure privileges for Dumpling, SELECT, RELOAD, LOCK TABLES, REPLICATION CLIENT, PROCESS, Deploy TiCDC, select tidb_version();, TiDB v4.0.8.rc.1 and later versions support TiCDC, scale-out.yml, cdc_servers, gc-ttl: 86400, tiup cluster scale-out <cluster-name> scale-out.yml, tiup cluster display <cluster-name>
- Follow-up Guidance: The source also provides the TiCDC scale-out.yml example and the commands to add TiCDC to an existing TiDB cluster and display cluster status.
- Classification Note: This is classified as operation because the content lists migration prerequisites, account and access requirements, deployment methods for Dumpling, required export privileges, and TiCDC deployment steps.

## Official Source Content

# Migrate from TiDB Self-Managed to TiDB Cloud

This document describes how to migrate data from your TiDB Self-Managed clusters to TiDB Cloud (AWS) through Dumpling and TiCDC.

The overall procedure is as follows:

1. Build the environment and prepare the tools.
2. Migrate full data. The process is as follows:
   1. Export data from TiDB Self-Managed to Amazon S3 using Dumpling.
   2. Import data from Amazon S3 to TiDB Cloud.
3. Replicate incremental data by using TiCDC.
4. Verify the migrated data.
## Prerequisites

It is recommended that you put the S3 bucket and the TiDB Cloud cluster in the same region. Cross-region migration might incur additional cost for data conversion.

Before migration, you need to prepare the following:

- An [AWS account](https://docs.aws.amazon.com/AmazonS3/latest/userguide/setting-up-s3.html#sign-up-for-aws-gsg) with administrator access
- An [AWS S3 bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html)
- [A TiDB Cloud account](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-quickstart) with at least the [`Project Data Access Read-Write`](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles) access to your target TiDB Cloud cluster hosted on AWS
## Prepare tools

You need to prepare the following tools:

- Dumpling: a data export tool
- TiCDC: a data replication tool
### Dumpling

[Dumpling](https://docs.pingcap.com/tidb/dev/dumpling-overview) is a tool that exports data from TiDB or MySQL into SQL or CSV files. You can use Dumpling to export full data from TiDB Self-Managed.

Before you deploy Dumpling, note the following:

- It is recommended to deploy Dumpling on a new EC2 instance in the same VPC as the TiDB cluster in TiDB Cloud.
- The recommended EC2 instance type is **c6g.4xlarge** (16 vCPU and 32 GiB memory). You can choose other EC2 instance types based on your needs. The Amazon Machine Image (AMI) can be Amazon Linux, Ubuntu, or Red Hat.

You can deploy Dumpling by using TiUP or using the installation package.
#### Deploy Dumpling using TiUP

Use [TiUP](https://docs.pingcap.com/tidb/stable/tiup-overview) to deploy Dumpling:

```bash
## Deploy TiUP
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
source /root/.bash_profile
## Deploy Dumpling and update to the latest version
tiup install dumpling
tiup update --self && tiup update dumpling
```
#### Deploy Dumpling using the installation package

To deploy Dumpling using the installation package:

1. Download the [toolkit package](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).

2. Extract it to the target machine. You can get Dumpling using TiUP by running `tiup install dumpling`. Afterwards, you can use `tiup dumpling ...` to run Dumpling. For more information, see [Dumpling introduction](https://docs.pingcap.com/tidb/stable/dumpling-overview#dumpling-introduction).
#### Configure privileges for Dumpling

You need the following privileges to export data from the upstream database:

- SELECT
- RELOAD
- LOCK TABLES
- REPLICATION CLIENT
- PROCESS
### Deploy TiCDC

You need to [deploy TiCDC](https://docs.pingcap.com/tidb/dev/deploy-ticdc) to replicate incremental data from the upstream TiDB cluster to TiDB Cloud.

1. Confirm whether the current TiDB version supports TiCDC. TiDB v4.0.8.rc.1 and later versions support TiCDC. You can check the TiDB version by executing `select tidb_version();` in the TiDB cluster. If you need to upgrade it, see [Upgrade TiDB Using TiUP](https://docs.pingcap.com/tidb/dev/deploy-ticdc#upgrade-ticdc-using-tiup).

2. Add the TiCDC component to the TiDB cluster. See [Add or scale out TiCDC to an existing TiDB cluster using TiUP](https://docs.pingcap.com/tidb/dev/deploy-ticdc#add-or-scale-out-ticdc-to-an-existing-tidb-cluster-using-tiup). Edit the `scale-out.yml` file to add TiCDC:

    ```yaml
    cdc_servers:
    - host: 10.0.1.3
      gc-ttl: 86400
      data_dir: /tidb-data/cdc-8300
    - host: 10.0.1.4
      gc-ttl: 86400
      data_dir: /tidb-data/cdc-8300
    ```

3. Add the TiCDC component and check the status.

    ```shell
    tiup cluster scale-out <cluster-name> scale-out.yml
    tiup cluster display <cluster-name>
    ```
