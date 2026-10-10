# Write batching, large delete patterns, and workload isolation

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/tidb-best-practices.md`
- Source Title: `TiDB Best Practices`
- Source Heading Path: `TiDB Best Practices > Scenarios and practices > Write | TiDB Best Practices > Scenarios and practices > Query`
- Source Line Ranges: `152-186`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`
- Topic Tags: `transactions`, `batching`, `delete`, `affected-rows`, `oltp`, `olap`, `workload-isolation`, `join-hints`, `index-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0067_be97292bc5`
- Source ID: `tidb-docs-8.1:best-practices/tidb-best-practices.md#write`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e3f794c5aab2888cb70be3fd6f41e7a1e4e85b87f7bf09f99bc7be1176ce44d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#write
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/tidb-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about batching `INSERT` or `UPDATE` or `DELETE`, transaction size guidance, large delete loops with `limit 5000` and `Affected Rows == 0`, SQL concurrency control with `SET`, join and index hints, or isolating OLTP and OLAP workloads with separate TiDB servers or TiFlash.
- Retrieval Keywords: single transaction, less than 200, less than 100 KB, split statements into batches, INSERT, UPDATE, DELETE, Delete from t where xx limit 5000;, Affected Rows == 0, affected_rows(), refine the WHERE condition, SET statement, Join operator, Use Index, Ignore Index hint, OLTP, OLAP, different TiDB servers, TiFlash, columnar storage engine, consistent reads
- Follow-up Guidance: The source also references `System Variables` for query requirements and specific statements.
- Classification Note: This is classified as performance for SQL because the content covers transaction batching, large delete patterns, query execution control, and workload isolation choices that influence performance.

## Official Source Content

### Write

As mentioned before, TiDB limits the size of a single transaction in the Key-Value layer. As for the SQL layer, a row of data is mapped to a Key-Value entry. For each additional index, one more Key-Value entry is added.

> **Note:**
>
> When you set the size limit for transactions, you need to consider the overhead of TiDB encoding and the extra transaction key. It is recommended that **the number of rows of each transaction is less than 200 and the data size of a single row is less than 100 KB**; otherwise, the performance is bad.

It is recommended to split statements into batches or add a limit to the statements, whether they are `INSERT`, `UPDATE` or `DELETE` statements.

When deleting a large amount of data, it is recommended to use `Delete from t where xx limit 5000;`. It deletes through the loop and use `Affected Rows == 0` as a condition to end the loop.

If the amount of data that needs to be deleted at a time is large, this loop method gets slower and slower because each deletion traverses backward. After deleting the previous data, lots of deleted flags remain for a short period (then all is cleared by Garbage Collection) and affect the following `DELETE` statement. If possible, it is recommended to refine the `WHERE` condition. Assume that you need to delete all data on `2017-05-26`, you can use the following statements:

```sql
for i from 0 to 23:
    while affected_rows > 0:
        delete from t where insert_time >= i:00:00 and insert_time < (i+1):00:00 limit 5000;
        affected_rows = select affected_rows()
```

This pseudocode means to split huge chunks of data into small ones and then delete, so that the earlier `Delete` statements do not affect the later ones.
### Query

For query requirements and specific statements, refer to [System Variables](https://docs.pingcap.com/tidb/stable/system-variables).

You can control the concurrency of SQL execution through the `SET` statement and the selection of the `Join` operator through hints.

In addition, you can also use MySQL's standard index selection, the hint syntax, or control the optimizer to select indexes through `Use Index`/`Ignore Index hint`.

If the application scenario has both OLTP and OLAP workloads, you can send the OLTP request and OLAP request to different TiDB servers, diminishing the impact of OLAP on OLTP. It is recommended to use machines with high-performance hardware (for example, more processor cores and larger memory) for the TiDB server that processes OLAP workloads.

To completely isolate OLTP and OLAP workloads, it is recommended to run OLAP applications on TiFlash. TiFlash is a columnar storage engine with great performance on OLAP workloads. TiFlash can achieve physical isolation on the storage layer and guarantees consistent reads.
