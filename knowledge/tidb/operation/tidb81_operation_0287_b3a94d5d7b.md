# Review changefeed configuration and start replication

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-cloud-storage.md`
- Source Title: `Sink to Cloud Storage`
- Source Heading Path: `Sink to Cloud Storage > Step 4. Review the configuration and start replication`
- Source Line Ranges: `165-174`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `changefeed`, `review`, `creation`, `replication`, `status`, `checkpoint`, `latency`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0287_b3a94d5d7b`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-cloud-storage.md#step-4-review-the-configuration-and-start-replication`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3623e9c653d7cc386124b4fe4ae43dee430f11bc68d56fb7e67b6148f18124f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-cloud-storage#step-4-review-the-configuration-and-start-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-cloud-storage.md

## Retrieval Guidance

- Use When: Use this content when looking for how to review a TiDB Cloud changefeed configuration, create the changefeed, and confirm that replication has started from the status and details page.
- Retrieval Keywords: Step 4. Review the configuration and start replication, Click Next to review the changefeed configuration, click Create, click Previous, status changing from Creating to Running, changefeed details page, checkpoint status, replication latency, relevant metrics, sink to cloud storage
- Follow-up Guidance: After the sink starts, you can click the name of the changefeed to open its details page and view checkpoint status, replication latency, and other relevant metrics.
- Classification Note: This is classified as an operation because the content describes the UI steps to review configuration, create the changefeed, and observe its running status and metrics in TiDB Cloud.

## Official Source Content

## Step 4. Review the configuration and start replication

Click **Next** to review the changefeed configuration.

- If you have verified that all configurations are correct, click **Create** to proceed with the creation of the changefeed.
- If you need to modify any configurations, click **Previous** to go back and make the necessary changes.

The sink will start shortly, and you will observe the status of the sink changing from **Creating** to **Running**.

Click the name of the changefeed to go to its details page. On this page, you can view more information about the changefeed, including the checkpoint status, replication latency, and other relevant metrics.
