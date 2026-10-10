# Migration upgrade overview and feasibility checks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-upgrade-migration-guide.md`
- Source Title: `Migrate and Upgrade a TiDB Cluster`
- Source Heading Path: `Migrate and Upgrade a TiDB Cluster | Migrate and Upgrade a TiDB Cluster > Step 1: Evaluate solution feasibility`
- Source Line Ranges: `5-44`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `br`, `ticdc`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `blue-green-upgrade`, `feasibility`, `compatibility`, `cluster-health`, `rollback`, `full-backup`, `incremental-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0466_8c779340d6`
- Source ID: `tidb-docs-8.1:tidb-upgrade-migration-guide.md#migrate-and-upgrade-a-tidb-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `172a20625f71fbc9faafd0a70443fc5cf9c95cf5c451211020fc92f240620ea1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-upgrade-migration-guide#migrate-and-upgrade-a-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-upgrade-migration-guide.md

## Retrieval Guidance

- Use When: Use this chunk when assessing whether a blue-green migration and upgrade with BR and TiCDC is feasible and what pre-checks are required before starting.
- Retrieval Keywords: Migrate and Upgrade a TiDB Cluster, blue-green upgrade, Step 1: Evaluate solution feasibility, BR full backup and restore, TiCDC incremental data replication, TiDB v6.5.0 or later, TiCDC valid index, TiCDC unsupported scenarios, Sequence replication not supported, TiFlash DDL replication not supported, avoid executing DDL operations on the upstream cluster during switchover, BR version compatibility matrix, BR usage restrictions, Region health, node resource utilization, rollback to the original cluster
- Follow-up Guidance: The next step in the source is to prepare the new cluster, including adjusting `tidb_gc_life_time`, migrating full data with BR, and upgrading the new cluster.
- Classification Note: This is classified as an operation chunk because it describes the migration and upgrade workflow, feasibility evaluation, compatibility checks, and cluster health checks.

## Official Source Content

# Migrate and Upgrade a TiDB Cluster

This document describes how to migrate and upgrade a TiDB cluster (also known as a blue-green upgrade) using [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) for full backup and restore, along with [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) for incremental data replication. This solution uses dual-cluster redundancy and incremental replication to enable smooth traffic switchover and fast rollback, providing a reliable and low-risk upgrade path for critical systems. It is recommended to regularly upgrade the database version to continuously benefit from performance improvements and new features, helping you maintain a secure and efficient database system. The key advantages of this solution include:

- **Controllable risk**: supports rollback to the original cluster within minutes, ensuring business continuity.
- **Data integrity**: uses a multi-stage verification mechanism to prevent data loss.
- **Minimal business impact**: requires only a brief maintenance window for the final switchover.

The core workflow for migration and upgrade is as follows:

1. **Pre-check risks**: verify cluster status and solution feasibility.
2. **Prepare the new cluster**: create a new cluster from a full backup of the old cluster and upgrade it to the target version.
3. **Replicate incremental data**: establish a forward data replication channel using TiCDC.
4. **Switch and verify**: perform multi-dimensional verification, switch business traffic to the new cluster, and set up a TiCDC reverse replication channel.
5. **Observe status**: maintain the reverse replication channel. After the observation period, clean up the environment.

**Rollback plan**: if the new cluster encounters issues during the migration and upgrade process, you can switch business traffic back to the original cluster at any time.

The following sections describe the standardized process and general steps for migrating and upgrading a TiDB cluster. The example commands are based on a TiDB Self-Managed environment.
## Step 1: Evaluate solution feasibility

Before migrating and upgrading, evaluate the compatibility of relevant components and check cluster health status.

- Check the TiDB cluster version: this solution applies to TiDB v6.5.0 or later versions.

- Verify TiCDC compatibility:

    - **Table schema requirements**: ensure that tables to be replicated contain valid indexes. For more information, see [TiCDC valid index](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#best-practices).
    - **Feature limitations**: TiCDC does not support Sequence or TiFlash DDL replication. For more information, see [TiCDC unsupported scenarios](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview#unsupported-scenarios).
    - **Best practices**: avoid executing DDL operations on the upstream cluster of TiCDC during switchover.

- Verify BR compatibility:

    - Review the compatibility matrix of BR full backup. For more information, see [BR version compatibility matrix](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#version-compatibility).
    - Check the known limitations of BR backup and restore. For more information, see [BR usage restrictions](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview#restrictions).

- Check the health status of the cluster, such as [Region](https://docs.pingcap.com/tidb/stable/glossary#regionpeerraft-group) health and node resource utilization.
