# Bulk update loops for large row sets

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-update-data.md`
- Source Title: `Update Data`
- Source Heading Path: `Update Data > Bulk-update | Update Data > Bulk-update > Write bulk-update loop`
- Source Line Ranges: `162-183`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `bulk-update`, `batching`, `iteration`, `select`, `where-clause`, `transaction-size`, `locks`, `conflicts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0077_fedc3ff7f2`
- Source ID: `tidb-docs-8.1:develop/dev-guide-update-data.md#bulk-update`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9e5ae3926fd233e62a5c7acd658f59726fb61b9070e76506153f3e64c8757c2d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-update-data#bulk-update
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-update-data.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs guidance for bulk-update loops, iterative updates for more than ten thousand rows, or why large updates should be split into portions.
- Retrieval Keywords: Bulk-update, bulk update loop, iterative updates, more than ten thousand, txn-total-size-limit, 100 MB by default, holding locks for too long, pessimistic transactions, causing conflicts, optimistic transactions, SELECT and UPDATE, primary key for the rows that need to be updated, WHERE clause to filter the rows, loop in your program or script
- Follow-up Guidance: The section says to first write a `SELECT` query in a loop and use its return value as the primary key for rows that need to be updated, with a `WHERE` clause to filter the rows.
- Classification Note: This is classified as an operation topic because the content describes an iterative bulk-update procedure and the operational reasons for batching updates.

## Official Source Content

## Bulk-update

When you need to update multiple rows of data in a table, you can [use `INSERT ON DUPLICATE KEY UPDATE`](#use-insert-on-duplicate-key-update) with the `WHERE` clause to filter the data that needs to be updated.

However, if you need to update a large number of rows (for example, more than ten thousand), it is recommended that you update the data iteratively, that is, updating only a portion of the data at each iteration until the update is complete. This is because TiDB limits the size of a single transaction ([txn-total-size-limit](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit), 100 MB by default). Too many data updates at once will result in holding locks for too long ([pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction), or causing conflicts ([optimistic transactions](https://docs.pingcap.com/tidb/stable/optimistic-transaction)). You can use a loop in your program or script to complete the operation.

However, if you need to update a large number of rows (for example, more than ten thousand), it is recommended that you update the data iteratively, that is, updating only a portion of the data at each iteration until the update is complete. This is because TiDB limits the size of a single transaction to 100 MB by default. Too many data updates at once will result in holding locks for too long ([pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction), or causing conflicts ([optimistic transactions](https://docs.pingcap.com/tidb/stable/optimistic-transaction)). You can use a loop in your program or script to complete the operation.

This section provides examples of writing scripts to handle iterative updates. This example shows how a combination of `SELECT` and `UPDATE` should be done to complete a bulk-update.
### Write bulk-update loop

First, you should write a `SELECT` query in a loop of your application or script. The return value of this query can be used as the primary key for the rows that need to be updated. Note that when defining this `SELECT` query, you need to use the `WHERE` clause to filter the rows that need to be updated.
