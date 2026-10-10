# Create Kafka changefeed and verify replicated change logs

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/replicate-data-to-kafka.md`
- Source Title: `Integrate Data with Apache Kafka and Apache Flink`
- Source Heading Path: `Integrate Data with Apache Kafka and Apache Flink > Step 2. Create a Kafka changefeed | Integrate Data with Apache Kafka and Apache Flink > Step 3. Write data to generate change logs`
- Source Line Ranges: `42-111`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`, `tiup`, `tidb`
- Topic Tags: `changefeed`, `kafka-sink`, `sink-uri`, `dispatchers`, `canal-json`, `replication`, `verification`, `workload-generation`, `kafka-consumer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0060_520aad86df`
- Source ID: `tidb-docs-8.1:replicate-data-to-kafka.md#step-2-create-a-kafka-changefeed`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `81e06512b971c957c1b8aed9949a1bf2ed9ffd60eb3d7f92737c879e64447c36`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/replicate-data-to-kafka#step-2-create-a-kafka-changefeed
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/replicate-data-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact TiCDC Kafka changefeed configuration, creation commands, status checks, workload generation, or Kafka consumer verification for incremental replication from TiDB.
- Retrieval Keywords: Step 2. Create a Kafka changefeed, changefeed.conf, [sink], dispatchers, matcher = ['*.*'], topic = "tidb_{schema}_{table}", partition="index-value", Customize the rules for Topic and Partition dispatchers of Kafka Sink, tiup cdc:v<CLUSTER_VERSION> cli changefeed create, --sink-uri, kafka://127.0.0.1:9092/kafka-topic-name?protocol=canal-json, --changefeed-id="kafka-changefeed", Create changefeed successfully!, ID: kafka-changefeed, network connectivity, multiple brokers, partition-num=3, replication-factor=1, max-message-bytes=1048576, tiup cdc:v<CLUSTER_VERSION> cli changefeed list, Manage TiCDC Changefeeds, Step 3. Write data to generate change logs, tiup bench tpcc, tpcc, go-tpc, kafka-console-consumer.sh, --bootstrap-server 127.0.0.1:9092, --from-beginning, canal-json
- Follow-up Guidance: After incremental data is replicated to Kafka, the document says you can use Flink to consume Kafka data or develop a Kafka consumer client for specific service scenarios.
- Classification Note: This is classified as a data_pipeline chunk because it covers TiCDC changefeed setup, Kafka sink parameters, change log generation, and verification of replicated data flow.

## Official Source Content

## Step 2. Create a Kafka changefeed

1. Create a changefeed configuration file.

    As required by Flink, incremental data of each table must be sent to an independent topic, and a partition must be dispatched for each event based on the primary key value. Therefore, you need to create a changefeed configuration file `changefeed.conf` with the following contents:

    ```
    [sink]
    dispatchers = [
    {matcher = ['*.*'], topic = "tidb_{schema}_{table}", partition="index-value"},
    ]
    ```

    For detailed description of `dispatchers` in the configuration file, see [Customize the rules for Topic and Partition dispatchers of Kafka Sink](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink).

2. Create a changefeed to replicate incremental data to Kafka:

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed create --server="http://127.0.0.1:8300" --sink-uri="kafka://127.0.0.1:9092/kafka-topic-name?protocol=canal-json" --changefeed-id="kafka-changefeed" --config="changefeed.conf"
    ```

    - If the changefeed is successfully created, changefeed information, such as changefeed ID, is displayed, as shown below:

        ```shell
        Create changefeed successfully!
        ID: kafka-changefeed
        Info: {... changfeed info json struct ...}
        ```

    - If no result is returned after you run the command, check the network connectivity between the server where you run the command and the Kafka machine specified in the sink URI.

    In a production environment, a Kafka cluster has multiple broker nodes. Therefore, you can add the addresses of multiple brokers to the sink UIR. This ensures stable access to the Kafka cluster. When the Kafka cluster is down, the changefeed still works. Suppose that a Kafka cluster has three broker nodes, with IP addresses being 127.0.0.1:9092, 127.0.0.2:9092, and 127.0.0.3:9092, respectively. You can create a changefeed with the following sink URI.

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed create --server="http://127.0.0.1:8300" --sink-uri="kafka://127.0.0.1:9092,127.0.0.2:9092,127.0.0.3:9092/kafka-topic-name?protocol=canal-json&partition-num=3&replication-factor=1&max-message-bytes=1048576" --config="changefeed.conf"
    ```

3. After creating the changefeed, run the following command to check the changefeed status:

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed list --server="http://127.0.0.1:8300"
    ```

    You can refer to [Manage TiCDC Changefeeds](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed) to manage the changefeed.
## Step 3. Write data to generate change logs

After the preceding steps are done, TiCDC sends change logs of incremental data in the TiDB cluster to Kafka. This section describes how to write data into TiDB to generate change logs.

1. Simulate service workload.

    To generate change logs in a lab environment, you can use go-tpc to write data to the TiDB cluster. Specifically, run the following command to use TiUP bench to create a `tpcc` database and write data to this new database.

    ```shell
    tiup bench tpcc -H 127.0.0.1 -P 4000 -D tpcc --warehouses 4 prepare
    tiup bench tpcc -H 127.0.0.1 -P 4000 -D tpcc --warehouses 4 run --time 300s
    ```

    For more details about go-tpc, refer to [How to Run TPC-C Test on TiDB](https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-tpcc).

2. Consume data in the Kafka topic.

    When a changefeed works normally, it writes data to the Kafka topic. Run `kafka-console-consumer.sh`. You can see that data is successfully written to the Kafka topic.

    ```shell
    ./bin/kafka-console-consumer.sh --bootstrap-server 127.0.0.1:9092 --from-beginning --topic `${topic-name}`
    ```

At this time, incremental data of the TiDB database is successfully replicated to Kafka. Next, you can use Flink to consume Kafka data. Alternatively, you can develop a Kafka consumer client yourself for specific service scenarios.
