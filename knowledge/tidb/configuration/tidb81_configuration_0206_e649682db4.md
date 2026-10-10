# Configure and review Apache Kafka changefeed settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-kafka.md`
- Source Title: `Sink to Apache Kafka`
- Source Heading Path: `Sink to Apache Kafka > Step 3. Set the changefeed | Sink to Apache Kafka > Step 4. Configure your changefeed specification | Sink to Apache Kafka > Step 5. Review the configurations`
- Source Line Ranges: `203-302`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `ecosystem`
- Topic Tags: `changefeed`, `kafka`, `table-filter`, `event-filter`, `column-selector`, `data-format`, `avro`, `canal-json`, `open-protocol`, `debezium`, `topic-distribution`, `partition-dispatcher`, `topic-configuration`, `rcu`, `review`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0206_e649682db4`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-kafka.md#step-3-set-the-changefeed`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e07320196e28026e991875fb77bf52cde275c7f4e0c75c27cfd13b1faa70c0e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-kafka#step-3-set-the-changefeed
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when configuring or reviewing a TiDB Cloud changefeed that sinks to Apache Kafka and you need details for table filters, event filters, column selectors, data format, topic distribution, partition distribution, topic configuration, RCUs, and final review fields.
- Retrieval Keywords: TiDB Cloud changefeed Apache Kafka, Table Filter, Filter Rules, *.*, Tables with valid keys, Tables without valid keys, !test.tbl1, Event Filter, Ignore event, Ignore SQL, Ignore insert value expression, Ignore update new value expression, Ignore update old value expression, Ignore delete value expression, Column Selector, Data Format, Avro, Canal-JSON, Open Protocol, Debezium, TiDB Extension, Schema Registry, HTTP Authentication, Topic Distribution, Distribute changelogs by table to Kafka Topics, Distribute changelogs by database to Kafka Topics, Send all changelogs to one specified Kafka Topic, Default Topic Name, Partition Distribution, single partition dispatcher for all tables, different partition dispatchers for different tables, Distribute changelogs by primary key or index value to Kafka partition, Distribute changelogs by table to Kafka partition, Distribute changelogs by timestamp to Kafka partition, Distribute changelogs by column value to Kafka partition, commitTs, Topic Configuration, Replication Factor, min.insync.replicas, Partition Number, Changefeed Specification, Replication Capacity Units, RCUs, Changefeed Name, Review the configurations
- Follow-up Guidance: The source also states that after setting the changefeed, you can specify Replication Capacity Units and Changefeed Name, then review all configurations, go back to fix any error, and click Create if there is no error.
- Classification Note: This chunk is classified as configuration because it describes the configurable fields and review items for creating a TiDB Cloud Apache Kafka changefeed, including filters, formats, topic and partition settings, and changefeed specification.

## Official Source Content

## Step 3. Set the changefeed

1. Customize **Table Filter** to filter the tables that you want to replicate. For the rule syntax, refer to [table filter rules](https://docs.pingcap.com/tidb/stable/table-filter).

    - **Filter Rules**: you can set filter rules in this column. By default, there is a rule `*.*`, which stands for replicating all tables. When you add a new rule, TiDB Cloud queries all the tables in TiDB and displays only the tables that match the rules in the box on the right. You can add up to 100 filter rules.
    - **Tables with valid keys**: this column displays the tables that have valid keys, including primary keys or unique indexes.
    - **Tables without valid keys**: this column shows tables that lack primary keys or unique keys. These tables present a challenge during replication because the absence of a unique identifier can result in inconsistent data when the downstream handles duplicate events. To ensure data consistency, it is recommended to add unique keys or primary keys to these tables before initiating the replication. Alternatively, you can add filter rules to exclude these tables. For example, you can exclude the table `test.tbl1` by using the rule `"!test.tbl1"`.

2. Customize **Event Filter** to filter the events that you want to replicate.

    - **Tables matching**: you can set which tables the event filter will be applied to in this column. The rule syntax is the same as that used for the preceding **Table Filter** area. You can add up to 10 event filter rules per changefeed.
    - **Event Filter**: you can use the following event filters to exclude specific events from the changefeed:
        - **Ignore event**: excludes specified event types.
        - **Ignore SQL**: excludes DDL events that match specified expressions. For example, `^drop` excludes statements starting with `DROP`, and `add column` excludes statements containing `ADD COLUMN`.
        - **Ignore insert value expression**: excludes `INSERT` statements that meet specific conditions. For example, `id >= 100` excludes `INSERT` statements where `id` is greater than or equal to 100.
        - **Ignore update new value expression**: excludes `UPDATE` statements where the new value matches a specified condition. For example, `gender = 'male'` excludes updates that result in `gender` being `male`.
        - **Ignore update old value expression**: excludes `UPDATE` statements where the old value matches a specified condition. For example, `age < 18` excludes updates where the old value of `age` is less than 18.
        - **Ignore delete value expression**: excludes `DELETE` statements that meet a specified condition. For example, `name = 'john'` excludes `DELETE` statements where `name` is `'john'`.

3. Customize **Column Selector** to select columns from events and send only the data changes related to those columns to the downstream.

    - **Tables matching**: specify which tables the column selector applies to. For tables that do not match any rule, all columns are sent.
    - **Column Selector**: specify which columns of the matched tables will be sent to the downstream.

    For more information about the matching rules, see [Column selectors](https://docs.pingcap.com/tidb/stable/ticdc-sink-to-kafka/#column-selectors).

4. In the **Data Format** area, select your desired format of Kafka messages.

    - Avro is a compact, fast, and binary data format with rich data structures, which is widely used in various flow systems. For more information, see [Avro data format](https://docs.pingcap.com/tidb/stable/ticdc-avro-protocol).
    - Canal-JSON is a plain JSON text format, which is easy to parse. For more information, see [Canal-JSON data format](https://docs.pingcap.com/tidb/stable/ticdc-canal-json).
    - Open Protocol is a row-level data change notification protocol that provides data sources for monitoring, caching, full-text indexing, analysis engines, and primary-secondary replication between different databases. For more information, see [Open Protocol data format](https://docs.pingcap.com/tidb/stable/ticdc-open-protocol). 
    - Debezium is a tool for capturing database changes. It converts each captured database change into a message called an "event" and sends these events to Kafka. For more information, see [Debezium data format](https://docs.pingcap.com/tidb/stable/ticdc-debezium).

5. Enable the **TiDB Extension** option if you want to add TiDB-extension fields to the Kafka message body.

    For more information about TiDB-extension fields, see [TiDB extension fields in Avro data format](https://docs.pingcap.com/tidb/stable/ticdc-avro-protocol#tidb-extension-fields) and [TiDB extension fields in Canal-JSON data format](https://docs.pingcap.com/tidb/stable/ticdc-canal-json#tidb-extension-field).

6. If you select **Avro** as your data format, you will see some Avro-specific configurations on the page. You can fill in these configurations as follows:

    - In the **Decimal** and **Unsigned BigInt** configurations, specify how TiDB Cloud handles the decimal and unsigned bigint data types in Kafka messages.
    - In the **Schema Registry** area, fill in your schema registry endpoint. If you enable **HTTP Authentication**, the fields for user name and password are displayed and automatically filled in with your TiDB cluster endpoint and password.

7. In the **Topic Distribution** area, select a distribution mode, and then fill in the topic name configurations according to the mode.

    If you select **Avro** as your data format, you can only choose the **Distribute changelogs by table to Kafka Topics** mode in the **Distribution Mode** drop-down list.

    The distribution mode controls how the changefeed creates Kafka topics, by table, by database, or creating one topic for all changelogs.

    - **Distribute changelogs by table to Kafka Topics**

        If you want the changefeed to create a dedicated Kafka topic for each table, choose this mode. Then, all Kafka messages of a table are sent to a dedicated Kafka topic. You can customize topic names for tables by setting a topic prefix, a separator between a database name and table name, and a suffix. For example, if you set the separator as `_`, the topic names are in the format of `<Prefix><DatabaseName>_<TableName><Suffix>`.

        For changelogs of non-row events, such as Create Schema Event, you can specify a topic name in the **Default Topic Name** field. The changefeed will create a topic accordingly to collect such changelogs.

    - **Distribute changelogs by database to Kafka Topics**

        If you want the changefeed to create a dedicated Kafka topic for each database, choose this mode. Then, all Kafka messages of a database are sent to a dedicated Kafka topic. You can customize topic names of databases by setting a topic prefix and a suffix.

        For changelogs of non-row events, such as Resolved Ts Event, you can specify a topic name in the **Default Topic Name** field. The changefeed will create a topic accordingly to collect such changelogs.

    - **Send all changelogs to one specified Kafka Topic**

        If you want the changefeed to create one Kafka topic for all changelogs, choose this mode. Then, all Kafka messages in the changefeed will be sent to one Kafka topic. You can define the topic name in the **Topic Name** field.
8. In the **Partition Distribution** area, you can decide which partition a Kafka message will be sent to. You can define **a single partition dispatcher for all tables**, or **different partition dispatchers for different tables**. TiDB Cloud provides four types of dispatchers:

    - **Distribute changelogs by primary key or index value to Kafka partition**

        If you want the changefeed to send Kafka messages of a table to different partitions, choose this distribution method. The primary key or index value of a row changelog will determine which partition the changelog is sent to. This distribution method provides a better partition balance and ensures row-level orderliness.

    - **Distribute changelogs by table to Kafka partition**

        If you want the changefeed to send Kafka messages of a table to one Kafka partition, choose this distribution method. The table name of a row changelog will determine which partition the changelog is sent to. This distribution method ensures table orderliness but might cause unbalanced partitions.

    - **Distribute changelogs by timestamp to Kafka partition**

        If you want the changefeed to send Kafka messages to different Kafka partitions randomly, choose this distribution method. The commitTs of a row changelog will determine which partition the changelog is sent to. This distribution method provides a better partition balance and ensures orderliness in each partition. However, multiple changes of a data item might be sent to different partitions and the consumer progress of different consumers might be different, which might cause data inconsistency. Therefore, the consumer needs to sort the data from multiple partitions by commitTs before consuming.

    - **Distribute changelogs by column value to Kafka partition**

        If you want the changefeed to send Kafka messages of a table to different partitions, choose this distribution method. The specified column values of a row changelog will determine which partition the changelog is sent to. This distribution method ensures orderliness in each partition and guarantees that the changelog with the same column values is send to the same partition.

9. In the **Topic Configuration** area, configure the following numbers. The changefeed will automatically create the Kafka topics according to the numbers.

    - **Replication Factor**: controls how many Kafka servers each Kafka message is replicated to. The valid value ranges from [`min.insync.replicas`](https://kafka.apache.org/33/documentation.html#brokerconfigs_min.insync.replicas) to the number of Kafka brokers.
    - **Partition Number**: controls how many partitions exist in a topic. The valid value range is `[1, 10 * the number of Kafka brokers]`.

10. Click **Next**.
## Step 4. Configure your changefeed specification

1. In the **Changefeed Specification** area, specify the number of Replication Capacity Units (RCUs) to be used by the changefeed.
2. In the **Changefeed Name** area, specify a name for the changefeed.
3. Click **Next** to check the configurations you set and go to the next page.
## Step 5. Review the configurations

On this page, you can review all the changefeed configurations that you set.

If you find any error, you can go back to fix the error. If there is no error, you can click the check box at the bottom, and then click **Create** to create the changefeed.
