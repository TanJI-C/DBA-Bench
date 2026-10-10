# PD scheduling behavior with topology labels and isolation level

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/schedule-replicas-by-topology-labels.md`
- Source Title: `Schedule Replicas by Topology Labels`
- Source Heading Path: `Schedule Replicas by Topology Labels > PD schedules based on topology label`
- Source Line Ranges: `276-292`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `tidb`
- Topic Tags: `topology-labels`, `replica-scheduling`, `replica-placement`, `isolation-level`, `max-replicas`, `max-store-down-time`, `disaster-recovery`, `region-replicas`, `zone`, `rack`, `host`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0057_f5a348eebf`
- Source ID: `tidb-docs-8.1:schedule-replicas-by-topology-labels.md#pd-schedules-based-on-topology-label`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `57f4651db42fa2e153ca9825c49ea88427651d5dea7474db4219212452b71961`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels#pd-schedules-based-on-topology-label
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/schedule-replicas-by-topology-labels.md

## Retrieval Guidance

- Use When: Use this chunk when asking how PD schedules Region replicas across topology labels such as zone, rack, and host under different `max-replicas` and `isolation-level` settings.
- Retrieval Keywords: PD schedules based on topology label, topology labels, replica scheduling, replica isolation, replica placement, Region replicas, max-replicas, isolation-level, max-store-down-time, zone, rack, host, 3 replicas 3 zones, 5 replicas 3 zones, PD will not perform scheduling, minimum physical isolation requirements, disaster recovery
- Follow-up Guidance: The content also explains how PD behaves after a zone failure or isolation that exceeds `max-store-down-time`, including cases where `isolation-level=zone` prevents additional scheduling even when the replica count is below `max-replicas`.
- Classification Note: This is classified as architecture because it describes the official scheduling behavior and isolation model PD uses to place TiKV Region replicas across the physical topology.

## Official Source Content

## PD schedules based on topology label

PD schedules replicas according to the label layer to make sure that different replicas of the same data are scattered as much as possible.

Take the topology in the previous section as an example.

Assume that the number of cluster replicas is 3 (`max-replicas=3`). Because there are 3 zones in total, PD ensures that the 3 replicas of each Region are respectively placed in z1, z2, and z3. In this way, the TiDB cluster is still available when one zone fails.

Then, assume that the number of cluster replicas is 5 (`max-replicas=5`). Because there are only 3 zones in total, PD cannot guarantee the isolation of each replica at the zone level. In this situation, the PD scheduler will ensure replica isolation at the host level. In other words, multiple replicas of a Region might be distributed in the same zone but not on the same host.

In the case of the 5-replica configuration, if z3 fails or is isolated as a whole, and cannot be recovered after a period of time (controlled by `max-store-down-time`), PD will make up the 5 replicas through scheduling. At this time, only 4 hosts are available. This means that host-level isolation cannot be guaranteed and that multiple replicas might be scheduled to the same host. But if the `isolation-level` value is set to `zone` instead of being left empty, this specifies the minimum physical isolation requirements for Region replicas. That is to say, PD will ensure that replicas of the same Region are scattered among different zones. PD will not perform corresponding scheduling even if following this isolation restriction does not meet the requirement of `max-replicas` for multiple replicas.

If the `isolation-level` setting is set to `zone`, this specifies the minimum isolation requirement for Region replicas at the physical level. In this case, PD will always guarantee that replicas of the same Region are distributed across different zones. Even if following this isolation restriction would not meet the multi-replica requirements of `max-replicas`, PD will not schedule accordingly. Taking a TiKV cluster distributed across three data zones (z1, z2, and z3) as an example, if each Region requires three replicas, PD distributes the three replicas of the same Region to these three data zones respectively. If a power outage occurs in z1 and cannot be recovered after a period of time (30 minutes by default, controlled by [`max-store-down-time`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-store-down-time)), PD determines that the Region replicas in z1 are no longer available. However, because `isolation-level` is set to `zone`, PD needs to strictly guarantee that different replicas of the same Region will not be scheduled to the same data zone. Because both z2 and z3 already have replicas, PD will not perform any scheduling under the minimum isolation level restriction of `isolation-level`, even if there are only two replicas at this moment.

Similarly, when `isolation-level` is set to `rack`, the minimum isolation level applies to different racks in the same data center. With this configuration, the isolation at the zone layer is guaranteed first if possible. When the isolation at the zone level cannot be guaranteed, PD tries to avoid scheduling different replicas to the same rack in the same zone. The scheduling works similarly when `isolation-level` is set to `host` where PD first guarantees the isolation level of rack, and then the level of host.

In summary, PD maximizes the disaster recovery of the cluster according to the current topology. Therefore, if you want to achieve a certain level of disaster recovery, deploy more machines on different sites according to the topology than the number of `max-replicas`. TiDB also provides mandatory configuration items such as `isolation-level` for you to more flexibly control the topological isolation level of data according to different scenarios.
