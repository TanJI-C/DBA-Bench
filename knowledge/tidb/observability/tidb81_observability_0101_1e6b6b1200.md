# TiDB Cloud monitoring maintenance window and impact on features

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notification-2024-04-16-monitoring-features-maintenance.md`
- Source Title: `2024-04-16 TiDB Cloud Monitoring Features Maintenance Notification`
- Source Heading Path: `[2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification | [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification > Maintenance window | [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification > Impact | [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification > Impact > Affected regions | [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification > Impact > Affected monitoring features | [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification > Completion and resumption | [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification > Get support`
- Source Line Ranges: `5-46`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `maintenance`, `monitoring`, `metrics`, `slow-query`, `prometheus`, `datadog`, `newrelic`, `availability`, `support`, `regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0101_1e6b6b1200`
- Source ID: `tidb-docs-8.1:tidb-cloud/notification-2024-04-16-monitoring-features-maintenance.md#2024-04-16-tidb-cloud-monitoring-features-maintenance-notification`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11ec96318414fdde36357f9af17992fce031ec7cd1b2c8259dce25c24d999632`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notification-2024-04-16-monitoring-features-maintenance#2024-04-16-tidb-cloud-monitoring-features-maintenance-notification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notification-2024-04-16-monitoring-features-maintenance.md

## Retrieval Guidance

- Use When: Use this when asking about the April 16, 2024 TiDB Cloud monitoring maintenance window, affected AWS regions, or temporary unavailability of monitoring features and integrations.
- Retrieval Keywords: 2024-04-16 TiDB Cloud Monitoring Features Maintenance Notification, maintenance window 2024-04-16 08:00 UTC+0 to 12:00 UTC+0, TiDB Cloud monitoring features maintenance, AWS Tokyo ap-northeast-1, AWS N. Virginia us-east-1, TiDB Cloud Dedicated clusters affected regions, TiDB Cloud Serverless clusters affected regions, Metrics page temporarily unavailable, Slow Query page temporarily unavailable, Prometheus DataDog NewRelic breakpoints, all other functionalities remain unaffected, read/write operations as usual, contact support team
- Follow-up Guidance: If there are questions or assistance is needed, the content says to contact the TiDB Cloud support team.
- Classification Note: This is classified as observability for the cloud component because the content is a TiDB Cloud notice about maintenance impact on monitoring features such as Metrics, Slow Query, and metrics integrations.

## Official Source Content

# [2024-04-16] TiDB Cloud Monitoring Features Maintenance Notification

This notification describes the details that you need to know about the TiDB Cloud [monitoring features](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster) maintenance on April 16, 2024.
## Maintenance window

- Start time: 2024-04-16 08:00 (UTC+0)
- End time: 2024-04-16 12:00 (UTC+0)
- Duration: 4 hours
## Impact
### Affected regions

During the maintenance window, the monitoring features in the following regions will be affected:

- TiDB Cloud Dedicated clusters：
    - Cloud Provider: AWS, Region: Tokyo (ap-northeast-1)
    - Cloud Provider: AWS, Region: N. Virginia (us-east-1)

- TiDB Cloud Serverless clusters：
    - Cloud Provider: AWS, Region: Tokyo (ap-northeast-1)
    - Cloud Provider: AWS, Region: N. Virginia (us-east-1)
### Affected monitoring features

> **Note:**
>
> The maintenance only affects monitoring features in the TiDB cluster. All the other functionalities remain unaffected. You can continue to manage the TiDB cluster and perform read/write operations or other operations as usual.

- The **Metrics** page will be temporarily unavailable for several short periods (each less than 20 minutes).
- The **Slow Query** page will be temporarily unavailable for several short periods (each less than 5 minutes).
- The metrics integration with Prometheus, DataDog, and NewRelic might have breakpoints.
## Completion and resumption

Once the maintenance is successfully completed, the affected functionalities will be reinstated, offering you an even better experience.
## Get support

If you have any questions or need assistance, contact our [support team](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support). We are here to address your concerns and provide any necessary guidance.
