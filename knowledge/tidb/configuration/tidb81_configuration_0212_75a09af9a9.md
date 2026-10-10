# Create and start a MySQL sink changefeed

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-mysql.md`
- Source Title: `Sink to MySQL`
- Source Heading Path: `Sink to MySQL > Create a MySQL sink`
- Source Line Ranges: `90-149`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `changefeed`, `mysql sink`, `connection test`, `table filter`, `event filter`, `start position`, `tso`, `rcu`, `cross-region replication`, `checkpoint`, `replication latency`, `gc lifetime`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0212_75a09af9a9`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-mysql.md#create-a-mysql-sink`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b528937bc490691017f43bd6c523f230599b1cc127a05722f9c88d762469253e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-mysql#create-a-mysql-sink
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about creating a MySQL sink changefeed in TiDB Cloud, including connection testing, filters, start position, RCUs, and post-creation status details.
- Retrieval Keywords: Create Changefeed, Destination MySQL, MySQL Connection, connectivity error, Table Filter, table filter rules, *.*, Tables with valid keys, Tables without valid keys, !test.tbl1, Event Filter, Ignore event, Ignore SQL, Ignore insert value expression, Ignore update new value expression, Ignore update old value expression, Ignore delete value expression, Start Replication Position, Start replication from a specific TSO, Start replication from now on, Start replication from a specific time, Changefeed Specification, Replication Capacity Units, RCUs, Changefeed Name, cross-region replication, Creating, Running, checkpoint, replication latency, SET GLOBAL tidb_gc_life_time = '10m';
- Follow-up Guidance: If existing data was loaded using Dumpling, this chunk says to use the TSO from the Dumpling metadata as the start replication position and restore `tidb_gc_life_time` to its original value after the sink is created.
- Classification Note: This chunk is classified as configuration because it provides the step-by-step changefeed creation settings and options for MySQL sink setup in TiDB Cloud.

## Official Source Content

## Create a MySQL sink

After completing the prerequisites, you can sink your data to MySQL.

1. Navigate to the cluster overview page of the target TiDB cluster, and then click **Data** > **Changefeed** in the left navigation pane.

2. Click **Create Changefeed**, and select **MySQL** as **Destination**.

3. Fill in the MySQL endpoints, user name, and password in **MySQL Connection**.

4. Click **Next** to test whether TiDB can connect to MySQL successfully:

    - If yes, you are directed to the next step of configuration.
    - If not, a connectivity error is displayed, and you need to handle the error. After the error is resolved, click **Next** again.

5. Customize **Table Filter** to filter the tables that you want to replicate. For the rule syntax, refer to [table filter rules](https://docs.pingcap.com/tidb/stable/table-filter).

    - **Filter Rules**: you can set filter rules in this column. By default, there is a rule `*.*`, which stands for replicating all tables. When you add a new rule, TiDB Cloud queries all the tables in TiDB and displays only the tables that match the rules in the box on the right. You can add up to 100 filter rules.
    - **Tables with valid keys**: this column displays the tables that have valid keys, including primary keys or unique indexes.
    - **Tables without valid keys**: this column shows tables that lack primary keys or unique keys. These tables present a challenge during replication because the absence of a unique identifier can result in inconsistent data when the downstream handles duplicate events. To ensure data consistency, it is recommended to add unique keys or primary keys to these tables before initiating the replication. Alternatively, you can add filter rules to exclude these tables. For example, you can exclude the table `test.tbl1` by using the rule `"!test.tbl1"`.

6. Customize **Event Filter** to filter the events that you want to replicate.

    - **Tables matching**: you can set which tables the event filter will be applied to in this column. The rule syntax is the same as that used for the preceding **Table Filter** area. You can add up to 10 event filter rules per changefeed.
    - **Event Filter**: you can use the following event filters to exclude specific events from the changefeed:
        - **Ignore event**: excludes specified event types.
        - **Ignore SQL**: excludes DDL events that match specified expressions. For example, `^drop` excludes statements starting with `DROP`, and `add column` excludes statements containing `ADD COLUMN`.
        - **Ignore insert value expression**: excludes `INSERT` statements that meet specific conditions. For example, `id >= 100` excludes `INSERT` statements where `id` is greater than or equal to 100.
        - **Ignore update new value expression**: excludes `UPDATE` statements where the new value matches a specified condition. For example, `gender = 'male'` excludes updates that result in `gender` being `male`.
        - **Ignore update old value expression**: excludes `UPDATE` statements where the old value matches a specified condition. For example, `age < 18` excludes updates where the old value of `age` is less than 18.
        - **Ignore delete value expression**: excludes `DELETE` statements that meet a specified condition. For example, `name = 'john'` excludes `DELETE` statements where `name` is `'john'`.

7. In **Start Replication Position**, configure the starting position for your MySQL sink.

    - If you have [loaded the existing data](#load-existing-data-optional) using Dumpling, select **Start replication from a specific TSO** and fill in the TSO that you get from Dumpling exported metadata files.
    - If you do not have any data in the upstream TiDB cluster, select **Start replication from now on**.
    - Otherwise, you can customize the start time point by choosing **Start replication from a specific time**.

8. Click **Next** to configure your changefeed specification.

    - In the **Changefeed Specification** area, specify the number of Replication Capacity Units (RCUs) to be used by the changefeed.
    - In the **Changefeed Name** area, specify a name for the changefeed.

9. Click **Next** to review the changefeed configuration.

    If you confirm that all configurations are correct, check the compliance of cross-region replication, and click **Create**.

    If you want to modify some configurations, click **Previous** to go back to the previous configuration page.

10. The sink starts soon, and you can see the status of the sink changes from **Creating** to **Running**.

    Click the changefeed name, and you can see more details about the changefeed, such as the checkpoint, replication latency, and other metrics.

11. If you have [loaded the existing data](#load-existing-data-optional) using Dumpling, you need to restore the GC time to its original value (the default value is `10m`) after the sink is created:

```sql
SET GLOBAL tidb_gc_life_time = '10m';
```
