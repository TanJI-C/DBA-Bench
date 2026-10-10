# TiFlash alert rules for schema and raft latency

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-alert-rules.md`
- Source Title: `TiFlash Alert Rules`
- Source Heading Path: `TiFlash Alert Rules | TiFlash Alert Rules > `TiFlash_schema_error` | TiFlash Alert Rules > `TiFlash_schema_apply_duration` | TiFlash Alert Rules > `TiFlash_raft_read_index_duration` | TiFlash Alert Rules > `TiFlash_raft_wait_index_duration``
- Source Line Ranges: `5-68`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tikv`
- Topic Tags: `alert-rules`, `schema-apply`, `raft-read-index`, `wait-index`, `latency`, `monitoring`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0119_ccf202270a`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-alert-rules.md#tiflash-alert-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `403ef8fb561cda8dfdfcbfe9fa437ea5695201c81ce77525449ae0651c5680f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-alert-rules#tiflash-alert-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-alert-rules.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiFlash alert rules and meanings for `TiFlash_schema_error`, `TiFlash_schema_apply_duration`, `TiFlash_raft_read_index_duration`, or `TiFlash_raft_wait_index_duration` in a self-managed cluster.
- Retrieval Keywords: TiFlash Alert Rules, TiFlash_schema_error, increase(tiflash_schema_apply_count{type="failed"}[15m]) > 0, tiflash_schema_apply_count, TiFlash_schema_apply_duration, histogram_quantile(0.99, sum(rate(tiflash_schema_apply_duration_seconds_bucket[1m])) BY (le, instance)) > 20, tiflash_schema_apply_duration_seconds_bucket, TiFlash_raft_read_index_duration, histogram_quantile(0.99, sum(rate(tiflash_raft_read_index_duration_seconds_bucket[1m])) BY (le, instance)) > 3, tiflash_raft_read_index_duration_seconds_bucket, read index, TiKV leader, TiKV region retries, busy store, network problems, TiFlash_raft_wait_index_duration, histogram_quantile(0.99, sum(rate(tiflash_raft_wait_index_duration_seconds_bucket[1m])) BY (le, instance)) > 2, tiflash_raft_wait_index_duration_seconds_bucket, Region Raft Index, communication error between TiKV and the proxy, check the TiKV cluster status, Get support
- Follow-up Guidance: The content says frequent retries might be caused by frequent splitting or migration of the TiKV cluster, and you can check the TiKV cluster status to identify the retry reason; for the other alerts, it says to get support from PingCAP or the community.
- Classification Note: This chunk is classified as observability for the TiFlash component because it defines monitoring alert rules, Prometheus expressions, trigger conditions, and brief troubleshooting notes for TiFlash and related TiKV latency symptoms.

## Official Source Content

# TiFlash Alert Rules

This document introduces the alert rules of the TiFlash cluster.
## `TiFlash_schema_error`

- Alert rule:

    `increase(tiflash_schema_apply_count{type="failed"}[15m]) > 0`

- Description:

    When the schema apply error occurs, an alert is triggered.

- Solution:

    The error might be caused by some wrong logic. [Get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
## `TiFlash_schema_apply_duration`

- Alert rule:

    `histogram_quantile(0.99, sum(rate(tiflash_schema_apply_duration_seconds_bucket[1m])) BY (le, instance)) > 20`

- Description:

    When the probability that the apply duration exceeds 20 seconds is over 99%, an alert is triggered.

- Solution:

    It might be caused by the internal problems of the TiFlash storage engine. [Get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
## `TiFlash_raft_read_index_duration`

- Alert rule:

    `histogram_quantile(0.99, sum(rate(tiflash_raft_read_index_duration_seconds_bucket[1m])) BY (le, instance)) > 3`

- Description:

    When the probability that the read index duration exceeds 3 seconds is over 99%, an alert is triggered.

    > **Note:**
    >
    > `read index` is the kvproto request sent to the TiKV leader. TiKV region retries, busy store, or network problems might lead to long request time of `read index`.

- Solution:

    The frequent retries might be caused by frequent splitting or migration of the TiKV cluster. You can check the TiKV cluster status to identify the retry reason.
## `TiFlash_raft_wait_index_duration`

- Alert rule:

    `histogram_quantile(0.99, sum(rate(tiflash_raft_wait_index_duration_seconds_bucket[1m])) BY (le, instance)) > 2`

- Description:

    When the probability that the waiting time for Region Raft Index in TiFlash exceeds 2 seconds is over 99%, an alert is triggered.

- Solution:

    It might be caused by a communication error between TiKV and the proxy. [Get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
