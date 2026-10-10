# TiDB Cloud changefeed overview, operations, billing, and states

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-overview.md`
- Source Title: `Changefeed`
- Source Heading Path: `Changefeed | Changefeed > View the Changefeed page | Changefeed > Create a changefeed | Changefeed > Query Changefeed RCUs | Changefeed > Scale a changefeed | Changefeed > Pause or resume a changefeed | Changefeed > Edit a changefeed | Changefeed > Delete a changefeed | Changefeed > Changefeed billing | Changefeed > Changefeed states`
- Source Line Ranges: `5-109`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `changefeed`, `streaming`, `sink`, `rcu`, `scaling`, `pause`, `resume`, `edit`, `delete`, `billing`, `replication-state`, `gc`, `limits`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0078_164a4ff078`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-overview.md#changefeed`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bcdf976d40adad28d66cdaf525c28a645a95b3d1f70cf16936650bfe6cc43f0e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-overview#changefeed
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the TiDB Cloud changefeed overview, supported sink targets, page navigation, operational actions, RCU scaling and querying, billing reference, limits, or the meaning of changefeed states.
- Retrieval Keywords: TiDB Cloud changefeed, Changefeed page, Data > Changefeed, stream data from TiDB Cloud, Apache Kafka, MySQL, TiDB Cloud, cloud storage, up to 100 changefeeds per cluster, up to 100 table filter rules per changefeed, TiDB Cloud Serverless clusters changefeed feature is unavailable, TiCDC Replication Capacity Units, RCUs, View changefeed RCUs, Scale Up/Down, Pause/Resume, Edit, Delete, changefeed billing, replication task state, CREATING, RUNNING, EDITING, PAUSING, PAUSED, RESUMING, DELETING, DELETED, WARNING, FAILED, checkpoint-ts, GC operations, default Time-To-Live TTL 24 hours
- Follow-up Guidance: The source also points to sink-specific creation tutorials for Apache Kafka, MySQL, TiDB Cloud, and cloud storage, and explains that editing is only allowed when the changefeed status is `Paused`.
- Classification Note: This is classified as data_pipeline for the cloud component because the content describes TiDB Cloud changefeed data streaming, sink destinations, operational controls, capacity units, and replication task states.

## Official Source Content

# Changefeed

TiDB Cloud changefeed helps you stream data from TiDB Cloud to other data services. Currently, TiDB Cloud supports streaming data to Apache Kafka, MySQL, TiDB Cloud and cloud storage.

> **Note:**
>
> - Currently, TiDB Cloud only allows up to 100 changefeeds per cluster.
> - Currently, TiDB Cloud only allows up to 100 table filter rules per changefeed.
> - For [TiDB Cloud Serverless clusters](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#tidb-cloud-serverless), the changefeed feature is unavailable.
## View the Changefeed page

To access the changefeed feature, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

    > **Tip:**
    >
    > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Changefeed** in the left navigation pane. The changefeed page is displayed.

On the **Changefeed** page, you can create a changefeed, view a list of existing changefeeds, and operate the existing changefeeds (such as scaling, pausing, resuming, editing, and deleting a changefeed).
## Create a changefeed

To create a changefeed, refer to the tutorials:

- [Sink to Apache Kafka](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka)
- [Sink to MySQL](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-mysql)
- [Sink to TiDB Cloud](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-tidb-cloud)
- [Sink to cloud storage](https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-cloud-storage)
## Query Changefeed RCUs

1. Navigate to the [**Changefeed**](#view-the-changefeed-page) page of your target TiDB cluster.
2. Locate the corresponding changefeed you want to query, and click **...** > **View** in the **Action** column.
3. You can see the current TiCDC Replication Capacity Units (RCUs) in the **Specification** area of the page.
## Scale a changefeed

You can change the TiCDC Replication Capacity Units (RCUs) of a changefeed by scaling up or down the changfeed.

> **Note:**
>
> - To scale a changefeed for a cluster, make sure that all changefeeds for this cluster are created after March 28, 2023.
> - If a cluster has changefeeds created before March 28, 2023, neither the existing changefeeds nor newly created changefeeds for this cluster support scaling up or down.

1. Navigate to the [**Changefeed**](#view-the-changefeed-page) page of your target TiDB cluster.
2. Locate the corresponding changefeed you want to scale, and click **...** > **Scale Up/Down** in the **Action** column.
3. Select a new specification.
4. Click **Submit**.

It takes about 10 minutes to complete the scaling process (during which the changfeed works normally) and a few seconds to switch to the new specification (during which the changefeed will be paused and resumed automatically).
## Pause or resume a changefeed

1. Navigate to the [**Changefeed**](#view-the-changefeed-page) page of your target TiDB cluster.
2. Locate the corresponding changefeed you want to pause or resume, and click **...** > **Pause/Resume** in the **Action** column.
## Edit a changefeed

> **Note:**
>
> TiDB Cloud currently only allows editing changefeeds in the paused status.

1. Navigate to the [**Changefeed**](#view-the-changefeed-page) page of your target TiDB cluster.
2. Locate the changefeed you want to pause, and click **...** > **Pause** in the **Action** column.
3. When the changefeed status changes to `Paused`, click **...** > **Edit** to edit the corresponding changefeed.

    TiDB Cloud populates the changefeed configuration by default. You can modify the following configurations:

    - Apache Kafka sink: all configurations.
    - MySQL sink: **MySQL Connection**, **Table Filter**, and **Event Filter**.
    - TiDB Cloud sink: **TiDB Cloud Connection**, **Table Filter**, and **Event Filter**.
    - Cloud storage sink: **Storage Endpoint**, **Table Filter**, and **Event Filter**.

4. After editing the configuration, click **...** > **Resume** to resume the corresponding changefeed.
## Delete a changefeed

1. Navigate to the [**Changefeed**](#view-the-changefeed-page) page of your target TiDB cluster.
2. Locate the corresponding changefeed you want to delete, and click **...** > **Delete** in the **Action** column.
## Changefeed billing

To learn the billing for changefeeds in TiDB Cloud, see [Changefeed billing](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-ticdc-rcu).
## Changefeed states

The state of a replication task represents the running state of the replication task. During the running process, replication tasks might fail with errors, or be manually paused or resumed. These behaviors can lead to changes of the replication task state.

The states are described as follows:

- `CREATING`: the replication task is being created.
- `RUNNING`: the replication task runs normally and the checkpoint-ts proceeds normally.
- `EDITING`: the replication task is being edited.
- `PAUSING`: the replication task is being paused.
- `PAUSED`: the replication task is paused.
- `RESUMING`: the replication task is being resumed.
- `DELETING`: the replication task is being deleted.
- `DELETED`: the replication task is deleted.
- `WARNING`: the replication task returns a warning. The replication cannot continue due to some recoverable errors. The changefeed in this state keeps trying to resume until the state transfers to `RUNNING`. The changefeed in this state blocks [GC operations](https://docs.pingcap.com/tidb/stable/garbage-collection-overview).
- `FAILED`: the replication task fails. Due to some errors, the replication task cannot resume and cannot be recovered automatically. If the issues are resolved before the garbage collection (GC) of the incremental data, you can manually resume the failed changefeed. The default Time-To-Live (TTL) duration for incremental data is 24 hours, which means that the GC mechanism does not delete any data within 24 hours after the changefeed is interrupted.
