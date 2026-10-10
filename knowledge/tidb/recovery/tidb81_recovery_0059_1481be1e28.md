# TiDB Cloud recovery group overview and architecture

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/recovery-group-overview.md`
- Source Title: `Recovery Group Overview (Beta)`
- Source Heading Path: `Recovery Group Overview (Beta) | Recovery Group Overview (Beta) > Architecture | Recovery Group Overview (Beta) > Key features and limitations | Recovery Group Overview (Beta) > What's next`
- Source Line Ranges: `5-37`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `disaster-recovery`, `replication`, `failover`, `reprotect`, `architecture`, `limitations`, `beta`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0059_1481be1e28`
- Source ID: `tidb-docs-8.1:tidb-cloud/recovery-group-overview.md#recovery-group-overview-beta`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `166f0ba9f9b817d368575ec8285e186a3a18321ad8db959e18cab040a125b02a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-overview#recovery-group-overview-beta
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/recovery-group-overview.md

## Retrieval Guidance

- Use When: Use this chunk when answering what a TiDB Cloud recovery group is, how failover and reprotect work between clusters, or what limitations apply to the feature.
- Retrieval Keywords: Recovery Group Overview (Beta), TiDB Cloud recovery group, TiDB Cloud Dedicated clusters, regional disasters, failover, reprotect, replication in the reverse direction, primary cluster, secondary cluster, replicated databases, recovery group architecture, client connections to replica databases, read-only queries, AWS support recovery groups, established between two clusters, bi-directional replication not supported, beta not recommended for production environments, Create Database Recovery Group, Failover and Reprotect Databases
- Follow-up Guidance: The source points to Create Database Recovery Group for getting started and Failover and Reprotect Databases for using a recovery group.
- Classification Note: This is classified as recovery for TiDB Cloud because the content defines a disaster-recovery architecture with replication, failover, reprotect, and stated feature limitations for recovery groups.

## Official Source Content

# Recovery Group Overview (Beta)

A TiDB Cloud recovery group allows you to replicate your databases between TiDB Cloud Dedicated clusters for protection against regional disasters. You can orchestrate the failover of databases from one cluster to another. After a failover to the secondary cluster, if the original primary cluster becomes available again, you can re-establish replication in the reverse direction to reprotect your databases.
## Architecture

A recovery group consists of a set of replicated databases that can be failed over together between two TiDB Cloud Dedicated clusters. Each recovery group is assigned a primary cluster, and databases on this primary cluster are associated with the group and are then replicated to the secondary cluster.

![Recovery Group](/media/tidb-cloud/recovery-group/recovery-group-overview.png)

- Recovery Group: a group of databases that are replicated between two clusters
- Primary Cluster: the cluster where the database is actively written by the application
- Secondary Cluster: the cluster where replicas of the database are located

> **Note**
>
> Client connections to the replica databases are not explicitly forced to be read-only by the Recovery Group feature. Ensuring that the application connecting to the replica databases only performs read-only queries is the responsibility of the application.
## Key features and limitations

- Currently, only TiDB Cloud Dedicated clusters hosted on AWS support recovery groups.
- Recovery groups are established between two clusters.
- Bi-directional replication of a database is not supported with recovery groups.

> **Warning**
>
> This feature is in beta and not recommended for production environments.
## What's next

- To get started with recovery groups, see [Create Database Recovery Group](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-get-started).
- To learn how to use a recovery group, see [Failover and Reprotect Databases](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-failover).
