# Release overview and scalability features in TiDB 6.6.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes | TiDB 6.6.0 Release Notes > Feature details | TiDB 6.6.0 Release Notes > Feature details > Scalability`
- Source Line Ranges: `5-83`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `dashboard`, `dm`, `lightning`
- Topic Tags: `release-notes`, `dmr`, `feature-overview`, `scalability`, `partitioned-raft-kv`, `ddl`, `distributed-ddl`, `resource-control`, `historical-sql-binding`, `foreign-key`, `multi-valued-indexes`, `physical-import`, `stale-read`, `compression-exchange`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0414_22ae9d5957`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#tidb-6-6-0-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `be6f35fad5ed57ef30ef2bdbc1d1643ee671e57d4a2bf55198b58c0e8729d6c7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#tidb-6-6-0-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: You need the TiDB 6.6.0 release summary that groups scalability, reliability, SQL, and DM features and names the exact feature entries.
- Retrieval Keywords: TiDB 6.6.0 Release Notes, Release date: February 20, 2023, TiDB version: 6.6.0-DMR, Partitioned Raft KV storage engine, batch aggregating data requests, Stale Read, compression exchange, Resource control, Historical SQL binding, Foreign key, Multi-valued indexes, DM supports physical import, distributed parallel execution framework for DDL operations, tidb_ddl_distribute_reorg
- Follow-up Guidance: See the linked feature documents for details on each listed capability.
- Classification Note: The chunk is a TiDB 6.6.0 release overview that summarizes new features and improvements across multiple product areas.

## Official Source Content

# TiDB 6.6.0 Release Notes

Release date: February 20, 2023

TiDB version: 6.6.0-[DMR](https://docs.pingcap.com/tidb/stable/releases/versioning#development-milestone-releases)

> **Note:**
>
> The TiDB 6.6.0-DMR documentation has been [archived](https://docs-archive.pingcap.com/tidb/v6.6/). PingCAP encourages you to use [the latest LTS version](https://docs.pingcap.com/tidb/stable) of the TiDB database.

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.6/quick-start-with-tidb)

In v6.6.0-DMR, the key new features and improvements are as follows:

<table>
<thead>
  <tr>
    <th>Category</th>
    <th>Feature</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td rowspan="3">Scalability and Performance<br /></td>
    <td>TiKV supports <a href="https://docs.pingcap.com/tidb/v6.6/partitioned-raft-kv" target="_blank">Partitioned Raft KV storage engine</a> (experimental)</td>
    <td>TiKV introduces the Partitioned Raft KV storage engine, and each Region uses an independent RocksDB instance, which can easily expand the storage capacity of the cluster from TB to PB and provide more stable write latency and stronger scalability.</td>
  </tr>
  <tr>
    <td>TiKV supports <a href="https://docs.pingcap.com/tidb/v6.6/system-variables#tidb_store_batch_size" target="_blank">batch aggregating data requests</a></td>
    <td>This enhancement significantly reduces total RPCs in TiKV batch-get operations. In situations where data is highly dispersed and the gRPC thread pool has insufficient resources, batching coprocessor requests can improve performance by more than 50%.</td>
  </tr>
  <tr>
    <td>TiFlash supports <a href="https://docs.pingcap.com/tidb/v6.6/stale-read" target="_blank">Stale Read</a> and <a href="https://docs.pingcap.com/tidb/v6.6/explain-mpp#mpp-version-and-exchange-data-compression" target="_blank">compression exchange</a></td>
    <td>TiFlash supports the stale read feature, which can improve query performance in scenarios where real-time requirements are not restricted. TiFlash supports data compression to improve the efficiency of parallel data exchange, and the overall TPC-H performance improves by 10%, which can save more than 50% of the network usage.</td>
  </tr>
  <tr>
    <td rowspan="2">Reliability and availability<br /></td>
    <td><a href="https://docs.pingcap.com/tidb/v6.6/tidb-resource-control" target="_blank">Resource control</a> (experimental)</td>
    <td>Support resource management based on resource groups, which maps database users to the corresponding resource groups and sets quotas for each resource group based on actual needs.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v6.6/sql-plan-management#create-a-binding-according-to-a-historical-execution-plan" target="_blank">Historical SQL binding</a></td>
    <td>Support binding historical execution plans and quickly binding execution plans on TiDB Dashboard.</td>
  </tr>
  <tr>
    <td rowspan="2">SQL functionalities<br /></td>
    <td><a href="https://docs.pingcap.com/tidb/v6.6/foreign-key" target="_blank">Foreign key</a> (experimental)</td>
    <td>Support MySQL-compatible foreign key constraints to maintain data consistency and improve data quality.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/v6.6/sql-statement-create-index#multi-valued-indexes" target="_blank">Multi-valued indexes</a> (experimental)</td>
    <td>Introduce MySQL-compatible multi-valued indexes and enhance the JSON type to improve TiDB's compatibility with MySQL 8.0.</td>
  </tr>
  <tr>
    <td>DB operations and observability<br /></td>
    <td><a href="https://docs.pingcap.com/tidb/v6.6/dm-precheck#check-items-for-physical-import" target="_blank">DM supports physical import</a> (experimental)</td>
    <td>TiDB Data Migration (DM) integrates TiDB Lightning's physical import mode to improve the performance of full data migration, with performance being up to 10 times faster.</td>
  </tr>
</tbody>
</table>
## Feature details
### Scalability

* Support Partitioned Raft KV storage engine (experimental) [#11515](https://github.com/tikv/tikv/issues/11515) [#12842](https://github.com/tikv/tikv/issues/12842) @[busyjay](https://github.com/busyjay) @[tonyxuqqi](https://github.com/tonyxuqqi) @[tabokie](https://github.com/tabokie) @[bufferflies](https://github.com/bufferflies) @[5kbpers](https://github.com/5kbpers) @[SpadeA-Tang](https://github.com/SpadeA-Tang) @[nolouch](https://github.com/nolouch)

    Before TiDB v6.6.0, TiKV's Raft-based storage engine used a single RocksDB instance to store the data of all 'Regions' of the TiKV instance. To support larger clusters more stably, starting from TiDB v6.6.0, a new TiKV storage engine is introduced, which uses multiple RocksDB instances to store TiKV Region data, and the data of each Region is independently stored in a separate RocksDB instance. The new engine can better control the number and level of files in the RocksDB instance, achieve physical isolation of data operations between Regions, and support stably managing more data. You can see it as TiKV managing multiple RocksDB instances through partitioning, which is why the feature is named Partitioned-Raft-KV. The main advantage of this feature is better write performance, faster scaling, and larger volume of data supported with the same hardware. It can also support larger cluster scales.

    Currently, this feature is experimental and not recommended for use in production environments.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-raft-kv).

* Support the distributed parallel execution framework for DDL operations (experimental) [#37125](https://github.com/pingcap/tidb/issues/37125) @[zimulala](https://github.com/zimulala)

    In previous versions, only one TiDB instance in the entire TiDB cluster was allowed to handle schema change tasks as a DDL owner. To further improve DDL concurrency for large table's DDL operations, TiDB v6.6.0 introduces the distributed parallel execution framework for DDL, through which all TiDB instances in the cluster can concurrently execute the `StateWriteReorganization` phase of the same task to speed up DDL execution. This feature is controlled by the system variable [`tidb_ddl_distribute_reorg`](https://docs.pingcap.com/tidb/v6.6/system-variables#tidb_ddl_distribute_reorg-new-in-v660) and is currently only supported for `Add Index` operations.
