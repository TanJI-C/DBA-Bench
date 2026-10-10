# Run the AppFlow integration and review notes

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-aws-appflow-integration.md`
- Source Title: `Integrate TiDB with Amazon AppFlow`
- Source Heading Path: `Integrate TiDB with Amazon AppFlow > Step 3. Run the flow | Integrate TiDB with Amazon AppFlow > Noteworthy things | Integrate TiDB with Amazon AppFlow > Need help?`
- Source Line Ranges: `210-262`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `flow-execution`, `verification`, `sql-query`, `cloudwatch-logs`, `insert-strategy`, `upsert-strategy`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0002_3390730d63`
- Source ID: `tidb-docs-8.1:develop/dev-guide-aws-appflow-integration.md#step-3-run-the-flow`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `afad55b0bdb99dd7fa4eee761d5536d80a0dc4e850faa4ad4229a54c07647c4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-aws-appflow-integration#step-3-run-the-flow
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-aws-appflow-integration.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to run an Amazon AppFlow flow for the TiDB integration, verify data landed in TiDB with a SQL query, or find the documented notes about CloudWatch logs and supported write strategies.
- Retrieval Keywords: Run flow, Amazon AppFlow, CloudWatch, sf_account, SELECT * FROM sf_account;, Salesforce Account object, Insert strategy, Update strategy, Upsert strategy, Starter is NOT a production environment, Discord, Slack, support ticket
- Follow-up Guidance: If anything goes wrong, the content says you can navigate to the CloudWatch page on the AWS Management Console to get logs, and it also lists Discord, Slack, and support ticket links for help.
- Classification Note: The chunk is classified as a cloud data pipeline integration topic because it covers executing an AppFlow flow, validating records written into a TiDB table, and operational notes for this AWS-based connector workflow.

## Official Source Content

## Step 3. Run the flow

On the page of the newly created flow, click **Run flow** in the upper-right corner.

![run flow](/media/develop/aws-appflow-step-run-flow.png)

The following screenshot shows an example that the flow runs successfully:

![run success](/media/develop/aws-appflow-step-run-success.png)

Query the `sf_account` table, and you can see that the records from the Salesforce **Account** object have been written to it:

```sql
test> SELECT * FROM sf_account;
+--------------------+-------------------------------------+--------------------+---------------+--------+----------------+
| id                 | name                                | type               | billing_state | rating | industry       |
+--------------------+-------------------------------------+--------------------+---------------+--------+----------------+
| 001Do000003EDTlIAO | Sample Account for Entitlements     | null               | null          | null   | null           |
| 001Do000003EDTZIA4 | Edge Communications                 | Customer - Direct  | TX            | Hot    | Electronics    |
| 001Do000003EDTaIAO | Burlington Textiles Corp of America | Customer - Direct  | NC            | Warm   | Apparel        |
| 001Do000003EDTbIAO | Pyramid Construction Inc.           | Customer - Channel | null          | null   | Construction   |
| 001Do000003EDTcIAO | Dickenson plc                       | Customer - Channel | KS            | null   | Consulting     |
| 001Do000003EDTdIAO | Grand Hotels & Resorts Ltd          | Customer - Direct  | IL            | Warm   | Hospitality    |
| 001Do000003EDTeIAO | United Oil & Gas Corp.              | Customer - Direct  | NY            | Hot    | Energy         |
| 001Do000003EDTfIAO | Express Logistics and Transport     | Customer - Channel | OR            | Cold   | Transportation |
| 001Do000003EDTgIAO | University of Arizona               | Customer - Direct  | AZ            | Warm   | Education      |
| 001Do000003EDThIAO | United Oil & Gas, UK                | Customer - Direct  | UK            | null   | Energy         |
| 001Do000003EDTiIAO | United Oil & Gas, Singapore         | Customer - Direct  | Singapore     | null   | Energy         |
| 001Do000003EDTjIAO | GenePoint                           | Customer - Channel | CA            | Cold   | Biotechnology  |
| 001Do000003EDTkIAO | sForce                              | null               | CA            | null   | null           |
+--------------------+-------------------------------------+--------------------+---------------+--------+----------------+
```
## Noteworthy things

- If anything goes wrong, you can navigate to the [CloudWatch](https://console.aws.amazon.com/cloudwatch/home) page on the AWS Management Console to get logs.
- The steps in this document are based on [Building custom connectors using the Amazon AppFlow Custom Connector SDK](https://aws.amazon.com/blogs/compute/building-custom-connectors-using-the-amazon-appflow-custom-connector-sdk/).
- [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) is **NOT** a production environment.
- To prevent excessive length, the examples in this document only show the `Insert` strategy, but `Update` and `Upsert` strategies are also tested and can be used.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
