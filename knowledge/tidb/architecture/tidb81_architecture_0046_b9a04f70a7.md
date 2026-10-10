# Metadata lock principles and implementation details

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/metadata-lock.md`
- Source Title: `Metadata Lock`
- Source Heading Path: `Metadata Lock > Principles | Metadata Lock > Principles > Description of the issue | Metadata Lock > Principles > Implementation details`
- Source Line Ranges: `106-133`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `metadata-lock`, `online-ddl`, `schema-version`, `transactions`, `consistency`, `implementation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0046_b9a04f70a7`
- Source ID: `tidb-docs-8.1:metadata-lock.md#principles`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4a134f9241418cfcd46975f20055cc504d0e667e912801fd9fc3213b63697aa7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/metadata-lock#principles
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/metadata-lock.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for the principles or implementation details of metadata lock, including schema version differences during online DDL state changes.
- Retrieval Keywords: Principles, Implementation details, online DDL, online asynchronous metadata change algorithm, metadata version, minor version changes, None -> Delete Only -> Write Only -> Write Reorg -> Public, data inconsistency, transaction context, metadata objects accessed by the DML, tables, views, state change, latest version of metadata is pushed to all TiDB nodes, differ by one version at most, metadata lock of the metadata object
- Follow-up Guidance: The source explains that TiDB records accessed metadata objects and versions in each transaction context, and a DDL state change proceeds only after all TiDB nodes acquire the metadata lock for that metadata object.
- Classification Note: This is classified as architecture because the content explains the underlying consistency issue in online DDL and the cluster-wide rules TiDB uses to implement metadata lock.

## Official Source Content

## Principles
### Description of the issue

DDL operations in TiDB are the online DDL mode. When a DDL statement is being executed, the metadata version of the defined object to be modified might go through multiple minor version changes. The online asynchronous metadata change algorithm only establishes that two adjacent minor versions are compatible, that is, operations between two versions do not break data consistency of the object that DDL changes.

When adding an index to a table, the state of the DDL statement changes as follows: None -> Delete Only, Delete Only -> Write Only, Write Only -> Write Reorg, Write Reorg -> Public.

The following commit process of transactions violates the preceding constraint:

| Transaction  | Version used by transaction  | Latest version in the cluster | Version difference |
|:-----|:-----------|:-----------|:----|
| txn1 | None       | None       | 0   |
| txn2 | DeleteOnly | DeleteOnly | 0   |
| txn3 | WriteOnly  | WriteOnly  | 0   |
| txn4 | None       | WriteOnly  | 2   |
| txn5 | WriteReorg | WriteReorg | 0   |
| txn6 | WriteOnly  | WriteReorg | 1   |
| txn7 | Public     | Public     | 0   |

In the preceding table, the metadata version used when `txn4` is committed is two versions different from the latest version in the cluster. This might cause data inconsistency.
### Implementation details

Metadata lock can ensure that the metadata versions used by all transactions in a TiDB cluster differ by one version at most. To achieve this goal, TiDB implements the following two rules:

- When executing a DML, TiDB records metadata objects accessed by the DML in the transaction context, such as tables, views, and corresponding metadata versions. These records are cleaned up when the transaction is committed.
- When a DDL statement changes state, the latest version of metadata is pushed to all TiDB nodes. If the difference between the metadata version used by all transactions related to this state change on a TiDB node and the current metadata version is less than two, the TiDB node is considered to acquire the metadata lock of the metadata object. The next state change can only be executed after all TiDB nodes in the cluster have obtained the metadata lock of the metadata object.
