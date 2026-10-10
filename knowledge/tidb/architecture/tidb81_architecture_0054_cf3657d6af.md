# Pessimistic transaction commit and lock acquisition flow

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pessimistic-transaction.md`
- Source Title: `TiDB Pessimistic Transaction Mode`
- Source Heading Path: `TiDB Pessimistic Transaction Mode > Pessimistic transaction commit process`
- Source Line Ranges: `143-156`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `2pc`, `commit-process`, `lock-acquisition`, `start-ts`, `write-requests`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0054_cf3657d6af`
- Source ID: `tidb-docs-8.1:pessimistic-transaction.md#pessimistic-transaction-commit-process`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `100c1d261171a1a15a39f48ce60bd65f8b11d0fb4d8d9c7a5dce0bf6aaf3c644`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pessimistic-transaction#pessimistic-transaction-commit-process
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about the internal flow of pessimistic transaction commit, especially how lock acquisition relates to 2PC and start_ts.
- Retrieval Keywords: Pessimistic transaction commit process, two-phase commit, 2PC, Acquire Pessimistic Lock, start_ts, begin request, writing request, pessimistic lock request, TiKV server, commit request
- Follow-up Guidance: It explains that pessimistic transactions use the same 2PC commit logic as optimistic transactions, but add an Acquire Pessimistic Lock phase before 2PC.
- Classification Note: This is classified as architecture because the content describes the internal request flow and commit phases across TiDB and TiKV.

## Official Source Content

## Pessimistic transaction commit process

In the transaction commit process, pessimistic transactions and optimistic transactions have the same logic. Both transactions adopt the two-phase commit (2PC) mode. The important adaptation of pessimistic transactions is DML execution.

![TiDB pessimistic transaction commit process](/media/pessimistic-transaction-commit.png)

The pessimistic transaction adds an `Acquire Pessimistic Lock` phase before 2PC. This phase includes the following steps:

1. (Same as the optimistic transaction mode) TiDB receives the `begin` request from the client, and the current timestamp is this transaction's start_ts.
2. When the TiDB server receives a writing request from the client, the TiDB server initiates a pessimistic lock request to the TiKV server, and the lock is persisted to the TiKV server.
3. (Same as the optimistic transaction mode) When the client sends the commit request, TiDB starts to perform the two-phase commit similar to the optimistic transaction mode.

![Pessimistic transactions in TiDB](/media/pessimistic-transaction-in-tidb.png)
