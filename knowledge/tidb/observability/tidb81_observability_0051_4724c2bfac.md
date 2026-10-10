# PD scheduler, service, and storage metrics

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/grafana-pd-dashboard.md`
- Source Title: `Key Monitoring Metrics of PD`
- Source Heading Path: `Key Monitoring Metrics of PD > Scheduler | Key Monitoring Metrics of PD > gRPC | Key Monitoring Metrics of PD > etcd | Key Monitoring Metrics of PD > TiDB | Key Monitoring Metrics of PD > Heartbeat | Key Monitoring Metrics of PD > Region storage`
- Source Line Ranges: `95-157`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`, `dashboard`, `shared`
- Topic Tags: `scheduler`, `grpc`, `etcd`, `heartbeat`, `region storage`, `raft`, `latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0051_4724c2bfac`
- Source ID: `tidb-docs-8.1:grafana-pd-dashboard.md#scheduler`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7714351aa69e31f9b45bd000cb2d9288b214970583e6a8d7a955e45073b71315`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/grafana-pd-dashboard#scheduler
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/grafana-pd-dashboard.md

## Retrieval Guidance

- Use When: Use this when you need scheduler activity, gRPC, etcd, TiDB request handling, heartbeat, or Region storage metrics from the PD dashboard.
- Retrieval Keywords: Scheduler, gRPC, etcd, TiDB, Heartbeat, Region storage, Scheduler is running, Balance leader movement, Balance Region movement, Balance leader event, Balance Region event, Replica checker, Rule checker, Region merge checker, Filter target, Filter source, Balance Direction, Completed commands rate, 99% Completed commands duration, Handle transactions count, 99% WAL fsync duration, Raft term, PD Server TSO handle time and Client recv time, Handle requests duration, Heartbeat region event QPS, Region heartbeat report error, 99% Region heartbeat latency, Syncer Index, history last index
- Follow-up Guidance: This section describes scheduler, service, heartbeat, and region storage panels with their listed metrics.
- Classification Note: This chunk is an observability reference for PD scheduler, gRPC, etcd, TiDB, heartbeat, and Region storage metrics.

## Official Source Content

## Scheduler

- Scheduler is running: The current running schedulers
- Balance leader movement: The leader movement details among TiKV instances
- Balance Region movement: The Region movement details among TiKV instances
- Balance leader event: The count of balance leader events
- Balance Region event: The count of balance Region events
- Balance leader scheduler: The inner status of balance leader scheduler
- Balance Region scheduler: The inner status of balance Region scheduler
- Replica checker: The replica checker's status
- Rule checker: The rule checker's status
- Region merge checker: The merge checker's status
- Filter target: The number of attempts that the store is selected as the scheduling target but failed to pass the filter
- Filter source: The number of attempts that the store is selected as the scheduling source but failed to pass the filter
- Balance Direction: The number of times that the Store is selected as the target or source of scheduling

![PD Dashboard - Scheduler metrics](/media/pd-dashboard-scheduler-v4.png)
## gRPC

- Completed commands rate: The rate per command type at which gRPC commands are completed
- 99% Completed commands duration: The rate per command type at which gRPC commands are completed (P99)

![PD Dashboard - gRPC metrics](/media/pd-dashboard-grpc-v2.png)
## etcd

- Handle transactions count: The rate at which etcd handles transactions
- 99% Handle transactions duration: The transaction handling rate (P99)
- 99% WAL fsync duration: The time consumed for writing WAL into the persistent storage. It is less than `1s` (P99)
- 99% Peer round trip time seconds: The network latency for etcd (P99) | The value is less than `1s`
- etcd disk WAL fsync rate: The rate of writing WAL into the persistent storage
- Raft term: The current term of Raft
- Raft committed index: The last committed index of Raft
- Raft applied index: The last applied index of Raft

![PD Dashboard - etcd metrics](/media/pd-dashboard-etcd-v2.png)
## TiDB

- PD Server TSO handle time and Client recv time: The duration between PD receiving the TSO request and the PD client getting the TSO response
- Handle requests count: The count of TiDB requests
- Handle requests duration: The time consumed for handling TiDB requests. It should be less than `100ms` (P99)

![PD Dashboard - TiDB metrics](/media/pd-dashboard-tidb-v4.png)
## Heartbeat

- Heartbeat region event QPS: The QPS of handling heartbeat messages, including updating the cache and persisting data
- Region heartbeat report: The count of heartbeats reported to PD per instance
- Region heartbeat report error: The count of heartbeats with the `error` status
- Region heartbeat report active: The count of heartbeats with the `ok` status
- Region schedule push: The count of corresponding schedule commands sent from PD per TiKV instance
- 99% Region heartbeat latency: The heartbeat latency per TiKV instance (P99)

![PD Dashboard - Heartbeat metrics](/media/pd-dashboard-heartbeat-v4.png)
## Region storage

- Syncer Index: The maximum index in the Region change history recorded by the leader
- history last index: The last index where the Region change history is synchronized successfully with the follower

![PD Dashboard - Region storage](/media/pd-dashboard-region-storage.png)
