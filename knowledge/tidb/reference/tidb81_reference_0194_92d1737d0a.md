# Transaction isolation levels and phantom reads

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-transaction-restraints.md`
- Source Title: `Transaction Restraints`
- Source Heading Path: `Transaction Restraints | Transaction Restraints > Isolation levels | Transaction Restraints > Snapshot Isolation can avoid phantom reads`
- Source Line Ranges: `5-25`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `transactions`, `isolation-levels`, `snapshot-isolation`, `read-committed`, `repeatable-read`, `phantom-reads`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0194_92d1737d0a`
- Source ID: `tidb-docs-8.1:develop/dev-guide-transaction-restraints.md#transaction-restraints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f913ae3a678f6d71f8b5efdae45d2de96f910c6dbd82c1efbf41ef3c0e8d4790`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-restraints#transaction-restraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-transaction-restraints.md

## Retrieval Guidance

- Use When: Use this chunk when asking which isolation levels TiDB supports or whether Snapshot Isolation avoids phantom reads.
- Retrieval Keywords: RC (Read Committed), SI (Snapshot Isolation), RR (Repeatable Read), phantom reads, Snapshot Isolation can avoid phantom reads, TiDB isolation levels
- Follow-up Guidance: The source also includes two examples that illustrate what phantom reads are in repeated query and concurrent insert/update situations.
- Classification Note: This is a reference chunk because it states the supported isolation levels in TiDB and defines phantom reads with examples.

## Official Source Content

# Transaction Restraints

This document briefly introduces the transaction restraints in TiDB.
## Isolation levels

The isolation levels supported by TiDB are **RC (Read Committed)** and **SI (Snapshot Isolation)**, where **SI** is basically equivalent to the **RR (Repeatable Read)** isolation level.

![isolation level](/media/develop/transaction_isolation_level.png)
## Snapshot Isolation can avoid phantom reads

The `SI` isolation level of TiDB can avoid **Phantom Reads**, but the `RR` in ANSI/ISO SQL standard cannot.

The following two examples show what **phantom reads** is.

- Example 1: **Transaction A** first gets `n` rows according to the query, and then **Transaction B** changes `m` rows other than these `n` rows or adds `m` rows that match the query of **Transaction A**. When **Transaction A** runs the query again, it finds that there are `n+m` rows that match the condition. It is like a phantom, so it is called a **phantom read**.

- Example 2: **Admin A** changes the grades of all students in the database from specific scores to ABCDE grades, but **Admin B** inserts a record with a specific score at this time. When **Admin A** finishes changing and finds that there is still a record (the one inserted by **Admin B**) that has not been changed yet. That is a **phantom read**.
