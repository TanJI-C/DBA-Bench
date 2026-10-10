# Log backup architecture and process

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-log-architecture.md`
- Source Title: `TiDB Log Backup and PITR Architecture`
- Source Heading Path: `TiDB Log Backup and PITR Architecture | TiDB Log Backup and PITR Architecture > Architecture | TiDB Log Backup and PITR Architecture > Process of log backup`
- Source Line Ranges: `5-55`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `log-backup`, `pitr`, `architecture`, `coordinator`, `checkpoint`, `metadata`, `gc`, `backup-progress`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0010_b7c4e93ad8`
- Source ID: `tidb-docs-8.1:br/br-log-architecture.md#tidb-log-backup-and-pitr-architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9141639eb61258095c225c14706c449faf9fe01c6ec19a96f9131d60a546a73`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-log-architecture#tidb-log-backup-and-pitr-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-log-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for the architecture, components, checkpoint concepts, or end-to-end process of TiDB log backup and PITR with BR.
- Retrieval Keywords: TiDB Log Backup and PITR Architecture, Process of log backup, br log start, br log status, local metadata, local checkpoint ts, global checkpoint ts, TiDB Coordinator, TiKV log backup observer, Register log backup task, Fetch log backup task, Read kv change data, Upload log data & metadata, Configure GC, Watch backup progress, Report global checkpoint ts
- Follow-up Guidance: It also states that PD persists the status of the log backup task and that you can view it using `br log status`.
- Classification Note: The classification is architecture because the content defines the main components, key concepts, and workflow of the log backup process across BR, TiDB, TiKV, and PD.

## Official Source Content

# TiDB Log Backup and PITR Architecture

This document introduces the architecture and process of TiDB log backup and point-in-time recovery (PITR) using a Backup & Restore (BR) tool as an example.
## Architecture

The log backup and PITR architecture is as follows:

![BR log backup and PITR architecture](/media/br/br-log-arch.png)
## Process of log backup

The process of a cluster log backup is as follows:

![BR log backup process design](/media/br/br-log-backup-ts.png)

System components and key concepts involved in the log backup process:

* **local metadata**: indicates the metadata backed up by a single TiKV node, including local checkpoint ts, global checkpoint ts, and backup file information.
* **local checkpoint ts** (in local metadata): indicates that all logs generated before local checkpoint ts in this TiKV node have been backed up to the target storage.
* **global checkpoint ts**: indicates that all logs generated before global checkpoint ts in all TiKV nodes have been backed up to the target storage. TiDB Coordinator calculates this timestamp by collecting local checkpoint ts of all TiKV node and then reports it to PD.
* **TiDB Coordinator**: a TiDB node is elected as the coordinator, which is responsible for collecting and calculating the progress of the entire log backup task (global checkpoint ts). This component is stateless in design, and after its failure, a new Coordinator is elected from the surviving TiDB nodes.
* **TiKV log backup observer**: runs on each TiKV node in the TiDB cluster, which is responsible for backing up log data. If a TiKV node fails, backing up the data range on it will be taken by other TiKV nodes after region re-election, and these nodes will back up data of the failure range starting from global checkpoint ts.

The complete backup process is as follows:

1. BR receives the `br log start` command.

   * BR parses the checkpoint ts (the start time of log backup) and storage path of the backup task.
   * **Register log backup task**: BR registers a log backup task in PD.

2. TiKV monitors the creation and update of the log backup task.

   * **Fetch log backup task**: The log backup observer of each TiKV node fetches the log backup task from PD and then backs up the log data in the specified range.

3. The log backup observer backs up the KV change logs continuously.

   * **Read kv change data**: reads KV change data and then saves the change log to [backup files in custom format](#log-backup-files).
   * **Fetch global checkpoint ts**: fetches the global checkpoint ts from PD.
   * **Generate local metadata**: generates the local metadata of the backup task, including local checkpoint ts, global checkpoint ts, and backup file information.
   * **Upload log data & metadata**: uploads the backup files and local metadata to the target storage periodically.
   * **Configure GC**: requests PD to prevent data that have not been backed up (greater than local checkpoint ts) from being recycled by the [TiDB GC mechanism](https://docs.pingcap.com/tidb/stable/garbage-collection-overview).

4. The TiDB Coordinator monitors the progress of the log backup task.

   * **Watch backup progress**: gets the backup progress of each Region (Region checkpoint ts) by polling all TiKV nodes.
   * **Report global checkpoint ts**: calculates the progress of the entire log backup task (global checkpoint ts) based on the Region checkpoint ts and then reports the global checkpoint ts to PD.

5. PD persists the status of the log backup task, and you can view it using `br log status`.
