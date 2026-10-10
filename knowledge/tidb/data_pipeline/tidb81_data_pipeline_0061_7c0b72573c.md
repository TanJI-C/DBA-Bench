# Replicate TiDB incremental data to Confluent Cloud with TiCDC

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/integrate-confluent-using-ticdc.md`
- Source Title: `Integrate Data with Confluent Cloud and Snowflake`
- Source Heading Path: `Integrate Data with Confluent Cloud and Snowflake | Integrate Data with Confluent Cloud and Snowflake > Replicate incremental data to Confluent Cloud | Integrate Data with Confluent Cloud and Snowflake > Replicate incremental data to Confluent Cloud > Step 1. Set up the environment | Integrate Data with Confluent Cloud and Snowflake > Replicate incremental data to Confluent Cloud > Step 2. Create an access key pair | Integrate Data with Confluent Cloud and Snowflake > Replicate incremental data to Confluent Cloud > Step 3. Create a Kafka changefeed | Integrate Data with Confluent Cloud and Snowflake > Replicate incremental data to Confluent Cloud > Step 4. Write data to generate change logs`
- Source Line Ranges: `5-160`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tiup`, `tidb`, `ecosystem`
- Topic Tags: `confluent`, `kafka`, `changefeed`, `avro`, `schema-registry`, `access-keys`, `sink-uri`, `topic-dispatch`, `benchmarking`, `change-logs`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0061_7c0b72573c`
- Source ID: `tidb-docs-8.1:ticdc/integrate-confluent-using-ticdc.md#integrate-data-with-confluent-cloud-and-snowflake`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `083caa8a5f2927b4df8ed175acb7f576060d4c803a1f87327abc7264d929d7ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc#integrate-data-with-confluent-cloud-and-snowflake
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/integrate-confluent-using-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented TiCDC procedure and exact parameters for replicating TiDB incremental data to Confluent Cloud in Avro format and verifying that Kafka topics receive change logs.
- Retrieval Keywords: TiCDC, Confluent Cloud, replicate incremental data, Avro format, Kafka changefeed, changefeed.conf, dispatchers, topic = "tidb_{schema}_{table}", partition="index-value", tiup playground --ticdc 1, cluster API key, Schema Registry API key, Schema Registry Endpoints, tiup cdc cli changefeed create, --sink-uri, protocol=avro, replication-factor=3, enable-tls=true, auto-create-topic=true, sasl-mechanism=plain, --schema-registry, confluent-changefeed, tiup cdc cli changefeed list, HTML URL Encoding Reference, go-tpc, tiup bench tpcc, Confluent Cloud Topics
- Follow-up Guidance: It also provides the command to list changefeeds, notes that no command output can indicate network connectivity issues to Confluent Cloud, and shows how to generate change logs with TiUP bench tpcc and observe target topics in the Confluent Cloud Console.
- Classification Note: This is classified as a TiCDC data pipeline chunk because the official content centers on creating a Kafka changefeed from TiDB to Confluent Cloud, including sink URI, schema registry, topic dispatch, and change-log generation.

## Official Source Content

# Integrate Data with Confluent Cloud and Snowflake

Confluent is an Apache Kafka-compatible streaming data platform that provides strong data integration capabilities. On this platform, you can access, store, and manage non-stop real-time streaming data.

Starting from TiDB v6.1.0, TiCDC supports replicating incremental data to Confluent in Avro format. This document introduces how to replicate TiDB incremental data to Confluent using [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview), and further replicate data to Snowflake, ksqlDB, and SQL Server via Confluent Cloud. The organization of this document is as follows:

1. Quickly deploy a TiDB cluster with TiCDC included.
2. Create a changefeed that replicates data from TiDB to Confluent Cloud.
3. Create Connectors that replicate data from Confluent Cloud to Snowflake, ksqlDB, and SQL Server.
4. Write data to TiDB using go-tpc, and observe data changes in Snowflake, ksqlDB, and SQL Server.

The preceding steps are performed in a lab environment. You can also deploy a cluster in a production environment by referring to these steps.
## Replicate incremental data to Confluent Cloud
### Step 1. Set up the environment

1. Deploy a TiDB cluster with TiCDC included.

    In a lab or testing environment, you can deploy a TiDB cluster with TiCDC included quickly by using TiUP Playground.

    ```shell
    tiup playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 1
    # View cluster status
    tiup status
    ```

    If TiUP is not installed yet, refer to [Install TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview#install-tiup). In a production environment, you can deploy a TiCDC as instructed in [Deploy TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc).

2. Register Confluent Cloud and create a Confluent cluster.

    Create a Basic cluster and make it accessible via Internet. For details, see [Quick Start for Confluent Cloud](https://docs.confluent.io/cloud/current/get-started/index.html).
### Step 2. Create an access key pair

1. Create a cluster API key.

    Sign in to [Confluent Cloud](https://confluent.cloud). Choose **Data integration** > **API keys** > **Create key**. On the **Select scope for API key** page that is displayed, select **Global access**.

    After creation, a key pair file is generated, as shown below.

    ```
    === Confluent Cloud API key: xxx-xxxxx ===

    API key:
    L5WWA4GK4NAT2EQV

    API secret:
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    Bootstrap server:
    xxx-xxxxx.ap-east-1.aws.confluent.cloud:9092
    ```

2. Record the Schema Registry Endpoints.

    In the Confluent Cloud Console, choose **Schema Registry** > **API endpoint**. Record the Schema Registry Endpoints. The following is an example:

    ```
    https://yyy-yyyyy.us-east-2.aws.confluent.cloud
    ```

3. Create a Schema Registry API key.

    In the Confluent Cloud Console, choose **Schema Registry** > **API credentials**. Click **Edit** and then **Create key**.

    After creation, a key pair file is generated, as shown below:

    ```
    === Confluent Cloud API key: yyy-yyyyy ===
    API key:
    7NBH2CAFM2LMGTH7
    API secret:
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    ```

    You can also perform this step by using Confluent CLI. For details, see [Connect Confluent CLI to Confluent Cloud Cluster](https://docs.confluent.io/confluent-cli/current/connect.html).
### Step 3. Create a Kafka changefeed

1. Create a changefeed configuration file.

    As required by Avro and Confluent Connector, incremental data of each table must be sent to an independent topic, and a partition must be dispatched for each event based on the primary key value. Therefore, you need to create a changefeed configuration file `changefeed.conf` with the following contents:

    ```
    [sink]
    dispatchers = [
    {matcher = ['*.*'], topic = "tidb_{schema}_{table}", partition="index-value"},
    ]
    ```

    For detailed description of `dispatchers` in the configuration file, see [Customize the rules for Topic and Partition dispatchers of Kafka Sink](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink).

2. Create a changefeed to replicate incremental data to Confluent Cloud:

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed create --server="http://127.0.0.1:8300" --sink-uri="kafka://<broker_endpoint>/ticdc-meta?protocol=avro&replication-factor=3&enable-tls=true&auto-create-topic=true&sasl-mechanism=plain&sasl-user=<broker_api_key>&sasl-password=<broker_api_secret>" --schema-registry="https://<schema_registry_api_key>:<schema_registry_api_secret>@<schema_registry_endpoint>" --changefeed-id="confluent-changefeed" --config changefeed.conf
    ```

    You need to replace the values of the following fields with those created or recorded in [Step 2. Create an access key pair](#step-2-create-an-access-key-pair):

    - `<broker_endpoint>`
    - `<broker_api_key>`
    - `<broker_api_secret>`
    - `<schema_registry_api_key>`
    - `<schema_registry_api_secret>`
    - `<schema_registry_endpoint>`

    Note that you should encode `<schema_registry_api_secret>` based on [HTML URL Encoding Reference](https://www.w3schools.com/tags/ref_urlencode.asp) before replacing its value. After you replace all the preceding fields, the configuration file is as follows:

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed create --server="http://127.0.0.1:8300" --sink-uri="kafka://xxx-xxxxx.ap-east-1.aws.confluent.cloud:9092/ticdc-meta?protocol=avro&replication-factor=3&enable-tls=true&auto-create-topic=true&sasl-mechanism=plain&sasl-user=L5WWA4GK4NAT2EQV&sasl-password=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" --schema-registry="https://7NBH2CAFM2LMGTH7:xxxxxxxxxxxxxxxxxx@yyy-yyyyy.us-east-2.aws.confluent.cloud" --changefeed-id="confluent-changefeed" --config changefeed.conf
    ```

    - Run the command to create a changefeed.

        - If the changefeed is successfully created, changefeed information, such as changefeed ID, is displayed, as shown below:

            ```shell
            Create changefeed successfully!
            ID: confluent-changefeed
            Info: {... changfeed info json struct ...}
            ```

        - If no result is returned after you run the command, check the network connectivity between the server where you run the command and Confluent Cloud. For details, see [Test connectivity to Confluent Cloud](https://docs.confluent.io/cloud/current/networking/testing.html).

3. After creating the changefeed, run the following command to check the changefeed status:

    ```shell
    tiup cdc:v<CLUSTER_VERSION> cli changefeed list --server="http://127.0.0.1:8300"
    ```

    You can refer to [Manage TiCDC Changefeeds](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed) to manage the changefeed.
### Step 4. Write data to generate change logs

After the preceding steps are done, TiCDC sends change logs of incremental data in the TiDB cluster to Confluent Cloud. This section describes how to write data into TiDB to generate change logs.

1. Simulate service workload.

    To generate change logs in a lab environment, you can use go-tpc to write data to the TiDB cluster. Specifically, run the following command to create a database `tpcc` in the TiDB cluster. Then, use TiUP bench to write data to this new database.

    ```shell
    tiup bench tpcc -H 127.0.0.1 -P 4000 -D tpcc --warehouses 4 prepare
    tiup bench tpcc -H 127.0.0.1 -P 4000 -D tpcc --warehouses 4 run --time 300s
    ```

    For more details about go-tpc, refer to [How to Run TPC-C Test on TiDB](https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-tpcc).

2. Observe data in Confluent Cloud.

    ![Confluent topics](/media/integrate/confluent-topics.png)

    In the Confluent Cloud Console, click **Topics**. You can see that the target topics have been created and are receiving data. At this time, incremental data of the TiDB database is successfully replicated to Confluent Cloud.
