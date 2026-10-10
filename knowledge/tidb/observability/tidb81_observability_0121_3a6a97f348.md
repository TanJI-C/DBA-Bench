# TiProxy health and metrics endpoints

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiproxy/tiproxy-api.md`
- Source Title: `TiProxy API`
- Source Heading Path: `TiProxy API > Get TiProxy health status | TiProxy API > Get TiProxy health status > Request URI | TiProxy API > Get TiProxy health status > Example | TiProxy API > Get TiProxy monitoring data | TiProxy API > Get TiProxy monitoring data > Request URI | TiProxy API > Get TiProxy monitoring data > Example`
- Source Line Ranges: `98-128`
- Source Scope: `self_managed`
- Primary Component: `tiproxy`
- Related Components: none
- Topic Tags: `api`, `health`, `metrics`, `monitoring`, `checksum`, `debugging`, `curl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0121_3a6a97f348`
- Source ID: `tidb-docs-8.1:tiproxy/tiproxy-api.md#get-tiproxy-health-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8d937f021296e1bc2e327c11f97c028bb7168a420c87b43e36c573a09f5e67df`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiproxy/tiproxy-api#get-tiproxy-health-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiproxy/tiproxy-api.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiProxy API endpoints for checking TiProxy health status, reading the configuration checksum, or accessing monitoring data.
- Retrieval Keywords: GET /api/debug/health, GET /metrics/, TiProxy health status, config_checksum, checksum of the configuration, TiProxy monitoring data, curl http://127.0.0.1:3080/api/debug/health, curl http://127.0.0.1:3080/metrics/
- Follow-up Guidance: The source states that when TiProxy is shutting down or offline, the health endpoint returns an error.
- Classification Note: This is observability content because it describes endpoints for health inspection and monitoring output, including the health response field config_checksum and the metrics path.

## Official Source Content

## Get TiProxy health status

This endpoint is used to get the health status of TiProxy and the checksum of the configuration. When TiProxy is running normally, this endpoint returns the checksum of the configuration. When TiProxy is shutting down or offline, it returns an error.
### Request URI

`GET /api/debug/health`
### Example

```bash
curl http://127.0.0.1:3080/api/debug/health
```

The output is as follows:

```bash
{"config_checksum":3006078629}
```
## Get TiProxy monitoring data
### Request URI

`GET /metrics/`
### Example

```bash
curl http://127.0.0.1:3080/metrics/
```
