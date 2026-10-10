# Cancel export tasks, speed limits, and pricing

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/serverless-export.md`
- Source Title: `Export Data from TiDB Cloud Serverless`
- Source Heading Path: `Export Data from TiDB Cloud Serverless > Examples > Cancel an export task | Export Data from TiDB Cloud Serverless > Export speed | Export Data from TiDB Cloud Serverless > Pricing`
- Source Line Ranges: `385-428`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `export`, `task-cancellation`, `console`, `cli`, `throughput`, `cluster-plan`, `pricing`, `request-units`, `beta`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0365_b89bdaa038`
- Source ID: `tidb-docs-8.1:tidb-cloud/serverless-export.md#cancel-an-export-task`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c184ee3e32e75ca08789913d2278d8c8ffd8eacf7aadc60df33c889a562b43f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/serverless-export#cancel-an-export-task
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/serverless-export.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to cancel a TiDB Cloud Serverless export task or needs the documented export speed and pricing details.
- Retrieval Keywords: Cancel an export task, ticloud serverless export cancel, -e <export-id>, Running status, Export speed, cluster plan, Free cluster plan, Up to 25 MiB/s, Scalable cluster plan, Up to 100 MiB/s, Pricing, beta period, Request Units (RUs), successful or canceled tasks, failed export tasks
- Follow-up Guidance: The source states that only export tasks in the Running status can be canceled, and that pricing charges only the Request Units generated during successful or canceled tasks while failed tasks are not charged.
- Classification Note: This chunk is classified as operation because it covers operational task cancellation along with documented throughput limits by cluster plan and pricing behavior for export tasks.

## Official Source Content

### Cancel an export task

To cancel an ongoing export task, take the following steps:

<div label="Console">

1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

   > **Tip:**
   >
   > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

2. Click the name of your target cluster to go to its overview page, and then click **Data** > **Import** in the left navigation pane.

3. On the **Import** page, click **Export** to view the export task list.

4. Choose the export task you want to cancel, and then click **Action**.

5. Choose **Cancel** in the drop-down list. Note that you can only cancel the export task that is in the **Running** status.

</div>

<div label="CLI">

```shell
ticloud serverless export cancel -c <cluster-id> -e <export-id>
```

</div>
## Export speed

The export speed depends on your [cluster plan](https://docs.pingcap.com/tidb/stable/tidb-cloud/select-cluster-tier#cluster-plans). For details, see the following table:

| Plan               | Export speed       |
|:-------------------|:-------------------|
| Free cluster plan      | Up to 25 MiB/s      |
| Scalable cluster plan  | Up to 100 MiB/s     |
## Pricing

The export service is free during the beta period. You only need to pay for the [Request Units (RUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#request-unit) generated during the export process of successful or canceled tasks. For failed export tasks, you will not be charged.
