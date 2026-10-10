# Bug fixes for TiCDC and TiDB Lightning, performance links, and contributors

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.1.0.md`
- Source Title: `TiDB 8.1.0 Release Notes`
- Source Heading Path: `TiDB 8.1.0 Release Notes > Bug fixes | TiDB 8.1.0 Release Notes > Performance test | TiDB 8.1.0 Release Notes > Contributors`
- Source Line Ranges: `338-371`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `lightning`, `pd`, `sql`
- Topic Tags: `bug-fixes`, `ticdc`, `changefeed`, `owner`, `grafana`, `replication`, `pulsar`, `timezone`, `ddl`, `lightning`, `data-import`, `logs`, `sensitive-information`, `performance-test`, `contributors`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0599_8deee76caf`
- Source ID: `tidb-docs-8.1:releases/release-8.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bf73d77f27ae19a3af6e5433ad53594afd34bca809948451568bdfa871871c83`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.1.0 release-note fixes for TiCDC or TiDB Lightning, or for the release's performance test links and contributor list.
- Retrieval Keywords: TiDB 8.1.0 Release Notes, Bug fixes, TiCDC, TiDB Lightning, /api/v2/owner/resign, owner resign, evicts the TiCDC owner node, downstream Pulsar is stopped, remove the changefeed causes the process to get stuck, Ownership history panel in Grafana, restarting PD might cause the TiCDC node to restart with an error, PD disk I/O causes severe latency in data replication, TIMEZONE type, DROP PRIMARY KEY, DROP UNIQUE KEY, Exchange Partition ... With Validation, changefeed to get stuck, no database selected, sensitive information to logs in server mode, invalid store ID 0, Unknown column in where clause, replace strategy, empty table of Parquet format, TPC-C performance test report, Sysbench performance test report, TiDB Cloud Dedicated cluster, Contributors
- Follow-up Guidance: The chunk also points to the TPC-C and Sysbench performance test reports and lists TiDB community contributors for the release.
- Classification Note: The official content is classified as a release-note section that combines bug fixes for TiCDC and TiDB Lightning with performance test references and contributor acknowledgments for TiDB 8.1.0.

## Official Source Content

- Fix the issue that calling the API (`/api/v2/owner/resign`) that evicts the TiCDC owner node causes the TiCDC task to restart unexpectedly [#10781](https://github.com/pingcap/tiflow/issues/10781) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that when the downstream Pulsar is stopped, removing the changefeed causes the normal TiCDC process to get stuck, which causes other changefeed processes to get stuck [#10629](https://github.com/pingcap/tiflow/issues/10629) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the **Ownership history** panel in Grafana is unstable [#10796](https://github.com/pingcap/tiflow/issues/10796) @[hongyunyan](https://github.com/hongyunyan)
        - Fix the issue that restarting PD might cause the TiCDC node to restart with an error [#10799](https://github.com/pingcap/tiflow/issues/10799) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that high latency in the PD disk I/O causes severe latency in data replication [#9054](https://github.com/pingcap/tiflow/issues/9054) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that the default value of `TIMEZONE` type is not set according to the correct time zone [#10931](https://github.com/pingcap/tiflow/issues/10931) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that `DROP PRIMARY KEY` and `DROP UNIQUE KEY` statements are not replicated correctly [#10890](https://github.com/pingcap/tiflow/issues/10890) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that TiCDC fails to execute the `Exchange Partition ... With Validation` DDL downstream after it is written upstream, causing the changefeed to get stuck [#10859](https://github.com/pingcap/tiflow/issues/10859) @[hongyunyan](https://github.com/hongyunyan)

    + TiDB Lightning

        - Fix the issue that TiDB Lightning reports `no database selected` during data import due to incompatible SQL statements in the source files [#51800](https://github.com/pingcap/tidb/issues/51800) @[lance6716](https://github.com/lance6716)
        - Fix the issue that TiDB Lightning might print sensitive information to logs in server mode [#36374](https://github.com/pingcap/tidb/issues/36374) @[kennytm](https://github.com/kennytm)
        - Fix the issue that killing the PD Leader causes TiDB Lightning to report the `invalid store ID 0` error during data import [#50501](https://github.com/pingcap/tidb/issues/50501) @[Leavrth](https://github.com/Leavrth)
        - Fix the issue that TiDB Lightning reports the `Unknown column in where clause` error when processing conflicting data using the `replace` strategy [#52886](https://github.com/pingcap/tidb/issues/52886) @[lyzx2001](https://github.com/lyzx2001)
        - Fix the issue that TiDB Lightning panics when importing an empty table of Parquet format [#52518](https://github.com/pingcap/tidb/issues/52518) @[kennytm](https://github.com/kennytm)
## Performance test

To learn about the performance of TiDB v8.1.0, you can refer to the [TPC-C performance test report](https://docs.pingcap.com/tidbcloud/v8.1-performance-benchmarking-with-tpcc) and [Sysbench performance test report](https://docs.pingcap.com/tidbcloud/v8.1-performance-benchmarking-with-sysbench) of the TiDB Cloud Dedicated cluster.
## Contributors

We would like to thank the following contributors from the TiDB community:

- [arturmelanchyk](https://github.com/arturmelanchyk) (First-time contributor)
- [CabinfeverB](https://github.com/CabinfeverB)
- [danqixu](https://github.com/danqixu) (First-time contributor)
- [imalasong](https://github.com/imalasong) (First-time contributor)
- [jiyfhust](https://github.com/jiyfhust)
- [negachov](https://github.com/negachov) (First-time contributor)
- [testwill](https://github.com/testwill)
- [yzhan1](https://github.com/yzhan1) (First-time contributor)
- [zxc111](https://github.com/zxc111) (First-time contributor)
