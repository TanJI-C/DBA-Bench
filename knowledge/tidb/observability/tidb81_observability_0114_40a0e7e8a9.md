# Monitoring dashboards and tool compatibility for resource control

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-resource-control.md`
- Source Title: `Use Resource Control to Achieve Resource Isolation`
- Source Heading Path: `Use Resource Control to Achieve Resource Isolation > Monitoring metrics and charts | Use Resource Control to Achieve Resource Isolation > Tool compatibility`
- Source Line Ranges: `613-640`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `tikv`, `br`, `lightning`, `ticdc`
- Topic Tags: `resource-control`, `monitoring`, `grafana`, `dashboard`, `metrics`, `resource-groups`, `tool-compatibility`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0114_40a0e7e8a9`
- Source ID: `tidb-docs-8.1:tidb-resource-control.md#monitoring-metrics-and-charts`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e89767f88a46a826283f375846b1a525abe6534270dfbd70a6090059370f36c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-resource-control#monitoring-metrics-and-charts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-resource-control.md

## Retrieval Guidance

- Use When: Use this chunk when you need where resource control metrics and charts are exposed or the documented compatibility of resource control with BR, TiDB Lightning, and TiCDC.
- Retrieval Keywords: Grafana TiDB Resource Control dashboard, TiDB Important Monitoring Metrics, Resource Control section, TiKV request QPS from different resource groups, Grafana TiKV dashboard, RESOURCE_GROUPS table, TiDB Dashboard Resource Manager page, TiDB Self-Managed only, TiDB Cloud does not provide resource control metrics, tool compatibility, BR, TiDB Lightning, TiCDC, DDL operations related to resource control
- Follow-up Guidance: The source says BR, TiDB Lightning, and TiCDC do not currently support processing DDL operations related to resource control, and their resource consumption is not limited by resource control.
- Classification Note: This is classified as observability because it identifies the official dashboards, metrics locations, and dashboard table views for monitoring resource control, while also noting related tool compatibility limits.

## Official Source Content

## Monitoring metrics and charts

TiDB regularly collects runtime information about resource control and provides visual charts of the metrics in Grafana's **TiDB** > **Resource Control** dashboard. The metrics are detailed in the **Resource Control** section of [TiDB Important Monitoring Metrics](https://docs.pingcap.com/tidb/stable/grafana-tidb-dashboard).

TiKV also records the request QPS from different resource groups. For more details, see [TiKV Monitoring Metrics Detail](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#grpc).

You can view the data of resource groups in the current [`RESOURCE_GROUPS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-resource-groups) table in TiDB Dashboard. For more details, see [Resource Manager page](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager).

> **Note:**
>
> This section is only applicable to TiDB Self-Managed. Currently, TiDB Cloud does not provide resource control metrics.

TiDB regularly collects runtime information about resource control and provides visual charts of the metrics in Grafana's **TiDB** > **Resource Control** dashboard.

TiKV also records the request QPS from different resource groups in Grafana's **TiKV** dashboard.
## Tool compatibility

The resource control feature does not impact the regular usage of data import, export, and other replication tools. BR, TiDB Lightning, and TiCDC do not currently support processing DDL operations related to resource control, and their resource consumption is not limited by resource control.
