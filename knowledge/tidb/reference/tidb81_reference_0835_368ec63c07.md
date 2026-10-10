# TiKV storage type options for Dedicated clusters on AWS

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/size-your-cluster.md`
- Source Title: `Determine Your TiDB Size`
- Source Heading Path: `Determine Your TiDB Size > Size TiKV > TiKV node storage types | Determine Your TiDB Size > Size TiKV > TiKV node storage types > Basic storage | Determine Your TiDB Size > Size TiKV > TiKV node storage types > Standard storage | Determine Your TiDB Size > Size TiKV > TiKV node storage types > Performance and Plus storage`
- Source Line Ranges: `185-211`
- Source Scope: `cloud`
- Primary Component: `tikv`
- Related Components: `cloud`
- Topic Tags: `storage-types`, `aws`, `dedicated`, `cluster-sizing`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0835_368ec63c07`
- Source ID: `tidb-docs-8.1:tidb-cloud/size-your-cluster.md#tikv-node-storage-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `376939113b19c364315be915d4ca449101146f77679eb9b47410edd64bb91f9e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/size-your-cluster#tikv-node-storage-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/size-your-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when identifying TiKV storage type options and automatic assignment rules for TiDB Cloud Dedicated clusters hosted on AWS.
- Retrieval Keywords: TiKV node storage types, TiDB Cloud Dedicated, AWS, Basic storage, Standard storage, Performance storage, Plus storage, created before April 1, 2025, v7.5.5, v8.1.2, v8.5.0, Raft logs, Request Support, Apply for TiKV storage type
- Follow-up Guidance: The source also states that Performance and Plus storage are only available upon request for clusters deployed on AWS through the TiDB Cloud console support flow.
- Classification Note: This is reference content because it lists TiKV storage types, their characteristics, and the version- and date-based automatic application conditions for AWS-hosted Dedicated clusters.

## Official Source Content

### TiKV node storage types

TiDB Cloud provides the following TiKV storage types for [TiDB Cloud Dedicated](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-dedicated) clusters hosted on AWS:

- [Basic storage](#basic-storage)
- [Standard storage](#standard-storage)
- [Performance and Plus storage](#performance-and-plus-storage)
#### Basic storage

The Basic storage is a general-purpose storage type that provides lower performance than the Standard storage.

The Basic storage type is applied automatically to the following clusters hosted on AWS:

- Existing clusters that are created before April 1, 2025. 
- New clusters that are created with TiDB versions earlier than v7.5.5, v8.1.2, or v8.5.0.
#### Standard storage

The Standard storage is ideal for most workloads, providing a balance between performance and cost efficiency. Compared with the Basic storage, it offers better performance by reserving ample disk resources for Raft logs. This reduces the impact of Raft I/O on data disk I/O, improving read and write performance for TiKV.

The Standard storage type is applied automatically to new clusters hosted on AWS and created with TiDB versions v7.5.5, v8.1.2, v8.5.0, or later.
#### Performance and Plus storage

The Performance and Plus storage provide higher performance and stability, with pricing that reflects these enhanced capabilities. Currently, these two storage types are only available upon request for clusters deployed on AWS. To request the Performance or Plus storage, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com) and click **Request Support**. Then, fill in "Apply for TiKV storage type" in the **Description** field and click **Submit**.
