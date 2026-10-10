# DM alert information overview

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-alert-rules.md`
- Source Title: `DM Alert Information`
- Source Heading Path: `DM Alert Information`
- Source Line Ranges: `5-12`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `shared`
- Topic Tags: `alerts`, `prometheus`, `monitoring`, `overview`, `tiup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0039_75d926c267`
- Source ID: `tidb-docs-8.1:dm/dm-alert-rules.md#dm-alert-information`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b4b1a5b0e56ddeae6df8ebd427665007442ca78d2680406801460069011231b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-alert-rules#dm-alert-information
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks for an overview of DM alert information, its default deployment behavior with TiUP, or how DM alerts relate to Prometheus-based monitoring metrics.
- Retrieval Keywords: DM Alert Information, alert system, DM cluster, TiUP, Prometheus, DM alert rules, handle alerts, DM monitoring metrics, monitoring metrics
- Follow-up Guidance: The source points to handle alerts for DM alert rules and solutions, and to DM monitoring metrics for the relationship between alerts and metrics.
- Classification Note: The content is classified as observability for the DM component because it describes DM alert information and monitoring metrics based on Prometheus.

## Official Source Content

# DM Alert Information

The [alert system](https://docs.pingcap.com/tidb/stable/dm/migrate-data-using-dm#step-8-monitor-the-task-and-check-logs) is deployed by default when you deploy a DM cluster using TiUP.

For more information about DM alert rules and the solutions, refer to [handle alerts](https://docs.pingcap.com/tidb/stable/dm/dm-handle-alerts).

Both DM alert information and monitoring metrics are based on Prometheus. For more information about their relationship, refer to [DM monitoring metrics](https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster).
