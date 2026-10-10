# PD information collection and TiKV store states

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-scheduling.md`
- Source Title: `TiDB Scheduling`
- Source Heading Path: `TiDB Scheduling > Information collection`
- Source Line Ranges: `64-104`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `heartbeats`, `store-state`, `region-state`, `offline`, `down`, `tombstone`, `topology-labels`, `status-monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0105_42cccf1829`
- Source ID: `tidb-docs-8.1:tidb-scheduling.md#information-collection`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0a9e7456cbb5f705609b487053671db6ddafcac6cf3e7ccfcdf0310f6e627f9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-scheduling#information-collection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-scheduling.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks what information PD collects from TiKV heartbeats or how TiKV store states such as Up, Disconnect, Offline, Down, and Tombstone are defined.
- Retrieval Keywords: Information collection, StoreState, RegionState, store heartbeat, Region heartbeat, PD control, Up, Disconnect, Offline, Down, Tombstone, max-store-down-time, leader_count, region_count, remove-tombstone, labels, topology
- Follow-up Guidance: The source also notes that PD can make more precise decisions through an expanded interface, such as when a maintainer manually sets a store offline through PD control so PD can balance all Regions immediately.
- Classification Note: This chunk is classified as architecture because it explains the status and heartbeat information model that PD uses to observe TiKV stores and Regions for scheduling decisions.

## Official Source Content

## Information collection

Scheduling is based on information collection. In short, the PD scheduling component needs to know the states of all TiKV peers and all Regions. TiKV peers report the following information to PD:

- State information reported by each TiKV peer:

    Each TiKV peer sends heartbeats to PD periodically. PD not only checks whether the store is alive, but also collects [`StoreState`](https://github.com/pingcap/kvproto/blob/release-8.1/proto/pdpb.proto#L473) in the heartbeat message. `StoreState` includes:

    * Total disk space
    * Available disk space
    * The number of Regions
    * Data read/write speed
    * The number of snapshots that are sent/received (The data might be replicated between replicas through snapshots)
    * Whether the store is overloaded
    * Labels (See [Perception of Topology](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels))

    You can use PD control to check the status of a TiKV store, which can be Up, Disconnect, Offline, Down, or Tombstone. The following is a description of all statuses and their relationship.

    + **Up**: The TiKV store is in service.
    + **Disconnect**: Heartbeat messages between the PD and the TiKV store are lost for more than 20 seconds. If the lost period exceeds the time specified by `max-store-down-time`, the status "Disconnect" changes to "Down".
    + **Down**: Heartbeat messages between the PD and the TiKV store are lost for a time longer than `max-store-down-time` (30 minutes by default). In this status, the TiKV store starts replenishing replicas of each Region on the surviving store.
    + **Offline**: A TiKV store is manually taken offline through PD Control. This is only an intermediate status for the store to go offline. The store in this status moves all its Regions to other "Up" stores that meet the relocation conditions. When `leader_count` and `region_count` (obtained through PD Control) both show `0`, the store status changes to "Tombstone" from "Offline". In the "Offline" status, **do not** disable the store service or the physical server where the store is located. During the process that the store goes offline, if the cluster does not have target stores to relocate the Regions (for example, inadequate stores to hold replicas in the cluster), the store is always in the "Offline" status.
    + **Tombstone**: The TiKV store is completely offline. You can use the `remove-tombstone` interface to safely clean up TiKV in this status. Starting from v6.5.0, if not manually handled, PD will automatically delete the Tombstone records stored internally one month after the node is converted to Tombstone.

    ![TiKV store status relationship](/media/tikv-store-status-relationship.png)

- Information reported by Region leaders:

    Each Region leader sends heartbeats to PD periodically to report [`RegionState`](https://github.com/pingcap/kvproto/blob/release-8.1/proto/pdpb.proto#L312), including:

    * Position of the leader itself
    * Positions of other replicas
    * The number of offline replicas
    * data read/write speed

PD collects cluster information by the two types of heartbeats and then makes decision based on it.

Besides, PD can get more information from an expanded interface to make a more precise decision. For example, if a store's heartbeats are broken, PD can't know whether the peer steps down temporarily or forever. It just waits a while (by default 30min) and then treats the store as offline if there are still no heartbeats received. Then PD balances all regions on the store to other stores.

But sometimes stores are manually set offline by a maintainer, so the maintainer can tell PD this by the PD control interface. Then PD can balance all regions immediately.
