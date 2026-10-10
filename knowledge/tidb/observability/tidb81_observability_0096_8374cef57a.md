# Grafana and TiDB Cloud metric value FAQ

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/monitor-prometheus-and-grafana-integration.md`
- Source Title: `Integrate TiDB Cloud with Prometheus and Grafana (Beta)`
- Source Heading Path: `Integrate TiDB Cloud with Prometheus and Grafana (Beta) > FAQ`
- Source Line Ranges: `107-111`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dashboard`, `ecosystem`
- Topic Tags: `faq`, `grafana`, `aggregation`, `metrics`, `display`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0096_8374cef57a`
- Source ID: `tidb-docs-8.1:tidb-cloud/monitor-prometheus-and-grafana-integration.md#faq`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84101a08875e31507e3009ff47f63ebc5fc99cc7006ba92cd8958e8611cd0e15`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/monitor-prometheus-and-grafana-integration#faq
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/monitor-prometheus-and-grafana-integration.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented explanation for why the same metric can show different values in Grafana and the TiDB Cloud console.
- Retrieval Keywords: FAQ, different values on Grafana and the TiDB Cloud console, aggregation calculation logic is different, mini step configuration in Grafana, fine-grained metric values
- Follow-up Guidance: The source says the displayed aggregated values might differ because Grafana and TiDB Cloud use different aggregation calculation logic, and mentions adjusting the mini step configuration in Grafana for more fine-grained metric values.
- Classification Note: This is classified as observability because it explains a metric display discrepancy between Grafana and the TiDB Cloud console in the monitoring context.

## Official Source Content

## FAQ

- Why does the same metric have different values on Grafana and the TiDB Cloud console at the same time?

    The aggregation calculation logic is different between Grafana and TiDB Cloud, so the displayed aggregated values might differ. You can adjust the `mini step` configuration in Grafana to get more fine-grained metric values.
