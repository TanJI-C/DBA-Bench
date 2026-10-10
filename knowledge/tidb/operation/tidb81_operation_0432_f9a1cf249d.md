# TiDB Cloud cluster upgrade mechanisms

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/upgrade-tidb-cluster.md`
- Source Title: `Upgrade a TiDB Cluster`
- Source Heading Path: `Upgrade a TiDB Cluster | Upgrade a TiDB Cluster > Regularly upgrade | Upgrade a TiDB Cluster > Contact support to upgrade`
- Source Line Ranges: `5-21`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `upgrade`, `support`, `maintenance`, `notification`, `version-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0432_f9a1cf249d`
- Source ID: `tidb-docs-8.1:tidb-cloud/upgrade-tidb-cluster.md#upgrade-a-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `927c0c1da03d59ed5d11105d5abd45e9a7a9eacf195ab3acff9f6d3a9150d67d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/upgrade-tidb-cluster#upgrade-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/upgrade-tidb-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when answering how TiDB Cloud upgrades a TiDB cluster, including regular upgrades and support-requested upgrades.
- Retrieval Keywords: Upgrade a TiDB Cluster, TiDB Cloud cluster upgrade mechanisms, Regularly upgrade, Contact support to upgrade, TiDB Cloud Support, Cloud Provider: AWS, Azure, or Google Cloud, Cluster Name, notify users via email before and after the upgrade, TiDB Cloud technical support will confirm with you the time period for the upgrade
- Follow-up Guidance: For a support-requested upgrade, the content says to contact the support team through TiDB Cloud Support and provide Cloud Provider and Cluster Name in the Description box.
- Classification Note: The content is classified as a cloud operation topic because it describes TiDB Cloud upgrade mechanisms, notifications, and support coordination for cluster version upgrades.

## Official Source Content

# Upgrade a TiDB Cluster

This document describes how to upgrade a TiDB cluster on TiDB Cloud. TiDB Cloud provides two upgrade mechanisms for upgrading your TiDB version.
## Regularly upgrade

For the TiDB version that is too low, TiDB Cloud will regularly upgrade it uniformly, and notify users via email before and after the upgrade.
## Contact support to upgrade

To submit an upgrade request, perform the steps in [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) to contact our support team. Note to provide the following information in the **Description** box:

- Cloud Provider: AWS, Azure, or Google Cloud
- Cluster Name: xxx

TiDB Cloud technical support will confirm with you the time period for the upgrade. After you have confirmed the upgrade time, TiDB Cloud technical support will do the upgrade in the confirmed time period.
