# PD dashboard overview

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-pd-dashboard.md`
- Source Title: `Key Monitoring Metrics of PD`
- Source Heading Path: `Key Monitoring Metrics of PD | Key Monitoring Metrics of PD > Key metrics description`
- Source Line Ranges: `5-28`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `dashboard`
- Topic Tags: `grafana`, `monitoring`, `dashboard`, `pd status`, `metrics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0048_df0962b43f`
- Source ID: `tidb-docs-8.1:grafana-pd-dashboard.md#key-monitoring-metrics-of-pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dfb780d867c65275e2e9b5c292e8bf51fca737f9db9acd22053f774fcc705ac9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-pd-dashboard#key-monitoring-metrics-of-pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-pd-dashboard.md

## Retrieval Guidance

- Use When: Use this when you need the PD dashboard overview and the basic PD status metrics shown in Grafana.
- Retrieval Keywords: PD dashboard, Key Monitoring Metrics of PD, PD role, Storage capacity, Current storage size, Current storage usage, Normal stores, Number of Regions, Abnormal stores, Region health, Current peer count, Prometheus & Grafana
- Follow-up Guidance: This section introduces the PD dashboard as part of the Grafana monitoring system and describes the main status metrics.
- Classification Note: This chunk is an observability overview for PD dashboard metrics and their high-level status descriptions.

## Official Source Content

# Key Monitoring Metrics of PD

If you use TiUP to deploy the TiDB cluster, the monitoring system (Prometheus & Grafana) is deployed at the same time. For more information, see [Overview of the Monitoring Framework](https://docs.pingcap.com/tidb/stable/tidb-monitoring-framework).

The Grafana dashboard is divided into a series of sub dashboards which include Overview, PD, TiDB, TiKV, Node\_exporter, Disk Performance, and Performance\_overview. A lot of metrics are there to help you diagnose.

You can get an overview of the component PD status from the PD dashboard, where the key metrics are displayed. This document provides a detailed description of these key metrics.

The following is the description of PD Dashboard metrics items:

- PD role: The role of the current PD instance
- Storage capacity: The total storage capacity for this TiDB cluster
- Current storage size: The storage size that is currently used by the TiDB cluster
- Current storage usage: The current storage usage rate
- Normal stores: The count of healthy storage instances
- Number of Regions: The total count of cluster Regions
- Abnormal stores: The count of unhealthy stores. The normal value is `0`. If the number is bigger than `0`, it means at least one instance is abnormal.
- Region health: The health status of Regions indicated via the count of unusual Regions including pending peers, down peers, extra peers, offline peers, missing peers, learner peers and incorrect namespaces. Generally, the number of pending peers should be less than `100`. The missing peers should not be persistently greater than `0`. If many empty Regions exist, enable Region Merge in time.
- Current peer count: The current count of all cluster peers
![PD Dashboard - Header](/media/pd-dashboard-header-v4.png)
## Key metrics description
