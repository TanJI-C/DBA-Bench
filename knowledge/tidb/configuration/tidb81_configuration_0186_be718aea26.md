# Kafka topic dispatch rules and schema-level DDL routing

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-sink-to-kafka.md`
- Source Title: `Replicate Data to Kafka`
- Source Heading Path: `Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink | Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink > Matcher rules | Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink > Topic dispatchers | Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink > Dispatch DDL events | Replicate Data to Kafka > Customize the rules for Topic and Partition dispatchers of Kafka Sink > Dispatch DDL events > Schema-level DDLs`
- Source Line Ranges: `216-269`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`
- Topic Tags: `kafka`, `dispatchers`, `matcher-rules`, `topic-dispatch`, `topic-expression`, `ddl-events`, `schema-level-ddl`, `default-topic`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0186_be718aea26`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-sink-to-kafka.md#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0995e0322edf2ebcf5a64992b1a0e21e3dfa9b5b0a05f53f632acc42c6c8737d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-kafka#customize-the-rules-for-topic-and-partition-dispatchers-of-kafka-sink
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-sink-to-kafka.md

## Retrieval Guidance

- Use When: Use this chunk when defining TiCDC Kafka `dispatchers` rules, topic expressions, default topic behavior, or routing for schema-level DDL events.
- Retrieval Keywords: dispatchers, matcher, topic dispatcher, partition, topic expression, default topic, --sink-uri, first matching topic expression, hello_{schema}_{table}, hello_{schema}_world, hard_code_topic_name, {schema}_{table}, schema-level DDLs, create database, drop database
- Follow-up Guidance: The source explains matcher precedence, valid topic expression format, and that schema-level DDL events are sent to the default topic specified in `--sink-uri`.
- Classification Note: This chunk is classified as configuration because it describes how to configure Kafka topic and partition dispatch rules, topic expressions, and DDL event routing in TiCDC.

## Official Source Content

## Customize the rules for Topic and Partition dispatchers of Kafka Sink
### Matcher rules

Take the following configuration of `dispatchers` as an example:

```toml
[sink]
dispatchers = [
  {matcher = ['test1.*', 'test2.*'], topic = "Topic expression 1", partition = "ts" },
  {matcher = ['test3.*', 'test4.*'], topic = "Topic expression 2", partition = "index-value" },
  {matcher = ['test1.*', 'test5.*'], topic = "Topic expression 3", partition = "table"},
  {matcher = ['test6.*'], partition = "ts"}
]
```

- For the tables that match the matcher rule, they are dispatched according to the policy specified by the corresponding topic expression. For example, the `test3.aa` table is dispatched according to "Topic expression 2"; the `test5.aa` table is dispatched according to "Topic expression 3".
- For a table that matches multiple matcher rules, it is dispatched according to the first matching topic expression. For example, the `test1.aa` table is distributed according to "Topic expression 1".
- For tables that do not match any matcher rule, the corresponding data change events are sent to the default topic specified in `--sink-uri`. For example, the `test10.aa` table is sent to the default topic.
- For tables that match the matcher rule but do not specify a topic dispatcher, the corresponding data changes are sent to the default topic specified in `--sink-uri`. For example, the `test6.aa` table is sent to the default topic.
### Topic dispatchers

You can use topic = "xxx" to specify a Topic dispatcher and use topic expressions to implement flexible topic dispatching policies. It is recommended that the total number of topics be less than 1000.

The format of the Topic expression is `[prefix]{schema}[middle][{table}][suffix]`.

- `prefix`: optional. Indicates the prefix of the Topic Name.
- `{schema}`: required. Used to match the schema name. Starting from v7.1.4, this parameter is optional.
- `middle`: optional. Indicates the delimiter between schema name and table name.
- `{table}`: optional. Used to match the table name.
- `suffix`: optional. Indicates the suffix of the Topic Name.

`prefix`, `middle` and `suffix` can only include the following characters: `a-z`, `A-Z`, `0-9`, `.`, `_` and `-`. `{schema}` and `{table}` are both lowercase. Placeholders such as `{Schema}` and `{TABLE}` are invalid.

Some examples:

- `matcher = ['test1.table1', 'test2.table2'], topic = "hello_{schema}_{table}"`
    - The data change events corresponding to `test1.table1` are sent to the topic named `hello_test1_table1`.
    - The data change events corresponding to `test2.table2` are sent to the topic named `hello_test2_table2`.
- `matcher = ['test3.*', 'test4.*'], topic = "hello_{schema}_world"`
    - The data change events corresponding to all tables in `test3` are sent to the topic named `hello_test3_world`.
    - The data change events corresponding to all tables in `test4` are sent to the topic named `hello_test4_world`.
- `matcher = ['test5.*, 'test6.*'], topic = "hard_code_topic_name"`
    - The data change events corresponding to all tables in `test5` and `test6` are sent to the topic named `hard_code_topic_name`. You can specify the topic name directly.
- `matcher = ['*.*'], topic = "{schema}_{table}"`
    - All tables listened by TiCDC are dispatched to separate topics according to the "schema_table" rule. For example, for the `test.account` table, TiCDC dispatches its data change log to a Topic named `test_account`.
### Dispatch DDL events
#### Schema-level DDLs

DDLs that are not related to a specific table are called schema-level DDLs, such as `create database` and `drop database`. The events corresponding to schema-level DDLs are sent to the default topic specified in `--sink-uri`.
