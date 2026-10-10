# DM architecture components and high availability

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-arch.md`
- Source Title: `Data Migration Architecture`
- Source Heading Path: `Data Migration Architecture | Data Migration Architecture > Architecture components | Data Migration Architecture > Architecture components > DM-master | Data Migration Architecture > Architecture components > DM-worker | Data Migration Architecture > Architecture components > dmctl | Data Migration Architecture > Architecture features | Data Migration Architecture > Architecture features > High availability`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `shared`
- Topic Tags: `architecture`, `components`, `dm-master`, `dm-worker`, `dmctl`, `high-availability`, `task-scheduling`, `embedded-etcd`, `leader-election`, `full-export`, `full-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0019_32ce9a7425`
- Source ID: `tidb-docs-8.1:dm/dm-arch.md#data-migration-architecture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `067b97676adc004c31f845d1ccabd98f5499c5fdb1ac97abc9abf256c4b2daa9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-arch#data-migration-architecture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-arch.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about Data Migration architecture, the roles of DM-master, DM-worker, and dmctl, or how DM high availability and task rescheduling work.
- Retrieval Keywords: Data Migration Architecture, DM-master, DM-worker, dmctl, embedded etcd, leader election, high availability, task scheduling, cluster management, data migration task management, topology information, monitoring the running state, sharded tables, DDL migration, persisting the binlog data to the local storage, data migration subtasks, creating updating or dropping data migration tasks, checking the state of data migration tasks, handling errors of data migration tasks, verifying the configuration correctness, idle DM-worker nodes, MySQL/MariaDB nodes, full export, full import
- Follow-up Guidance: The source also notes that high availability is not supported when a data migration task is in the process of full export or import, and explains the reasons for each phase.
- Classification Note: The chunk is classified as architecture for the self-managed DM component because it describes DM architecture components and the official high-availability behavior of DM-master and DM-worker.

## Official Source Content

# Data Migration Architecture

This document introduces the architecture of Data Migration (DM).

DM consists of three components: DM-master, DM-worker, and dmctl.

![Data Migration architecture](/media/dm/dm-architecture-2.0.png)
## Architecture components
### DM-master

DM-master manages and schedules the operations of data migration tasks.

- Storing the topology information of the DM cluster
- Monitoring the running state of DM-worker processes
- Monitoring the running state of data migration tasks
- Providing a unified portal for the management of data migration tasks
- Coordinating the DDL migration of sharded tables in each instance under the sharding scenario
### DM-worker

DM-worker executes specific data migration tasks.

- Persisting the binlog data to the local storage
- Storing the configuration information of the data migration subtasks
- Orchestrating the operation of the data migration subtasks
- Monitoring the running state of the data migration subtasks

For more details of DM-worker, see [DM-worker Introduction](https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro).
### dmctl

dmctl is a command line tool used to control the DM cluster.

- Creating, updating, or dropping data migration tasks
- Checking the state of data migration tasks
- Handling errors of data migration tasks
- Verifying the configuration correctness of data migration tasks
## Architecture features
### High availability

When you deploy multiple DM-master nodes, all DM-master nodes use the embedded etcd to form a cluster. The DM-master cluster is used to store metadata such as cluster node information and task configuration. The leader node elected through etcd is used to provide services such as cluster management and data migration task management. Therefore, if the number of available DM-master nodes exceeds half of the deployed nodes, the DM cluster can normally provide services.

When the number of deployed DM-worker nodes exceeds the number of upstream MySQL/MariaDB nodes, the extra DM-worker nodes are idle by default. If a DM-worker node goes offline or is isolated from the DM-master leader, DM-master automatically schedules data migration tasks of the original DM-worker node to other idle DM-worker nodes. (If a DM-worker node is isolated, it automatically stops the data migration tasks on it); if there are no available idle DM-worker nodes, the data migration tasks of the original DM-worker are temporarily hung until one DM-worker node becomes idle, and then the tasks are automatically resumed.

> **Note:**
>
> When the data migration task is in the process of full export or import, the migration task does not support high availability. Here are the main reasons:
>
> - For the full export, MySQL does not support exporting from a specific snapshot point yet. This means that after the data migration task is rescheduled or restarted, the export cannot resume from the previous interruption point.
>
> - For the full import, DM-worker does not support reading exported full data across the nodes yet. This means that after the data migration task is scheduled to a new DM-worker node, you cannot read the exported full data on the original DM-worker node before the scheduling happens.
