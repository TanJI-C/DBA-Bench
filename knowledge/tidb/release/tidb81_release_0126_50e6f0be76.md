# TiDB 3.0.7 release notes and component fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.7.md`
- Source Title: `TiDB 3.0.7 Release Notes`
- Source Heading Path: `TiDB 3.0.7 Release Notes | TiDB 3.0.7 Release Notes > TiDB | TiDB 3.0.7 Release Notes > TiKV`
- Source Line Ranges: `5-26`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `release-notes`, `bug-fixes`, `lock-ttl`, `timezone`, `query-correctness`, `precision`, `statistics`, `deadlock-detection`, `memory-leak`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0126_50e6f0be76`
- Source ID: `tidb-docs-8.1:releases/release-3.0.7.md#tidb-3-0-7-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f81ae926160f4e4229cb0c873d3048f6e4baf3757b5493ffa41018e809d034d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.7#tidb-3-0-7-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.7.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.7 release-note fixes involving lock TTL, timezone parsing, query correctness, precision conversion, statistics accuracy, TiKV deadlock detector behavior, or a potential memory leak.
- Retrieval Keywords: TiDB 3.0.7 Release Notes, TiDB version 3.0.7, TiDB Ansible version 3.0.7, lock TTL too large local time behind PD timestamp, #13868, timezone incorrect parsing date from strings using gotime.Local, #13793, binSearch builtinIntervalRealSig does not return an error, #13767, precision lost when an integer is converted to an unsigned floating point or decimal type, #13755, not null flag not properly reset USING clause Natural Outer Join Outer Join, #13739, statistics are not accurate data race when statistics are updated, #13687, TiKV deadlock detector only observe valid Regions deadlock manager valid Region, #6110, potential memory leak issue, #6128
- Follow-up Guidance: The source groups these fixes under the TiDB and TiKV sections of the TiDB 3.0.7 Release Notes dated December 4, 2019.
- Classification Note: This is a self-managed release-notes chunk for shared TiDB 3.0.7 component fixes spanning both TiDB and TiKV.

## Official Source Content

# TiDB 3.0.7 Release Notes

Release date: December 4, 2019

TiDB version: 3.0.7

TiDB Ansible version: 3.0.7
## TiDB

- Fix the issue that the lock TTL's value is too large because the TiDB server's local time is behind PD's timestamp [#13868](https://github.com/pingcap/tidb/pull/13868)
- Fix the issue that the timezone is incorrect after parsing the date from strings using `gotime.Local` [#13793](https://github.com/pingcap/tidb/pull/13793)
- Fix the issue that the result might be incorrect because the `binSearch` function does not return an error in the implementation of `builtinIntervalRealSig` [#13767](https://github.com/pingcap/tidb/pull/13767)
- Fix the issue that data is incorrect because the precision is lost when an integer is converted to an unsigned floating point or decimal type [#13755](https://github.com/pingcap/tidb/pull/13755)
- Fix the issue that the result is incorrect because the `not null` flag is not properly reset when the `USING` clause is used in Natural Outer Join and Outer Join [#13739](https://github.com/pingcap/tidb/pull/13739)
- Fix the issue that the statistics are not accurate because a data race occurs when statistics are updated [#13687](https://github.com/pingcap/tidb/pull/13687)
## TiKV

- Make the deadlock detector only observe valid Regions to make sure the deadlock manager is in a valid Region [#6110](https://github.com/tikv/tikv/pull/6110)
- Fix a potential memory leak issue [#6128](https://github.com/tikv/tikv/pull/6128)
