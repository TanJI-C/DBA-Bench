# Deadlocks overview and mitigation options

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-transaction-troubleshoot.md`
- Source Title: `Handle Transaction Errors`
- Source Heading Path: `Handle Transaction Errors | Handle Transaction Errors > Deadlocks | Handle Transaction Errors > Deadlocks > Solution 1: avoid deadlocks | Handle Transaction Errors > Deadlocks > Solution 2: reduce transaction granularity | Handle Transaction Errors > Deadlocks > Solution 3: use optimistic transactions | Handle Transaction Errors > Deadlocks > Solution 4: retry`
- Source Line Ranges: `5-73`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `transactions`, `deadlocks`, `pessimistic-transactions`, `optimistic-transactions`, `retry`, `locking`, `schema-design`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0021_d6e6f64c14`
- Source ID: `tidb-docs-8.1:develop/dev-guide-transaction-troubleshoot.md#handle-transaction-errors`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `419725ff54f9cd0ea7df451f5bd84fb58dec742f3abc74a6cb224daf58c5f2f0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-troubleshoot#handle-transaction-errors
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-transaction-troubleshoot.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing `ERROR 1213: Deadlock found when trying to get lock; try restarting transaction` in TiDB transactions and looking for the documented mitigation options.
- Retrieval Keywords: ERROR 1213: Deadlock found when trying to get lock; try restarting transaction, deadlock, pessimistic transaction mode, BEGIN, UPDATE books SET stock=stock-1 WHERE id=1, UPDATE books SET stock=stock-1 WHERE id=2, UPDATE books SET stock=stock-1 WHERE id IN (1, 2), avoid deadlocks, reduce transaction granularity, use optimistic transactions, application retry and error handling
- Follow-up Guidance: The source also points to application retry and error handling for optimistic transactions and retry logic after deadlock errors.
- Classification Note: This is classified as diagnosis because the content identifies the deadlock error, explains how it occurs, and lists documented ways to mitigate it.

## Official Source Content

# Handle Transaction Errors

This document introduces how to handle transaction errors, such as deadlocks and application retry errors.
## Deadlocks

The following error in your application indicates a deadlock issue:

```sql
ERROR 1213: Deadlock found when trying to get lock; try restarting transaction
```

A deadlock occurs when two or more transactions are waiting for each other to release the lock they already hold, or the inconsistent lock order results in a loop waiting for the lock resources.

The following is an example of a deadlock using the table `books` in the [`bookshop`](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) database:

First, insert 2 rows into the table `books`:

```sql
INSERT INTO books (id, title, stock, published_at) VALUES (1, 'book-1', 10, now()), (2, 'book-2', 10, now());
```

In TiDB pessimistic transaction mode, if two clients execute the following statements respectively, a deadlock will occur:

| Client-A                                                      | Client-B                                                            |
| --------------------------------------------------------------| --------------------------------------------------------------------|
| BEGIN;                                                        |                                                                     |
|                                                               | BEGIN;                                                              |
| UPDATE books SET stock=stock-1 WHERE id=1;                    |                                                                     |
|                                                               | UPDATE books SET stock=stock-1 WHERE id=2;                          |
| UPDATE books SET stock=stock-1 WHERE id=2; -- execution will be blocked |                                                                     |
|                                                               | UPDATE books SET stock=stock-1 WHERE id=1; -- a deadlock error occurs |

After client-B encounters a deadlock error, TiDB automatically rolls back the transaction in client-B. Updating `id=2` in client-A will be executed successfully. You can then run `COMMIT` to finish the transaction.
### Solution 1: avoid deadlocks

To get better performance, you can avoid deadlocks at the application level by adjusting the business logic or schema design. In the example above, if client-B also uses the same update order as client-A, that is, they update books with `id=1` first, and then update books with `id=2`. The deadlock can then be avoided:

| Client-A                                                    | Client-B                                                         |
| ---------------------------------------------------------- | ----------------------------------------------------------------|
| BEGIN;                                                     |                                                                 |
|                                                            | BEGIN;                                                          |
| UPDATE books SET stock=stock-1 WHERE id=1;                 |                                                                 |
|                                                            | UPDATE books SET stock=stock-1 WHERE id=1;  -- will be blocked  |
| UPDATE books SET stock=stock-1 WHERE id=2;                 |                                                                 |
| COMMIT;                                                    |                                                                 |
|                                                            | UPDATE books SET stock=stock-1 WHERE id=2;                      |
|                                                            | COMMIT;                                                         |

Alternatively, you can update 2 books with 1 SQL statement, which can also avoid the deadlock and execute more efficiently:

```sql
UPDATE books SET stock=stock-1 WHERE id IN (1, 2);
```
### Solution 2: reduce transaction granularity

If you only update 1 book in each transaction, you can also avoid deadlocks. However, the trade-off is that too small transaction granularity may affect performance.
### Solution 3: use optimistic transactions

There are no deadlocks in the optimistic transaction model. But in your application, you need to add the optimistic transaction retry logic in case of failure. For details, see [Application retry and error handling](#application-retry-and-error-handling).
### Solution 4: retry

Add the retry logic in the application as suggested in the error message. For details, see [Application retry and error handling](#application-retry-and-error-handling).
