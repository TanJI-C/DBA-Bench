# TiDB 3.0.11 release notes: compatibility changes, new features, and bug fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.11.md`
- Source Title: `TiDB 3.0.11 Release Notes`
- Source Heading Path: `TiDB 3.0.11 Release Notes | TiDB 3.0.11 Release Notes > Compatibility Changes | TiDB 3.0.11 Release Notes > New Features | TiDB 3.0.11 Release Notes > Bug Fixes`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `lightning`
- Topic Tags: `release-notes`, `compatibility`, `new-features`, `bug-fixes`, `tidb-binlog`, `tls`, `partitioned-tables`, `transactions`, `query-results`, `ansible`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0102_ee5aeba766`
- Source ID: `tidb-docs-8.1:releases/release-3.0.11.md#tidb-3-0-11-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eaffb29909afa5ab2590559473a27a129a04e23568ea7cc8e9056f25cb6f880e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.11#tidb-3-0-11-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.11.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 3.0.11 release summary covering compatibility changes, new features, and bug fixes across TiDB, TiKV, TiDB Binlog, TiDB Lightning, and TiDB Ansible.
- Retrieval Keywords: TiDB 3.0.11 Release Notes, 3.0.11, max-index-length, information_schema.PARTITIONS, bidirectional data replication between TiDB clusters, TiDB Binlog, TiDB Lightning TLS configuration, create_users.yml, ansible_user, SHOW TABLE STATUS, tidb_snapshot, SET SESSION tidb_snapshot, Sort Merge Join, ORDER BY DESC, This partition function is not allowed, select max() from subquery, Union, SHOW BINDINGS, DROP BINDING, alias 256 characters, MySQL protocol, DIV, select 1 / '2007' div 1, Hibernate Regions, wait for region replication complete
- Follow-up Guidance: The source also states that some known issues exist in this version and that these issues are fixed in newer versions.
- Classification Note: This is a release-notes chunk for a self-managed release because the official content lists version 3.0.11 compatibility changes, new features, and bug fixes for multiple TiDB components.

## Official Source Content

# TiDB 3.0.11 Release Notes

Release date: March 4, 2020

TiDB version: 3.0.11

TiDB Ansible version: 3.0.11

> **Warning:**
>
> Some known issues are found in this version, and these issues are fixed in new versions. It is recommended that you use the latest 3.0.x version.
## Compatibility Changes

* TiDB
    + Add the `max-index-length` configuration item to control the maximum index length, which is compatible with the behavior of TiDB versions before 3.0.7 or of MySQL [#15057](https://github.com/pingcap/tidb/pull/15057)
## New Features

* TiDB
    + Support showing the meta information of partitioned tables in the `information_schema.PARTITIONS` table [#14849](https://github.com/pingcap/tidb/pull/14849)

* TiDB Binlog
    + Support the bidirectional data replication between TiDB clusters [#884](https://github.com/pingcap/tidb-binlog/pull/884) [#909](https://github.com/pingcap/tidb-binlog/pull/909)

* TiDB Lightning
    + Support the TLS configuration [#44](https://github.com/tikv/importer/pull/44) [#270](https://github.com/pingcap/tidb-lightning/pull/270)

* TiDB Ansible
    + Modify the logic of `create_users.yml` so that users of the control machine do not have to be consistent with `ansible_user` [#1184](https://github.com/pingcap/tidb-ansible/pull/1184)
## Bug Fixes

* TiDB
    + Fix the issue of Goroutine leaks when retrying an optimistic transaction because queries using `Union` are not marked read-only [#15076](https://github.com/pingcap/tidb/pull/15076)
    + Fix the issue that `SHOW TABLE STATUS` fails to correctly output the table status at the snapshot time because the value of the `tidb_snapshot` parameter is not correctly used when executing the `SET SESSION tidb_snapshot = 'xxx';` statement [#14391](https://github.com/pingcap/tidb/pull/14391)
    + Fix the incorrect result caused by a SQL statement that contains `Sort Merge Join` and `ORDER BY DESC` at the same time [#14664](https://github.com/pingcap/tidb/pull/14664)
    + Fix the panic of TiDB server when creating partition tables using the unsupported expression. The error information `This partition function is not allowed` is returned after fixing this panic. [#14769](https://github.com/pingcap/tidb/pull/14769)
    + Fix the incorrect result occurred when executing the `select max() from subquery` statement with the subquery containing `Union` [#14944](https://github.com/pingcap/tidb/pull/14944)
    + Fix the issue that an error message is returned when executing the `SHOW BINDINGS` statement after executing `DROP BINDING` that drops the execution binding [#14865](https://github.com/pingcap/tidb/pull/14865)
    + Fix the issue that the connection is broken because the maximum length of an alias in a query is 256 characters in the MySQL protocol, but TiDB does not [cut the alias](https://dev.mysql.com/doc/refman/8.0/en/identifier-length.html) in the query results according to this protocol [#14940](https://github.com/pingcap/tidb/pull/14940)
    + Fix the incorrect query result that might occur when using the string type in `DIV`. For instance, now you can correctly execute the `select 1 / '2007' div 1` statement [#14098](https://github.com/pingcap/tidb/pull/14098)

* TiKV
    + Optimize the log output by removing unnecessary logs [#6657](https://github.com/tikv/tikv/pull/6657)
    + Fix the panic that might occur when the peer is removed under high loads [#6704](https://github.com/tikv/tikv/pull/6704)
    + Fix the issue that Hibernate Regions are not waken up in some cases [#6732](https://github.com/tikv/tikv/pull/6732) [#6738](https://github.com/tikv/tikv/pull/6738)

* TiDB Ansible
    + Update outdated document links in `tidb-ansible` [#1169](https://github.com/pingcap/tidb-ansible/pull/1169)
    + Fix the issue that undefined variables might occur in the `wait for region replication complete` task [#1173](https://github.com/pingcap/tidb-ansible/pull/1173)
