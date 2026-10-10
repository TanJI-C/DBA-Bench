# TiDB 4.0 GA new features across TiDB, TiFlash, TiKV, PD, BR, and TiCDC

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0-ga.md`
- Source Title: `TiDB 4.0 GA Release Notes`
- Source Heading Path: `TiDB 4.0 GA Release Notes > New Features`
- Source Line Ranges: `31-65`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `tikv`, `pd`, `br`, `ticdc`, `dashboard`
- Topic Tags: `release-notes`, `new-features`, `configuration`, `sql`, `partitioning`, `collation`, `dashboard`, `monitoring`, `backup`, `restore`, `changefeed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0141_2ab0b10dfd`
- Source ID: `tidb-docs-8.1:releases/release-4.0-ga.md#new-features`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0dc7b2e2966b895b08e28f1b79428251f18ba4a1d0f6a3fb51e536cf81068609`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0-ga#new-features
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0-ga.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 4.0 GA new features such as `committer-concurrency`, `tmp-storage-quota`, `show table partition regions`, partition-related SQL support, TiFlash log search and TIMESTAMP handling, PD Dashboard proxy prefix and hotspot monitoring items, BR support for `Sequence` and `View`, or TiCDC Changefeed and Sink URI validation features.
- Retrieval Keywords: TiDB 4.0 GA, New Features, committer-concurrency, tmp-storage-quota, show table partition regions, insert/replace into tbl_name partition, partition_name_list, admin check index, admin cleanup index, admin recover index, Hash partition pruning, range partition pruning, Distinct, collations, TiFlash, min commit ts, Lock CF, TIMESTAMP, 1970-01-01 00:00:00, regular expressions, TiKV, ascii_bin, latin1_bin, PD, TiDB Dashboard, reverse proxy resource prefix, pending peer, down peer, Direction of hotspot move leader, Direction of hotspot move peer, Hot cache read entry number, BR, Sequence, View, TiCDC, Sink URI, Changefeed, PD and TiKV versions, node roles, HTTP API
- Follow-up Guidance: This chunk also includes PD client Region interface additions for `pending peer` and `down peer` information and TiCDC HTTP API node role information.
- Classification Note: The official content is classified as release-note new features spanning TiDB, TiFlash, TiKV, PD, BR, and TiCDC in TiDB 4.0 GA.

## Official Source Content

## New Features

* TiDB
    - Add the `committer-concurrency` configuration item to control the number of `goroutines` in the retry-commit phase [#16849](https://github.com/pingcap/tidb/pull/16849)
    - Support the `show table partition regions` syntax [#17294](https://github.com/pingcap/tidb/pull/17294)
    - Add the `tmp-storage-quota` configuration item to limit the temporary disk space used by the TiDB server [#15700](https://github.com/pingcap/tidb/pull/15700)
    - Support checking whether the partitioned table uses a unique prefix index when creating and changing tables [#17213](https://github.com/pingcap/tidb/pull/17213)
    - Support the `insert/replace into tbl_name partition`(`partition_name_list`) statement [#17313](https://github.com/pingcap/tidb/pull/17313)
    - Support checking the value of `collations` when using the `Distinct` function [#17240](https://github.com/pingcap/tidb/pull/17240)
    - Support the `is null` filter condition during the Hash partition pruning [#17310](https://github.com/pingcap/tidb/pull/17310)
    - Support `admin check index`, `admin cleanup index`, and `admin recover index` in partitioned tables [#17392](https://github.com/pingcap/tidb/pull/17392) [#17405](https://github.com/pingcap/tidb/pull/17405) [#17317](https://github.com/pingcap/tidb/pull/17317)
    - Support range partition pruning for the `in` expressions  [#17320](https://github.com/pingcap/tidb/pull/17320)

* TiFlash
    - Support filtering out the data corresponding to the qualified `TSO` through the `min commit ts` value of the `Lock CF` when the Learner reads the data
    - Add the feature that the system explicitly reports an error to avoid incorrect calculation results when the value of `TIMESTAMP` type is less than `1970-01-01 00:00:00`
    - Support using flags in regular expressions when searching logs

* TiKV
    - Support collation rules of `ascii_bin` and `latin1_bin` encoding [#7919](https://github.com/tikv/tikv/pull/7919)

* PD
    - Support specifying the reverse proxy resource prefix for built-in TiDB Dashboard [#2457](https://github.com/pingcap/pd/pull/2457)
    - Support returning the `pending peer` and `down peer` information in interfaces of the PD client Region [#2443](https://github.com/pingcap/pd/pull/2443)
    - Add monitoring items such as `Direction of hotspot move leader`, `Direction of hotspot move peer`, and `Hot cache read entry number` [#2448](https://github.com/pingcap/pd/pull/2448)

* Tools
    + Backup & Restore (BR)
        - Support the backup and restore of `Sequence` and `View` [#242](https://github.com/pingcap/br/pull/242)
    + TiCDC
        - Support checking the validity of `Sink URI` when creating `Changefeed` [#561](https://github.com/pingcap/tiflow/pull/561)
        - Support checking whether the PD and TiKV versions meet the system requirements during system startup [#570](https://github.com/pingcap/tiflow/pull/570)
        - Support scheduling multiple tables in the same scheduling task generation cycle [#572](https://github.com/pingcap/tiflow/pull/572)
        - Add information about node roles in HTTP API [#591](https://github.com/pingcap/tiflow/pull/591)
