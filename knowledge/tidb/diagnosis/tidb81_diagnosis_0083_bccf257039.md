# TiDB Binlog troubleshooting process

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/troubleshoot-tidb-binlog.md`
- Source Title: `TiDB Binlog Troubleshooting`
- Source Heading Path: `TiDB Binlog Troubleshooting`
- Source Line Ranges: `5-18`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `troubleshooting`, `monitoring`, `metrics`, `binlogctl`, `pump`, `drainer`, `logs`, `error-handling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0083_bccf257039`
- Source ID: `tidb-docs-8.1:tidb-binlog/troubleshoot-tidb-binlog.md#tidb-binlog-troubleshooting`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3560ec9924e89c90173818b11201d83906eb403fbd5c8decbe8fd1c916bd0d7f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/troubleshoot-tidb-binlog#tidb-binlog-troubleshooting
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/troubleshoot-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiDB Binlog errors and you need the documented process for checking monitoring metrics, Pump and Drainer node states, and logs.
- Retrieval Keywords: TiDB Binlog Troubleshooting, TiDB Binlog troubleshooting process, TiDB Binlog Monitoring, binlogctl tool, Pump, Drainer, monitoring metric, state of each Pump or Drainer node, ERROR, WARN, Pump log, Drainer log, TiDB Binlog Error Handling, FAQ
- Follow-up Guidance: After identifying the problem, the content points to FAQ and TiDB Binlog Error Handling for solutions, and to submitting an issue if those do not help.
- Classification Note: The official content is classified as diagnosis because it provides a step-by-step troubleshooting flow for locating TiDB Binlog problems through metrics, node state checks, and log inspection.

## Official Source Content

# TiDB Binlog Troubleshooting

This document describes how to troubleshoot TiDB Binlog to find the problem.

If you encounter errors while running TiDB Binlog, take the following steps to troubleshoot:

1. Check whether each monitoring metric is normal or not. Refer to [TiDB Binlog Monitoring](https://docs.pingcap.com/tidb/stable/tidb-binlog/monitor-tidb-binlog-cluster) for details.

2. Use the [binlogctl tool](https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-control) to check whether the state of each Pump or Drainer node is normal or not.

3. Check whether `ERROR` or `WARN` exists in the Pump log or Drainer log.

After finding out the problem by the above steps, refer to [FAQ](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq) and [TiDB Binlog Error Handling](https://docs.pingcap.com/tidb/stable/tidb-binlog/handle-tidb-binlog-errors) for the solution. If you fail to find the solution or the solution provided does not help, submit an [issue](https://github.com/pingcap/tidb-binlog/issues) for help.
