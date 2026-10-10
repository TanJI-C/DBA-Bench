# Kafka sink DDL routing and partition dispatcher rules

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink > Dispatch DDL events > Table-level DDLs | Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink > Partition dispatchers`
- Source Line Ranges: `270-326`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `kafka`, `sink-uri`, `dispatchers`, `ddl-events`, `topic-routing`, `partitioning`, `ordering`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0187_3c12343509`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#table-level-ddls`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8be4d195d127ff965eb7588b495a54526877a86c6a3a1216c883366fb3150ddb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#table-level-ddls
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how TiCDC Kafka sink routes table-level DDLs to topics and how `partition` or `dispatcher` rules affect partitioning and ordering.
- Retrieval Keywords: table-level DDLs, alter table, create table, drop table test.table1, rename table test.table1 to test.table10, dispatchers, matcher = ['test.*'], topic = {schema}_{table}, partition = "xxx", default, index-value, columns, table, ts, index = "index1", columns = ["id", "a"], first matching rule takes precedence, dispatcher to partition alias, `dispatcher` and `partition` cannot appear in the same rule
- Follow-up Guidance: The content also states that `partition` is an alias for `dispatcher` since v6.1.0, but both cannot be used in the same rule.
- Classification Note: This is classified as configuration because it defines Kafka sink dispatcher syntax, matching rules, topic routing behavior for DDL events, and partitioning options.

## Official Source Content

#### Table-level DDLs

DDLs that are related to a specific table are called table-level DDLs, such as `alter table` and `create table`. The events corresponding to table-level DDLs are sent to the corresponding topic according to dispatcher configurations.

For example, for a dispatcher like `matcher = ['test.*'], topic = {schema}_{table}`, DDL events are dispatched as follows:

- If a single table is involved in the DDL event, the DDL event is sent to the corresponding topic as is. For example, for the DDL event `drop table test.table1`, the event is sent to the topic named `test_table1`.
- If multiple tables are involved in the DDL event (`rename table` / `drop table` / `drop view` may involve multiple tables), the DDL event is split into multiple events and sent to the corresponding topics. For example, for the DDL event `rename table test.table1 to test.table10, test.table2 to test.table20`, the event `rename table test.table1 to test.table10` is sent to the topic named `test_table1` and the event `rename table test.table2 to test.table20` is sent to the topic named `test.table2`.
### Partition dispatchers

You can use `partition = "xxx"` to specify a partition dispatcher. It supports five dispatchers: `default`, `index-value`, `columns`, `table`, and `ts`. The dispatcher rules are as follows:

- `default`: uses the `table` dispatcher rule by default. It calculates the partition number using the schema name and table name, ensuring data from a table is sent to the same partition. As a result, the data from a single table only exists in one partition and is guaranteed to be ordered. However, this dispatcher rule limits the send throughput, and the consumption speed cannot be improved by adding consumers.
- `index-value`: calculates the partition number using either the primary key, a unique index, or an index explicitly specified by `index`, distributing table data across multiple partitions. The data from a single table is sent to multiple partitions, and the data in each partition is ordered. You can improve the consumption speed by adding consumers.
- `columns`: calculates the partition number using the values of explicitly specified columns, distributing table data across multiple partitions. The data from a single table is sent to multiple partitions, and the data in each partition is ordered. You can improve the consumption speed by adding consumers.
- `table`: calculates the partition number using the schema name and table name.
- `ts`: calculates the partition number using the commitTs of the row change, distributing table data across multiple partitions. The data from a single table is sent to multiple partitions, and the data in each partition is ordered. You can improve the consumption speed by adding consumers. However, multiple changes of a data item might be sent to different partitions and the consumer progress of different consumers might be different, which might cause data inconsistency. Therefore, the consumer needs to sort the data from multiple partitions by commitTs before consuming.

Take the following configuration of `dispatchers` as an example:

```toml
[sink]
dispatchers = [
    {matcher = ['test.*'], partition = "index-value"},
    {matcher = ['test1.*'], partition = "index-value", index = "index1"},
    {matcher = ['test2.*'], partition = "columns", columns = ["id", "a"]},
    {matcher = ['test3.*'], partition = "table"},
]
```

- Tables in the `test` database use the `index-value` dispatcher, which calculates the partition number using the value of the primary key or unique index. If a primary key exists, the primary key is used; otherwise, the shortest unique index is used.
- Tables in the `test1` table use the `index-value` dispatcher and calculate the partition number using values of all columns in the index named `index1`. If the specified index does not exist, an error is reported. Note that the index specified by `index` must be a unique index.
- Tables in the `test2` database use the `columns` dispatcher and calculate the partition number using the values of columns `id` and `a`. If any of the columns does not exist, an error is reported.
- Tables in the `test3` database use the `table` dispatcher.
- Tables in the `test4` database use the `default` dispatcher, that is the `table` dispatcher, as they do not match any of the preceding rules.

If a table matches multiple dispatcher rules, the first matching rule takes precedence.

> **Note:**
>
> Since v6.1.0, to clarify the meaning of the configuration, the configuration used to specify the partition dispatcher has been changed from `dispatcher` to `partition`, with `partition` being an alias for `dispatcher`. For example, the following two rules are exactly equivalent.
>
> ```
> [sink]
> dispatchers = [
>    {matcher = ['*.*'], dispatcher = "index-value"},
>    {matcher = ['*.*'], partition = "index-value"},
> ]
> ```
>
> However, `dispatcher` and `partition` cannot appear in the same rule. For example, the following rule is invalid.
>
> ```
> {matcher = ['*.*'], dispatcher = "index-value", partition = "table"},
> ```
