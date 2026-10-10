# TiDB Cloud monitoring maintenance window and impact notice

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/notification-2024-04-09-monitoring-features-maintenance.md`
- Source Title: `2024-04-09 TiDB Cloud Monitoring Features Maintenance Notification`
- Source Heading Path: `[2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification | [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification > Maintenance window | [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification > Impact | [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification > Impact > Affected regions | [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification > Impact > Affected monitoring features | [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification > Completion and resumption | [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification > Get support`
- Source Line Ranges: `5-53`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `maintenance`, `monitoring`, `metrics`, `slow-query`, `regions`, `availability`, `support`, `notification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0100_a9ca6a2893`
- Source ID: `tidb-docs-8.1:tidb-cloud/notification-2024-04-09-monitoring-features-maintenance.md#2024-04-09-tidb-cloud-monitoring-features-maintenance-notification`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6fd615efdb2a6478f28bd06d9a08bdf3e4c9c9ee8d0a2478a8fc7bf7073ab7d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/notification-2024-04-09-monitoring-features-maintenance#2024-04-09-tidb-cloud-monitoring-features-maintenance-notification
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/notification-2024-04-09-monitoring-features-maintenance.md

## Retrieval Guidance

- Use When: Use this chunk when asking about the TiDB Cloud monitoring maintenance on 2024-04-09, including the maintenance window, affected regions, and temporary impact on monitoring features.
- Retrieval Keywords: 2024-04-09 TiDB Cloud Monitoring Features Maintenance Notification, maintenance window 2024-04-09 08:00 UTC+0 12:00 UTC+0, Metrics page temporarily unavailable, Slow Query page temporarily unavailable, Prometheus DataDog NewRelic breakpoints, TiDB Cloud Dedicated clusters AWS Oregon us-west-2, AWS Seoul ap-northeast-2, AWS Frankfurt eu-central-1, Google Cloud Oregon us-west1, Google Cloud Tokyo asia-northeast1, Google Cloud Singapore asia-southeast1, Google Cloud Iowa us-central1, Google Cloud Taiwan asia-east1, TiDB Cloud Serverless clusters AWS Frankfurt eu-central-1, TiDB Cloud Serverless clusters AWS Oregon us-west-2, all other functionalities remain unaffected, read/write operations as usual, contact support team
- Follow-up Guidance: If questions or assistance are needed, the source says to contact the support team.
- Classification Note: This chunk is classified as observability for TiDB Cloud because it is a maintenance notification about monitoring features, including Metrics, Slow Query, and metrics integrations in specific cloud regions.

## Official Source Content

# [2024-04-09] TiDB Cloud Monitoring Features Maintenance Notification

This notification describes the details that you need to know about the TiDB Cloud [monitoring features](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-tidb-cluster) maintenance on April 9, 2024.
## Maintenance window

- Start time: 2024-04-09 08:00 (UTC+0)
- End time: 2024-04-09 12:00 (UTC+0)
- Duration: 4 hours
## Impact
### Affected regions

During the maintenance window, the monitoring features in the following regions will be affected:

- TiDB Cloud Dedicated clusters：
    - Cloud Provider: AWS, Region: Oregon (us-west-2)
    - Cloud Provider: AWS, Region: Seoul (ap-northeast-2)
    - Cloud Provider: AWS, Region: Frankfurt (eu-central-1)
    - Cloud Provider: AWS, Region: Oregon (us-west-2)
    - Cloud Provider: Google Cloud, Region: Oregon (us-west1)
    - Cloud Provider: Google Cloud, Region: Tokyo (asia-northeast1)
    - Cloud Provider: Google Cloud, Region: Singapore (asia-southeast1)
    - Cloud Provider: Google Cloud, Region: Iowa (us-central1)
    - Cloud Provider: Google Cloud, Region: Taiwan (asia-east1)

- TiDB Cloud Serverless clusters：
    - Cloud Provider: AWS, Region: Frankfurt (eu-central-1)
    - Cloud Provider: AWS, Region: Oregon (us-west-2)
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
