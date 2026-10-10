# AWS DMS migration prerequisites

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-connect-aws-dms.md`
- Source Title: `Connect AWS DMS to TiDB Cloud clusters`
- Source Heading Path: `Connect AWS DMS to TiDB Cloud clusters | Connect AWS DMS to TiDB Cloud clusters > Prerequisites | Connect AWS DMS to TiDB Cloud clusters > Prerequisites > An AWS account with enough access | Connect AWS DMS to TiDB Cloud clusters > Prerequisites > A TiDB Cloud account and a TiDB cluster`
- Source Line Ranges: `5-25`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `aws dms`, `prerequisites`, `accounts`, `ti db cloud cluster`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0299_91ed9fd95b`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-connect-aws-dms.md#connect-aws-dms-to-tidb-cloud-clusters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4e8a5580f8e97c1d16fb31d7472430e29c8a4d2aac7456aa2a0eb6f329516991`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-connect-aws-dms#connect-aws-dms-to-tidb-cloud-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-connect-aws-dms.md

## Retrieval Guidance

- Use When: Use this chunk when identifying the prerequisite accounts and cluster types needed before connecting AWS DMS to a TiDB Cloud cluster.
- Retrieval Keywords: AWS DMS prerequisites, AWS account with enough access, DMS-related resources, TiDB Cloud account, TiDB Cloud Serverless cluster, TiDB Cloud Dedicated cluster, Connect AWS DMS to TiDB Cloud clusters
- Follow-up Guidance: The source points to AWS account setup and IAM documents and to TiDB Cloud Serverless and TiDB Cloud Dedicated cluster creation documents.
- Classification Note: This is classified as configuration because the content lists required accounts and cluster prerequisites before any AWS DMS connection setup.

## Official Source Content

# Connect AWS DMS to TiDB Cloud clusters

[AWS Database Migration Service (AWS DMS)](https://aws.amazon.com/dms/) is a cloud service that makes it possible to migrate relational databases, data warehouses, NoSQL databases, and other types of data stores. You can use AWS DMS to migrate your data from or into TiDB Cloud clusters. This document describes how to connect AWS DMS to a TiDB Cloud cluster.
## Prerequisites
### An AWS account with enough access

You are expected to have an AWS account with enough access to manage DMS-related resources. If not, refer to the following AWS documents:

- [Sign up for an AWS account](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_GettingStarted.SettingUp.html#sign-up-for-aws)
- [Identity and access management for AWS Database Migration Service](https://docs.aws.amazon.com/dms/latest/userguide/security-iam.html)
### A TiDB Cloud account and a TiDB cluster

You are expected to have a TiDB Cloud account and a TiDB Cloud Serverless or TiDB Cloud Dedicated cluster. If not, refer to the following documents to create one:

- [Create a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster-serverless)
- [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster)
