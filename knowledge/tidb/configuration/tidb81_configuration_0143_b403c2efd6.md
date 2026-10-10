# Configure Flink to consume Kafka data

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/replicate-data-to-kafka.md`
- Source Title: `Integrate Data with Apache Kafka and Apache Flink`
- Source Heading Path: `Integrate Data with Apache Kafka and Apache Flink > (Optional) Step 4. Configure Flink to consume Kafka data`
- Source Line Ranges: `112-167`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `ticdc`
- Topic Tags: `flink`, `kafka-connector`, `sql-client`, `table-creation`, `canal-json`, `consumer`, `query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0143_b403c2efd6`
- Source ID: `tidb-docs-8.1:replicate-data-to-kafka.md#optional-step-4-configure-flink-to-consume-kafka-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `55c7c99e17fdb93878ebd59389310839da06da0a7906fed3df7266b79dd2e86c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/replicate-data-to-kafka#optional-step-4-configure-flink-to-consume-kafka-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/replicate-data-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the optional Flink configuration to consume TiCDC data from Kafka, including connector jars, Flink SQL client commands, table definition, and query example.
- Retrieval Keywords: (Optional) Step 4. Configure Flink to consume Kafka data, Flink Kafka connector, flink-connector-kafka-1.15.0.jar, flink-sql-connector-kafka-1.15.0.jar, kafka-clients-3.2.0.jar, lib directory, restart it to load the new plugin, ./bin/sql-client.sh, CREATE TABLE tpcc_orders, connector = kafka, topic = tidb_tpcc_orders, properties.bootstrap.servers = 127.0.0.1:9092, properties.group.id = testGroup, format = canal-json, scan.startup.mode = earliest-offset, properties.auto.offset.reset = earliest, SELECT * FROM tpcc_orders
- Follow-up Guidance: The source says to replace topic and properties.bootstrap.servers with the actual values in the environment, and then query SELECT * FROM tpcc_orders to see new data.
- Classification Note: This is classified as a configuration chunk because it provides concrete Flink connector installation details and SQL configuration for consuming Kafka data.

## Official Source Content

## (Optional) Step 4. Configure Flink to consume Kafka data

1. Install a Flink Kafka connector.

    In the Flink ecosystem, a Flink Kafka connector is used to consume Kafka data and output data to Flink. However, Flink Kafka connectors are not automatically installed. To use it, add a Flink Kafka connector and its dependencies to the Flink installation directory after installing Flink. Specifically, download the following jar files to the `lib` directory of the Flink installation directory. If you have already run the Flink cluster, restart it to load the new plugin.

    - [flink-connector-kafka-1.15.0.jar](https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-kafka/1.15.0/flink-connector-kafka-1.15.0.jar)
    - [flink-sql-connector-kafka-1.15.0.jar](https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/1.15.0/flink-sql-connector-kafka-1.15.0.jar)
    - [kafka-clients-3.2.0.jar](https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/3.2.0/kafka-clients-3.2.0.jar)

2. Create a table.

    In the directory where Flink is installed, run the following command to start the Flink SQL client:

    ```shell
    [root@flink flink-1.15.0]# ./bin/sql-client.sh
    ```

    Then, run the following command to create a table named `tpcc_orders`.

    ```sql
    CREATE TABLE tpcc_orders (
        o_id INTEGER,
        o_d_id INTEGER,
        o_w_id INTEGER,
        o_c_id INTEGER,
        o_entry_d STRING,
        o_carrier_id INTEGER,
        o_ol_cnt INTEGER,
        o_all_local INTEGER
    ) WITH (
    'connector' = 'kafka',
    'topic' = 'tidb_tpcc_orders',
    'properties.bootstrap.servers' = '127.0.0.1:9092',
    'properties.group.id' = 'testGroup',
    'format' = 'canal-json',
    'scan.startup.mode' = 'earliest-offset',
    'properties.auto.offset.reset' = 'earliest'
    )
    ```

    Replace `topic` and `properties.bootstrap.servers` with the actual values in the environment.

3. Query data of the table.

    Run the following command to query data of the `tpcc_orders` table:

    ```sql
    SELECT * FROM tpcc_orders;
    ```

    After this command is executed, you can see that there is new data in the table, as shown in the following figure.

    ![SQL query result](/media/integrate/sql-query-result.png)

Data integration with Kafka is done.
