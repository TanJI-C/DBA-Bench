# Create a Snowflake sink from Confluent Cloud data

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/integrate-confluent-using-ticdc.md`
- Source Title: `Integrate Data with Confluent Cloud and Snowflake`
- Source Heading Path: `Integrate Data with Confluent Cloud and Snowflake > Integrate data with Snowflake | Integrate Data with Confluent Cloud and Snowflake > Integrate data with Snowflake > Prerequisites | Integrate Data with Confluent Cloud and Snowflake > Integrate data with Snowflake > Integration procedure`
- Source Line Ranges: `161-193`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `snowflake`, `connector`, `sink`, `prerequisites`, `authentication`, `avro`, `topic-selection`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0062_138f3dafcf`
- Source ID: `tidb-docs-8.1:ticdc/integrate-confluent-using-ticdc.md#integrate-data-with-snowflake`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4f0a09fc17bf3b7a0f207b7cbb5ca6d1d3c5caf4b0554efea23c222df6087621`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc#integrate-data-with-snowflake
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/integrate-confluent-using-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants the documented Confluent Cloud Snowflake Sink connector setup for TiDB incremental data already present in Confluent topics.
- Retrieval Keywords: Snowflake Sink, Confluent Cloud Console, Data integration > Connectors > Snowflake Sink, Snowflake, TPCC, TiCDC schema, private key, Key Pair Authentication, select the topic you want to replicate, Database name, Schema name, Input Kafka record value format AVRO, Input Kafka record key format AVRO, connector status Running, Data > Database > TPCC > TiCDC
- Follow-up Guidance: It also notes that the replicated data visible in Snowflake reflects TiDB change logs with a different table structure from TiDB, and that this issue is addressed in the next section.
- Classification Note: This is classified as an ecosystem data pipeline chunk because the official content describes configuring a Snowflake Sink connector in Confluent Cloud to deliver TiDB incremental data into Snowflake.

## Official Source Content

## Integrate data with Snowflake

Snowflake is a cloud native data warehouse. With Confluent, you can replicate TiDB incremental data to Snowflake by creating Snowflake Sink Connectors.
### Prerequisites

- You have registered and created a Snowflake cluster. See [Getting Started with Snowflake](https://docs.snowflake.com/en/user-guide-getting-started.html).
- Before connecting to the Snowflake cluster, you have generated a private key for it. See [Key Pair Authentication & Key Pair Rotation](https://docs.snowflake.com/en/user-guide/key-pair-auth.html).
### Integration procedure

1. Create a database and a schema in Snowflake.

    In the Snowflake control console, choose **Data** > **Database**. Create a database named `TPCC` and a schema named `TiCDC`.

2. In the Confluent Cloud Console, choose **Data integration** > **Connectors** > **Snowflake Sink**. The page shown below is displayed.

    ![Add snowflake sink connector](/media/integrate/add-snowflake-sink-connector.png)

3. Select the topic you want to replicate to Snowflake. Then go to the next page.

    ![Configuration](/media/integrate/configuration.png)

4. Specify the authentication information for connecting Snowflake. Fill in **Database name** and **Schema name** with the values you created in the previous step. Then go to the next page.

    ![Configuration](/media/integrate/configuration.png)

5. On the **Configuration** page, select `AVRO` for both **Input Kafka record value format** and **Input Kafka record key format**. Then click **Continue**. Wait until the connector is created and the status becomes **Running**, which might take several minutes.

    ![Data preview](/media/integrate/data-preview.png)

6. In the Snowflake console, choose **Data** > **Database** > **TPCC** > **TiCDC**. You can see that TiDB incremental data has been replicated to Snowflake. Data integration with Snowflake is done (see the preceding figure). However, the table structure in Snowflake is different from that in TiDB, and data is inserted into Snowflake incrementally. In most scenarios, you expect the data in Snowflake to be a replica of the data in TiDB, rather than storing TiDB change logs. This problem will be addressed in the next section.
