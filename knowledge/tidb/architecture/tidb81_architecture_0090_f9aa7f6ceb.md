# TiDB Cloud transaction models, isolation, and non-transactional DML

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/transaction-concepts.md`
- Source Title: `Transactions`
- Source Heading Path: `Transactions | Transactions > Optimistic transaction mode | Transactions > Pessimistic transaction mode | Transactions > Transaction isolation levels | Transactions > Non-transactional DML statements`
- Source Line Ranges: `5-40`
- Source Scope: `cloud`
- Primary Component: `tidb`
- Related Components: `cloud`, `sql`
- Topic Tags: `transactions`, `optimistic-transactions`, `pessimistic-transactions`, `locking`, `conflict-retry`, `isolation-levels`, `snapshot-isolation`, `repeatable-read`, `acid`, `non-transactional-dml`, `batch-processing`, `dry-run`, `transaction-size-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0090_f9aa7f6ceb`
- Source ID: `tidb-docs-8.1:tidb-cloud/transaction-concepts.md#transactions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6ecfd1fb7ec3e03c998a98f4aed1d6cc360950ff2ef7fd80aaff97b77a5a4c71`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/transaction-concepts#transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/transaction-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about TiDB Cloud transaction models, conflict behavior and retries, `SELECT FOR UPDATE`, transaction isolation semantics, or non-transactional DML for batch processing and transaction size limits.
- Retrieval Keywords: optimistic transaction mode, pessimistic transaction mode, SELECT FOR UPDATE, transaction isolation levels, Snapshot Isolation, SI, REPEATABLE-READ, ACID, non-transactional DML statements, batch data processing, transaction size limit, DRY RUN, distributed transactions, Google Percolator, conflicts, retry, locking
- Follow-up Guidance: The source points to related documentation for TiDB Optimistic Transaction Model, TiDB Pessimistic Transaction Mode, TiDB Transaction Isolation Levels, and Non-Transactional DML Statements.
- Classification Note: This is classified as architecture because the content explains TiDB Cloud transaction behavior and semantics, including optimistic and pessimistic models, isolation guarantees, locking, and non-transactional DML execution.

## Official Source Content

# Transactions

TiDB provides complete distributed transactions, and the model has some optimizations on the basis of [Google Percolator](https://research.google.com/pubs/pub36726.html).
## Optimistic transaction mode

TiDB's optimistic transaction model does not detect conflicts until the commit phase. If there are conflicts, the transaction needs a retry. But this model is inefficient if the conflict is severe, because operations before the retry are invalid and need to repeat.

Assume that the database is used as a counter. High access concurrency might lead to severe conflicts, resulting in multiple retries or even timeouts. Therefore, in the scenario of severe conflicts, it is recommended to use the pessimistic transaction mode or to solve problems at the system architecture level, such as placing a counter in Redis. Nonetheless, the optimistic transaction model is efficient if the access conflict is not very severe.

For more information, see [TiDB Optimistic Transaction Model](https://docs.pingcap.com/tidb/stable/optimistic-transaction).
## Pessimistic transaction mode

In TiDB, the pessimistic transaction mode has almost the same behavior as in MySQL. The transaction applies a lock during the execution phase, which avoids retries in conflict situations and ensures a higher success rate. By applying the pessimistic locking, you can also lock data in advance using `SELECT FOR UPDATE`.

However, if the application scenario has fewer conflicts, the optimistic transaction model has better performance.

For more information, see [TiDB Pessimistic Transaction Mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction).
## Transaction isolation levels

Transaction isolation is one of the foundations of database transaction processing. Isolation is one of the four key properties of a transaction (commonly referred to as [ACID](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#acid)).

TiDB implements Snapshot Isolation (SI) consistency, which it advertises as `REPEATABLE-READ` for compatibility with MySQL. This differs from the [ANSI Repeatable Read isolation level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#difference-between-tidb-and-ansi-repeatable-read) and the [MySQL Repeatable Read level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#difference-between-tidb-and-mysql-repeatable-read).

For more information, see [TiDB Transaction Isolation Levels](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels).
## Non-transactional DML statements

A non-transactional DML statement is a DML statement split into multiple SQL statements (which is, multiple batches) to be executed in sequence. It enhances the performance and ease of use in batch data processing at the expense of transactional atomicity and isolation.

Usually, memory-consuming transactions need to be split into multiple SQL statements to bypass the transaction size limit. Non-transactional DML statements integrate this process into the TiDB kernel to achieve the same effect. It is helpful to understand the effect of non-transactional DML statements by splitting SQL statements. The `DRY RUN` syntax can be used to preview the split statements.

For more information, see [Non-Transactional DML Statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml).
