# Causal consistency behavior and examples

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/transaction-overview.md`
- Source Title: `Transactions`
- Source Heading Path: `Transactions > Causal consistency | Transactions > Causal consistency > Transactions with potential causal relationship have the consistent logical order and physical commit order | Transactions > Causal consistency > Transactions with no causal relationship do not guarantee consistent logical order and physical commit order | Transactions > Causal consistency > Reads without lock do not create causal relationship`
- Source Line Ranges: `305-373`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `causal-consistency`, `async-commit`, `one-phase-commit`, `commit-latency`, `linear-consistency`, `transaction-ordering`, `locking`, `read-without-lock`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0118_c4c027d9ee`
- Source ID: `tidb-docs-8.1:transaction-overview.md#causal-consistency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `625a2f468a507ae87fd544130711b1b5f805de5ac70068d81ec63e50f5cec1ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/transaction-overview#causal-consistency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/transaction-overview.md

## Retrieval Guidance

- Use When: Use this chunk when searching for causal consistency semantics in TiDB, the `START TRANSACTION WITH CAUSAL CONSISTENCY ONLY` syntax, or examples comparing causal consistency with linear consistency.
- Retrieval Keywords: causal consistency, START TRANSACTION WITH CAUSAL CONSISTENCY ONLY, linear consistency, async commit, one-phase commit, tidb_enable_async_commit, tidb_enable_1pc, PD timestamp, lower commit latency, potential causal relationship, physical commit order, logical order, reads without lock do not create causal relationship, FOR UPDATE, write skew
- Follow-up Guidance: The content states that transactions with causal consistency take effect only when the async commit and one-phase commit features are enabled.
- Classification Note: This is classified as architecture because it explains the transaction ordering model, consistency guarantees, and causal relationship behavior between TiDB transactions and PD timestamp acquisition.

## Official Source Content

## Causal consistency

> **Note:**
>
> Transactions with causal consistency take effect only when the async commit and one-phase commit features are enabled. For details of the two features, see [`tidb_enable_async_commit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_async_commit-new-in-v50) and [`tidb_enable_1pc`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_1pc-new-in-v50).

TiDB supports enabling causal consistency for transactions. Transactions with causal consistency, when committed, do not need to get timestamp from PD and have lower commit latency. The syntax to enable causal consistency is as follows:

```sql
START TRANSACTION WITH CAUSAL CONSISTENCY ONLY;
```

By default, TiDB guarantees linear consistency. In the case of linear consistency, if transaction 2 is committed after transaction 1 is committed, logically, transaction 2 should occur after transaction 1. Causal consistency is weaker than linear consistency. In the case of causal consistency, the commit order and occurrence order of two transactions can be guaranteed consistent only when the data locked or written by transaction 1 and transaction 2 have an intersection, which means that the two transactions have a causal relationship known to the database. Currently, TiDB does not support passing in external causal relationship.

Two transactions with causal consistency enabled have the following characteristics:

+ [Transactions with potential causal relationship have the consistent logical order and physical commit order](#transactions-with-potential-causal-relationship-have-the-consistent-logical-order-and-physical-commit-order)
+ [Transactions with no causal relationship do not guarantee consistent logical order and physical commit order](#transactions-with-no-causal-relationship-do-not-guarantee-consistent-logical-order-and-physical-commit-order)
+ [Reads without lock do not create causal relationship](#reads-without-lock-do-not-create-causal-relationship)
### Transactions with potential causal relationship have the consistent logical order and physical commit order

Assume that both transaction 1 and transaction 2 adopt causal consistency and have the following statements executed:

| Transaction 1 | Transaction 2 |
|-------|-------|
| START TRANSACTION WITH CAUSAL CONSISTENCY ONLY | START TRANSACTION WITH CAUSAL CONSISTENCY ONLY |
| x = SELECT v FROM t WHERE id = 1 FOR UPDATE | |
| UPDATE t set v = $(x + 1) WHERE id = 2 | |
| COMMIT | |
| | UPDATE t SET v = 2 WHERE id = 1 |
| | COMMIT |

In the example above, transaction 1 locks the `id = 1` record and transaction 2 modifies the `id = 1` record. Therefore, transaction 1 and transaction 2 have a potential causal relationship. Even with the causal consistency enabled, as long as transaction 2 is committed after transaction 1 is successfully committed, logically, transaction 2 must occur after transaction 1. Therefore, it is impossible that a transaction reads transaction 2's modification on the `id = 1` record without reading transaction 1's modification on the `id = 2` record.
### Transactions with no causal relationship do not guarantee consistent logical order and physical commit order

Assume that the initial values of `id = 1` and `id = 2` are both `0`. Assume that both transaction 1 and transaction 2 adopt causal consistency and have the following statements executed:

| Transaction 1 | Transaction 2 | Transaction 3 |
|-------|-------|-------|
| START TRANSACTION WITH CAUSAL CONSISTENCY ONLY | START TRANSACTION WITH CAUSAL CONSISTENCY ONLY | |
| UPDATE t set v = 3 WHERE id = 2 | | |
| | UPDATE t SET v = 2 WHERE id = 1 | |
| | | BEGIN |
| COMMIT | | |
| | COMMIT | |
| | | SELECT v FROM t WHERE id IN (1, 2) |

In the example above, transaction 1 does not read the `id = 1` record, so transaction 1 and transaction 2 have no causal relationship known to the database. With causal consistency enabled for the transactions, even if transaction 2 is committed after transaction 1 is committed in terms of physical time order, TiDB does not guarantee that transaction 2 logically occurs after transaction 1.

If transaction 3 begins before transaction 1 is committed, and if transaction 3 reads the `id = 1` and `id = 2` records after transaction 2 is committed, transaction 3 might read the value of `id = 1` to be `2` but the value of `id = 2` to be `0`.
### Reads without lock do not create causal relationship

Assume that both transaction 1 and transaction 2 adopt causal consistency and have the following statements executed:

| Transaction 1 | Transaction 2 |
|-------|-------|
| START TRANSACTION WITH CAUSAL CONSISTENCY ONLY | START TRANSACTION WITH CAUSAL CONSISTENCY ONLY |
| | UPDATE t SET v = 2 WHERE id = 1 |
| SELECT v FROM t WHERE id = 1 | |
| UPDATE t set v = 3 WHERE id = 2 | |
| | COMMIT |
| COMMIT | |

In the example above, reads without lock do not create causal relationship. Transaction 1 and transaction 2 have created write skew. In this case, it would have been unreasonable if the two transactions still had causal relationship. Therefore, the two transactions with causal consistency enabled have no definite logical order.
