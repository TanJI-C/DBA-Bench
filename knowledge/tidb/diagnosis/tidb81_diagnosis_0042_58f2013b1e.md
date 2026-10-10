# DDL errors, blocking, and stuck execution troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/sql-faq.md`
- Source Title: `SQL FAQs`
- Source Heading Path: `SQL FAQs > DDL Execution > What are the causes of the "Information schema is out of date" error? | SQL FAQs > DDL Execution > Error is reported when executing DDL statements under high concurrency? | SQL FAQs > DDL Execution > Why is DDL execution blocked? | SQL FAQs > DDL Execution > Identify the cause of stuck DDL execution`
- Source Line Ranges: `301-339`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`
- Topic Tags: `ddl`, `schema`, `information-schema`, `concurrency`, `owner-election`, `goroutine`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0042_58f2013b1e`
- Source ID: `tidb-docs-8.1:faq/sql-faq.md#what-are-the-causes-of-the-information-schema-is-out-of-date-error`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c41a8852d556d6dc38134a57f23880a079af2c689115eaa7357942a9a6dbae82`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/sql-faq#what-are-the-causes-of-the-information-schema-is-out-of-date-error
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/sql-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing `Information schema is out of date`, DDL failures under high concurrency, blocked DDL execution, or a stuck DDL that requires identifying the DDL Owner and checking goroutine stacks.
- Retrieval Keywords: Information schema is out of date, DDL lease, 45s by default, failed to load the latest schema, failed to connect to PD or TiKV, disconnected from PD due to the keepalive setting, DDL statements under high concurrency, key conflicts, keep the number of concurrent DDL statements under 20, retry the failed statements from the client, Reorg queue, General DDLs, first-in-first-out queue, concurrent framework, Reorg workers, CPU/4 per node, curl http://{TiDBIP}:10080/info/all, DDL META OPM, curl -X POST http://{TiDBIP}:10080/ddl/owner/resign, Goroutine stack
- Follow-up Guidance: The content says to identify the DDL Owner using `curl http://{TiDBIP}:10080/info/all` or the monitoring dashboard **DDL** > **DDL META OPM**, then if the owner exists export the Goroutine stack, or if the owner does not exist try `curl -X POST http://{TiDBIP}:10080/ddl/owner/resign`.
- Classification Note: This is classified as diagnosis because the content explains causes of specific DDL and schema errors and provides ways to identify blocking, owner-election, and stuck execution conditions.

## Official Source Content

### What are the causes of the "Information schema is out of date" error?

When executing a DML statement, if TiDB fails to load the latest schema within a DDL lease (45s by default), the `Information schema is out of date` error might occur. Possible causes are as follows:

- The TiDB instance that executed this DML was killed, and the transaction execution corresponding to this DML statement took longer than a DDL lease. When the transaction was committed, the error occurred.
- TiDB failed to connect to PD or TiKV while executing this DML statement. As a result, TiDB failed to load schema within a DDL lease or disconnected from PD due to the keepalive setting.
### Error is reported when executing DDL statements under high concurrency?

When you execute DDL statements (such as creating tables in batches) under high concurrency, a very few of these statements might fail because of key conflicts during the concurrent execution.

It is recommended to keep the number of concurrent DDL statements under 20. Otherwise, you need to retry the failed statements from the client.
### Why is DDL execution blocked?

Before TiDB v6.2.0, TiDB allocates DDL statements to two first-in-first-out queues based on the type of DDL statements. More specifically, Reorg DDLs go to the Reorg queue and General DDLs go to the general queue. Because of the first-in-first-out limitation and the need for serial execution of DDL statements on the same table, multiple DDL statements might be blocked during execution.

For example, consider the following DDL statements:

- DDL 1: `CREATE INDEX idx on t(a int);`
- DDL 2: `ALTER TABLE t ADD COLUMN b int;`
- DDL 3: `CREATE TABLE t1(a int);`

Due to the limitation of the first-in-first-out queue, DDL 3 must wait for DDL 2 to execute. Also, because DDL statements on the same table need to be executed in serial, DDL 2 must wait for DDL 1 to execute. Therefore, DDL 3 needs to wait for DDL 1 to be executed first, even if they operate on different tables.

Starting from TiDB v6.2.0, the TiDB DDL module uses a concurrent framework. In the concurrent framework, there is no longer the limitation of the first-in-first-out queue. Instead, TiDB picks up the DDL task that can be executed from all DDL tasks. Additionally, the number of Reorg workers has been expanded, approximately to `CPU/4` per node. This allows TiDB to build indexes for multiple tables simultaneously in the concurrent framework.

Whether your cluster is a new cluster or an upgraded cluster from an earlier version, TiDB automatically uses the concurrent framework in TiDB v6.2 and later versions. You do not need to make manual adjustments.
### Identify the cause of stuck DDL execution

1. Eliminate other reasons that make the DDL statement execution slow.
2. Use one of the following methods to identify the DDL Owner node:
    - Use `curl http://{TiDBIP}:10080/info/all` to obtain the owner of the current cluster.
    - View the owner during a specific time period from the monitoring dashboard **DDL** > **DDL META OPM**.

- If the owner does not exist, try manually triggering owner election with: `curl -X POST http://{TiDBIP}:10080/ddl/owner/resign`.
- If the owner exists, export the Goroutine stack and check for the possible stuck location.
