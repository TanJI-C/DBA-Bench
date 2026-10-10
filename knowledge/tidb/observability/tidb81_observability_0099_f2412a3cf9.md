# TiDB Cloud monitoring overview, metrics, alerting, events, and integrations

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitoring-concepts.md`
- Source Title: `Monitoring`
- Source Heading Path: `Monitoring | Monitoring > Built-in metrics | Monitoring > Built-in alerting | Monitoring > Cluster events | Monitoring > Third-party metrics integrations (Beta)`
- Source Line Ranges: `5-48`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dm`, `ticdc`, `shared`
- Topic Tags: `monitoring`, `metrics`, `alerting`, `events`, `integrations`, `beta`, `performance`, `notifications`, `changefeed`, `data-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0099_f2412a3cf9`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitoring-concepts.md#monitoring`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `08909b253da8b42feba8b7e212ffe78a05736f1303e535b402d8cd761dd02c64`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitoring-concepts#monitoring
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitoring-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for an overview of TiDB Cloud monitoring capabilities, including built-in metrics, built-in alerting, cluster events, and third-party metrics integrations.
- Retrieval Keywords: TiDB Cloud monitoring, Built-in metrics, Metrics page, Built-in alerting, Alerts page, Resource usage alerts, Data migration alerts, Changefeed alerts, Cluster events, Events page, event type, status, message, trigger time, trigger user, Third-party metrics integrations, Beta, Datadog integration, Prometheus and Grafana integration, New Relic integration, cluster performance, notifications
- Follow-up Guidance: The source points to related pages for TiDB Cloud Built-in Metrics, TiDB Cloud Built-in Alerting, TiDB Cloud Cluster Event, and Third-Party Metrics Integration (Beta).
- Classification Note: This is classified as observability for the cloud component because the content describes TiDB Cloud tools for monitoring cluster performance, alerts, events, and external metrics integrations.

## Official Source Content

# Monitoring

Monitoring in TiDB Cloud provides tools and integrations that enable you to oversee cluster performance, track activity, and respond to issues in a timely manner.
## Built-in metrics

Built-in metrics refer to a full set of standard metrics of your cluster that TiDB Cloud collects and presents on the **Metrics** page. With these metrics, you can easily identify performance issues and determine whether your current database deployment meets your requirements.

For more information, see [TiDB Cloud Built-in Metrics](https://docs.pingcap.com/tidb/stable/tidb-cloud/built-in-monitoring).
## Built-in alerting

Built-in alerting refers to the cluster alerting mechanism that TiDB Cloud provides to assist you in monitoring your cluster. Currently, TiDB Cloud provides the following three types of alerts:

- Resource usage alerts

- Data migration alerts

- Changefeed alerts

On the Alerts page of the TiDB Cloud console, you can view alerts of your cluster, edit alert rules, and subscribe to alert notification emails.

For more information, see [TiDB Cloud Built-in Alerting](https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-built-in-alerting).
## Cluster events

In TiDB Cloud, an event indicates a change in your TiDB Cloud cluster. TiDB Cloud logs the historical events at the cluster level to help you track cluster activities. You can view the logged events on the **Events** page, including the event type, status, message, trigger time, and trigger user.

For more information, see [TiDB Cloud Cluster Event](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-events).
## Third-party metrics integrations (Beta)

TiDB Cloud lets you integrate any of the following third-party metrics services to receive TiDB Cloud alerts and view the performance metrics of your TiDB cluster.

- Datadog integration

- Prometheus and Grafana integration

- New Relic integration

Currently, these third-party metrics integrations are in beta.

For more information, see [Third-Party Metrics Integration (Beta)](https://docs.pingcap.com/tidb/stable/tidb-cloud/third-party-monitoring-integrations).
