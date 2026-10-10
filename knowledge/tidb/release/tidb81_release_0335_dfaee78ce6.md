# Security and observability new features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > New features > Security | TiDB 6.3.0 Release Notes > New features > Observability`
- Source Line Ranges: `58-85`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `dashboard`
- Topic Tags: `release-notes`, `security`, `encryption-at-rest`, `sm3`, `sm4`, `authentication`, `metrics`, `slow-log`, `trace`, `deadlock-history`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0335_dfaee78ce6`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#security`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f7c5be1f8a98f41f431209141693ab8b421bb95ec029fc78e2b3a03269fbef4a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 6.3.0 release notes for new security capabilities such as SM3 or SM4, or for observability additions including latency breakdown, slow logs, TRACE, and deadlock history.
- Retrieval Keywords: TiDB 6.3.0-DMR, SM4 algorithm, encryption at rest, data-encryption-method, sm4-ctr, SM3 algorithm, tidb_sm3_password, authentication plugin, TiDB JDBC, TiDB-JDBC, fine-grained metrics of SQL query execution time, latency breakdown, slow logs, TRACE statements, full-link duration, RocksDB writing to disk, TiDB Dashboard, deadlock history
- Follow-up Guidance: The chunk states that `data-encryption-method` can be set to `sm4-ctr`, that `tidb_sm3_password` encrypts and validates passwords with SM3, and that TiDB Dashboard deadlock history helps when lock waiting time in slow logs is excessively long.
- Classification Note: This is a shared release-notes chunk because it combines security and observability features across TiDB, TiKV, and TiDB Dashboard in 6.3.0.

## Official Source Content

### Security

* TiKV supports the SM4 algorithm for encryption at rest [#13041](https://github.com/tikv/tikv/issues/13041) @[jiayang-zheng](https://github.com/jiayang-zheng)

    Add the [SM4 algorithm](https://docs.pingcap.com/tidb/stable/encryption-at-rest) for TiKV encryption at rest. When you configure encryption at rest, you can enable the SM4 encryption capacity by setting the value of the `data-encryption-method` configuration to `sm4-ctr`.

* TiDB supports authentication with the SM3 algorithm [#36192](https://github.com/pingcap/tidb/issues/36192) @[CbcWestwolf](https://github.com/CbcWestwolf)

    TiDB adds an authentication plugin [`tidb_sm3_password`](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql) based on the SM3 algorithm. When this plugin is enabled, the user password is encrypted and validated using the SM3 algorithm.

* TiDB JDBC supports authentication with the SM3 algorithm [#25](https://github.com/pingcap/mysql-connector-j/issues/25) @[lastincisor](https://github.com/lastincisor)

    Authenticating the user password needs client-side support. Now because [JDBC supports the SM3 algorithm](https://docs.pingcap.com/tidb/stable/develop/dev-guide-choose-driver-or-orm#java-drivers), you can connect to TiDB using SM3 authentication via TiDB-JDBC.
### Observability

* TiDB provides fine-grained metrics of SQL query execution time [#34106](https://github.com/pingcap/tidb/issues/34106) @[cfzjywxk](https://github.com/cfzjywxk)

    TiDB v6.3.0 provides fine-grained data metrics for [detailed observation of execution time](https://docs.pingcap.com/tidb/stable/latency-breakdown). Through the complete and segmented metrics, you can clearly understand the main time consumption of SQL queries, and then quickly find key problems and save time in troubleshooting.

* Enhanced output for slow logs and `TRACE` statements [#34106](https://github.com/pingcap/tidb/issues/34106) @[cfzjywxk](https://github.com/cfzjywxk)

    TiDB v6.3.0 enhances the output of slow logs and `TRACE`. You can observe the [full-link duration](https://docs.pingcap.com/tidb/stable/latency-breakdown) of SQL queries from TiDB parsing to KV RocksDB writing to disk, which further enhances the diagnostic capabilities.

* TiDB Dashboard provides deadlock history information [#34106](https://github.com/pingcap/tidb/issues/34106) @[cfzjywxk](https://github.com/cfzjywxk)

    From v6.3.0, TiDB Dashboard provides deadlock history. If you check the slow log in TiDB Dashboard and find the lock waiting time of some SQL statements to be excessively long, you can check the deadlock history to locate the root cause, which makes your diagnosis easier.
