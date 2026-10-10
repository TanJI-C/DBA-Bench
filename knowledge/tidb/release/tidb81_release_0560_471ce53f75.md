# SQL feature: transactional LOAD DATA behavior

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.6.0.md`
- Source Title: `TiDB 7.6.0 Release Notes`
- Source Heading Path: `TiDB 7.6.0 Release Notes > Feature details > SQL`
- Source Line Ranges: `161-170`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `load data`, `transactions`, `rollback`, `mysql compatibility`, `dml`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0560_471ce53f75`
- Source ID: `tidb-docs-8.1:releases/release-7.6.0.md#sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a6a25df2e5a9c645f2e8985f1a3960e25b4cee5cf9739c0d2a2637a793f72987`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.6.0#sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when answering how `LOAD DATA` transaction behavior changed in TiDB v7.6.0, especially for explicit transactions, rollbacks, MySQL compatibility, or the effect of transaction mode.
- Retrieval Keywords: LOAD DATA, explicit transactions, rollbacks, transactional behavior, MySQL, tidb_dml_batch_size, optimistic transaction, pessimistic transaction, commits all rows in one transaction
- Follow-up Guidance: The source also points to the `LOAD DATA` statement documentation for more information.
- Classification Note: This is a release-note SQL feature describing new `LOAD DATA` transactional semantics in TiDB v7.6.0.

## Official Source Content

### SQL

* `LOAD DATA` supports explicit transactions and rollbacks [#49079](https://github.com/pingcap/tidb/pull/49079) @[ekexium](https://github.com/ekexium)

    Compared with MySQL, the transactional behavior of the `LOAD DATA` statement varies in different TiDB versions before v7.6.0, so you might need to make additional adjustments when using this statement. Specifically, before v4.0.0, `LOAD DATA` commits every 20000 rows. From v4.0.0 to v6.6.0, TiDB commits all rows in one transaction by default and also supports committing every fixed number of rows by setting the [`tidb_dml_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_batch_size) system variable. Starting from v7.0.0, `tidb_dml_batch_size` no longer takes effect on `LOAD DATA` and TiDB commits all rows in one transaction.

    Starting from v7.6.0, TiDB processes `LOAD DATA` in transactions in the same way as other DML statements, especially in the same way as MySQL. The `LOAD DATA` statement in a transaction no longer automatically commits the current transaction or starts a new transaction. Moreover, you can explicitly commit or roll back the `LOAD DATA` statement in a transaction. Additionally, the `LOAD DATA` statement is affected by the TiDB transaction mode setting (optimistic or pessimistic transaction). These improvements simplify the migration process from MySQL to TiDB and offer a more unified and controllable experience for data import.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).
