# New SQL, transaction, collation, and log redaction features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > New features > SQL > `EXCEPT` and `INTERSECT` operators | What's New in TiDB 5.0 > New features > Transaction | What's New in TiDB 5.0 > New features > Character set and collation | What's New in TiDB 5.0 > New features > Security`
- Source Line Ranges: `105-150`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `tiflash`, `sql`
- Topic Tags: `sql operators`, `transactions`, `schema version`, `collation`, `security`, `log redaction`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0202_77952eaa85`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#except-and-intersect-operators`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a0a4c14eb153442a69efb60705ab9b2f47d668b8abbff275d34b05bfbddaab27`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#except-and-intersect-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 5.0 additions around `INTERSECT` and `EXCEPT`, pessimistic transaction `SCHEMA VERSION` amendment behavior, new collations, or log redaction settings across TiDB, TiKV, PD, and TiFlash.
- Retrieval Keywords: `INTERSECT` operator, `EXCEPT` operator, set operators, pessimistic transaction mode, `SCHEMA VERSION`, `Information schema is changed`, `tidb_enable_amend_pessimistic_txn`, TiDB Binlog, `Change Column`, `utf8mb4_unicode_ci`, `utf8_unicode_ci`, case-insensitive comparison sort, log redaction, `tidb_redact_log`, `security.redact-info-log`, `security.redact_info_log`, GDPR
- Follow-up Guidance: The content also lists fixed and remaining incompatibility issues for `tidb_enable_amend_pessimistic_txn` and names the exact variables and configuration items required to enable log desensitization.
- Classification Note: This is classified as a TiDB release chunk because it summarizes new SQL, transaction, collation, and security features introduced in the TiDB 5.0 release notes.

## Official Source Content

#### `EXCEPT` and `INTERSECT` operators

[User document](https://docs.pingcap.com/tidb/stable/functions-and-operators/set-operators), [#18031](https://github.com/pingcap/tidb/issues/18031)

The `INTERSECT` operator is a set operator, which returns the intersection of the result sets of two or more queries. To some extent, it is an alternative to the `Inner Join` operator.

The `EXCEPT` operator is a set operator, which combines the result sets of two queries and returns elements that are in the first query result but not in the second.
### Transaction

[#18005](https://github.com/pingcap/tidb/issues/18005)

In the pessimistic transaction mode, if the tables involved in a transaction contain concurrent DDL operations or `SCHEMA VERSION` changes, the system automatically updates the transaction's `SCHEMA VERSION` to the latest to ensure the successful transaction commit, and to avoid that the client receives the `Information schema is changed` error when the transaction is interrupted by DDL operations or `SCHEMA VERSION` changes.

This feature is disabled by default. To enable the feature, modify the value of `tidb_enable_amend_pessimistic_txn` system variable. This feature is introduced in v4.0.7 and has the following issues fixed in v5.0:

+ The compatibility issue that occurs when TiDB Binlog executes `Add Column` operations
+ The data inconsistency issue that occurs when using the feature together with the unique index
+ The data inconsistency issue that occurs when using the feature together with the added index

Currently, this feature still has the following incompatibility issues:

+ Transaction's semantics might change when there are concurrent transactions
+ Known compatibility issue that occurs when using the feature together with TiDB Binlog
+ Incompatibility with `Change Column`
### Character set and collation

- Support the `utf8mb4_unicode_ci` and `utf8_unicode_ci` collations. [User document](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations), [#17596](https://github.com/pingcap/tidb/issues/17596)
- Support the case-insensitive comparison sort for collations
### Security

[User document](https://docs.pingcap.com/tidb/stable/log-redaction), [#18566](https://github.com/pingcap/tidb/issues/18566)

To meet security compliance requirements (such as *General Data Protection Regulation*, or GDPR), the system supports desensitizing information (such as ID and credit card number) in the output error messages and logs, which can avoid leaking sensitive information.

TiDB supports desensitizing the output log information. To enable this feature, use the following switches:

+ The global variable [`tidb_redact_log`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_redact_log). Its default value is `0`, which means that desensitization is disabled. To enable desensitization for tidb-server logs, set the variable value to `1`.
+ The configuration item `security.redact-info-log`. Its default value is `false`, which means that desensitization is disabled. To enable desensitization for tikv-server logs, set the variable value to `true`.
+ The configuration item `security.redact-info-log`. Its default value is `false`, which means that desensitization is disabled. To enable desensitization for pd-server logs, set the variable value to `true`.
+ The configuration item `security.redact_info_log` for tiflash-server and `security.redact-info-log` for tiflash-learner. Their default values are both `false`, which means that desensitization is disabled. To enable desensitization for tiflash-server and tiflash-learner logs, set the values of both variables to `true`.

This feature is introduced in v5.0. To use the feature, enable the system variable and all configuration items above.
