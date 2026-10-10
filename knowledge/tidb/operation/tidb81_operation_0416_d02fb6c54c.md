# Rotate, revoke, and restore CMEK access

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-encrypt-cmek.md`
- Source Title: `Encryption at Rest Using Customer-Managed Encryption Keys`
- Source Heading Path: `Encryption at Rest Using Customer-Managed Encryption Keys > Rotate CMEK | Encryption at Rest Using Customer-Managed Encryption Keys > Revoke and restore CMEK`
- Source Line Ranges: `152-170`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cmek`, `key-rotation`, `access-revocation`, `cluster-pause`, `cluster-restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0416_d02fb6c54c`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-encrypt-cmek.md#rotate-cmek`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c3930cb6f68d973f82e322f7cf9b09b8e4fd9fe46115fd1a53d79ed68535755`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-encrypt-cmek#rotate-cmek
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-encrypt-cmek.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about rotating a CMEK in AWS KMS or what happens when TiDB Cloud access to CMEK is revoked and later restored.
- Retrieval Keywords: Rotate CMEK, automatic CMEK rotation, AWS KMS rotate keys, Encryption Access, revoke and restore CMEK, KMS Key policy, pause all the clusters, running clusters are not affected, cluster will not be able to restore normally, restore the CMEK access policy, restore all clusters
- Follow-up Guidance: The source states that with automatic CMEK rotation enabled on AWS KMS, you do not need to update Encryption Access in TiDB Cloud, including the CMEK ID.
- Classification Note: This is classified as operation because the content describes ongoing key lifecycle handling, temporary access revocation, and cluster pause or restore behavior tied to CMEK access.

## Official Source Content

## Rotate CMEK

You can configure [automatic CMEK rotation](http://docs.aws.amazon.com/kms/latest/developerguide/rotate-keys.html) on AWS KMS. With this rotation enabled, you do not need to update **Encryption Access** in project settings in TiDB Cloud, including the CMEK ID.
## Revoke and restore CMEK

If you need to temporarily revoke TiDB Cloud's access to CMEK, follow these steps:

1. On the AWS KMS console, revoke the corresponding permissions and update the KMS Key policy.
2. On the TiDB Cloud console, pause all the clusters in the project.

> **Note:**
>
> After you revoke CMEK on AWS KMS, your running clusters are not affected. However, when you pause a cluster and then restore the cluster, the cluster will not be able to restore normally because it cannot access CMEK.

After revoking TiDB Cloud's access to CMEK, if you need to restore the access, follow these steps:

1. On the AWS KMS console, restore the CMEK access policy.
2. On the TiDB Cloud console, restore all clusters in the project.
