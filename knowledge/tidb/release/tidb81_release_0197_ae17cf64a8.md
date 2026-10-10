# Release overview, SQL, transactions, collation, and security updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes | TiDB 5.0 RC Release Notes > SQL | TiDB 5.0 RC Release Notes > SQL > Support clustered index (experimental) | TiDB 5.0 RC Release Notes > SQL > Support invisible indexes | TiDB 5.0 RC Release Notes > SQL > Support `EXCEPT` and `INTERSECT` operators | TiDB 5.0 RC Release Notes > Transaction | TiDB 5.0 RC Release Notes > Transaction > Increase the success rate of executing pessimistic transactions | TiDB 5.0 RC Release Notes > Character set and collation | TiDB 5.0 RC Release Notes > Security | TiDB 5.0 RC Release Notes > Security > Support desensitizing error messages and log files`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `sql`
- Topic Tags: `release-notes`, `clustered-index`, `invisible-index`, `set-operators`, `pessimistic-transactions`, `collation`, `log-redaction`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0197_ae17cf64a8`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#tidb-5-0-rc-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cf3f8de4114b6c599fd647c794df32558825eb9ef91cc50dd2da369ab1ec737d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#tidb-5-0-rc-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.0.0-rc release-note details about clustered index, invisible indexes, `EXCEPT` and `INTERSECT`, pessimistic transaction `SCHEMA VERSION` handling, case-insensitive collation, or log and error-message redaction settings.
- Retrieval Keywords: TiDB 5.0.0-rc, clustered index, tidb_enable_clustered_index, select tidb_pk_type from information_schema.tables, information_schema.tables, tidb_pk_type, invisible indexes, ALTER INDEX, Visible, Invisible, EXCEPT, INTERSECT, set operators, pessimistic transactions, SCHEMA VERSION, Information schema is changed, case-insensitive comparison sort, character set and collation, desensitizing error messages and log files, log redaction, tidb_redact_log, security.redact-info-log, security.redact_info_log, tidb-server, tikv-server, pd-server, tiflash-server, tiflash-learner
- Follow-up Guidance: The chunk also includes the exact variables and configurations for enabling clustered index and redaction in TiDB, TiKV, PD, TiFlash, and tiflash-learner.
- Classification Note: This is classified as a release chunk because the official content is a TiDB 5.0 RC release-note summary of SQL, transaction, collation, and security feature updates.

## Official Source Content

# TiDB 5.0 RC Release Notes

Release date: January 12, 2021

TiDB version: 5.0.0-rc

TiDB v5.0.0-rc is the predecessor version of TiDB v5.0. In v5.0, PingCAP will be dedicated to helping enterprises quickly build applications based on TiDB, freeing them from worries about database performance, performance jitter, security, high availability, disaster recovery, troubleshooting SQL performance, and so on.

In v5.0, the key new features or improvements are as follows:

+ Clustered index. When this feature is enabled, database performance is improved. For example, in the TPC-C tpmC test, TiDB's performance, with clustered index enabled, improves by 39%.
+ Async commit. When this feature is enabled, the write latency is reduced. For example, in the Sysbench olpt-insert test, the write latency of TiDB, with async commit enabled, is reduced by 37.3%.
+ Reduced jitters. This is achieved by improving the optimizer stability and by limiting system tasks' usages of I/O, network, CPU, and memory resources. For example, in the 72-hour performance test, the standard deviation of Sysbench TPS jitter is reduced from 11.09% to 3.36%.
+ Raft Joint Consensus algorithm, which ensures the system availability during the Region membership change.
+ Optimized `EXPLAIN` features and invisible index, which helps Database Administrators (DBAs) debug SQL statements more efficiently.
+ Guaranteed reliability for enterprise data. You can back up data from TiDB to AWS S3 storage and Google Cloud GCS, or restore data from these cloud storage platforms.
+ Improved performance of data import from or data export to AWS S3 storage or TiDB/MySQL, which helps enterprises quickly build applications on the cloud. For example, in the TPC-C test, the performance of importing 1 TiB data improves by 40%, from 254 GiB/h to 366 GiB/h.
## SQL
### Support clustered index (experimental)

When the clustered index feature is enabled, TiDB performance improves significantly (for example in the TPC-C tpmC test, TiDB's performance, with clustered index enabled, improves by 39%) in the following cases:

+ When data is inserted, the clustered index reduces one write of the index data from the network.
+ When a query with an equivalent condition only involves the primary key, the clustered index reduces one read of index data from the network.
+ When a query with a range condition only involves the primary key, the clustered index reduces multiple reads of index data from the network.
+ When a query with an equivalent or range condition involves the primary key prefix, the clustered index reduces multiple reads of index data from the network.

Clustered index defines the physical storage order of data in a table. The data in the table is sorted only according to the definition of the clustered index. Each table has only one clustered index.

Users can enable the clustered index feature by modifying the `tidb_enable_clustered_index` variable. When enabled, the feature takes effect only on newly created tables and applies to the primary key that has multiple columns or is non-integer types in a single column. If the primary key is an integer type in a single column, or if the table has no primary key, the data is sorted in the same way as before, without being affected by the clustered index.

For example, to check whether a table (`tbl_name`) has a clustered index, execute `select tidb_pk_type from information_schema.tables where table_name = '{tbl_name}'`.

+ [User document](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_clustered_index-new-in-v50)
+ Related issue: [#4841](https://github.com/pingcap/tidb/issues/4841)
### Support invisible indexes

When users tune performance or select optimal indexes, they can set an index to be `Visible` or `Invisible` by using SQL statements. This setting can avoid performing resource-consuming operations, such as `DROP INDEX` and `ADD INDEX`.

To modify the visibility of an index, use the `ALTER INDEX` statement. After the modification, the optimizer decides whether to add this index to the index list based on the index visibility.

+ [User document](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index)
+ Related issue: [#9246](https://github.com/pingcap/tidb/issues/9246)
### Support `EXCEPT` and `INTERSECT` operators

The `INTERSECT` operator is a set operator, which returns the intersection of the result sets of two or more queries. To some extent, it is an alternative to the `InnerJoin` operator.

The `EXCEPT` operator is a set operator, which combines the result sets of two queries and returns elements that are in the first query result but not in the second.

+ [User document](https://docs.pingcap.com/tidb/stable/functions-and-operators/set-operators)
+ Related issue: [#18031](https://github.com/pingcap/tidb/issues/18031)
## Transaction
### Increase the success rate of executing pessimistic transactions

In the pessimistic transaction mode, if the tables involved in a transaction contain concurrent DDL operations or `SCHEMA VERSION` changes, the system automatically updates the transaction's `SCHEMA VERSION` to the latest to avoid the transaction being interrupted by DDL operations and to ensure the successful transaction commit. If the transaction is interrupted, the client receives the `Information schema is changed` error message.

+ Related issue: [#18005](https://github.com/pingcap/tidb/issues/18005)
## Character set and collation

Support case-insensitive comparison sort for character sets.

+ [User document](https://docs.pingcap.com/tidb/stable/character-set-and-collation#new-framework-for-collations)
+ Related issue: [#17596](https://github.com/pingcap/tidb/issues/17596)
## Security
### Support desensitizing error messages and log files

TiDB now supports desensitizing error messages and log files to avoid leaking sensitive information such as ID information and credit card number.

Users can enable the desensitization feature for different components:

+ For the TiDB side, set the `tidb_redact_log=1` variable using SQL statements in tidb-server.
+ For the TiKV side, set the `security.redact-info-log = true` configuration in tikv-server.
+ For the PD side, set the `security.redact-info-log = true` configuration in pd-server. [#2852](https://github.com/tikv/pd/issues/2852) [#3011](https://github.com/tikv/pd/pull/3011)
+ For the TiFlash side, set the `security.redact_info_log = true` configuration in tiflash-server and set `security.redact-info-log = true` in tiflash-learner.

[User document](https://docs.pingcap.com/tidb/stable/log-redaction)

Related issue: [#18566](https://github.com/pingcap/tidb/issues/18566)
