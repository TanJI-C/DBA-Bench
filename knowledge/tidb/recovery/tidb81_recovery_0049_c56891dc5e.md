# Resume Reparo after interrupted restore using TSO

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs > Reparo is interrupted during the full and incremental restore process. Can I use the last TSO in the log to resume replication?`
- Source Line Ranges: `266-272`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `reparo`, `restore`, `checkpoint-tso`, `start-tso`, `stop-tso`, `safe-mode`, `resume-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0049_c56891dc5e`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#reparo-is-interrupted-during-the-full-and-incremental-restore-process-can-i-use-the-last-tso-in-the-log-to-resume-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1594abf95e5fb1519a9aa8f2cb1492fd52015173aa71db9b1f335da52265c896`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#reparo-is-interrupted-during-the-full-and-incremental-restore-process-can-i-use-the-last-tso-in-the-log-to-resume-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when resuming Reparo after an interrupted full and incremental restore by using the last TSO in the log.
- Retrieval Keywords: Reparo, checkpoint-tso, start-tso, stop-tso, safe-mode, last TSO in the log, full and incremental restore, resume replication
- Follow-up Guidance: The source says to record the last TSO as `checkpoint-tso`, restart Reparo once with `start-tso`, `stop-tso`, and `safe-mode = true`, then start it again with a later `start-tso`, `stop-tso = 0`, and `safe-mode = false` to resume replication.
- Classification Note: This is classified as recovery because the content provides the documented procedure to resume Reparo after an interrupted restore using TSO settings.

## Official Source Content

## Reparo is interrupted during the full and incremental restore process. Can I use the last TSO in the log to resume replication?

Yes. Reparo does not automatically enable the safe-mode when you start it. You need to perform the following steps manually:

1. After Reparo is interrupted, record the last TSO in the log as `checkpoint-tso`.
2. Modify the Reparo configuration file, set the configuration item `start-tso` to `checkpoint-tso + 1`, set `stop-tso` to `checkpoint-tso + 80,000,000,000` (approximately five minutes after the `checkpoint-tso`), and set `safe-mode` to `true`. Start Reparo, and Reparo replicates data to `stop-tso` and then stops automatically.
3. After Reparo stops automatically, set `start-tso` to `checkpoint tso + 80,000,000,001`, set `stop-tso` to `0`, and set `safe-mode` to `false`. Start Reparo to resume replication.
