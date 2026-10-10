# TiCDC key concepts, roles, ResolvedTS, and CheckpointTS

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-architecture.md`
- Source Title: `Architecture and Principles of TiCDC`
- Source Heading Path: `Architecture and Principles of TiCDC > Key concepts of TiCDC | Architecture and Principles of TiCDC > Key concepts of TiCDC > Architecture-related concepts | Architecture and Principles of TiCDC > Key concepts of TiCDC > Timestamp-related concepts | Architecture and Principles of TiCDC > Key concepts of TiCDC > Timestamp-related concepts > ResolvedTS | Architecture and Principles of TiCDC > Key concepts of TiCDC > Timestamp-related concepts > CheckpointTS`
- Source Line Ranges: `82-139`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tikv`, `tidb`
- Topic Tags: `consistency`, `at-least-once`, `capture`, `owner`, `processor`, `changefeed`, `timestamps`, `resolvedts`, `checkpointts`, `transactions`, `dml`, `ddl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0064_f2e70663f0`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-architecture.md#key-concepts-of-ticdc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ca8ddb82a60372c450bc708118bf6d5413250302d1e99e54ac18f61235cfd5b0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-architecture#key-concepts-of-ticdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiCDC consistency guarantees, core roles, or the meanings and relationships of ResolvedTS and CheckpointTS.
- Retrieval Keywords: Key concepts of TiCDC, at least once, single table transaction consistency, eventual transaction consistency in multiple tables, Capture, Capture Owner, Processor, Changefeed, ResolvedTS, CheckpointTS, table ResolvedTS, global ResolvedTS, table CheckpointTS, processor CheckpointTS, global CheckpointTS, table ResolvedTS >= global ResolvedTS >= table CheckpointTS >= global CheckpointTS, <resolvedTS: timestamp>
- Follow-up Guidance: The chunk further explains that Puller receives pushed data and decides whether to scan incremental data, Sorter orders data by timestamp, Mounter assembles sink-consumable data, and Sink replicates changes between CheckpointTS and ResolvedTS.
- Classification Note: This is classified as architecture because the content defines TiCDC roles and the timestamp model that describes replication status and consistency behavior.

## Official Source Content

## Key concepts of TiCDC

For the downstream relational databases, TiCDC ensures the consistency of transactions in a single table and eventual transaction consistency in multiple tables. In addition, TiCDC ensures that any data change that has occurred in the upstream TiDB cluster can be replicated to the downstream at least once.
### Architecture-related concepts

- Capture: The process that runs the TiCDC node. Multiple Capture processes constitute a TiCDC cluster. Each Capture process is responsible for replicating data changes in TiKV, including receiving and actively pulling data changes, and replicating the data to the downstream.
- Capture Owner: The owner Capture among multiple Capture processes. Only one owner role exists in a TiCDC cluster at a time. The Capture Owner is responsible for scheduling data within the cluster.
- Processor: The logical thread inside Capture. Each Processor is responsible for processing the data of one or more tables in the same replication stream. A Capture node can run multiple Processors.
- Changefeed: A task that replicates data from an upstream TiDB cluster to a downstream system. A changefeed contains multiple Tasks, and each Task is processed by a Capture node.
### Timestamp-related concepts

TiCDC introduces a series of timestamps (TS) to indicate the status of data replication. These timestamps are used to ensure that data is replicated to the downstream at least once and that the consistency of data is guaranteed.
#### ResolvedTS

This timestamp exists in both TiKV and TiCDC.

- ResolvedTS in TiKV: Represents the start time of the earliest transaction in a Region leader, that is, `ResolvedTS` = max(`ResolvedTS`, min(`StartTS`)). Because a TiDB cluster contains multiple TiKV nodes, the minimum ResolvedTS of the Region leader on all TiKV nodes is called the global ResolvedTS. The TiDB cluster ensures that all transactions before the global ResolvedTS are committed. Alternatively, you can assume that there are no uncommitted transactions before this timestamp.

- ResolvedTS in TiCDC:

    - table ResolvedTS: Each table has a table-level ResolvedTS, which indicates all data changes in the table that are smaller than the Resolved TS have been received. To make it simple, this timestamp is the same as the minimum value of the ResolvedTS of all Regions corresponding to this table on the TiKV node.
    - global ResolvedTS: The minimum ResolvedTS of all Processors on all TiCDC nodes. Because each TiCDC node has one or more Processors, each Processor corresponds to multiple table pipelines.

    For TiCDC, the ResolvedTS sent by TiKV is a special event in the format of `<resolvedTS: timestamp>`. In general, the ResolvedTS satisfies the following constraints:

    ```
    table ResolvedTS >= global ResolvedTS
    ```
#### CheckpointTS

This timestamp exists only in TiCDC. It means that the data changes that occur before this timestamp have been replicated to the downstream system.

- table CheckpointTS: Because TiCDC replicates data in tables, the table checkpointTS indicates all data changes that occur before CheckpointTS have been replicated at the table level.
- processor CheckpointTS: Indicates the minimum table CheckpointTS on a Processor.
- global CheckpointTS: Indicates the minimum CheckpointTS among all Processors.

Generally, a checkpointTS satisfies the following constraint:

```
table CheckpointTS >= global CheckpointTS
```

Because TiCDC only replicates data smaller than the global ResolvedTS to the downstream, the complete constraint is as follows:

```
table ResolvedTS >= global ResolvedTS >= table CheckpointTS >= global CheckpointTS
```

After data changes and transactions are committed, the ResolvedTS on the TiKV node will continue to advance, and the Puller module on the TiCDC node keeps receiving data pushed by TiKV. The Puller module also decides whether to scan incremental data based on the data changes it has received, which ensures that all data changes are sent to the TiCDC node.

The Sorter module sorts data received by the Puller module in ascending order according to the timestamp. This process ensures data consistency at the table level. Next, the Mounter module assembles the data changes from the upstream into a format that the Sink module can consume, and sends it to the Sink module. The Sink module replicates the data changes between the CheckpointTS and the ResolvedTS to the downstream in the order of the timestamp, and advances the checkpointTS after the downstream receives the data changes.

The preceding sections only cover data changes of DML statements and do not include DDL statements. The following sections introduce the timestamp related to DDL statements.
