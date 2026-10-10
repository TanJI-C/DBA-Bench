# Observability features: independent Dashboard pod and Performance Overview panels

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.5.0.md`
- Source Title: `TiDB 6.5.0 Release Notes`
- Source Heading Path: `TiDB 6.5.0 Release Notes > New features > Observability`
- Source Line Ranges: `123-147`
- Source Scope: `all`
- Primary Component: `dashboard`
- Related Components: `operator`, `pd`, `tiflash`, `ticdc`, `shared`
- Topic Tags: `dashboard`, `kubernetes`, `grafana`, `performance-overview`, `monitoring`, `diagnosis`, `tiflash`, `ticdc`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0074_53ec6c8839`
- Source ID: `tidb-docs-8.1:releases/release-6.5.0.md#observability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a3ded8ac6d1d09a1922924692c519119a6205a0994fce802cf59c370ef80d859`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.5.0#observability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.5.0.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about TiDB 6.5.0 observability updates for deploying TiDB Dashboard as an independent Pod on Kubernetes or for new Grafana Performance Overview panels for TiFlash and TiCDC.
- Retrieval Keywords: TiDB Dashboard independent Pod, Kubernetes, TiDB Operator v1.4.0, PD nodes, Performance Overview dashboard, Grafana, TiFlash panels, CDC panels, TiCDC, overall performance diagnosis, independent Dashboard pod
- Follow-up Guidance: The source also points to documentation for deploying TiDB Dashboard independently and for performance tuning methods related to the Performance Overview dashboard.
- Classification Note: This is classified as observability because the content covers Dashboard deployment for diagnosis access and Grafana Performance Overview monitoring panels for TiFlash and TiCDC.

## Official Source Content

### Observability

* TiDB Dashboard can be deployed on Kubernetes as an independent Pod [#1447](https://github.com/pingcap/tidb-dashboard/issues/1447) @[SabaPing](https://github.com/SabaPing)

    TiDB v6.5.0 (and later) and TiDB Operator v1.4.0 (and later) support deploying TiDB Dashboard as an independent Pod on Kubernetes. Using TiDB Operator, you can access the IP address of this Pod to start TiDB Dashboard.

    Independently deploying TiDB Dashboard provides the following benefits:

    - The compute work of TiDB Dashboard does not pose pressure on PD nodes. This ensures more stable cluster operation.
    - The user can still access TiDB Dashboard for diagnosis even if the PD node is unavailable.
    - Accessing TiDB Dashboard on the internet does not involve the privileged interfaces of PD. Therefore, the security risk of the cluster is reduced.

  For more information, see [documentation](https://docs.pingcap.com/tidb-in-kubernetes/v1.5/get-started#deploy-tidb-dashboard-independently).

* Performance Overview dashboard adds TiFlash and CDC (Change Data Capture) panels [#39230](https://github.com/pingcap/tidb/issues/39230) @[dbsid](https://github.com/dbsid)

    Since v6.1.0, TiDB has introduced the Performance Overview dashboard in Grafana, which provides a system-level entry for overall performance diagnosis of TiDB, TiKV, and PD. In v6.5.0, the Performance Overview dashboard adds TiFlash and CDC panels. With these panels, starting from v6.5.0, you can use the Performance Overview dashboard to analyze the performance of all components in a TiDB cluster.

    The TiFlash and CDC panels reorganize the TiFlash and TiCDC monitoring information, which can help you greatly improve the efficiency of analyzing and troubleshooting TiFlash and TiCDC performance issues.

    - On the [TiFlash panels](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#tiflash), you can easily view the request types, latency analysis, and resource usage overview of your TiFlash cluster.
    - On the [CDC panels](https://docs.pingcap.com/tidb/stable/grafana-performance-overview-dashboard#cdc), you can easily view the health, replication latency, data flow, and downstream write latency of your TiCDC cluster.

  For more information, see [documentation](https://docs.pingcap.com/tidb/stable/performance-tuning-methods).
