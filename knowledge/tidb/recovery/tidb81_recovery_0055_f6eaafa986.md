# Recovery group failover prerequisites and procedure

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/recovery-group-failover.md`
- Source Title: `Failover and Reprotect Databases`
- Source Heading Path: `Failover and Reprotect Databases | Failover and Reprotect Databases > Prerequisites | Failover and Reprotect Databases > Failover databases using a recovery group`
- Source Line Ranges: `5-41`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `recovery-group`, `failover`, `disaster-recovery`, `replication`, `prerequisites`, `console`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0055_f6eaafa986`
- Source ID: `tidb-docs-8.1:tidb-cloud/recovery-group-failover.md#failover-and-reprotect-databases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13fb7501c036f050183292eff2f814de51739a7ab873985ecb6467f8efb9b102`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-failover#failover-and-reprotect-databases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/recovery-group-failover.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB Cloud recovery group failover prerequisites, what Failover does, or the console steps and warnings to promote the secondary cluster during a regional outage.
- Retrieval Keywords: Failover and Reprotect Databases, Prerequisites, Failover databases using a recovery group, recovery group, Failover, secondary cluster, primary copy, regional outage, successfully replicating, TiDB Cloud console, Action menu, Performing a failover will sever the existing replication relationship, healthy state, I understand, failover group
- Follow-up Guidance: The same source also describes the Reprotect action for reversing replication back to the original region after the outage is resolved.
- Classification Note: This is classified as cloud recovery content because it describes recovery group replication between clusters and the TiDB Cloud console procedure for failover.

## Official Source Content

# Failover and Reprotect Databases

Databases in a recovery group are replicated from one cluster to another, typically in a different region of the cloud service provider.

The **Failover** action promotes the replicated databases in the secondary region to be the new primary copy, ensuring ongoing availability during a regional outage.

When the regional outage is resolved, the ability to reverse the replication from the recovery region back to the original region is done using the **Reprotect** action. This ensures that the databases are protected against future disasters impacting their new region, and prepares them for migration back to the original region if desired.
## Prerequisites

Before performing a failover, a recovery group should have been created and be successfully replicating to the secondary cluster. For more information, see [Get Started with Recovery Groups](https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-get-started).

![Protected Recovery Group](/media/tidb-cloud/recovery-group/recovery-group-protected.png)
## Failover databases using a recovery group

In the event of a disaster, you can use the recovery group to failover databases to the secondary cluster.

1. In the [TiDB Cloud console](https://tidbcloud.com/), switch to your target project using the combo box in the upper-left corner.

2. In the left navigation pane, click **Recovery Group**.

3. On the **Recovery Group** page, locate the name of the recovery group that you wish to failover.

4. Click the **Action** menu for the recovery group, and then click **Failover**. The failover dialog is displayed.

    > **Warning**
    >
    > Performing a failover will sever the existing replication relationship.

5. Select the secondary TiDB Cloud cluster to be promoted to the primary copy. Ensure that the selected cluster is in a healthy state.

6. Confirm that you understand the potentially disruptive nature of a failover by typing **Failover** into the confirmation entry and clicking **I understand, failover group** to begin the failover.

    ![Fail Over Recovery Group](/media/tidb-cloud/recovery-group/recovery-group-failover.png)
