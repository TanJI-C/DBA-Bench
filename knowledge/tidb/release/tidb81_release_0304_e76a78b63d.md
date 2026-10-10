# 6.1.0 bug fixes across TiDB, TiKV, PD, Dashboard, TiFlash, TiCDC, DM, and Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.0.md`
- Source Title: `TiDB 6.1.0 Release Notes`
- Source Heading Path: `TiDB 6.1.0 Release Notes > Bug fixes`
- Source Line Ranges: `371-438`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `dashboard`, `tiflash`, `ticdc`, `dm`, `lightning`
- Topic Tags: `bug-fixes`, `query-results`, `ddl`, `memory`, `plan-cache`, `raft`, `upgrade`, `top-sql`, `data-consistency`, `data-loss`, `replication`, `checkpoint`, `precheck`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0304_e76a78b63d`
- Source ID: `tidb-docs-8.1:releases/release-6.1.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4d30e8c55f6ec6421f8689faf08f37ce93c945d080d8cfd0ce5b6b19b38e3a96`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB 6.1.0 Bug fixes section that lists fixed issues across TiDB, TiKV, PD, Dashboard, TiFlash, TiCDC, DM, and TiDB Lightning.
- Retrieval Keywords: TiDB 6.1.0 Bug fixes, in function processes the bit type data, UnionScan cannot maintain the order, Merge Join operator gets wrong results, index join result might be wrong in the dynamic pruning mode, partitioned table is dropped garbage-collected, DDL statements might be stuck after the PD node of a cluster is replaced, INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY, Grafana dashboard, max_allowed_packet does not take effect, TopSQL memory leak, Plan Cache might be wrong on the PointGet plan, Plan Cache in the RC isolation level, Raft log lag is increasing when a TiKV instance is taken offline, failed to load_latest_options, invalid store ID 0, Follower Read, not leader status code, TSO fallback, removed tombstone store appears again after the PD leader transfer, scheduling cannot start immediately after the PD leader transfer, Top SQL cannot collect the CPU overhead, potential data inconsistency after a lot of INSERT and DELETE operations, TiCDC excessive memory usage, data loss in special incremental scanning scenarios, DM start-time time zone issue, checkpoint flush may cause the data of failed rows to be skipped, uppercase table cannot be replicated, SHOW CREATE TABLE, precheck does not check local disk resources and cluster availability, incorrect routing for schemas, PD configuration is not restored correctly, Local-backend import failure, auto_increment column, auto_random
- Follow-up Guidance: The chunk groups the fixed issues by component, including TiDB, TiKV, PD, TiDB Dashboard, TiFlash, TiCDC, DM, and TiDB Lightning.
- Classification Note: This is classified as a release chunk because it is the Bug fixes section of the TiDB 6.1.0 release notes and lists resolved defects by component.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the issue of possible panic that might occur when the `in` function processes the `bit` type data [#33070](https://github.com/pingcap/tidb/issues/33070)
    - Fix the issue of wrong query result because the `UnionScan` operator cannot maintain the order [#33175](https://github.com/pingcap/tidb/issues/33175)
    - Fix the issue that the Merge Join operator gets wrong results in certain cases [#33042](https://github.com/pingcap/tidb/issues/33042)
    - Fix the issue that the `index join` result might be wrong in the dynamic pruning mode [#33231](https://github.com/pingcap/tidb/issues/33231)
    - Fix the issue that data might not be garbage-collected when some partitions of a partitioned table is dropped [#33620](https://github.com/pingcap/tidb/issues/33620)
    - Fix the issue that some DDL statements might be stuck for a period after the PD node of a cluster is replaced [#33908](https://github.com/pingcap/tidb/issues/33908)
    - Fix the issue that the TiDB server might run out of memory when the `INFORMATION_SCHEMA.CLUSTER_SLOW_QUERY` table is queried. This issue can be triggered when you check slow queries on the Grafana dashboard [#33893](https://github.com/pingcap/tidb/issues/33893)
    - Fix the issue that the system variable `max_allowed_packet` does not take effect [#31422](https://github.com/pingcap/tidb/issues/31422)
    - Fix the issue of memory leak in the TopSQL module [#34525](https://github.com/pingcap/tidb/issues/34525) [#34502](https://github.com/pingcap/tidb/issues/34502)
    - Fix the issue that the Plan Cache might be wrong on the PointGet plan [#32371](https://github.com/pingcap/tidb/issues/32371)
    - Fix the issue that query result might be wrong when Plan Cache is started in the RC isolation level [#34447](https://github.com/pingcap/tidb/issues/34447)

+ TiKV

    - Fix the issue that the Raft log lag is increasing when a TiKV instance is taken offline [#12161](https://github.com/tikv/tikv/issues/12161)
    - Fix the issue that TiKV panics and destroys peers unexpectedly because the target Region to be merged is invalid [#12232](https://github.com/tikv/tikv/issues/12232)
    - Fix the issue that TiKV reports the `failed to load_latest_options` error when upgrading from v5.3.1 or v5.4.0 to v6.0.0 or later versions [#12269](https://github.com/tikv/tikv/issues/12269)
    - Fix the issue of OOM caused by appending Raft logs when the memory resource is insufficient [#11379](https://github.com/tikv/tikv/issues/11379)
    - Fix the issue of TiKV panic caused by the race between destroying peers and batch splitting Regions [#12368](https://github.com/tikv/tikv/issues/12368)
    - Fix the issue of TiKV memory usage spike in a short time after `stats_monitor` falls into a dead loop [#12416](https://github.com/tikv/tikv/issues/12416)
    - Fix the issue that TiKV reports the `invalid store ID 0` error when using Follower Read [#12478](https://github.com/tikv/tikv/issues/12478)

+ PD

    - Fix the wrong status code of `not leader` [#4797](https://github.com/tikv/pd/issues/4797)
    - Fix a bug of TSO fallback in some corner cases [#4884](https://github.com/tikv/pd/issues/4884)
    - Fix the issue that a removed tombstone store appears again after the PD leader transfer ​​[#4941](https://github.com/tikv/pd/issues/4941)
    - Fix the issue that scheduling cannot start immediately after the PD leader transfer [#4769](https://github.com/tikv/pd/issues/4769)

+ TiDB Dashboard

    - Fix a bug that Top SQL cannot collect the CPU overhead of the SQL statements that were running before the Top SQL feature is enabled [#33859](https://github.com/pingcap/tidb/issues/33859)

+ TiFlash

    - Fix potential data inconsistency after a lot of INSERT and DELETE operations [#4956](https://github.com/pingcap/tiflash/issues/4956)

+ Tools

    + TiCDC

        - Fix excessive memory usage by optimizing the way DDL schemas are buffered [#1386](https://github.com/pingcap/tiflow/issues/1386)
        - Fix data loss that occurs in special incremental scanning scenarios [#5468](https://github.com/pingcap/tiflow/issues/5468)

    + TiDB Data Migration (DM)

        - Fix the `start-time` time zone issue and change DM behavior from using the downstream time zone to using the upstream time zone [#5471](https://github.com/pingcap/tiflow/issues/5471)
        - Fix the issue that DM occupies more disk space after the task automatically resumes [#3734](https://github.com/pingcap/tiflow/issues/3734) [#5344](https://github.com/pingcap/tiflow/issues/5344)
        - Fix the problem that checkpoint flush may cause the data of failed rows to be skipped [#5279](https://github.com/pingcap/tiflow/issues/5279)
        - Fix the issue that in some cases manually executing the filtered DDL in the downstream might cause task resumption failure [#5272](https://github.com/pingcap/tiflow/issues/5272)
        - Fix an issue that the uppercase table cannot be replicated when `case-sensitive: true` is not set [#5255](https://github.com/pingcap/tiflow/issues/5255)
        - Fix the DM worker panic issue that occurs when the primary key is not first in the index returned by the `SHOW CREATE TABLE` statement [#5159](https://github.com/pingcap/tiflow/issues/5159)
        - Fix the issue that CPU usage may increase and a large amount of log is printed when GTID is enabled or when the task is automatically resumed [#5063](https://github.com/pingcap/tiflow/issues/5063)
        - Fix the offline option and other usage issues in DM WebUI [#4993](https://github.com/pingcap/tiflow/issues/4993)
        - Fix the issue that incremental tasks fail to start when GTID is empty in the upstream [#3731](https://github.com/pingcap/tiflow/issues/3731)
        - Fix the issue that empty configurations may cause dm-master to panic [#3732](https://github.com/pingcap/tiflow/issues/3732)

    + TiDB Lightning

        - Fix the issue that the precheck does not check local disk resources and cluster availability [#34213](https://github.com/pingcap/tidb/issues/34213)
        - Fix the issue of incorrect routing for schemas [#33381](https://github.com/pingcap/tidb/issues/33381)
        - Fix the issue that the PD configuration is not restored correctly when TiDB Lightning panics [#31733](https://github.com/pingcap/tidb/issues/31733)
        - Fix the issue of Local-backend import failure caused by out-of-bounds data in the `auto_increment` column [#27937](https://github.com/pingcap/tidb/issues/27937)
        - Fix the issue of local backend import failure when the `auto_random` or `auto_increment` column is null [#34208](https://github.com/pingcap/tidb/issues/34208)
