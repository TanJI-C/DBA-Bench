# Pessimistic transaction mode overview and switching methods

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pessimistic-transaction.md`
- Source Title: `TiDB Pessimistic Transaction Mode`
- Source Heading Path: `TiDB Pessimistic Transaction Mode | TiDB Pessimistic Transaction Mode > Switch transaction mode`
- Source Line Ranges: `5-39`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `pessimistic-transactions`, `transaction-mode`, `session-configuration`, `global-configuration`, `begin-statements`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0136_1bcc3a01e3`
- Source ID: `tidb-docs-8.1:pessimistic-transaction.md#tidb-pessimistic-transaction-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e17dbbddb53da1b14a8646545d611714249bb26484ec86e85aae5b5430b17a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pessimistic-transaction#tidb-pessimistic-transaction-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pessimistic-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to switch TiDB to pessimistic transaction mode or how BEGIN statements interact with the tidb_txn_mode setting.
- Retrieval Keywords: tidb_txn_mode, SET GLOBAL tidb_txn_mode = 'pessimistic', BEGIN PESSIMISTIC, BEGIN /*T! PESSIMISTIC */, BEGIN OPTIMISTIC, Switch transaction mode, newly created clusters default to using the pessimistic transaction mode
- Follow-up Guidance: It also states that BEGIN PESSIMISTIC and BEGIN OPTIMISTIC take precedence over the tidb_txn_mode system variable.
- Classification Note: This is classified as configuration because the content explains the tidb_txn_mode system variable and SQL statements used to select the transaction mode.

## Official Source Content

# TiDB Pessimistic Transaction Mode

To make the usage of TiDB closer to traditional databases and reduce the cost of migration, starting from v3.0, TiDB supports the pessimistic transaction mode on top of the optimistic transaction model. This document describes the features of the TiDB pessimistic transaction mode.

> **Note:**
>
> Starting from v3.0.8, newly created TiDB clusters use the pessimistic transaction mode by default. However, this does not affect your existing cluster if you upgrade it from v3.0.7 or earlier to v3.0.8 or later. In other words, **only newly created clusters default to using the pessimistic transaction mode**.
## Switch transaction mode

You can set the transaction mode by configuring the [`tidb_txn_mode`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_mode) system variable. The following command sets all explicit transactions (that is, non-autocommit transactions) executed by newly created sessions in the cluster to the pessimistic transaction mode:

```sql
SET GLOBAL tidb_txn_mode = 'pessimistic';
```

You can also explicitly enable the pessimistic transaction mode by executing the following SQL statements:

```sql
BEGIN PESSIMISTIC;
```

```sql
BEGIN /*T! PESSIMISTIC */;
```

The `BEGIN PESSIMISTIC;` and `BEGIN OPTIMISTIC;` statements take precedence over the `tidb_txn_mode` system variable. Transactions started with these two statements ignore the system variable and support using both the pessimistic and optimistic transaction modes.
