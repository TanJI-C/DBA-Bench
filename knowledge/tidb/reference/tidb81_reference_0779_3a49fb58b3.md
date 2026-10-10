# TiDB Binlog glossary terms

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-glossary.md`
- Source Title: `TiDB Binlog Glossary`
- Source Heading Path: `TiDB Binlog Glossary | TiDB Binlog Glossary > Binlog | TiDB Binlog Glossary > Binlog event | TiDB Binlog Glossary > Checkpoint | TiDB Binlog Glossary > Safe mode`
- Source Line Ranges: `5-26`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`
- Topic Tags: `glossary`, `binlog`, `binlog-event`, `checkpoint`, `safe-mode`, `drainer`, `replication`, `incremental-replication`, `downstream`, `commit-ts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0779_3a49fb58b3`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-glossary.md#tidb-binlog-glossary`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bb8fb8e968b8c1670215f91ec940ac770fdad0abe82467b0e36f72de4f1954c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-glossary#tidb-binlog-glossary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-glossary.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for glossary definitions of TiDB Binlog terms such as binlog, binlog event types, checkpoint commit-ts behavior, or safe mode statement rewriting in incremental replication.
- Retrieval Keywords: TiDB Binlog Glossary, Binlog, Binlog event, INSERT, UPDATE, DELETE, Checkpoint, commit-ts, Drainer, downstream, Safe mode, safe-mode, incremental replication task, REPLACE, DELETE and REPLACE, MySQL, TiDB
- Follow-up Guidance: The source states that safe mode is automatically enabled within 5 minutes after Drainer is started, and that manually modifying the `safe-mode` parameter is valid only when the downstream is MySQL or TiDB.
- Classification Note: This is reference content because it defines official TiDB Binlog terms used in logs, monitoring, configurations, and documentation.

## Official Source Content

# TiDB Binlog Glossary

This document lists the terms used in the logs, monitoring, configurations, and documentation of TiDB Binlog.
## Binlog

In TiDB Binlog, binlogs refer to the binary log data from TiDB. They also refer to the binary log data that Drainer writes to Kafka or files. The former and the latter are in different formats. In addition, binlogs in TiDB and binlogs in MySQL are also in different formats.
## Binlog event

The DML binlogs from TiDB have three types of event: `INSERT`, `UPDATE`, and `DELETE`. In the monitoring dashboard of Drainer, you can see the number of different events that correspond to the replication data.
## Checkpoint

A checkpoint indicates the position from which a replication task is paused and resumed, or is stopped and restarted. It records the commit-ts that Drainer replicates to the downstream. When restarted, Drainer reads the checkpoint and starts replicating data from the corresponding commit-ts.
## Safe mode

Safe mode refers to the mode that supports the idempotent import of DML when a primary key or unique index exists in the table schema in the incremental replication task.

In this mode, the `INSERT` statement is re-written as `REPLACE`, and the `UPDATE` statement is re-written as `DELETE` and `REPLACE`. Then the re-written statement is executed to the downstream. Safe mode is automatically enabled within 5 minutes after Drainer is started. You can manually enable the mode by modifying the `safe-mode` parameter in the configuration file, but this configuration is valid only when the downstream is MySQL or TiDB.
