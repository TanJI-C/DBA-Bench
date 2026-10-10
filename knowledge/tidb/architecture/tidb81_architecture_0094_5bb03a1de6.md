# TiDB SQL layer overview and distributed SQL processing

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-computing.md`
- Source Title: `TiDB Computing`
- Source Heading Path: `TiDB Computing > SQL layer overview | TiDB Computing > SQL layer overview > SQL computing | TiDB Computing > SQL layer overview > Distributed SQL operations | TiDB Computing > SQL layer overview > Architecture of SQL layer`
- Source Line Ranges: `116-157`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `sql-layer`, `stateless-nodes`, `sql-computing`, `predicate-pushdown`, `pre-aggregation`, `rpc`, `query-plan`, `mysql-protocol`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0094_5bb03a1de6`
- Source ID: `tidb-docs-8.1:tidb-computing.md#sql-layer-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1f62d5a5e80ee05da18dfc4c79fe41c2f3bf2c387f15c16fcd975d53c410040e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-computing#sql-layer-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-computing.md

## Retrieval Guidance

- Use When: Use this chunk when describing the TiDB SQL layer, how TiDB Server translates SQL into Key-Value operations, and how predicate pushdown and pre-aggregation reduce RPC overhead in distributed SQL processing.
- Retrieval Keywords: SQL layer overview, TiDB Server, translates SQL statements into Key-Value operations, stateless nodes, SQL computing, Distributed SQL operations, predicate pushdown, pre-aggregation, Count(*), select count(*) from user where name = "TiDB", Key Range, [StartKey, EndKey), [0, MaxInt64), Scan Key Range, Filter data, RPC overhead, distributed SQL, Architecture of SQL layer, Load Balancer, MySQL Protocol Packet, query plans, execute a query plan
- Follow-up Guidance: The source further states that a user's SQL request can be sent to TiDB Server directly or via `Load Balancer`, after which TiDB Server parses `MySQL Protocol Packet`, develops and optimizes query plans, interacts with TiKV, and returns query results.
- Classification Note: This is classified as architecture because the content explains the responsibilities and processing flow of the TiDB SQL layer and its interaction with TiKV during distributed query execution.

## Official Source Content

## SQL layer overview

TiDB's SQL layer, TiDB Server, translates SQL statements into Key-Value operations, forwards the operations to TiKV, the distributed Key-Value storage layer, assembles the results returned by TiKV, and finally returns the query results to the client.

The nodes at this layer are stateless. These nodes themselves do not store data and are completely equivalent.
### SQL computing

The simplest solution to SQL computing is the [mapping of table data to Key-Value](#mapping-of-table-data-to-key-value) as described in the previous section, which maps SQL queries to KV queries, acquires the corresponding data through the KV interface, and performs various computations.

For example, to execute the `select count(*) from user where name = "TiDB"` SQL statement, TiDB needs to read all data in the table, then checks whether the `name` field is `TiDB`, and if so, returns this row. The process is as follows:

1. Construct the Key Range: all `RowID` in a table are in `[0, MaxInt64)` range. According to the row data `Key` encoding rule, using `0` and `MaxInt64` can construct a `[StartKey, EndKey)` range that is left-closed and right-open.
2. Scan Key Range: read the data in TiKV according to the key range constructed above.
3. Filter data: for each row of data read, calculate the `name = "TiDB"` expression. If the result is `true`, return to this row. If not, skip this row.
4. Calculate `Count(*)`: for each row that meets the requirements, add up to the result of `Count(*)`.

**The entire process is illustrated as follows:**

![naive sql flow](/media/tidb-computing-native-sql-flow.jpeg)

This solution is intuitive and feasible, but has some obvious problems in a distributed database scenario:

- As the data is being scanned, each row is read from TiKV via a KV operation with at least one RPC overhead, which can be very high if there is a large amount of data to be scanned.
- It is not applicable to all rows. Data that does not meet the conditions does not need to be read.
- From the returned result of this query, only the number of rows that match the requirements is needed, not the value of those rows.
### Distributed SQL operations

To solve the problems above, the computation should be as close to the storage node as possible to avoid a large number of RPC callings. First of all, the SQL predicate condition `name = "TiDB"` should be pushed down to the storage node for computation, so that only valid rows are returned, which avoids meaningless network transfers. Then, the aggregation function `Count(*)` can also be pushed down to the storage nodes for pre-aggregation, and each node only has to return a result of `Count(*)`. The SQL layer will sum up the `Count(*)` results returned by each node.

The following image shows how data returns layer by layer:

![dist sql flow](/media/tidb-computing-dist-sql-flow.png)
### Architecture of SQL layer

The previous sections introduce some functions of the SQL layer and I hope you have a basic understanding of how SQL statements are handled. In fact, TiDB's SQL layer is much more complicated, with many modules and layers. The following diagram lists the important modules and calling relationships:

![tidb sql layer](/media/tidb-computing-tidb-sql-layer.png)

The user's SQL request is sent to TiDB Server either directly or via `Load Balancer`. TiDB Server will parse `MySQL Protocol Packet`, get the content of requests, parse the SQL request syntactically and semantically, develop and optimize query plans, execute a query plan, get and process the data. All data is stored in the TiKV cluster, so in this process, TiDB Server needs to interact with TiKV and get the data. Finally, TiDB Server needs to return the query results to the user.
