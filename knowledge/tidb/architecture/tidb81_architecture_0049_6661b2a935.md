# Optimistic transaction overview, 2PC principles, and tradeoffs

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimistic-transaction.md`
- Source Title: `TiDB Optimistic Transaction Model`
- Source Heading Path: `TiDB Optimistic Transaction Model | TiDB Optimistic Transaction Model > Principles of optimistic transactions | TiDB Optimistic Transaction Model > Advantages and disadvantages`
- Source Line Ranges: `5-64`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`
- Topic Tags: `optimistic-transactions`, `two-phase-commit`, `mvcc`, `start-ts`, `commit-ts`, `tradeoffs`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0049_6661b2a935`
- Source ID: `tidb-docs-8.1:optimistic-transaction.md#tidb-optimistic-transaction-model`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9fdac74d965eb5f81eb98b290cb0dbb3a825ccd13390183bf172198c3184fc0a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimistic-transaction#tidb-optimistic-transaction-model
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving an overview of TiDB optimistic transactions, including 2PC flow, `start_ts` and `commit_ts`, MVCC snapshot reads, and the stated advantages and disadvantages versus pessimistic transactions.
- Retrieval Keywords: TiDB Optimistic Transaction Model, optimistic transactions, two-phase commit, 2PC, MVCC, start_ts, commit_ts, PD timestamp, prewrite, Primary Key, Region distribution, asynchronously cleans the locks, pessimistic transactions, OOM when extensive data is written in the memory
- Follow-up Guidance: The source notes that `COMMIT` can return errors in optimistic transactions and that newly created clusters starting from v3.0.8 default to pessimistic transaction mode.
- Classification Note: This is classified as architecture because the content explains the transaction model, component roles of TiDB, PD, and TiKV, and the end-to-end 2PC commit procedure and tradeoffs.

## Official Source Content

# TiDB Optimistic Transaction Model

With optimistic transactions, conflicting changes are detected as part of a transaction commit. This helps improve the performance when concurrent transactions are infrequently modifying the same rows, because the process of acquiring row locks can be skipped. In the case that concurrent transactions frequently modify the same rows (a conflict), optimistic transactions might perform worse than [pessimistic transactions](https://docs.pingcap.com/tidb/stable/pessimistic-transaction).

Before enabling optimistic transactions, make sure that your application correctly handles that a `COMMIT` statement could return errors. If you are unsure of how your application handles this, it is recommended to instead use Pessimistic Transactions.

> **Note:**
>
> Starting from v3.0.8, TiDB uses the [pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) by default. However, this does not affect your existing cluster if you upgrade it from v3.0.7 or earlier to v3.0.8 or later. In other words, **only newly created clusters default to using the pessimistic transaction mode**.
## Principles of optimistic transactions

To support distributed transactions, TiDB adopts two-phase commit (2PC) in optimistic transactions. The procedure is as follows:

![2PC in TiDB](/media/2pc-in-tidb.png)

1. The client begins a transaction.

    TiDB gets a timestamp (monotonically increasing in time and globally unique) from PD as the unique transaction ID of the current transaction, which is called `start_ts`. TiDB implements multi-version concurrency control, so `start_ts` also serves as the version of the database snapshot obtained by this transaction. This means that the transaction can only read the data from the database at `start_ts`.

2. The client issues a read request.

    1. TiDB receives routing information (how data is distributed among TiKV nodes) from PD.
    2. TiDB receives the data of the `start_ts` version from TiKV.

3. The client issues a write request.

    TiDB checks whether the written data satisfies constraints (to ensure the data types are correct, the NOT NULL constraint is met). **Valid data is stored in the private memory of this transaction in TiDB**.

4. The client issues a commit request.

5. TiDB begins 2PC, and persists data in store while guaranteeing the atomicity of transactions.

    1. TiDB selects a Primary Key from the data to be written.
    2. TiDB receives the information of Region distribution from PD, and groups all keys by Region accordingly.
    3. TiDB sends prewrite requests to all TiKV nodes involved. Then, TiKV checks whether there are conflict or expired versions. Valid data is locked.
    4. TiDB receives all responses in the prewrite phase and the prewrite is successful.
    5. TiDB receives a commit version number from PD and marks it as `commit_ts`.
    6. TiDB initiates the second commit to the TiKV node where Primary Key is located. TiKV checks the data, and cleans the locks left in the prewrite phase.
    7. TiDB receives the message that reports the second phase is successfully finished.

6. TiDB returns a message to inform the client that the transaction is successfully committed.

7. TiDB asynchronously cleans the locks left in this transaction.
## Advantages and disadvantages

From the process of transactions in TiDB above, it is clear that TiDB transactions have the following advantages:

* Simple to understand
* Implement cross-node transaction based on single-row transaction
* Decentralized lock management

However, TiDB transactions also have the following disadvantages:

* Transaction latency due to 2PC
* In need of a centralized timestamp allocation service
* OOM (out of memory) when extensive data is written in the memory
