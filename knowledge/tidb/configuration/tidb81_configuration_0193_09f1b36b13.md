# Pulsar sink dispatch rules for topics partitions and DDL

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-pulsar.md`
- Source Title: `Replicate Data to Pulsar`
- Source Heading Path: `Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink | Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink > Matching rules for Matcher | Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink > Topic dispatcher | Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink > Dispatch DDL events | Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink > Dispatch DDL events > Database-level DDL events | Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink > Dispatch DDL events > Table-level DDL events | Replicate Data to Pulsar > Customize the dispatching rules for topics and partitions in Pulsar Sink > Partition dispatcher`
- Source Line Ranges: `251-332`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `pulsar`, `dispatchers`, `matcher`, `topic-dispatcher`, `partition-dispatcher`, `ddl-events`, `topic-expression`, `partitioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0193_09f1b36b13`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-pulsar.md#customize-the-dispatching-rules-for-topics-and-partitions-in-pulsar-sink`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3e8bfbe408aee886e7f2d5ec91f72014d77aa1d10ad513d2186a64b44a405c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-pulsar#customize-the-dispatching-rules-for-topics-and-partitions-in-pulsar-sink
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-pulsar.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiCDC Pulsar sink `dispatchers` match tables, build topic expressions, route DDL events, or choose a partition dispatcher.
- Retrieval Keywords: dispatchers, matcher, topic = "xxx", partition = "xxx", Matching rules for Matcher, Topic dispatcher, Dispatch DDL events, Database-level DDL events, Table-level DDL events, Partition dispatcher, default topic specified in --sink-uri, topic expression, {schema}_{table}, hello_{schema}_{table}, persistent://abc/def/, default, ts, index-value, table, exclusive subscription model, RENAME TABLE, DROP TABLE, DROP VIEW, CREATE DATABASE, ALTER TABLE
- Follow-up Guidance: The chunk explains first-match behavior for matcher rules, the topic expression format `[tenant_and_namespace][prefix]{schema}[middle][{table}][suffix]`, and how database-level and table-level DDL events are dispatched.
- Classification Note: This is classified as configuration because the content defines TiCDC Pulsar sink dispatcher settings, matching behavior, topic expressions, DDL routing rules, and partitioning options.

## Official Source Content

## Customize the dispatching rules for topics and partitions in Pulsar Sink
### Matching rules for Matcher

Take the `dispatchers` configuration item in the following sample configuration file as an example:

```toml
[sink]
dispatchers = [
  {matcher = ['test1.*', 'test2.*'], topic = "Topic expression 1", partition = "ts" },
  {matcher = ['test3.*', 'test4.*'], topic = "Topic expression 2", partition = "index-value" },
  {matcher = ['test1.*', 'test5.*'], topic = "Topic expression 3", partition = "table"},
  {matcher = ['test6.*'], partition = "default"},
  {matcher = ['test7.*'], partition = "test123"}
]
```

- The tables that match a matcher rule are dispatched according to the policy specified by the corresponding topic expression. For example, the table `test3.aa` is dispatched according to `Topic expression 2`, and the table `test5.aa` is dispatched according to `Topic expression 3`.
- For a table that matches more than one matcher rule, it is dispatched according to the first matching topic expression. For example, the table `test1.aa` is dispatched according to `Topic expression 1`.
- For tables that do not match any matcher, the corresponding data change events are sent to the default topic specified in `-sink-uri`. For example, the table `test10.aa` is sent to the default topic.
- For tables that match the matcher rule but do not have a topic dispatcher specified, the corresponding data changes are sent to the default topic specified in `-sink-uri`. For example, the table `test6.abc` is sent to the default topic.
### Topic dispatcher

You can use `topic = "xxx"` to specify a topic dispatcher and use topic expressions to implement flexible topic dispatching policies. It is recommended that the total number of topics be less than 1000.

The format of a topic expression is `[tenant_and_namespace][prefix]{schema}[middle][{table}][suffix]`. The following are the meanings of each part:

- `tenant_and_namespace`：Optional. Represents the tenant and namespace of the topic, such as `persistent://abc/def/`. If not configured, it means that the topic is in the default namespace `default` under the default tenant `public` of Pulsar.
- `prefix`: Optional. Represents the prefix of the topic name.
- `{schema}`: Optional. Represents the database name.
- `middle`: Optional. Represents the separator between a database name and a table name.
- `{table}`: Optional. Represents the table name.
- `suffix`: Optional. Represents the suffix of the topic name.

`prefix`, `middle`, and `suffix` only support uppercase and lowercase letters (`a-z`, `A-Z`), numbers (`0-9`), dots (`.`), underscores (`_`), and hyphens (`-`). `{schema}` and `{table}` must be lowercase. Placeholders such as `{Schema}` and `{TABLE}` that contain uppercase letters are invalid.

The following are some examples:

- `matcher = ['test1.table1', 'test2.table2'], topic = "hello_{schema}_{table}"`
    - Data change events corresponding to the table `test1.table1` are despatched to a topic named `hello_test1_table1`.
    - Data change events corresponding to the table `test2.table2` are despatched to a topic named `hello_test2_table2`.

- `matcher = ['test3.*', 'test4.*'], topic = "hello_{schema}_world"`
    - Data change events for all tables under `test3` are despatched to a topic named `hello_test3_world`.
    - Data change events for all tables under `test4` are despatched to a topic named `hello_test4_world`.

- `matcher = ['*.*'], topic = "{schema}_{table}"`
    - For all tables that TiCDC listens on, they are despatched to separate topics according to the `databaseName_tableName` rule. For example, for the table `test.account`, TiCDC despatches its data change log to a topic named `test_account`.
### Dispatch DDL events
#### Database-level DDL events

DDL statements such as `CREATE DATABASE` and `DROP DATABASE` that are not related to a specific table are called database-level DDL statements. Events corresponding to database-level DDL statements are dispatched to the default topic specified in `--sink-uri`.
#### Table-level DDL events

DDL statements such as `ALTER TABLE` and `CREATE TABLE` that are related to a specific table are called table-level DDL statements. Events corresponding to table-level DDL statements are dispatched to an appropriate topic according to the configuration of `dispatchers`.

For example, for a `dispatchers` configuration like `matcher = ['test.*'], topic = {schema}_{table}`, the DDL events are despatched as follows:

- If a DDL event only involves a single table, the DDL event is dispatched to the appropriate topic as it is. For example, for the DDL event `DROP TABLE test.table1`, the event is dispatched to the topic named `test_table1`.

- If a DDL event involves more than one table (`RENAME TABLE`, `DROP TABLE`, and `DROP VIEW` might all involve more than one table), the single DDL event is split into multiple ones and dispatched to appropriate topics. For example, for the DDL event `RENAME TABLE test.table1 TO test.table10, test.table2 TO test.table20`, the processing is as follows:

    - Dispatch the DDL event for `RENAME TABLE test.table1 TO test.table10` to a topic named `test_table1`.
    - Dispatch the DDL event for `RENAME TABLE test.table2 TO test.table20` to a topic named `test_table2`.
### Partition dispatcher

Currently, TiCDC only supports consumers to consume messages using the exclusive subscription model, that is, each consumer can consume messages from all partitions in a topic.

You can specify a partition dispatcher with `partition = "xxx"`. The following partition dispatches are supported: `default`, `ts`, `index-value`, and `table`. If you fill in any other string, TiCDC will pass that string as the `key` of the message in the messages sent to the Pulsar server.

The dispatching rules are as follows:

- `default`: By default, events are dispatched by the schema name and table name, which is the same as when `table` is specified.
- `ts`: Use commitTs of row changes to perform hash calculation and dispatch events.
- `index-value`: Use the value of the table primary key or unique index to perform hash calculation and dispatch events.
- `table`: Use the schema name and table name to perform hash calculation and dispatch events.
- Other self-defined string: The self-defined string is used directly as the key for the Pulsar message, and the Pulsar producer uses this key value for dispatching.
