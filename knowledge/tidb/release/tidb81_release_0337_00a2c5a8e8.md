# New features in transactions, stability, and ease of use

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > New features > Transactions | TiDB 6.3.0 Release Notes > New features > Stability | TiDB 6.3.0 Release Notes > New features > Ease of use`
- Source Line Ranges: `124-157`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `sql`
- Topic Tags: `transactions`, `pessimistic-transactions`, `read-committed`, `tso`, `stability`, `statistics`, `partition-pruning`, `globalstats`, `titan`, `placement-rules`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0337_00a2c5a8e8`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#transactions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e5902f98b627747b4ade38984c5dab91b2081c62c6a65953f7aa94a8c15f7520`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.3.0 release-note changes for transactions, stability, or ease of use, including pessimistic transaction unique checks, Read-Committed TSO fetching, outdated statistics behavior, Titan disabling, partition pruning with GlobalStats, and Placement Rules with TiFlash.
- Retrieval Keywords: TiDB 6.3.0 Transactions, TiDB 6.3.0 Stability, TiDB 6.3.0 Ease of use, tidb_constraint_check_in_place_pessimistic, unique constraints, pessimistic transactions, bulk DML operations, Read-Committed isolation level, tidb_rc_write_check_ts, TSO fetching, Plan Cache hit, batch DML statements, resource-consuming queries, lightweight queries, read requests scheduling, P99 latency, tidb_enable_pseudo_for_outdated_stats, outdated stats, pseudo statistics, disable Titan, online TiKV nodes, dynamic pruning, static partition pruning, GlobalStats, partition pruning settings, SQL-based data Placement Rules, TiFlash replicas, placement-rules-in-sql
- Follow-up Guidance: The content specifies that `tidb_constraint_check_in_place_pessimistic` is disabled by default and that the default value of `tidb_enable_pseudo_for_outdated_stats` changes to `OFF` since v6.3.0.
- Classification Note: This is classified as a release chunk because it groups new 6.3.0 changes under Transactions, Stability, and Ease of use with named system variables and feature behaviors.

## Official Source Content

### Transactions

* Support deferring checks of unique constraints in pessimistic transactions [#36579](https://github.com/pingcap/tidb/issues/36579) @[ekexium](https://github.com/ekexium)

    You can use the [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) system variable to control when TiDB checks [unique constraints](https://docs.pingcap.com/tidb/stable/constraints#pessimistic-transactions) in pessimistic transactions. This variable is disabled by default. When the variable is enabled (set to `ON`), TiDB will defer locking operations and unique constraint checks in pessimistic transactions until necessary, thus improving the performance of bulk DML operations.

* Optimize the way of fetching TSO in the Read-Committed isolation level [#36812](https://github.com/pingcap/tidb/issues/36812) @[TonsnakeLin](https://github.com/TonsnakeLin)

    In the Read-Committed isolation level, the system variable [`tidb_rc_write_check_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_rc_write_check_ts-new-in-v630) is introduced to control how TSO is fetched. In the case of Plan Cache hit, TiDB improves the execution efficiency of batch DML statements by reducing the frequency of fetching TSO, and reduces the execution time of running tasks in batch.
### Stability

* Reduce the impact of resource-consuming queries on the response time of lightweight queries [#13313](https://github.com/tikv/tikv/issues/13313) @[glorv](https://github.com/glorv)

    When resource-consuming queries and lightweight queries are executed at the same time, the response time of lightweight queries is affected. In this case, to ensure the quality of transactional services, lightweight queries are expected to be processed by TiDB first. In v6.3.0, TiKV optimizes the scheduling mechanism of read requests, so that the execution time of resource-consuming queries in each round can meet expectations. This drastically reduces the impact of resource-consuming queries on the response time of lightweight queries and reduces P99 latency by more than 50% for mixed workload scenarios.

* Modify the default policy of loading statistics when statistics become outdated [#27601](https://github.com/pingcap/tidb/issues/27601) @[xuyifangreeneyes](https://github.com/xuyifangreeneyes)

    In v5.3.0, TiDB introduced the system variable [`tidb_enable_pseudo_for_outdated_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_pseudo_for_outdated_stats-new-in-v530) to control how the optimizer behaves when the statistics become outdated. The default value is `ON`, which means keeping the behavior of the old version: When the statistics on objects that are involved in a SQL statement are outdated, the optimizer considers that statistics (other than the total number of rows on the table) are no longer reliable and uses pseudo statistics instead. After tests and analyses of actual user scenarios, the default value of `tidb_enable_pseudo_for_outdated_stats` is changed to `OFF` since v6.3.0. Even if the statistics become outdated, the optimizer will still use the statistics on the table, which makes the execution plan more stable.

* Disabling Titan becomes GA @[tabokie](https://github.com/tabokie)

    You can [disable Titan](https://docs.pingcap.com/tidb/stable/storage-engine/titan-configuration#disable-titan) for online TiKV nodes.

* Use `static` partition pruning when GlobalStats are not ready [#37535](https://github.com/pingcap/tidb/issues/37535) @[Yisaer](https://github.com/Yisaer)

    When [`dynamic pruning`](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) is enabled, the optimizer selects execution plans based on [GlobalStats](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-of-partitioned-tables-in-dynamic-pruning-mode). Before GlobalStats are fully collected, using pseudo statistics might cause performance regression. In v6.3.0, this issue is addressed by maintaining the `static` mode if you enable dynamic pruning before GlobalStats are collected. TiDB remains in the `static` mode until GlobalStats are collected. This ensures performance stability when you change the partition pruning settings.
### Ease of use

* Address the conflict between SQL-based data Placement Rules and TiFlash replicas [#37171](https://github.com/pingcap/tidb/issues/37171) @[lcwangchao](https://github.com/lcwangchao)

    TiDB v6.0.0 provides [SQL-based data Placement Rules](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql). But this feature conflicts with TiFlash replicas due to implementation issues. TiDB v6.3.0 optimizes the implementation mechanisms, and resolves the conflict between SQL-based data Placement Rules and TiFlash.
