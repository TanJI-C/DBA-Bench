# PD dashboard integration settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > `dashboard` | PD Configuration File > `dashboard` > `disable-custom-prom-addr` | PD Configuration File > `dashboard` > `tidb-cacert-path` | PD Configuration File > `dashboard` > `tidb-cert-path` | PD Configuration File > `dashboard` > `tidb-key-path``
- Source Line Ranges: `491-515`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `shared`
- Topic Tags: `dashboard`, `prometheus`, `tls`, `sql-service`, `certificates`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0129_2dec157257`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#dashboard`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af00342e8d84bfb5be21df18db791d123074dc508c11a086ab85e3d8aa73b80f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this when looking up PD built-in TiDB Dashboard configuration for custom Prometheus address handling or TLS certificate paths used to connect to TiDB SQL services.
- Retrieval Keywords: PD `dashboard`, TiDB Dashboard, disable-custom-prom-addr, custom Prometheus data source address, TiDB Dashboard reports an error, tidb-cacert-path, tidb-cert-path, tidb-key-path, connect to TiDB's SQL services using TLS
- Follow-up Guidance: When `disable-custom-prom-addr` is set to `true`, configuring a custom Prometheus data source address in TiDB Dashboard causes TiDB Dashboard to report an error.
- Classification Note: This is a dashboard configuration section because the content defines settings for the TiDB Dashboard built in PD, including Prometheus source behavior and TLS file paths.

## Official Source Content

## `dashboard`

Configuration items related to the [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) built in PD.
### `disable-custom-prom-addr`

+ Whether to disable configuring a custom Prometheus data source address in [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro).
+ Default value: `false`
+ When it is set to `true`, if you configure a custom Prometheus data source address in TiDB Dashboard, TiDB Dashboard reports an error.
### `tidb-cacert-path`

+ The path of the root CA certificate file. You can configure this path when you connect to TiDB's SQL services using TLS.
+ Default value: `""`
### `tidb-cert-path`

+ The path of the SSL certificate file. You can configure this path when you connect to TiDB's SQL services using TLS.
+ Default value: `""`
### `tidb-key-path`

+ The path of the SSL private key file. You can configure this path when you connect to TiDB's SQL services using TLS.
+ Default value: `""`
