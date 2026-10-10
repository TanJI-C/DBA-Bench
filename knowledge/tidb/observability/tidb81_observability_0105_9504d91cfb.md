# Data Migration alerts and recommended actions

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md`
- Source Title: `Precheck Errors, Migration Errors, and Alerts for Data Migration`
- Source Heading Path: `Precheck Errors, Migration Errors, and Alerts for Data Migration > Alerts`
- Source Line Ranges: `97-126`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`
- Topic Tags: `alerts`, `email-subscription`, `export-errors`, `import-errors`, `incremental-migration`, `paused-jobs`, `replication-lag`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0105_9504d91cfb`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md#alerts`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8e5bdbfdf9eb0968bf62bf35d683e2fe413b791841cf7eceacd03b33d58cbb5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting#alerts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-dm-precheck-and-troubleshooting.md

## Retrieval Guidance

- Use When: Use this when looking for TiDB Cloud Data Migration alert names, their recommended actions, or where to subscribe to alert emails.
- Retrieval Keywords: Alerts, TiDB Cloud alert emails, Data migration job met error during data export, Data migration job met error during data import, Data migration job met error during incremental data migration, Data migration job has been paused for more than 6 hours during incremental migration, Replication lag is larger than 10 minutes and stilling increasing for more than 20 minutes, TiDB Cloud Support, TiDB Cloud Built-in Alerting
- Follow-up Guidance: If needed, the document points to TiDB Cloud Support and TiDB Cloud Built-in Alerting for more information.
- Classification Note: This chunk classifies as observability because it lists Data Migration alerts and their recommended actions.

## Official Source Content

## Alerts

You can subscribe to TiDB Cloud alert emails to be informed in time when an alert occurs.

The following are alerts about Data Migration: 

- "Data migration job met error during data export"

    Recommended action: check the error message on the data migration page, and see [Migration errors and solutions](#migration-errors-and-solutions) for help.

- "Data migration job met error during data import"

    Recommended action: check the error message on the data migration page, and see [Migration errors and solutions](#migration-errors-and-solutions) for help.

- "Data migration job met error during incremental data migration"

    Recommended action: check the error message on the data migration page, and see [Migration errors and solutions](#migration-errors-and-solutions) for help.

- "Data migration job has been paused for more than 6 hours during incremental migration" 

    Recommended action: resume the data migration job or ignore this alert.     

- "Replication lag is larger than 10 minutes and stilling increasing for more than 20 minutes"

    - Recommended action: contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for help.

If you need help to address these alerts, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for consultation.

For more information about how to subscribe to alert emails, see [TiDB Cloud Built-in Alerting](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting).
