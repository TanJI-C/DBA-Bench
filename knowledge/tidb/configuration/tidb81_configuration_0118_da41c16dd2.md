# Deployment example and TiKV label planning for 3-AZ topology

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/multi-data-centers-in-one-city-deployment.md`
- Source Title: `Multiple Availability Zones in One Region Deployment`
- Source Heading Path: `Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > Deployment example | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > Deployment example > Topology example | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > Deployment example > TiKV labels | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > Deployment example > TiKV labels planning example | Multiple Availability Zones in One Region Deployment > Three AZs in one region deployment > High availability and disaster recovery analysis`
- Source Line Ranges: `94-170`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `shared`, `tiup`
- Topic Tags: `topology`, `labels`, `replica-placement`, `location-labels`, `region-replicas`, `multi-raft`, `scaling`, `rack-awareness`, `availability-zones`, `disaster-recovery`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0118_da41c16dd2`
- Source ID: `tidb-docs-8.1:multi-data-centers-in-one-city-deployment.md#deployment-example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce4b2aa464a1614566dd5f917f39b7271ec4d82c96bfaf25a12dfd182b073e35`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/multi-data-centers-in-one-city-deployment#deployment-example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/multi-data-centers-in-one-city-deployment.md

## Retrieval Guidance

- Use When: Use this chunk when describing a 3-AZ deployment example, TiKV label planning, and how `replication.location-labels` and `server.labels` affect Region replica placement and availability.
- Retrieval Keywords: Deployment example, Topology example, TiKV labels, TiKV labels planning example, High availability and disaster recovery analysis, Multi-Raft, Region replicas, replication.location-labels, server.labels, zone az rack host, three replicas of each Region form a Raft group, size of each Region is 96 MB by default, PD optimally schedules Region replicas, cluster initialization configuration file, rolling upgrade operations
- Follow-up Guidance: The source includes a full configuration example with `replication.location-labels: ["zone","az","rack","host"]` and per-TiKV `server.labels`, plus an explanation of why a logical `zone` layer is used to simplify future AZ scale-out and avoid relabeling and rebalancing.
- Classification Note: This chunk is classified as configuration because it focuses on topology configuration, PD location labels, and TiKV `server.labels` planning used for replica scheduling and disaster recovery.

## Official Source Content

### Deployment example

This section provides a topology example, and introduces TiKV labels and TiKV labels planning.
#### Topology example

The following example assumes that three AZs (AZ1, AZ2, and AZ3) are located in one region; each AZ has two sets of racks and each rack has three servers. The example ignores the hybrid deployment or the scenario where multiple instances are deployed on one machine. The deployment of a TiDB cluster (three replicas) on three AZs in one region is as follows:

![3-AZ in One Region](/media/multi-data-centers-in-one-city-deployment-sample.png)
#### TiKV labels

TiKV is a Multi-Raft system where data is divided into Regions and the size of each Region is 96 MB by default. Three replicas of each Region form a Raft group. For a TiDB cluster of three replicas, because the number of Region replicas is independent of the TiKV instance numbers, three replicas of a Region are only scheduled to three TiKV instances. This means that even if the cluster is scaled out to have N TiKV instances, it is still a cluster of three replicas.

Because a Raft group of three replicas tolerates only one replica failure, even if the cluster is scaled out to have N TiKV instances, this cluster still tolerates only one replica failure. Two failed TiKV instances might cause some Regions to lose replicas and the data in this cluster is no longer complete. SQL requests that access data from these Regions will fail. The probability of two simultaneous failures among N TiKV instances is much higher than the probability of two simultaneous failures among three TiKV instances. This means that the more TiKV instances the Multi-Raft system is scaled out to have, the less the availability of the system.

Because of the preceding limitation, `label` is used to describe the location information of TiKV. The label information is refreshed to the TiKV startup configuration file with deployment or rolling upgrade operations. The started TiKV reports its latest label information to PD. Based on the user-registered label name (the label metadata) and the TiKV topology, PD optimally schedules Region replicas and improves the system availability.
#### TiKV labels planning example

To improve the availability and disaster recovery of the system, you need to design and plan TiKV labels according to your existing physical resources and the disaster recovery capability. You also need to edit the cluster initialization configuration file according to the planned topology:

```ini
server_configs:
  pd:
    replication.location-labels: ["zone","az","rack","host"]

tikv_servers:
  - host: 10.63.10.30
    config:
      server.labels: { zone: "z1", az: "az1", rack: "r1", host: "30" }
  - host: 10.63.10.31
    config:
      server.labels: { zone: "z1", az: "az1", rack: "r1", host: "31" }
  - host: 10.63.10.32
    config:
      server.labels: { zone: "z1", az: "az1", rack: "r2", host: "32" }
  - host: 10.63.10.33
    config:
      server.labels: { zone: "z1", az: "az1", rack: "r2", host: "33" }

  - host: 10.63.10.34
    config:
      server.labels: { zone: "z2", az: "az2", rack: "r1", host: "34" }
  - host: 10.63.10.35
    config:
      server.labels: { zone: "z2", az: "az2", rack: "r1", host: "35" }
  - host: 10.63.10.36
    config:
      server.labels: { zone: "z2", az: "az2", rack: "r2", host: "36" }
  - host: 10.63.10.37
    config:
      server.labels: { zone: "z2", az: "az2", rack: "r2", host: "37" }

  - host: 10.63.10.38
    config:
      server.labels: { zone: "z3", az: "az3", rack: "r1", host: "38" }
  - host: 10.63.10.39
    config:
      server.labels: { zone: "z3", az: "az3", rack: "r1", host: "39" }
  - host: 10.63.10.40
    config:
      server.labels: { zone: "z3", az: "az3", rack: "r2", host: "40" }
  - host: 10.63.10.41
    config:
      server.labels: { zone: "z3", az: "az3", rack: "r2", host: "41" }
```

In the preceding example, `zone` is the logical availability zone layer that controls the isolation of replicas (three replicas in the example cluster).

Considering that the AZs might be scaled out in the future, the three-layer label structure (`az`, `rack`, and `host`) is not directly adopted. Assuming that `AZ2`, `AZ3`, and `AZ4` are to be scaled out, you only need to scale out the AZs in the corresponding availability zone and scale out the racks in the corresponding AZ.

If this three-layer label structure is directly adopted, after scaling out an AZ, you might need to apply new labels and the data in TiKV needs to be rebalanced.
### High availability and disaster recovery analysis

The multiple AZs in one region deployment can guarantee that if one AZ fails, the cluster can automatically recover services without manual intervention. Data consistency is also guaranteed. Note that scheduling policies are used to optimize performance, but when a failure occurs, these policies prioritize availability over performance.
