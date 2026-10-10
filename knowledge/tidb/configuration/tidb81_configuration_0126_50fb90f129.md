# PD metric push interval

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > `metric` > `interval``
- Source Line Ranges: `267-271`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `shared`
- Topic Tags: `metrics`, `prometheus`, `interval`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0126_50fb90f129`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#interval`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `792f8497038e60625ccd7fd1d105d266155f424f7e563e4f2f4552dbeadb10ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#interval
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this when looking up the PD configuration item that sets the interval for pushing monitoring metric data to Prometheus.
- Retrieval Keywords: metric interval, PD `metric` `interval`, Prometheus push interval, monitoring metric data is pushed to Prometheus, default value `15s`
- Follow-up Guidance: 
- Classification Note: This is a PD configuration setting for metrics because the content defines the `metric` > `interval` option and its default value.

## Official Source Content

### `interval`

+ The interval at which monitoring metric data is pushed to Prometheus
+ Default value: `15s`
