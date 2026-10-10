# PD scheduling strategies and operator dispatch

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-scheduling.md`
- Source Title: `TiDB Scheduling`
- Source Heading Path: `TiDB Scheduling > Scheduling strategies | TiDB Scheduling > Scheduling implementation`
- Source Line Ranges: `105-151`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `replica-placement`, `leader-balance`, `hotspot-balance`, `capacity-balance`, `scheduling-rate`, `topology-awareness`, `operator-dispatch`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0106_dd4337db0a`
- Source ID: `tidb-docs-8.1:tidb-scheduling.md#scheduling-strategies`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b449b5c91cd5edb0273e3c7f4b43fb491c198fd591f7f6dd8d093986feaa4b97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-scheduling#scheduling-strategies
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-scheduling.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about PD scheduling strategies, replica placement logic, balancing goals, scheduling speed limits, or how operators are dispatched through Region heartbeats.
- Retrieval Keywords: Scheduling strategies, Scheduling implementation, max-replicas, location-labels, labels, replica count, replicas at different positions, leader balance, hot spot balance, storage size balance, capacity, concurrent scheduling tasks, operator dispatch, pending operator, heartbeat responses, Region leader
- Follow-up Guidance: The source states that PD puts a new operator into heartbeat responses when it receives a Region heartbeat and then monitors progress through follow-up Region heartbeats.
- Classification Note: This chunk is classified as architecture because it describes the scheduling policy framework and the operator dispatch mechanism used by PD after collecting cluster information.

## Official Source Content

## Scheduling strategies

After collecting the information, PD needs some strategies to make scheduling plans.

**Strategy 1: The number of replicas of a Region needs to be correct**

PD can know that the replica count of a Region is incorrect from the Region leader's heartbeat. If it happens, PD can adjust the replica count by adding/removing replica(s). The reason for incorrect replica count can be:

* Store failure, so some Region's replica count is less than expected;
* Store recovery after failure, so some Region's replica count could be more than expected;
* [`max-replicas`](https://github.com/pingcap/pd/blob/v4.0.0-beta/conf/config.toml#L95) is changed.

**Strategy 2: Replicas of a Region need to be at different positions**

Note that here "position" is different from "machine". Generally PD can only ensure that replicas of a Region are not at a same peer to avoid that the peer's failure causes more than one replicas to become lost. However in production, you might have the following requirements:

* Multiple TiKV peers are on one machine;
* TiKV peers are on multiple racks, and the system is expected to be available even if a rack fails;
* TiKV peers are in multiple data centers, and the system is expected to be available even if a data center fails;

The key to these requirements is that peers can have the same "position", which is the smallest unit for failure toleration. Replicas of a Region must not be in one unit. So, we can configure [labels](https://github.com/tikv/tikv/blob/v4.0.0-beta/etc/config-template.toml#L140) for the TiKV peers, and set [location-labels](https://github.com/pingcap/pd/blob/v4.0.0-beta/conf/config.toml#L100) on PD to specify which labels are used for marking positions.

**Strategy 3: Replicas need to be balanced between stores**

The size limit of a Region replica is fixed, so keeping the replicas balanced between stores is helpful for data size balance.

**Strategy 4: Leaders need to be balanced between stores**

Read and write operations are performed on leaders according to the Raft protocol, so that PD needs to distribute leaders into the whole cluster instead of several peers.

**Strategy 5: Hot spots need to be balanced between stores**

PD can detect hot spots from store heartbeats and Region heartbeats, so that PD can distribute hot spots.

**Strategy 6: Storage size needs to be balanced between stores**

When started up, a TiKV store reports `capacity` of storage, which indicates the store's space limit. PD will consider this when scheduling.

**Strategy 7: Adjust scheduling speed to stabilize online services**

Scheduling utilizes CPU, memory, network and I/O traffic. Too much resource utilization will influence online services. Therefore, PD needs to limit the number of the concurrent scheduling tasks. By default this strategy is conservative, while it can be changed if quicker scheduling is required.
## Scheduling implementation

PD collects cluster information from store heartbeats and Region heartbeats, and then makes scheduling plans from the information and strategies. Scheduling plans are a sequence of basic operators. Every time PD receives a Region heartbeat from a Region leader, it checks whether there is a pending operator on the Region or not. If PD needs to dispatch a new operator to a Region, it puts the operator into heartbeat responses, and monitors the operator by checking follow-up Region heartbeats.

Note that here "operators" are only suggestions to the Region leader, which can be skipped by Regions. Leader of Regions can decide whether to skip a scheduling operator or not based on its current status.
