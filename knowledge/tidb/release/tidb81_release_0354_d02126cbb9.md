# Backup and restore: EBS volume snapshot backup support

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > New features > Backup and restore`
- Source Line Ranges: `224-234`
- Source Scope: `kubernetes`
- Primary Component: `operator`
- Related Components: `br`, `cloud`
- Topic Tags: `backup`, `restore`, `ebs`, `volume-snapshots`, `eks`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0354_d02126cbb9`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#backup-and-restore`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ca5180a953ea2af49b036c2112212d2fecae06541ab2e9cb008dee6f0a6d993`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#backup-and-restore
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.4.0 backup and restore support for using EBS volume snapshots with TiDB Operator on EKS and storing metadata in AWS S3.
- Retrieval Keywords: backup and restore, TiDB Operator, EBS volume snapshots, AWS EBS, EKS, AWS S3, volume snapshots, backup by snapshot, restore by snapshot
- Follow-up Guidance: The content points to the TiDB in Kubernetes user document for backup to AWS S3 by snapshot.
- Classification Note: This is classified as a release note for the operator component because it introduces a Kubernetes-specific backup capability implemented with TiDB Operator.

## Official Source Content

### Backup and restore

* Support backing up a TiDB cluster using EBS volume snapshots [#33849](https://github.com/pingcap/tidb/issues/33849) @[fengou1](https://github.com/fengou1)

    If your TiDB cluster is deployed on EKS and uses AWS EBS volumes, and you have the following requirements when backing up TiDB cluster data, you can use TiDB Operator to back up the data by volume snapshots and metadata to AWS S3:

    - Minimize the impact of backup, for example, to keep the impact on QPS and transaction latency less than 5%, and to occupy no cluster CPU and memory.
    - Back up and restore data in a short time. For example, finish backup within 1 hour and restore data in 2 hours.

  For more information, see [User document](https://docs.pingcap.com/tidb-in-kubernetes/v1.4/backup-to-aws-s3-by-snapshot).
