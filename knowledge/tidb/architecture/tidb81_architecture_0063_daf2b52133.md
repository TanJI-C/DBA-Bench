# TiCDC architecture, components, changefeeds, and tasks

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-architecture.md`
- Source Title: `Architecture and Principles of TiCDC`
- Source Heading Path: `Architecture and Principles of TiCDC | Architecture and Principles of TiCDC > TiCDC architecture | Architecture and Principles of TiCDC > TiCDC components | Architecture and Principles of TiCDC > Changefeeds and tasks`
- Source Line Ranges: `5-81`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `architecture`, `capture`, `owner`, `processor`, `pipeline`, `puller`, `sorter`, `mounter`, `sink`, `changefeed`, `task`, `high-availability`, `etcd`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0063_daf2b52133`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-architecture.md#architecture-and-principles-of-ticdc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fe619d751f544d4f33ec9dc3a24b5f7c52b194e5fb9f4b05cc887769602732ad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-architecture#architecture-and-principles-of-ticdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-architecture.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs an overview of TiCDC architecture, including Capture, owner Capture, Processor, table pipelines, changefeeds, and Tasks.
- Retrieval Keywords: TiCDC architecture, TiCDC components, Capture process, owner Capture, Processor, table pipeline, Puller, Sorter, Mounter, Sink, changefeed, Task, etcd in PD, high availability, replicating DDL statements, cdc cli changefeed create, sink-uri, Kafka
- Follow-up Guidance: The chunk also includes a changefeed creation example and the flow in which the owner Capture stores changefeed information in etcd, splits it into Tasks, and Capture processes pull data from TiKV and complete replication.
- Classification Note: This is classified as architecture because the content defines the TiCDC cluster structure, component roles, scheduling with etcd in PD, and the changefeed-to-Task processing model.

## Official Source Content

# Architecture and Principles of TiCDC
## TiCDC architecture

Consisting of multiple TiCDC nodes, a TiCDC cluster uses a distributed and stateless architecture. The design of TiCDC and its components is as follows:

![TiCDC architecture](/media/ticdc/ticdc-architecture-1.jpg)
## TiCDC components

In the preceding diagram, a TiCDC cluster consists of multiple nodes running TiCDC instances. Each TiCDC instance carries a Capture process. One of the Capture processes is elected as the owner Capture, which is responsible for scheduling workload, replicating DDL statements, and performing management tasks.

Each Capture process contains one or multiple Processor threads for replicating data from tables in the upstream TiDB. Because table is the minimum unit of data replication in TiCDC, a Processor is composed of multiple table pipelines.

Each pipeline contains the following components: Puller, Sorter, Mounter, and Sink.

![TiCDC architecture](/media/ticdc/ticdc-architecture-2.jpg)

These components work in serial with each other to complete the replication process, including pulling data, sorting data, loading data, and replicating data from the upstream to the downstream. The components are described as follows:

- Puller: pulls DDL and row changes from TiKV nodes.
- Sorter: sorts the changes received from TiKV nodes in ascending order of timestamps.
- Mounter: converts the changes into a format that TiCDC sink can process based on the schema information.
- Sink: replicates the changes to the downstream system.

To realize high availability, each TiCDC cluster runs multiple TiCDC nodes. These nodes regularly report their status to the etcd cluster in PD, and elect one of the nodes as the owner of the TiCDC cluster. The owner node schedules data based on the status stored in etcd and writes the scheduling results to etcd. The Processor completes tasks according to the status in etcd. If the node running the Processor fails, the cluster schedules tables to other nodes. If the owner node fails, the Capture processes in other nodes will elect a new owner. See the following figure:

![TiCDC architecture](/media/ticdc/ticdc-architecture-3.PNG)
## Changefeeds and tasks

Changefeed and Task in TiCDC are two logical concepts. The specific description is as follows:

- Changefeed: Represents a replication task. It carries the information about the tables to be replicated and the downstream.
- Task: After TiCDC receives a replication task, it splits this task into several subtasks. Such a subtask is called Task. These Tasks are assigned to the Capture processes of the TiCDC nodes for processing.

For example:

```
cdc cli changefeed create --server="http://127.0.0.1:8300" --sink-uri="kafka://127.0.0.1:9092/cdc-test?kafka-version=2.4.0&partition-num=6&max-message-bytes=67108864&replication-factor=1"
cat changefeed.toml
......
[sink]
dispatchers = [
    {matcher = ['test1.tab1', 'test2.tab2'], topic = "{schema}_{table}"},
    {matcher = ['test3.tab3', 'test4.tab4'], topic = "{schema}_{table}"},
]
```

For a detailed description of the parameters in the preceding `cdc cli changefeed create` command, see [TiCDC Changefeed Configuration Parameters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-config).

The preceding `cdc cli changefeed create` command creates a changefeed task that replicates `test1.tab1`, `test1.tab2`, `test3.tab3`, and `test4.tab4` to the Kafka cluster. The processing flow after TiCDC receives this command is as follows:

1. TiCDC sends this task to the owner Capture process.
2. The owner Capture process saves information about this changefeed task in etcd in PD.
3. The owner Capture process splits the changefeed task into several Tasks and notifies other Capture processes of the Tasks to be completed.
4. The Capture processes start pulling data from TiKV nodes, process the data, and complete replication.

The following is the TiCDC architecture diagram with Changefeed and Task included:

![TiCDC architecture](/media/ticdc/ticdc-architecture-6.jpg)

In the preceding diagram, a changefeed is created to replicate four tables to downstream. This changefeed is split into three Tasks, which are sent to the three Capture processes respectively in the TiCDC cluster. After TiCDC processes the data, the data is replicated to the downstream system.

TiCDC supports replicating data to MySQL, TiDB, and Kafka databases. The preceding diagram only illustrates the process of data transfer at the changefeed level. The following sections describe in detail how TiCDC processes data, using Task1 that replicates table `table1` as an example.

![TiCDC architecture](/media/ticdc/ticdc-architecture-5.jpg)

1. Push data: When a data change occurs, TiKV pushes data to the Puller module.
2. Scan incremental data: The Puller module pulls data from TiKV when it finds the data changes received not continuous.
3. Sort data: The Sorter module sorts the data received from TiKV based on the timestamps and sends the sorted data to the Mounter module.
4. Mount data: After receiving the data changes, the Mounter module loads the data in a format that TiCDC sink can understand.
5. Replicate data: The Sink module replicates the data changes to the downstream.

The upstream of TiCDC is the distributed relational database TiDB that supports transactions. When TiCDC replicates data, it should ensure the consistency of data and that of transactions when replicating multiple tables, which is a great challenge. The following sections introduce the key technologies and concepts used by TiCDC to address this challenge.
