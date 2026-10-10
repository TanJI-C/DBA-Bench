# Online asynchronous DDL execution and parallel framework

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/ddl-introduction.md`
- Source Title: `Execution Principles and Best Practices of DDL Statements`
- Source Heading Path: `Execution Principles and Best Practices of DDL Statements > DDL execution principles > How the online DDL asynchronous change works in TiDB`
- Source Line Ranges: `63-133`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `ddl`, `online-schema-change`, `asynchronous-execution`, `owner`, `job-queue`, `parallel-ddl`, `schema-version`, `add-index`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0004_ae5d02b12f`
- Source ID: `tidb-docs-8.1:best-practices/ddl-introduction.md#how-the-online-ddl-asynchronous-change-works-in-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5cc45c7efbe3f96b4979842c1d17f5696fc29b9e5c928f648fbe5b630357ab91`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/ddl-introduction#how-the-online-ddl-asynchronous-change-works-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/ddl-introduction.md

## Retrieval Guidance

- Use When: Use this chunk when explaining how TiDB online asynchronous DDL transitions through compatible schema states, how `ADD INDEX` moves to `public`, or how the DDL Owner schedules parallel DDL tasks and job queues.
- Retrieval Keywords: online asynchronous DDL, small version states, schema version, ADD INDEX, absent -> delete only -> write only -> write reorg -> public, DDL Owner, parallel DDL framework, same table are mutually blocked, DROP DATABASE, logical DDL, physical DDL, general job queue, add index job queue, job history queue, first-in-first-out
- Follow-up Guidance: It also provides the pre-v6.2.0 asynchronous schema change flow, including `start job`, Owner processing, KV-layer job queues, and movement to the `job history queue`.
- Classification Note: Classified as architecture because the content describes the DDL execution model, state transitions, Owner role, queueing, and concurrency framework inside TiDB.

## Official Source Content

### How the online DDL asynchronous change works in TiDB

From the beginning of its design, the TiDB DDL module has opted for an online asynchronous change mode, which lets you modify your applications without experiencing any downtime.

DDL changes involve transitioning from one state to another, typically from a "before change" state to an "after change" state. With online DDL changes, this transition occurs by introducing multiple small version states that are mutually compatible. During the execution of a DDL statement, TiDB nodes in the same cluster are allowed to have different small version changes, as long as the difference between the small versions of the change objects is not more than two versions. This is possible because adjacent small versions can be mutually compatible.

In this way, evolving through multiple small versions ensures that metadata can be correctly synchronized across multiple TiDB nodes. This helps maintain the correctness and consistency of user transactions that involve changing data during the process.

Taking `ADD INDEX` as an example, the entire process of state change is as follows:

```
absent -> delete only -> write only -> write reorg -> public
```

For users, the newly created index is unavailable before the `public` state.

<div label="Parallel DDL framework starting from v6.2.0">

Before TiDB v6.2.0, because the Owner can only execute one DDL task of the same type (either logical or physical) at a time, which is relatively strict, and affects the user experience.

If there is no dependency between DDL tasks, parallel execution does not affect data correctness and consistency. For example, user A adds an index to the `T1` table, while user B deletes a column from the `T2` table. These two DDL statements can be executed in parallel.

To improve the user experience of DDL execution, starting from v6.2.0, TiDB enables the Owner to determine the relevance of DDL tasks. The logic is as follows:

+ DDL statements to be performed on the same table are mutually blocked.
+ `DROP DATABASE` and DDL statements that affect all objects in the database are mutually blocked.
+ Adding indexes and column type changes on different tables can be executed concurrently.
+ A logical DDL statement must wait for the previous logical DDL statement to be executed before it can be executed.
+ In other cases, DDL can be executed based on the level of availability for concurrent DDL execution.

Specifically, TiDB 6.2.0 has enhanced the DDL execution framework in the following aspects:

+ The DDL Owner can execute DDL tasks in parallel based on the preceding logic.
+ The first-in-first-out issue in the DDL Job queue has been addressed. The DDL Owner no longer selects the first job in the queue, but instead selects the job that can be executed at the current time.
+ The number of workers that handle physical DDL statements has been increased, enabling multiple physical DDL statements to be executed in parallel.

    Because all DDL tasks in TiDB are implemented using an online change approach, TiDB can determine the relevance of new DDL jobs through the Owner, and schedule DDL tasks based on this information. This approach enables the distributed database to achieve the same level of DDL concurrency as traditional databases.

The concurrent DDL framework enhances the execution capability of DDL statements in TiDB, making it more compatible with the usage patterns of commercial databases.

</div>
<div label="Online DDL asynchronous change before TiDB v6.2.0">

Before v6.2.0, the process of handling asynchronous schema changes in the TiDB SQL layer is as follows:

1. MySQL Client sends a DDL request to a TiDB server.

2. After receiving the request, a TiDB server parses and optimizes the request at the MySQL Protocol layer, and then sends it to the TiDB SQL layer for execution.

    Once the SQL layer of TiDB receives the DDL request, it starts the `start job` module to encapsulate the request into a specific DDL job (that is, a DDL task), and then stores this job in the corresponding DDL job queue in the KV layer based on the statement type. The corresponding worker is notified of the job that requires processing.

3. When receiving the notification to process the job, the worker determines whether it has the role of the DDL Owner. If it does, it directly processes the job. Otherwise, it exits without any processing.

    If a TiDB server is not the Owner role, then another node must be the Owner. The worker of the node in the Owner role periodically checks whether there is an available job that can be executed. If such a job is identified, the worker will process the job.

4. After the worker processes the Job, it removes the job from the job queue in the KV layer and places it in the `job history queue`. The `start job` module that encapsulated the job periodically checks the ID of the job in the `job history queue` to see whether it has been processed. If so, the entire DDL operation corresponding to the job ends.

5. TiDB server returns the DDL processing result to the MySQL Client.

Before TiDB v6.2.0, the DDL execution framework had the following limitations:

- The TiKV cluster only has two queues: `general job queue` and `add index job queue`, which handle logical DDL and physical DDL, respectively.
- The DDL Owner always processes DDL jobs in a first-in-first-out way.
- The DDL Owner can only execute one DDL task of the same type (either logical or physical) at a time, which is relatively strict, and affects the user experience.

These limitations might lead to some "unintended" DDL blocking behavior. For more details, see [SQL FAQ - DDL Execution](https://docs.pingcap.com/tidb/stable/sql-faq#ddl-execution).

</div>
