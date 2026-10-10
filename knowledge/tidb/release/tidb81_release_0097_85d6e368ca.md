# PD, TiKV, tools, and TiDB Ansible changes in 3.0.0-rc.3

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.0-rc.3.md`
- Source Title: `TiDB 3.0.0-rc.3 Release Notes`
- Source Heading Path: `TiDB 3.0.0-rc.3 Release Notes > PD | TiDB 3.0.0-rc.3 Release Notes > TiKV | TiDB 3.0.0-rc.3 Release Notes > Tools | TiDB 3.0.0-rc.3 Release Notes > TiDB Ansible`
- Source Line Ranges: `60-122`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `tidb`, `tiup`
- Topic Tags: `release-notes`, `scheduling`, `replication`, `monitoring`, `raftstore`, `coprocessor`, `pessimistic-transactions`, `tikv-ctl`, `binlog`, `ansible`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0097_85d6e368ca`
- Source ID: `tidb-docs-8.1:releases/release-3.0.0-rc.3.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `46efeaddf3717d45e51514079a0666e625a2ac3a83dc53b00e6524126b03f238`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.0-rc.3#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.0-rc.3.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 3.0.0-rc.3 release-note details for PD, TiKV, tools, or TiDB Ansible, especially scheduling, monitoring metrics, vector calculation, pessimistic transactions, tikv-ctl commands, or Binlog changes.
- Retrieval Keywords: TiDB 3.0.0-rc.3, PD, TiKV, Tools, TiDB Ansible, enable-two-way-merge, AddLightLearner, AddLightPeer, store-balance-rate, READ_INDEX-related monitoring metrics, GC worker-related monitoring metrics, vector calculation, Top-N, Stream aggregation, AVG, First, SUM, MAX/MIN, Like expression, MultiplyDecimal, BitAnd, BitOr, BitXor, UnaryNot, ResolveLockLite, single statement rollback, pessimistic transaction-related monitoring items, tikv-ctl bad-regions, tombstone command, dist_release, TiDB Binlog, Pump, Drainer, advertise-addr, GetMvccByEncodeKey, maximum QPS value
- Follow-up Guidance: 
- Classification Note: The content is classified as a shared release-note chunk because it covers multiple components in 3.0.0-rc.3, including PD, TiKV, TiDB Binlog tools, and TiDB Ansible.

## Official Source Content

## PD

- Add the `enable-two-way-merge` configuration item to allow only one-way merging [#1583](https://github.com/pingcap/pd/pull/1583)
- Add scheduling operations for `AddLightLearner` and `AddLightPeer` to make Region Scatter scheduling unrestricted by the limit mechanism [#1563](https://github.com/pingcap/pd/pull/1563)
- Fix the issue of insufficient reliability because the data might only have one replica replication when the system is started [#1581](https://github.com/pingcap/pd/pull/1581)
- Optimize configuration check logic to avoid configuration item errors [#1585](https://github.com/pingcap/pd/pull/1585)
- Adjust the definition of the `store-balance-rate` configuration to the upper limit of the number of balance operators generated per minute [#1591](https://github.com/pingcap/pd/pull/1591)
- Fix the issue that the store might have been unable to generate scheduled operations [#1590](https://github.com/pingcap/pd/pull/1590)
## TiKV

+ Engine
    - Fix the issue that incomplete snapshots are generated in the system caused by the iterator not checking the status [#4936](https://github.com/tikv/tikv/pull/4936)
    - Fix the data loss issue caused by a delay of flushing data to the disk when receiving snapshots after a power failure in abnormal conditions [#4850](https://github.com/tikv/tikv/pull/4850)

+ Server
    - Add a feature to check the validity of the `block-size` configuration [#4928](https://github.com/tikv/tikv/pull/4928)
    - Add `READ_INDEX`-related monitoring metrics [#4830](https://github.com/tikv/tikv/pull/4830)
    - Add GC worker-related monitoring metrics [#4922](https://github.com/tikv/tikv/pull/4922)

+ Raftstore
    - Fix the issue that the cache of the local reader is not cleared correctly [#4778](https://github.com/tikv/tikv/pull/4778)
    - Fix the issue that the request delay might be increased when transferring the leader and changing `conf` [#4734](https://github.com/tikv/tikv/pull/4734)
    - Fix the issue that a stale command is wrongly reported [#4682](https://github.com/tikv/tikv/pull/4682)
    - Fix the issue that the command might be pending for a long time [#4810](https://github.com/tikv/tikv/pull/4810)
    - Fix the issue that files are damaged after a power failure, which is caused by a delay of synchronizing the snapshot file to the disk [#4807](https://github.com/tikv/tikv/pull/4807), [#4850](https://github.com/tikv/tikv/pull/4850)

+ Coprocessor
    - Support Top-N in vector calculation [#4827](https://github.com/tikv/tikv/pull/4827)
    - Support `Stream` aggregation in vector calculation [#4786](https://github.com/tikv/tikv/pull/4786)
    - Support the `AVG` aggregate function in vector calculation [#4777](https://github.com/tikv/tikv/pull/4777)
    - Support the `First` aggregate function in vector calculation [#4771](https://github.com/tikv/tikv/pull/4771)
    - Support the `SUM` aggregate function in vector calculation [#4797](https://github.com/tikv/tikv/pull/4797)
    - Support the `MAX`/`MIN` aggregate function in vector calculation [#4837](https://github.com/tikv/tikv/pull/4837)
    - Support the `Like` expression in vector calculation [#4747](https://github.com/tikv/tikv/pull/4747)
    - Support the `MultiplyDecimal` expression in vector calculation [#4849](https://github.com/tikv/tikv/pull/4849 )
    - Support the `BitAnd`/`BitOr`/`BitXor` expression in vector calculation [#4724](https://github.com/tikv/tikv/pull/4724)
    - Support the `UnaryNot` expression in vector calculation [#4808](https://github.com/tikv/tikv/pull/4808)

+ Transaction
    - Fix the issue that an error occurs caused by non-pessimistic locking conflicts in pessimistic transactions [#4801](https://github.com/tikv/tikv/pull/4801), [#4883](https://github.com/tikv/tikv/pull/4883)
    - Reduce unnecessary calculation for optimistic transactions after enabling pessimistic transactions to improve the performance [#4813](https://github.com/tikv/tikv/pull/4813)
    - Add a feature of single statement rollback to ensure that the whole transaction does not need a rollback operation in a deadlock situation [#4848](https://github.com/tikv/tikv/pull/4848)
    - Add pessimistic transaction-related monitoring items [#4852](https://github.com/tikv/tikv/pull/4852)
    - Support using the `ResolveLockLite` command to resolve lightweight locks to improve the performance when severe conflicts exist [#4882](https://github.com/tikv/tikv/pull/4882)

+ tikv-ctl
    - Add the `bad-regions` command to support checking more abnormal conditions [#4862](https://github.com/tikv/tikv/pull/4862)
    - Add a feature of forcibly executing the `tombstone` command [#4862](https://github.com/tikv/tikv/pull/4862)

+ Misc
    - Add the `dist_release` compiling command [#4841](https://github.com/tikv/tikv/pull/4841)
## Tools

+ TiDB Binlog
    - Fix the wrong offset issue caused by Pump not checking the returned value when it fails to write data [#640](https://github.com/pingcap/tidb-binlog/pull/640)
    - Add the `advertise-addr` configuration in Drainer to support the bridge mode in the container environment [#634](https://github.com/pingcap/tidb-binlog/pull/634)
    - Add the `GetMvccByEncodeKey` function in Pump to speed up querying the transaction status [#632](https://github.com/pingcap/tidb-binlog/pull/632)
## TiDB Ansible

- Add a monitoring item to predict the maximum QPS value of the cluster ("hide" by default) [#f5cfa4d](https://github.com/pingcap/tidb-ansible/commit/f5cfa4d903bbcd77e01eddc8d31eabb6e6157f73)
