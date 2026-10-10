# Driver usage for reading Kafka binlog data

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/binlog-consumer-client.md`
- Source Title: `Binlog Consumer Client User Guide`
- Source Heading Path: `Binlog Consumer Client User Guide > Customized development > Driver`
- Source Line Ranges: `122-147`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `driver`, `kafka`, `commit-ts`, `offset`, `cluster-id`, `topic`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0266_bf782e9e41`
- Source ID: `tidb-docs-8.1:tidb-binlog/binlog-consumer-client.md#driver`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9bfaee3f1725c3c8a8560ecb2a3a28d0c422d494133ae3162efcab3dbf2cb33`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-consumer-client#driver
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/binlog-consumer-client.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Driver options and examples for reading binlog data from Kafka and locating records by `commit ts`.
- Retrieval Keywords: Driver, TiDB-Tools, read the binlog data in Kafka, locate the binlog stored in Kafka based on `commit ts`, KafkaAddr, CommitTS, Offset, ClusterID, Topic, <ClusterID>_obinlog, convert a binlog to SQL, print data, Golang version
- Follow-up Guidance: The content notes that Driver provides examples for replicating data to MySQL and printing data, and that only the Golang version of Driver and example code are currently available.
- Classification Note: This is classified as operation because it describes how Driver is used to read Kafka binlog data and what runtime parameters and examples are involved.

## Official Source Content

### Driver

The [TiDB-Tools](https://github.com/pingcap/tidb-tools/) project provides [Driver](https://github.com/pingcap/tidb/tree/release-8.1/pkg/tidb-binlog/driver), which is used to read the binlog data in Kafka. It has the following features:

* Read the Kafka data.
* Locate the binlog stored in Kafka based on `commit ts`.

You need to configure the following information when using Driver:

* `KafkaAddr`: the address of the Kafka cluster
* `CommitTS`: from which `commit ts` to start reading the binlog
* `Offset`: from which Kafka `offset` to start reading data. If `CommitTS` is set, you needn't configure this parameter.
* `ClusterID`: the cluster ID of the TiDB cluster
* `Topic`: the topic name of Kafka. If Topic is empty, use the default name in Drainer `<ClusterID>_obinlog`.

You can use Driver by quoting the Driver code in package and refer to the example code provided by Driver to learn how to use Driver and parse the binlog data.

Currently, two examples are provided:

* Using Driver to replicate data to MySQL. This example shows how to convert a binlog to SQL
* Using Driver to print data

> **Note:**
>
> - The example code only shows how to use Driver. If you want to use Driver in the production environment, you need to optimize the code.
> - Currently, only the Golang version of Driver and example code are available. If you want to use other languages, you need to generate the code file in the corresponding language based on the binlog proto file and develop an application to read the binlog data in Kafka, parse the data, and output the data to the downstream. You are also welcome to optimize the example code and submit the example code of other languages to [TiDB-Tools](https://github.com/pingcap/tidb-tools).
