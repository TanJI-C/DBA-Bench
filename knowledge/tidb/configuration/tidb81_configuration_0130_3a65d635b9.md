# Dashboard public path and telemetry compatibility settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > `dashboard` > `public-path-prefix` | PD Configuration File > `dashboard` > `enable-telemetry``
- Source Line Ranges: `516-530`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`
- Topic Tags: `reverse-proxy`, `url-prefix`, `telemetry`, `compatibility`, `deprecated-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0130_3a65d635b9`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#public-path-prefix`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c66d0cec3d33efdc14757e0081a0f1b0b8cae101918b0767ef84414e318a081b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#public-path-prefix
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when locating PD dashboard configuration for reverse proxy URL path prefix behavior or the retained but nonfunctional telemetry compatibility setting in TiDB Dashboard.
- Retrieval Keywords: public-path-prefix, enable-telemetry, TiDB Dashboard, reverse proxy, public URL path prefix, web resources, /dashboard, telemetry feature removed, retained solely for compatibility with earlier versions, access issues might occur
- Follow-up Guidance: The source also points to Use TiDB Dashboard behind a Reverse Proxy for details.
- Classification Note: This is classified as dashboard configuration because the content defines TiDB Dashboard settings `public-path-prefix` and `enable-telemetry` in the PD configuration file.

## Official Source Content

### `public-path-prefix`

+ When TiDB Dashboard is accessed behind a reverse proxy, this item sets the public URL path prefix for all web resources.
+ Default value: `/dashboard`
+ Do **not** modify this configuration item when TiDB Dashboard is accessed not behind a reverse proxy; otherwise, access issues might occur. See [Use TiDB Dashboard behind a Reverse Proxy](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-reverse-proxy) for details.
### `enable-telemetry`

> **Warning:**
>
> Starting from v8.1.0, the telemetry feature in TiDB Dashboard is removed, and this configuration item is no longer functional. It is retained solely for compatibility with earlier versions.

+ Before v8.1.0, this configuration item controls whether to enable telemetry collection in TiDB Dashboard.
+ Default value: `false`
