# Performance Overview query latency and connection analysis

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/performance-tuning-methods.md`
- Source Title: `Performance Analysis and Tuning`
- Source Heading Path: `Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Query latency breakdown and key latency metrics > Duration, Connection Idle Duration, and Connection Count | Performance Analysis and Tuning > Performance analysis and tuning using the Performance Overview dashboard > Query latency breakdown and key latency metrics > Parse, Compile, and Execute Duration`
- Source Line Ranges: `252-336`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `sql`, `tikv`, `shared`
- Topic Tags: `database time`, `query latency`, `connection idle duration`, `connection count`, `active connections`, `short connections`, `parse`, `compile`, `execute`, `prepared plan cache`, `tso`, `kv request`, `bottleneck analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0135_1c2d0f73fd`
- Source ID: `tidb-docs-8.1:performance-tuning-methods.md#duration-connection-idle-duration-and-connection-count`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4805849246114a3bb09c28844deb8a8a5d0fcfecc09788e3716f110581fa1543`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/performance-tuning-methods#duration-connection-idle-duration-and-connection-count
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/performance-tuning-methods.md

## Retrieval Guidance

- Use When: Use this chunk when analyzing TiDB Performance Overview dashboard latency breakdown, connection idle time, connection counts, or whether bottlenecks are inside TiDB versus outside the database.
- Retrieval Keywords: Performance Overview dashboard, Duration panel, Connection Idle Duration panel, Connection Count panel, average latency, P99 latency, avg-in-txn, avg-not-in-txn, active connections, disconnection/s, short connections, Parse Duration, Compile Duration, Execute Duration, get token, query latency breakdown, prepared plan cache, StmtExecute, query command interface, TSO wait time, KV request time, token-limit
- Follow-up Guidance: The content also explains the formula `avg Query Duration = avg Get Token + avg Parse Duration + avg Compile Duration + avg Execute Duration` and gives examples of bottlenecks in `compile` and `execute` phases.
- Classification Note: This is classified under performance for the dashboard component because the official content focuses on dashboard panels and metrics used to analyze query latency, connection behavior, and SQL processing phases in TiDB.

## Official Source Content

#### Duration, Connection Idle Duration, and Connection Count

The Duration panel contains the average and P99 latency of all statements, and the average latency of each SQL type. The Connection Idle Duration panel contains the average and the P99 connection idle duration. Connection idle duration includes the following two states:

- in-txn: The interval between processing the previous SQL and receiving the next SQL statement when the connection is within a transaction.
- not-in-txn: The interval between processing the previous SQL and receiving the next SQL statement when the connection is not within a transaction.

An applications perform transactions with the same database connection. By comparing the average query latency with the connection idle duration, you can determine if TiDB is the bottleneck for overall system, or if user response time jitter is caused by TiDB.

- If the application workload is not read-only and contains transactions, by comparing the average query latency with `avg-in-txn`, you can determine the proportion in processing transactions inside and outside the database, and identify the bottleneck in user response time.
- If the application workload is read-only or autocommit mode is on, you can compare the average query latency with `avg-not-in-txn`.

In real customer scenarios, it is not rare that the bottleneck is outside the database, for example:

- The client server configuration is too low and the CPU resources are exhausted.
- HAProxy is used as a TiDB cluster proxy, and the HAProxy CPU resource is exhausted.
- HAProxy is used as a TiDB cluster proxy, and the network bandwidth of the HAProxy server is used up under high workload.
- The network latency from the application server to the database is high. For example, the network latency is high because in public-cloud deployments the applications and the TiDB cluster are not in the same region, or the dns workload balancer and the TiDB cluster are not in the same region.
- The bottleneck is in client applications. The application server's CPU cores and Numa resources cannot be fully utilized. For example, only one JVM is used to establish thousands of JDBC connections to TiDB.

In the Connection Count panel, you can check the total number of connections and also the number of connections on each TiDB node, which helps you determine whether the total number of connections is normal and whether the number of connections on each TiDB node is unbalanced. `active connections` indicates the number of active connections, which is equal to the database time per second. The Y axis on the right (`disconnection/s`) indicates the number of disconnections per second in a cluster, which can be used to determine whether the application uses short connections.

**Example 1: The number of disconnection/s is too high**

![high disconnection/s](/media/performance/high_disconnections.png)

In this workload:

- The average latency and P99 latency of all SQL statements are 10.8 ms and 84.1 ms, respectively.
- The average connection idle time in transactions `avg-in-txn` is 9.4 ms.
- The total number of connections to the cluster is 3,700, and the number of connections to each TiDB node is 1,800. The average number of active connections is 40.3, which indicates that most of the connections are idle. The average number of `disconnection/s` is 55.8, which indicates that the application is connecting and disconnecting frequently. The behavior of short connections will have a certain impact on TiDB resources and response time.

**Example 2: TiDB is the bottleneck of user response time**

![TiDB is the Bottleneck](/media/performance/tpcc_duration_idle.png)

In this TPC-C workload:

- The average latency and P99 latency of all SQL statements are 477 us and 3.13 ms, respectively. The average latencies of the commit statement, insert statement, and query statement are 2.02 ms, 609 us, and 468 us, respectively.
- The average connection idle time in transactions `avg-in-txn` is 171 us.

The average query latency is significantly greater than `avg-in-txn`, which means the main bottleneck in transactions is inside the database.

**Example 3: TiDB is not the bottleneck of user response time**

![TiDB is not Bottleneck](/media/performance/cloud_query_long_idle.png)

In this workload, the average query latency is 1.69 ms and `avg-in-txn` is 18 ms, indicating that TiDB spends 1.69 ms on average to process a SQL statement in transactions, and then needs to wait for 18 ms to receive the next statement.

The average query latency is significantly lower than `avg-in-txn`. The bottleneck of user response time is not in TiDB. This example is in a public cloud environment, where high network latency between the application and the database results in extremely high connection idle time, because the application and the database are not in the same region.
#### Parse, Compile, and Execute Duration

In TiDB, there is a [typical processing flow](https://docs.pingcap.com/tidb/stable/sql-optimization-concepts) from sending query statements to returning results.

SQL processing in TiDB consists of four phases, `get token`, `parse`, `compile`, and `execute`.

- `get token`: Usually only a few microseconds and can be ignored. The token is limited only when the number of connections to a single TiDB instance reaches the [token-limit](https://docs.pingcap.com/tidb/stable/tidb-configuration-file) limit.
- `parse`: The query statements are parsed into abstract syntax tree (AST).
- `compile`: Execution plans are compiled based on the AST from the `parse` phase and statistics. The `compile` phase contains logical optimization and physical optimization. Logical optimization optimizes query plans by rules, such as column pruning based on relational algebra. Physical optimization estimates the cost of the execution plans by statistics by a cost-based optimizer and selects a physical execution plan with the lowest cost.
- `execute`: The time consumption to execute a SQL statement. TiDB first waits for the globally unique timestamp TSO. Then the executor constructs the TiKV API request based on the Key range of the operator in the execution plan and distributes it to TiKV. `execute` time includes the TSO wait time, the KV request time, and the time spent by TiDB executor in processing data.

If an application uses the `query` or `StmtExecute` MySQL command interface only, you can use the following formula to identify the bottleneck in average latency.

```
avg Query Duration = avg Get Token + avg Parse Duration + avg Compile Duration + avg Execute Duration
```

Usually, the `execute` phase accounts for the most of the `query` latency. However, the `parse` and `compile` phases can also take a large part in the following cases:

- Long latency in the `parse` phase: For example, when the `query` statement is long, much CPU will be consumed to parse the SQL text.
- Long latency in the `compile` phase: If the prepared plan cache is not hit, TiDB needs to compile an execution plan for every SQL execution. The latency in the `compile` phase can be several or tens of milliseconds or even higher. If prepared plan cache is not hit, logical and physical optimization are done in the `compile` phase, which consumes a lot of CPU and memory, makes Go Runtime (TiDB is written in [`Go`](https://go.dev/)) under pressure, and affects the performance of other TiDB components. Prepared plan cache is important for efficient processing of OLTP workload in TiDB.

**Example 1: Database bottleneck in the `compile` phase**

![Compile](/media/performance/long_compile.png)

In the preceding figure, the average time of the `parse`, `compile`, and `execute` phases are 17.1 us, 729 us, and 681 us, respectively. The `compile` latency is high because the application uses the `query` command interface and cannot use prepared plan cache.

**Example 2: Database bottleneck in the `execute` phase**

![Execute](/media/performance/long_execute.png)

In this TPC-C workload, the average time of `parse`, `compile` and `execute` phases are 7.39 us, 38.1 us, and 12.8 ms, respectively. The `execute` phase is the bottleneck of the `query` latency.
