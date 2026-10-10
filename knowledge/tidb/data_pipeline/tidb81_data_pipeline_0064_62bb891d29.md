# Consume TiCDC data in ksqlDB and SQL Server via Confluent

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/integrate-confluent-using-ticdc.md`
- Source Title: `Integrate Data with Confluent Cloud and Snowflake`
- Source Heading Path: `Integrate Data with Confluent Cloud and Snowflake > Integrate data with ksqlDB | Integrate Data with Confluent Cloud and Snowflake > Integrate data with SQL Server`
- Source Line Ranges: `317-391`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `confluent`, `ksqldb`, `sql-server`, `sink-connector`, `avro`, `upsert`, `replication`, `stream-processing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0064_62bb891d29`
- Source ID: `tidb-docs-8.1:ticdc/integrate-confluent-using-ticdc.md#integrate-data-with-ksqldb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d7fc37f1ef46ea7745f45d63a4b1fa6baa09b1d58f280af494a7c324c437fd3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc#integrate-data-with-ksqldb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/integrate-confluent-using-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented Confluent Cloud steps and exact SQL or connector fields to consume TiCDC data in ksqlDB or replicate it to SQL Server.
- Retrieval Keywords: ksqlDB, Confluent Cloud, CREATE STREAM orders, tidb_tpcc_orders, value_format='AVRO', SELECT * FROM ORDERS EMIT CHANGES, Microsoft SQL Server Sink, Data integration, Connectors, Input Kafka record value format, AVRO, Insert mode, UPSERT, Auto create table, Auto add columns, PK mode, record_key, Input Kafka record key format, Delete on null, sqlcmd, create database tpcc
- Follow-up Guidance: The chunk provides both the ksqlDB stream definition for the `tidb_tpcc_orders` topic and the SQL Server Sink connector configuration values required on the Confluent Cloud configuration page.
- Classification Note: This is classified as a data pipeline chunk because it covers downstream stream-processing access in ksqlDB and sink-based replication to SQL Server through Confluent.

## Official Source Content

## Integrate data with ksqlDB

ksqlDB is a database purpose-built for stream processing applications. You can create ksqlDB clusters on Confluent Cloud and access incremental data replicated by TiCDC.

1. Select **ksqlDB** in the Confluent Cloud Console and create a ksqlDB cluster as instructed.

    Wait until the ksqlDB cluster status is **Running**. This process takes several minutes.

2. In the ksqlDB Editor, run the following command to create a stream to access the `tidb_tpcc_orders` topic:

    ```sql
    CREATE STREAM orders (o_id INTEGER, o_d_id INTEGER, o_w_id INTEGER, o_c_id INTEGER, o_entry_d STRING, o_carrier_id INTEGER, o_ol_cnt INTEGER, o_all_local INTEGER) WITH (kafka_topic='tidb_tpcc_orders', partitions=3, value_format='AVRO');
    ```

3. Run the following command to check the orders STREAM data:

    ```sql
    SELECT * FROM ORDERS EMIT CHANGES;
    ```

    ![Select from orders](/media/integrate/select-from-orders.png)

    You can see that the incremental data has been replicated to ksqlDB, as shown in the preceding figure. Data integration with ksqlDB is done.
## Integrate data with SQL Server

Microsoft SQL Server is a relational database management system (RDBMS) developed by Microsoft. With Confluent, you can replicate TiDB incremental data to SQL Server by creating SQL Server Sink Connectors.

1. Connect to SQL Server and create a database named `tpcc`.

    ```shell
    [ec2-user@ip-172-1-1-1 bin]$ sqlcmd -S 10.61.43.14,1433 -U admin
    Password:
    1> create database tpcc
    2> go
    1> select name from master.dbo.sysdatabases
    2> go
    name
    ----------------------------------------------------------------------
    master
    tempdb
    model
    msdb
    rdsadmin
    tpcc
    (6 rows affected)
    ```

2. In the Confluent Cloud Console, choose **Data integration** > **Connectors** > **Microsoft SQL Server Sink**. The page shown below is displayed.

    ![Topic selection](/media/integrate/topic-selection.png)

3. Select the topic you want to replicate to SQL Server. Then go to the next page.

    ![Authentication](/media/integrate/authentication.png)

4. Fill in the connection and authentication information. Then go to the next page.

5. On the **Configuration** page, configure the following fields and click **Continue**.

    | Field | Value |
    | :- | :- |
    | Input Kafka record value format | AVRO |
    | Insert mode | UPSERT |
    | Auto create table | true |
    | Auto add columns | true |
    | PK mode | record_key |
    | Input Kafka record key format | AVRO |
    | Delete on null | true |

6. After configuration, click **Continue**. Wait until the connector status becomes **Running**, which might take several minutes.

    ![Results](/media/integrate/results.png)

7. Connect SQL Server and observe the data. You can see that the incremental data has been replicated to SQL Server, as shown in the preceding figure. Data integration with SQL Server is done.
