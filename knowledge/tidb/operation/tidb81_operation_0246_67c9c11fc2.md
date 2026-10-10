# TiCDC start and stop flow

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-architecture.md`
- Source Title: `Architecture and Principles of TiCDC`
- Source Heading Path: `Architecture and Principles of TiCDC > Major processes | Architecture and Principles of TiCDC > Major processes > Start TiCDC | Architecture and Principles of TiCDC > Major processes > Stop TiCDC`
- Source Line Ranges: `149-182`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: none
- Topic Tags: `start`, `stop`, `owner`, `capture`, `processor`, `replication tasks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0246_67c9c11fc2`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-architecture.md#major-processes`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `272888e3e07a68f5a942e8bb861810e290acc559da2432a145706107fb5c5380`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-architecture#major-processes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when describing the internal TiCDC start and stop flow for owner and non-owner nodes, including Capture, Processor, task scheduling, and replication task transfer.
- Retrieval Keywords: Start TiCDC, Stop TiCDC, Owner, Capture process, Processor, Task scheduling command, tablePipeline, changefeed information, latest CheckpointTS, replication tasks are transferred to other nodes
- Follow-up Guidance: The content notes that these processes occur only within TiCDC and are transparent to users, so users do not need to care about which TiCDC node they are starting.
- Classification Note: This is classified as operation because it describes the startup and shutdown process steps for TiCDC nodes and how replication tasks are managed during those flows.

## Official Source Content

## Major processes

This section describes the major processes of TiCDC to help you better understand its working principles.

Note that the following processes occur only within TiCDC and are transparent to users. Therefore, you do not need to care about which TiCDC node you are starting.
### Start TiCDC

- For a TiCDC node that is not an owner, it works as follows:

    1. Starts the Capture process.
    2. Starts the Processor.
    3. Receives the Task scheduling command executed by the Owner.
    4. Starts or stops tablePipeline according to the scheduling command.

- For an owner TiCDC node, it works as follows:

    1. Starts the Capture process.
    2. The node is elected as the Owner and the corresponding thread is started.
    3. Reads the changefeed information.
    4. Starts the changefeed management process.
    5. Reads the schema information in TiKV according to the changefeed configuration and the latest CheckpointTS to determine the tables to be replicated.
    6. Reads the list of tables currently replicated by each Processor and distributes the tables to be added.
    7. Updates the replication progress.
### Stop TiCDC

Usually, you stop a TiCDC node when you need to upgrade it or perform some planned maintenance operations. The process of stopping a TiCDC node is as follows:

1. The node receives the command to stop itself.
2. The node sets its service status to unavailable.
3. The node stops receiving new replication tasks.
4. The node notifies the Owner node to transfer its data replication tasks to other nodes.
5. The node stops after the replication tasks are transferred to other nodes.
