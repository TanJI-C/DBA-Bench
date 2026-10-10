# Create a recovery group in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/recovery-group-get-started.md`
- Source Title: `Get Started with Recovery Groups`
- Source Heading Path: `Get Started with Recovery Groups | Get Started with Recovery Groups > Prerequisites | Get Started with Recovery Groups > Create a new recovery group`
- Source Line Ranges: `5-55`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`
- Topic Tags: `recovery-group`, `prerequisites`, `dedicated-cluster`, `aws`, `replication`, `database-selection`, `initial-replication`, `backup`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0057_44016d4eb7`
- Source ID: `tidb-docs-8.1:tidb-cloud/recovery-group-get-started.md#get-started-with-recovery-groups`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5e7644739ed7c34b45be1e520101bd33d513075cb4d5741df7b3f648ec668ca3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-get-started#get-started-with-recovery-groups
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/recovery-group-get-started.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs prerequisites, supported scope, or console steps to create a TiDB Cloud recovery group and choose primary, secondary, and replicated databases.
- Retrieval Keywords: Create Recovery Group, Recovery Group, TiDB Cloud Dedicated cluster, Organization Owner, Project Owner, AWS, primary cluster, secondary cluster, Assign all databases (current and future), Assign specific databases, initial replication, backup before setting up the recovery group, regional disasters
- Follow-up Guidance: The source also explains that initial replication can affect online query performance and that selected databases on the primary cluster will replace the content of the databases at the secondary cluster during initial replication.
- Classification Note: The official content is classified under recovery in TiDB Cloud because it describes recovery group prerequisites and creation for database replication between dedicated clusters.

## Official Source Content

# Get Started with Recovery Groups

This document describes how to create a recovery group to protect your databases running on TiDB Cloud Dedicated clusters using the [TiDB Cloud console](https://tidbcloud.com/). It also shows how to view details of a recovery group.
## Prerequisites

- A recovery group replicates your databases to another cluster to protect your databases from regional disasters. Before creating a recovery group, you need to have two TiDB Cloud Dedicated clusters. One cluster hosts the primary databases, and a second cluster hosts the replicas of the primary databases. If you have not done so already, follow the steps in [Create a TiDB Cloud Dedicated Cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster) to create the necessary clusters.
- To create a recovery group, you must be in the `Organization Owner` role of your organization or the `Project Owner` role of the target project.

> **Note**
>
> Currently, only TiDB Cloud Dedicated clusters hosted on AWS support recovery groups.
## Create a new recovery group

To create a recovery group, perform the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com/), switch to your target project using the combo box in the upper-left corner.

2. In the left navigation pane, click **Recovery Group**.

3. On the **Recovery Group** page, click **Create Recovery Group**.

4. On the **Create Recovery Group** page, enter a name for the recovery group.

    > **Note**
    >
    > Currently only one resiliency level is supported. For more information, see [About resiliency levels](#about-resiliency-levels).

5. Select the TiDB Cloud Dedicated cluster that will be the primary cluster for this group.

6. Select the TiDB Cloud Dedicated cluster that will be the secondary cluster where databases will be replicated for this group.

7. Select which databases you wish to replicate as part of this recovery group.

    > **Note**
    >
    > When assigning databases to the group, you can select specific databases, or select all (non-system) databases on the primary cluster (current and future).
    >
    > - If you **Assign all databases (current and future)**, any future databases added to the cluster will be automatically included in this recovery group and replicated to the secondary cluster.
    > - If you **Assign specific databases**, select the specific databases on the primary cluster that you want to replicate to the secondary cluster. If any databases are added to the primary cluster in the future, these new databases will not be automatically replicated as part of this recovery group.
   >
    > During the initial replication, due to the volume of data transferred, the online query performance at the primary or secondary clusters might be affected. Schedule the initial protection of databases for a less busy period.

    > **Warning**
    > 
    > During the initial replication, the content of the selected databases at the primary cluster will replace the content of the databases at the secondary cluster. If you wish to preserve the unique content at the secondary cluster, complete a backup before setting up the recovery group.

8. Review the summary information, and then click **Create** to begin protecting the databases as part of the new recovery group.
