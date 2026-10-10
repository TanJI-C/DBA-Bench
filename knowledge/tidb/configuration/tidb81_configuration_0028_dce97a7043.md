# PD store limit concepts and pd-ctl usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-store-limit.md`
- Source Title: `Store Limit`
- Source Heading Path: `Store Limit | Store Limit > Implementation principles | Store Limit > Usage | Store Limit > Usage > View setting of the current store | Store Limit > Usage > Set limit for all stores | Store Limit > Usage > Set limit for a single store | Store Limit > Usage > Principles of store limit v2`
- Source Line Ranges: `5-78`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `store-limit`, `scheduling`, `token-bucket`, `pd-ctl`, `add-peer`, `remove-peer`, `store-limit-v2`, `snapshot-speed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0028_dce97a7043`
- Source ID: `tidb-docs-8.1:configure-store-limit.md#store-limit`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `420950e8d3758706f480d2feb53d2a700959be9565eeaf921725152b30e03d0c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-store-limit#store-limit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-store-limit.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD Store Limit concepts, pd-ctl commands to view or set add-peer and remove-peer limits, or the meaning of store limit v2 and Snapshot Speed.
- Retrieval Keywords: Store Limit, PD, pd-ctl, store limit, store limit add-peer, store limit remove-peer, store limit all 5, store limit 1 5, add-peer, remove-peer, token bucket, operator, replace-down-replica, store-limit-version, v2, store limit v2, TiKV Details, Snapshot, Snapshot Speed, snap-io-max-bytes-per-sec
- Follow-up Guidance: The source also states that when `store-limit-version` is set to `v2`, you can check the scheduling upper limit in **TiKV Details** > **Snapshot** > **Snapshot Speed** and adjust `snap-io-max-bytes-per-sec` to change a node's scheduling speed.
- Classification Note: This is classified as configuration because the content explains PD Store Limit behavior and provides `pd-ctl` commands and related settings such as `store-limit-version` and `snap-io-max-bytes-per-sec`.

## Official Source Content

# Store Limit

Store Limit is a feature of PD, introduced in TiDB 3.0. It is designed to control the scheduling speed in a finer manner for better performance in different scenarios.
## Implementation principles

PD performs scheduling at the unit of operator. An operator might contain several scheduling operations. For example:

```
"replace-down-replica {mv peer: store [2] to [3]} (kind:region,replica, region:10(4,5), createAt:2020-05-18 06:40:25.775636418 +0000 UTC m=+2168762.679540369, startAt:2020-05-18 06:40:25.775684648 +0000 UTC m=+2168762.679588599, currentStep:0, steps:[add learner peer 20 on store 3, promote learner peer 20 on store 3 to voter, remove peer on store 2])"
```

In this above example, the `replace-down-replica` operator contains the following specific operations:

1. Add a learner peer with the ID `20` to `store 3`.
2. Promote the learner peer with the ID `20` on `store 3` to a voter.
3. Delete the peer on `store 2`.

Store Limit achieves the store-level speed limit by maintaining a mapping from store IDs to token buckets in memory. The different operations here correspond to different token buckets. Currently, Store Limit only supports limiting the speed of two operations: adding learners/peers and deleting peers. That is, each store has two types of token buckets.

Every time an operator is generated, it checks whether enough tokens exist in the token buckets for its operations. If yes, the operator is added to the scheduling queue, and the corresponding token is taken from the token bucket. Otherwise, the operator is abandoned. Because the token bucket replenishes tokens at a fixed rate, the speed limit is thus achieved.

Store Limit is different from other limit-related parameters in PD (such as `region-schedule-limit` and `leader-schedule-limit`) in that it mainly limits the consuming speed of operators, while other parameters limits the generating speed of operators. Before introducing the Store Limit feature, the speed limit of scheduling is mostly at the global scope. Therefore, even if the global speed is limited, it is still possible that the scheduling operations are concentrated on some stores, affecting the performance of the cluster. By limiting the speed at a finer level, Store Limit can better control the scheduling behavior.
## Usage

The parameters of Store Limit can be configured using `pd-ctl`.
### View setting of the current store

To view the limit setting of the current store, run the following commands:

```bash
store limit                         // Shows the speed limit of adding and deleting peers in all stores.
store limit add-peer                // Shows the speed limit of adding peers in all stores.
store limit remove-peer             // Shows the speed limit of deleting peers in all stores. 
```
### Set limit for all stores

To set the speed limit for all stores, run the following commands:

```bash
store limit all 5                   // All stores can at most add and delete 5 peers per minute.
store limit all 5 add-peer          // All stores can at most add 5 peers per minute.
store limit all 5 remove-peer       // All stores can at most delete 5 peers per minute.
```
### Set limit for a single store

To set the speed limit for a single store, run the following commands:

```bash
store limit 1 5                     // store 1 can at most add and delete 5 peers per minute.
store limit 1 5 add-peer            // store 1 can at most add 5 peers per minute.
store limit 1 5 remove-peer         // store 1 can at most delete 5 peers per minute.
```
### Principles of store limit v2

> **Warning:**
> 
> Store limit v2 is an experimental feature. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

When [`store-limit-version`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#store-limit-version-new-in-v710) is set to `v2`, store limit v2 takes effect. In v2 mode, the limit of operators are dynamically adjusted based on the capability of TiKV snapshots. When TiKV has fewer pending tasks, PD increases its scheduling tasks. Otherwise, PD reduces the scheduling tasks for the node. Therefore, you do not need to manually set `store limit` to speed up the scheduling process.

In v2 mode, the execution speed of TiKV becomes the main bottleneck during migration. You can check whether the current scheduling speed has reached the upper limit through the **TiKV Details** > **Snapshot** > **Snapshot Speed** panel. To increase or decrease the scheduling speed of a node, you can adjust the TiKV snapshot limit ([`snap-io-max-bytes-per-sec`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#snap-io-max-bytes-per-sec)).
