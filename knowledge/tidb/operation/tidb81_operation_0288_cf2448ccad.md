# Create and verify a TiDB Cloud sink changefeed

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-tidb-cloud.md`
- Source Title: `Sink to TiDB Cloud`
- Source Heading Path: `Sink to TiDB Cloud > Create a TiDB Cloud sink`
- Source Line Ranges: `60-113`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`, `tidb`
- Topic Tags: `changefeed`, `creation`, `connection`, `table-filter`, `event-filter`, `tso`, `rcu`, `verification`, `metrics`, `gc-lifetime`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0288_cf2448ccad`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-tidb-cloud.md#create-a-tidb-cloud-sink`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e760ea99454a6cf183879e2a85f4b48599b3d4846f0ff7a6345bebb1bccb81f8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-tidb-cloud#create-a-tidb-cloud-sink
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-tidb-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when you need the UI steps and configurable fields to create, test, and verify a TiDB Cloud sink changefeed to a TiDB Cloud Serverless cluster.
- Retrieval Keywords: Create a TiDB Cloud sink, Data > Changefeed, Create Changefeed, TiDB Cloud as the destination, TiDB Cloud Connection, destination TiDB Cloud Serverless cluster, user name and password, connectivity error, Table Filter, table filter rules, *.*, up to 100 filter rules, Tables with valid keys, Tables without valid keys, !test.tbl1, Event Filter, up to 10 event filter rules per changefeed, Ignore event, Ignore SQL, Ignore insert value expression, Ignore update new value expression, Ignore update old value expression, Ignore delete value expression, Start Replication Position, TSO from Dumpling exported metadata files, Changefeed Specification, Replication Capacity Units, RCUs, Changefeed Name, Creating, Running, checkpoint, replication latency, other metrics, SET GLOBAL tidb_gc_life_time = '10m';
- Follow-up Guidance: The source states that after the sink is created, you can open the changefeed details to view the checkpoint, replication latency, and other metrics, and then restore `tidb_gc_life_time` to its original value.
- Classification Note: This is classified as operation because the content provides the step-by-step procedure to create a changefeed, configure filters and start position, validate connectivity, and verify running status and metrics.

## Official Source Content

## Create a TiDB Cloud sink

After completing the prerequisites, you can sink your data to the destination TiDB Cloud Serverless cluster.

1. Navigate to the cluster overview page of the target TiDB cluster, and then click **Data** > **Changefeed** in the left navigation pane.

2. Click **Create Changefeed**, and select **TiDB Cloud** as the destination.

3. In the **TiDB Cloud Connection** area, select the destination TiDB Cloud Serverless cluster, and then fill in the user name and password of the destination cluster.

4. Click **Next** to establish the connection between the two TiDB clusters and test whether the changefeed can connect them successfully:

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

7. In the **Start Replication Position** area, fill in the TSO that you get from Dumpling exported metadata files.

8. Click **Next** to configure your changefeed specification.

    - In the **Changefeed Specification** area, specify the number of Replication Capacity Units (RCUs) to be used by the changefeed.
    - In the **Changefeed Name** area, specify a name for the changefeed.

9. Click **Next** to review the changefeed configuration.

    If you confirm that all configurations are correct, check the compliance of cross-region replication, and click **Create**.

    If you want to modify some configurations, click **Previous** to go back to the previous configuration page.

10. The sink starts soon, and you can see the status of the sink changes from **Creating** to **Running**.

    Click the changefeed name, and you can see more details about the changefeed, such as the checkpoint, replication latency, and other metrics.

11. Restore [tidb_gc_life_time](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50) to its original value (the default value is `10m`) after the sink is created:

    ```sql
    SET GLOBAL tidb_gc_life_time = '10m';
    ```
