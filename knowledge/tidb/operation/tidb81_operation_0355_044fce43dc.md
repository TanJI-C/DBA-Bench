# Delete a recovery group in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/recovery-group-delete.md`
- Source Title: `Delete a Recovery Group`
- Source Heading Path: `Delete a Recovery Group | Delete a Recovery Group > Delete a recovery group`
- Source Line Ranges: `5-24`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `recovery-group`, `deletion`, `replication`, `disaster-protection`, `console`, `warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0355_044fce43dc`
- Source ID: `tidb-docs-8.1:tidb-cloud/recovery-group-delete.md#delete-a-recovery-group`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5423145af41a7d90654c68c969c3f63e54ad93c103f34e065b96daba3473efa9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/recovery-group-delete#delete-a-recovery-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/recovery-group-delete.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the TiDB Cloud console procedure and consequences for deleting a recovery group.
- Retrieval Keywords: Delete a Recovery Group, delete a recovery group, TiDB Cloud console, Recovery Group page, Action menu, Delete, I understand, delete it, replication relationships, databases are no longer protected against disasters
- Follow-up Guidance: The content states that deleting a recovery group also removes all associated replication relationships and that the associated databases are no longer protected against disasters.
- Classification Note: The classification is operation because the content provides a step-by-step console procedure to delete a recovery group in TiDB Cloud.

## Official Source Content

# Delete a Recovery Group

When a recovery group is no longer needed, you can delete it.
## Delete a recovery group

When a recovery group is no longer needed to manage the replication of a set of databases, you can delete it from the system.

1. In the [TiDB Cloud console](https://tidbcloud.com/), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Recovery Group**.
3. On the **Recovery Group** page, locate the name of the recovery group that you wish to delete.
4. Click the **Action** menu for the recovery group, and then click **Delete**. The deletion dialog is displayed.

    > **Warning**
    >
    > - Deleting a recovery group also removes all associated replication relationships associated with that recovery group. 
    > - The databases associated with the recovery group are no longer protected against disasters.

5. Confirm that you understand the impact of the deletion by typing the name of the recovery group and clicking **I understand, delete it**.
