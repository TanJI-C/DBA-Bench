# TiDB Cloud cluster events page, logged event types, and retention

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-events.md`
- Source Title: `TiDB Cloud Cluster Events`
- Source Heading Path: `TiDB Cloud Cluster Events | TiDB Cloud Cluster Events > View the Events page | TiDB Cloud Cluster Events > Logged events | TiDB Cloud Cluster Events > Event retention policy`
- Source Line Ranges: `5-58`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `events`, `monitoring`, `cluster-level`, `event-types`, `changefeed`, `retention`, `audit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0106_e83f7dd5a1`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-events.md#tidb-cloud-cluster-events`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5f0a29d1f34a810faed148f9626258bd654983ddf224b6254081ab25b2fb17d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-events#tidb-cloud-cluster-events
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-events.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks about the TiDB Cloud cluster-level Events page, which event types are logged, what event details are shown, or how long event data is retained.
- Retrieval Keywords: TiDB Cloud Cluster Events, Events page, Monitoring > Events, cluster-level events, logged events, event type, status, message, time, triggered by, trigger user, CreateCluster, PauseCluster, ResumeCluster, ModifyClusterSize, BackupCluster, ExportBackup, RestoreFromCluster, CreateChangefeed, PauseChangefeed, ResumeChangefeed, DeleteChangefeed, EditChangefeed, ScaleChangefeed, FailedChangefeed, ImportData, UpdateSpendingLimit, ResourceLimitation, event retention policy, 7 days
- Follow-up Guidance: The content also states that you can open a cluster overview from the Clusters page and then click Monitoring > Events in the left navigation pane.
- Classification Note: This is classified as observability for the cloud component because it describes viewing cluster historical events, supported logged event types, and event retention on the TiDB Cloud Events page.

## Official Source Content

# TiDB Cloud Cluster Events

TiDB Cloud logs the historical events at the cluster level. An *event* indicates a change in your TiDB Cloud cluster. You can view the logged events on the **Events** page, including the event type, status, message, trigger time, and trigger user.

This document describes how to view the events for TiDB Cloud clusters using the **Events** page and lists the supported event types.
## View the Events page

To view the events on the **Events** page, take the following steps:

1. On the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project, click the name of your target cluster to go to its overview page.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. In the left navigation pane, click **Monitoring** > **Events**.
## Logged events

TiDB Cloud logs the following types of cluster events:

| Event Type| Description |
|:--- |:--- |
| CreateCluster |  Create a cluster |  
| PauseCluster |   Pause a cluster |  
| ResumeCluster |   Resume a cluster | 
| ModifyClusterSize |   Modify cluster size | 
| BackupCluster |   Back up a cluster |  
| ExportBackup |   Export a backup |
| RestoreFromCluster |   Restore a cluster |  
| CreateChangefeed |   Create a changefeed |  
| PauseChangefeed |   Pause a changefeed | 
| ResumeChangefeed |   Resume a changefeed | 
| DeleteChangefeed |   Delete a changefeed |  
| EditChangefeed |  Edit a changefeed |  
| ScaleChangefeed |   Scale the specification of a changefeed |  
| FailedChangefeed |   Changefeed failures |  
| ImportData |   Import data to a cluster |  
| UpdateSpendingLimit |   Update spending limit of a TiDB Cloud Serverless scalable cluster |  
| ResourceLimitation |   Update resource limitation of a TiDB Cloud Serverless cluster |  

For each event, the following information is logged:

- Event Type
- Status
- Message
- Time
- Triggered By
## Event retention policy

Event data is kept for 7 days.
