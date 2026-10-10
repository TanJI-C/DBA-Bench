# Binlog write failures and duplicate writes to Pump

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs > TiDB fails to write to binlog and gets stuck, and `listener stopped, waiting for manual stop` appears in the log | TiDB Binlog FAQs > TiDB writes duplicate binlogs to Pump`
- Source Line Ranges: `252-265`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `binlog-write`, `pump`, `timeout`, `listener-stopped`, `duplicate-binlog`, `retry`, `deduplication`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0082_2c6a511945`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#tidb-fails-to-write-to-binlog-and-gets-stuck-and-listener-stopped-waiting-for-manual-stop-appears-in-the-log`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f3234c22599db32e84ebfccdb73b91acb55658c6fe22ab830d5978ce4827f530`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#tidb-fails-to-write-to-binlog-and-gets-stuck-and-listener-stopped-waiting-for-manual-stop-appears-in-the-log
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiDB Binlog write failures, `listener stopped, waiting for manual stop` log messages, or duplicate binlog writes to Pump.
- Retrieval Keywords: listener stopped, waiting for manual stop, binlog write failure, TiDB gets stuck, TiDB v3.0.12 and earlier versions, v3.0.13, duplicate binlogs, Pump timeout, default 15s, retry writing binlog, next available Pump node, same TSO, Drainer de-duplicates
- Follow-up Guidance: The source says to determine the specific cause of the binlog write failure, and if binlog is slowly written into the downstream, consider scaling out Pump or increasing the timeout time for writing binlog.
- Classification Note: This is classified as diagnosis because the content explains symptoms, causes, and behavior related to binlog write failures and duplicate writes to Pump.

## Official Source Content

## TiDB fails to write to binlog and gets stuck, and `listener stopped, waiting for manual stop` appears in the log

In TiDB v3.0.12 and earlier versions, the binlog write failure causes TiDB to report the fatal error. TiDB does not automatically exit but only stops the service, which seems like getting stuck. You can see the `listener stopped, waiting for manual stop` error in the log.

You need to determine the specific causes of the binlog write failure. If the failure occurs because binlog is slowly written into the downstream, you can consider scaling out Pump or increasing the timeout time for writing binlog.

Since v3.0.13, the error-reporting logic is optimized. The binlog write failure causes transaction execution to fail and TiDB Binlog will return an error but will not get TiDB stuck.
## TiDB writes duplicate binlogs to Pump

This issue does not affect the downstream and replication logic.

When the binlog write fails or becomes timeout, TiDB retries writing binlog to the next available Pump node until the write succeeds. Therefore, if the binlog write to a Pump node is slow and causes TiDB timeout (default 15s), then TiDB determines that the write fails and tries to write to the next Pump node. If binlog is actually successfully written to the timeout-causing Pump node, the same binlog is written to multiple Pump nodes. When Drainer processes the binlog, it automatically de-duplicates binlogs with the same TSO, so this duplicate write does not affect the downstream and replication logic.
