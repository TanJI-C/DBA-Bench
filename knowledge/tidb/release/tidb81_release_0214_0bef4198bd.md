# Bug fixes for TiDB, TiKV, PD, TiFlash, and Dumpling

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.4.md`
- Source Title: `TiDB 5.0.4 Release Notes`
- Source Heading Path: `TiDB 5.0.4 Release Notes > Bug Fixes`
- Source Line Ranges: `107-178`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dumpling`
- Topic Tags: `bug fixes`, `upgrade compatibility`, `panic`, `query results`, `transactions`, `mpp`, `placement rules`, `metrics`, `memory leak`, `disk full`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0214_0bef4198bd`
- Source ID: `tidb-docs-8.1:releases/release-5.0.4.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd1c13bbfdb10fef5fe75d7259883dcb2096a0effdcc8d1530fcb8f6da7fd841`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.4#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.4.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 5.0.4 bug fixes across TiDB, TiKV, PD, TiFlash, or Dumpling for issues involving panic, wrong query results, pessimistic transactions, upgrade compatibility, placement rules, metrics, memory leak, or disk full.
- Retrieval Keywords: TiDB 5.0.4 Bug Fixes, TiDB panic partitioned table IS NULL, #23802, FLOAT64 overflow check different with MySQL, #23897, case when wrong character set collation, #26662, committing pessimistic transactions write conflicts, #25964, index keys repeatedly committed pessimistic transaction, #26359, async commit locks panic, #25778, INDEX MERGE column might not be found, #25045, ALTER USER REQUIRE SSL clears authentication_string, #25225, tidb_gc_scan_lock_mode PHYSICAL LEGACY, #25100, TIKV_REGION_PEERS DOWN status, #24879, memory leaks when HTTP API is used, #24649, views do not support DEFINER, #24414, tidb-server --help exits with code 2, #24046, dml_batch_size does not take effect, #24709, read_from_storage partitioned table error, #20372, projection operator panic, #24264, statistics cause queries to panic, #24061, approx_percentile BIT column panic, #23662, Coprocessor Cache panel Grafana wrong metrics, #26338, truncating the same partition DDL statements stuck, #26229, session variable GROUP BY wrong query results, #27106, VARCHAR timestamp implicit conversion join wrong, #25902, associated subquery wrong results, #27233, TiKV corrupted snapshot files disk full, #10813, TiKV panic upgrading from pre-5.0 with Titan enabled, #10843, cannot be rolled back to v5.0.x, #10843, upgraded from TiKV v3.x with Titan enabled, #10774, left pessimistic locks parsing failure, #26404, batch_get_command keys unencoded Load Base Split, #10542, PD down peers not fixed in time, #4077, replication.max-replicas default placement rules stays constant, #3886, PD panic when scaling out TiKV, #3868, multiple schedulers scheduling conflict, #3807, scheduler appears again after deletion, #2572, TiFlash duplicated region error DAQ requests, TiFlash COUNT COUNT DISTINCT unexpected results, TiFlash MPP tasks memory leak panic, TiFlash multiple disks restore data, TiFlash store size metrics inaccurate under heavy writing, TiFlash wrong values metrics, Dumpling show table status stuck MySQL 8.0.3, #322
- Follow-up Guidance: This chunk is followed by a separate TiCDC bug fixes section in the same TiDB 5.0.4 release notes.
- Classification Note: The official content is a release-notes bug-fix summary for self-managed TiDB 5.0.4 covering multiple components: TiDB, TiKV, PD, TiFlash, and Dumpling.

## Official Source Content

## Bug Fixes

+ TiDB

    - Fix the issue that TiDB might panic when querying a partitioned table and the partition key has the `IS NULL` condition [#23802](https://github.com/pingcap/tidb/issues/23802)
    - Fix the issue that the overflow check of the `FLOAT64` type is different with that of MySQL [#23897](https://github.com/pingcap/tidb/issues/23897)
    - Fix the wrong character set and collation for the `case when` expression [#26662](https://github.com/pingcap/tidb/issues/26662)
    - Fix the issue that committing pessimistic transactions might cause write conflicts [#25964](https://github.com/pingcap/tidb/issues/25964)
    - Fix a bug that the index keys in a pessimistic transaction might be repeatedly committed [#26359](https://github.com/pingcap/tidb/issues/26359) [#10600](https://github.com/tikv/tikv/pull/10600)
    - Fix the issue that TiDB might panic when resolving the async commit locks [#25778](https://github.com/pingcap/tidb/issues/25778)
    - Fix a bug that a column might not be found when using `INDEX MERGE` [#25045](https://github.com/pingcap/tidb/issues/25045)
    - Fix a bug that `ALTER USER REQUIRE SSL` clears users' `authentication_string` [#25225](https://github.com/pingcap/tidb/issues/25225)
    - Fix a bug that the value of the `tidb_gc_scan_lock_mode` global variable on a new cluster shows "PHYSICAL" instead of the actual default mode "LEGACY" [#25100](https://github.com/pingcap/tidb/issues/25100)
    - Fix the bug that the `TIKV_REGION_PEERS` system table does not show the correct `DOWN` status [#24879](https://github.com/pingcap/tidb/issues/24879)
    - Fix the issue of memory leaks that occurs when HTTP API is used [#24649](https://github.com/pingcap/tidb/pull/24649)
    - Fix the issue that views do not support `DEFINER` [#24414](https://github.com/pingcap/tidb/issues/24414)
    - Fix the issue that `tidb-server --help` exits with the code `2` [#24046](https://github.com/pingcap/tidb/issues/24046)
    - Fix the issue that setting the global variable `dml_batch_size` does not take effect [#24709](https://github.com/pingcap/tidb/issues/24709)
    - Fix the issue that using `read_from_storage` and partitioned table at the same time causes an error [#20372](https://github.com/pingcap/tidb/issues/20372)
    - Fix the issue that TiDB panics when executing the projection operator [#24264](https://github.com/pingcap/tidb/issues/24264)
    - Fix the issue that statistics might cause queries to panic [#24061](https://github.com/pingcap/tidb/pull/24061)
    - Fix the issue that using the `approx_percentile` function on a `BIT` column might panic [#23662](https://github.com/pingcap/tidb/issues/23662)
    - Fix the issue that the metrics on the **Coprocessor Cache** panel in Grafana are wrong [#26338](https://github.com/pingcap/tidb/issues/26338)
    - Fix the issue that concurrently truncating the same partition causes DDL statements to stuck [#26229](https://github.com/pingcap/tidb/issues/26229)
    - Fix the issue of wrong query results that occurs when the session variable is used as the `GROUP BY` item [#27106](https://github.com/pingcap/tidb/issues/27106)
    - Fix the wrong implicit conversion between `VARCHAR` and timestamp when joining tables [#25902](https://github.com/pingcap/tidb/issues/25902)
    - Fix the wrong results in associated subquery statements [#27233](https://github.com/pingcap/tidb/issues/27233)

+ TiKV

    - Fix the potential disk full issue caused by corrupted snapshot files [#10813](https://github.com/tikv/tikv/issues/10813)
    - Fix the TiKV panic issue that occurs when upgrading from a pre-5.0 version with Titan enabled [#10843](https://github.com/tikv/tikv/pull/10843)
    - Fix the issue that TiKV of a newer version cannot be rolled back to v5.0.x [#10843](https://github.com/tikv/tikv/pull/10843)
    - Fix the TiKV panic issue that occurs when upgrading from a pre-5.0 version to a 5.0 version or later. If a cluster was upgraded from TiKV v3.x with Titan enabled before the upgrade, this cluster might encounter the issue. [#10774](https://github.com/tikv/tikv/issues/10774)
    - Fix the parsing failure caused by the left pessimistic locks [#26404](https://github.com/pingcap/tidb/issues/26404)
    - Fix the panic that occurs when calculating duration on certain platforms [#10571](https://github.com/tikv/tikv/pull/10571)
    - Fix the issue that the keys of `batch_get_command` in Load Base Split are unencoded [#10542](https://github.com/tikv/tikv/issues/10542)

+ PD

    - Fix the issue that PD does not fix the down peers in time [#4077](https://github.com/tikv/pd/issues/4077)
    - Fix the issue that the replica count of the default placement rules stays constant after `replication.max-replicas` is updated [#3886](https://github.com/tikv/pd/issues/3886)
    - Fix a bug that PD might panic when scaling out TiKV [#3868](https://github.com/tikv/pd/issues/3868)
    - Fix the scheduling conflict issue that occurs when multiple schedulers are running at same time [#3807](https://github.com/tikv/pd/issues/3807)
    - Fix the issue that the scheduler might appear again even if it has been deleted [#2572](https://github.com/tikv/pd/issues/2572)

+ TiFlash

    - Fix the potential panic issue that occurs when running table scan tasks
    - Fix the potential memory leak issue that occurs when executing MPP tasks
    - Fix a bug that TiFlash raises the `duplicated region` error when handling DAQ requests
    - Fix the issue of unexpected results when executing the aggregation functions `COUNT` or `COUNT DISTINCT`
    - Fix the potential panic issue that occurs when executing MPP tasks
    - Fix a potential bug that TiFlash cannot restore data when deployed on multiple disks
    - Fix the potential panic issue that occurs when deconstructing `SharedQueryBlockInputStream`
    - Fix the potential panic issue that occurs when deconstructing `MPPTask`
    - Fix the issue of unexpected results when TiFlash fails to establish MPP connections
    - Fix the potential panic issue that occurs when resolving locks
    - Fix the issue that the store size in metrics is inaccurate under heavy writing
    - Fix a bug of incorrect results that occurs when queries contain filters like `CONSTANT`, `<`, `<=`, `>`, `>=`, or `COLUMN`
    - Fix the potential issue that TiFlash cannot garbage-collect the delta data after running for a long time
    - Fix a potential bug that metrics display wrong values
    - Fix the potential issue of data inconsistency that occurs when TiFlash is deployed on multiple disks

+ Tools

    + Dumpling

        - Fix the issue that the execution of `show table status` is stuck in MySQL 8.0.3 or a later version [#322](https://github.com/pingcap/dumpling/issues/322)

    + TiCDC
