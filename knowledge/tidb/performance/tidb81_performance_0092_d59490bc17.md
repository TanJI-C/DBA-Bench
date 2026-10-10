# DELETE performance considerations and iterative bulk-delete guidance

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-delete-data.md`
- Source Title: `Delete Data`
- Source Heading Path: `Delete Data > Performance considerations | Delete Data > Performance considerations > TiDB GC mechanism | Delete Data > Performance considerations > Update statistical information | Delete Data > Bulk-delete | Delete Data > Bulk-delete > Write a bulk-delete loop`
- Source Line Ranges: `189-224`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `performance`, `garbage-collection`, `safe-point`, `disk-usage`, `statistics`, `optimizer`, `bulk-delete`, `transactions`, `txn-total-size-limit`, `loop`, `limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0092_d59490bc17`
- Source ID: `tidb-docs-8.1:develop/dev-guide-delete-data.md#performance-considerations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cb399710d538a4e70b9d915b5dcb2e846eb3125be56b356cb379988a9cfc117d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-delete-data#performance-considerations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-delete-data.md

## Retrieval Guidance

- Use When: Use this chunk when you need guidance on DELETE performance behavior, GC and safe_point effects on disk usage, statistics updates after large deletes, or iterative bulk-delete with LIMIT.
- Retrieval Keywords: Performance considerations, TiDB GC mechanism, Garbage Collection, safe_point, DELETE does not immediately reduce disk usage, Update statistical information, manual collection, statistics, optimizer, index selection, Bulk-delete, iterative way, txn-total-size-limit, 100 MB by default, SELECT and DELETE, Write a bulk-delete loop, LIMIT
- Follow-up Guidance: The source says you can write a DELETE statement in an application or script loop, filter with WHERE, and use LIMIT to constrain the number of rows deleted in a single statement.
- Classification Note: This is classified as performance because the content explains GC timing, disk-usage implications, statistics and optimizer effects after large deletes, and the iterative bulk-delete pattern for transaction-size limits.

## Official Source Content

## Performance considerations
### TiDB GC mechanism

TiDB does not delete the data immediately after you run the `DELETE` statement. Instead, it marks the data as ready for deletion. Then it waits for TiDB GC (Garbage Collection) to clean up the outdated data. Therefore, the `DELETE` statement **_DOES NOT_** immediately reduce disk usage.

GC is triggered once every 10 minutes by default. Each GC calculates a time point called **safe_point**. Any data earlier than this time point will not be used again, so TiDB can safely clean it up.

For more information, see [GC mechanism](https://docs.pingcap.com/tidb/stable/garbage-collection-overview).
### Update statistical information

TiDB uses [statistical information](https://docs.pingcap.com/tidb/stable/statistics) to determine index selection. There is a high risk that the index is not correctly selected after a large volume of data is deleted. You can use [manual collection](https://docs.pingcap.com/tidb/stable/statistics#manual-collection) to update the statistics. It provides the TiDB optimizer with more accurate statistical information for SQL performance optimization.
## Bulk-delete

When you need to delete multiple rows of data from a table, you can choose the [`DELETE` example](#example) and use the `WHERE` clause to filter the data that needs to be deleted.

However, if you need to delete a large number of rows (more than ten thousand), it is recommended that you delete the data in an iterative way, that is, deleting a portion of the data at each iteration until the deletion is completed. This is because TiDB limits the size of a single transaction ([`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit), 100 MB by default). You can use loops in your programs or scripts to perform such operations.

However, if you need to delete a large number of rows (more than ten thousand), it is recommended that you delete the data in an iterative way, that is, deleting a portion of the data at each iteration until the deletion is completed. This is because TiDB limits the size of a single transaction to 100 MB by default. You can use loops in your programs or scripts to perform such operations.

This section provides an example of writing a script to handle an iterative delete operation that demonstrates how you should do a combination of `SELECT` and `DELETE` to complete a bulk-delete.
### Write a bulk-delete loop

You can write a `DELETE` statement in the loop of your application or script, use the `WHERE` clause to filter data, and use `LIMIT` to constrain the number of rows to be deleted in a single statement.
