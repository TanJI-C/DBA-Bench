# PD scheduling overview, requirements, and basic operators

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-scheduling.md`
- Source Title: `TiDB Scheduling`
- Source Heading Path: `TiDB Scheduling | TiDB Scheduling > Scheduling situations | TiDB Scheduling > Scheduling requirements | TiDB Scheduling > Basic scheduling operators`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tidb`
- Topic Tags: `scheduling`, `regions`, `replicas`, `leaders`, `raft`, `high-availability`, `load-balancing`, `operator-basics`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0104_c2efaaead0`
- Source ID: `tidb-docs-8.1:tidb-scheduling.md#tidb-scheduling`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3424a8ae1587626bc27a9678e2cc4afa076acad3d740ce5040828f18490fd332`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-scheduling#tidb-scheduling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-scheduling.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for a PD scheduling overview, core scheduling requirements, or the basic Region scheduling operators in a TiDB cluster.
- Retrieval Keywords: PD scheduling, Placement Driver, TiDB Scheduling, Scheduling situations, Scheduling requirements, Basic scheduling operators, Regions, replicas, leaders, followers, Raft, high availability, load balancing, AddReplica, RemoveReplica, TransferLeader
- Follow-up Guidance: For more detail, the source next explains what store and Region heartbeat information PD collects before making scheduling plans.
- Classification Note: This chunk is classified as architecture because it describes PD's role, scheduling requirements, and the fundamental operator model used to manage Regions and replicas.

## Official Source Content

# TiDB Scheduling

The Placement Driver ([PD](https://github.com/tikv/pd)) works as the manager in a TiDB cluster, and it also schedules Regions in the cluster. This article introduces the design and core concepts of the PD scheduling component.
## Scheduling situations

TiKV is the distributed key-value storage engine used by TiDB. In TiKV, data is organized as Regions, which are replicated on several stores. In all replicas, a leader is responsible for reading and writing, and followers are responsible for replicating Raft logs from the leader.

Now consider about the following situations:

* To utilize storage space in a high-efficient way, multiple Replicas of the same Region need to be properly distributed on different nodes according to the Region size;
* For multiple data center topologies, one data center failure only causes one replica to fail for all Regions;
* When a new TiKV store is added, data can be rebalanced to it;
* When a TiKV store fails, PD needs to consider:
    * Recovery time of the failed store.
        * If it's short (for example, the service is restarted), whether scheduling is necessary or not.
        * If it's long (for example, disk fault and data is lost), how to do scheduling.
    * Replicas of all Regions.
        * If the number of replicas is not enough for some Regions, PD needs to complete them.
        * If the number of replicas is more than expected (for example, the failed store re-joins into the cluster after recovery), PD needs to delete them.
* Read/Write operations are performed on leaders, which cannot be distributed only on a few individual stores;
* Not all Regions are hot, so loads of all TiKV stores need to be balanced;
* When Regions are in balancing, data transferring utilizes much network/disk traffic and CPU time, which can influence online services.

These situations can occur at the same time, which makes it harder to resolve. Also, the whole system is changing dynamically, so a scheduler is needed to collect all information about the cluster, and then adjust the cluster. So, PD is introduced into the TiDB cluster.
## Scheduling requirements

The above situations can be classified into two types:

1. A distributed and highly available storage system must meet the following requirements:

    * The right number of replicas.
    * Replicas need to be distributed on different machines according to different topologies.
    * The cluster can perform automatic disaster recovery from TiKV peers' failure.

2. A good distributed system needs to have the following optimizations:

    * All Region leaders are distributed evenly on stores;
    * Storage capacity of all TiKV peers are balanced;
    * Hot spots are balanced;
    * Speed of load balancing for the Regions needs to be limited to ensure that online services are stable;
    * Maintainers are able to take peers online/offline manually.

After the first type of requirements is satisfied, the system will be failure tolerable. After the second type of requirements is satisfied, resources will be utilized more efficiently and the system will have better scalability.

To achieve the goals, PD needs to collect information firstly, such as state of peers, information about Raft groups and the statistics of accessing the peers. Then we need to specify some strategies for PD, so that PD can make scheduling plans from these information and strategies. Finally, PD distributes some operators to TiKV peers to complete scheduling plans.
## Basic scheduling operators

All scheduling plans contain three basic operators:

* Add a new replica
* Remove a replica
* Transfer a Region leader between replicas in a Raft group

They are implemented by the Raft commands `AddReplica`, `RemoveReplica`, and `TransferLeader`.
