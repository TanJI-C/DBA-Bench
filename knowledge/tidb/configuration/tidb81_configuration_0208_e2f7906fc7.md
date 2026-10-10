# Configure Pulsar changefeed replication, partitioning, and review

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-pulsar.md`
- Source Title: `Sink to Apache Pulsar`
- Source Heading Path: `Sink to Apache Pulsar > Step 3. Configure the changefeed replication | Sink to Apache Pulsar > Step 4. Configure specification and review`
- Source Line Ranges: `108-195`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `shared`
- Topic Tags: `changefeed`, `pulsar`, `table-filter`, `event-filter`, `start-position`, `tso`, `canal-json`, `topic-distribution`, `partition-distribution`, `replication-capacity-units`, `review`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0208_e2f7906fc7`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-pulsar.md#step-3-configure-the-changefeed-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0b85bad7126a3aab04158eda79763e5bbfeae9f6a4ca051e11a09ded2fb16a4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-pulsar#step-3-configure-the-changefeed-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-pulsar.md

## Retrieval Guidance

- Use When: Use this chunk when configuring a TiDB Cloud changefeed to Apache Pulsar, including table and event filters, start replication position, Canal-JSON format, topic and partition distribution, RCUs, and final review.
- Retrieval Keywords: Table Filter, Filter Rules, *.*, Tables with valid keys, Tables without valid keys, !test.tbl1, Event Filter, Tables matching, Ignore event, Ignore SQL, Ignore insert value expression, Ignore update new value expression, Ignore update old value expression, Ignore delete value expression, Start Replication Position, Start replication from now on, Start replication from a specific TSO, Start replication from a specific time, TSO, garbage collection safe point, Data Format, Canal-JSON, TiDB Extension, Topic Distribution, Send all changelogs to one specified Pulsar Topic, Distribute changelogs by table to Pulsar Topics, Distribute changelogs by database to Pulsar Topics, Default Topic Name, Pulsar Tenant, Pulsar Namespace, Partition Distribution, Primary key or unique index, Table, Timestamp, Column value, Replication Capacity Units, RCUs, Specification and Name, Submit
- Follow-up Guidance: The source notes that when Pulsar is the downstream, the changefeed does not automatically create topics, so the required topics must be created in advance.
- Classification Note: This is classified as configuration because the content defines changefeed setup options and review items for TiDB Cloud replication to Apache Pulsar.

## Official Source Content

## Step 3. Configure the changefeed replication

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

3. In the **Start Replication Position** area, select the starting point for the changefeed to replicate data to Pulsar:

    - **Start replication from now on**: the changefeed will begin replicating data from the current point onwards.
    - **Start replication from a specific TSO**: the changefeed will begin replicating data from the specified [TSO](https://docs.pingcap.com/tidb/stable/tso) onwards. The specified TSO must be within the [garbage collection safe point](https://docs.pingcap.com/tidb/stable/read-historical-data#how-tidb-manages-the-data-versions).
    - **Start replication from a specific time**: the changefeed will begin replicating data from the specified timestamp onwards. The specified timestamp must be within the garbage collection safe point.

4. In the **Data Format** area, select your desired format of Pulsar messages.

    - Canal-JSON is a plain JSON text format, which is easy to parse. For more information, see [TiCDC Canal-JSON Protocol](https://docs.pingcap.com/tidb/stable/ticdc-canal-json/).

    - To add TiDB-extension fields to the Pulsar message body, enable the **TiDB Extension** option. For more information, see [TiDB extension field in TiCDC Canal-JSON Protocol](https://docs.pingcap.com/tidb/stable/ticdc-canal-json/#tidb-extension-field).

5. In the **Topic Distribution** area, select a distribution mode, and then fill in the topic name configurations according to the mode.

    The distribution mode controls how the changefeed distributes event messages to Pulsar topics, by sending all messages to one topic, or sending to specific topics by table or by database.

    > **Note:**
    >
    > When you select Pulsar as the downstream, the changefeed does not automatically create topics. You must create the required topics in advance.

    - **Send all changelogs to one specified Pulsar Topic**

        If you want the changefeed to send all messages to a single Pulsar topic, choose this mode. You can specify a topic name in the **Topic Name** field.

    - **Distribute changelogs by table to Pulsar Topics**

        If you want the changefeed to send all Pulsar messages of each table to a dedicated Pulsar topic, choose this mode. You can specify topic names for tables by setting the **Topic Prefix**, a **Separator** between a database name and table name, and a **Topic Suffix**. For example, if you set the separator as `_`, the Pulsar messages will be sent to topics whose names are in the format of `<Topic Prefix><DatabaseName>_<TableName><Topic Suffix>`. You need to create these topics in advance on Pulsar.

        For changelogs of non-row events, such as Create Schema Event, you can specify a topic name in the **Default Topic Name** field. The changefeed sends the non-row events to this topic to collect such changelogs.

    - **Distribute changelogs by database to Pulsar Topics**

        If you want the changefeed to send all Pulsar messages of each database to a dedicated Pulsar topic, choose this mode. You can specify topic names for databases by setting the **Topic Prefix** and **Topic Suffix**.

        For changelogs of non-row events, such as Resolved Ts Event, you can specify a topic name in the **Default Topic Name** field. The changefeed sends the non-row events to this topic to collect such changelogs.

    Because Pulsar supports multi-tenancy, you might also set the **Pulsar Tenant** and **Pulsar Namespace** if they are different from the defaults.

6. In the **Partition Distribution** area, you can decide which partition a Pulsar message is sent to. You can define **a single partition dispatcher for all tables** or **different partition dispatchers for different tables**. TiDB Cloud provides four rule options to distribute change events to Pulsar partitions:

    - **Primary key or unique index**

        If you want the changefeed to send Pulsar messages of a table to different partitions, choose this distribution method. The primary key or index value of a row changelog determines which partition the changelog is sent to. This distribution method provides better partition balance and ensures row-level orderliness.

    - **Table**

        If you want the changefeed to send Pulsar messages of a table to one Pulsar partition, choose this distribution method. The table name of a row changelog determines which partition the changelog is sent to. This distribution method ensures table orderliness but might cause unbalanced partitions.

    - **Timestamp**
        If you want the changefeed to send Pulsar messages to different Pulsar partitions based on the timestamp, choose this distribution method. The commitTs of a row changelog determines which partition the changelog is sent to. This distribution method provides better partition balance and ensures orderliness in each partition. However, multiple changes of a data item might be sent to different partitions and the consumer progress of different consumers might be different, which might cause data inconsistency. Therefore, the consumer needs to sort the data from multiple partitions by commitTs before consuming.

    - **Column value**

        If you want the changefeed to send Pulsar messages of a table to different partitions, choose this distribution method. The specified column values of a row changelog will determine which partition the changelog is sent to. This distribution method ensures orderliness in each partition and guarantees that changelogs with the same column values are sent to the same partition.

7. Click **Next**.
## Step 4. Configure specification and review

1. In the **Specification and Name** section:

    - Specify the number of [Replication Capacity Units (RCUs)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-billing-ticdc-rcu) for the changefeed.
    - Enter a name for the changefeed.

2. Review all changefeed configurations.

    - If you find an issue, you can go back to previous steps to resolve the problem.
    - If there are no issues, you can click **Submit** to create the changefeed.
