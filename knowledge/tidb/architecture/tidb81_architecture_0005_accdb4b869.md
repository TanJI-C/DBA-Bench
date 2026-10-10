# Scenario overview and TiDB data distribution principles

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/high-concurrency-best-practices.md`
- Source Title: `Highly Concurrent Write Best Practices`
- Source Heading Path: `Highly Concurrent Write Best Practices | Highly Concurrent Write Best Practices > Target audience | Highly Concurrent Write Best Practices > Highly-concurrent write-intensive scenario | Highly Concurrent Write Best Practices > Data distribution principles in TiDB`
- Source Line Ranges: `5-48`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `high-concurrency`, `write-heavy`, `target-audience`, `workload-characteristics`, `data-distribution`, `regions`, `raft-group`, `leader-scheduling`, `hotspot-avoidance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0005_accdb4b869`
- Source ID: `tidb-docs-8.1:best-practices/high-concurrency-best-practices.md#highly-concurrent-write-best-practices`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d4e40fad176f77cc06a983e977f3f81a56bdc705d41b61dab9692517ae87373d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#highly-concurrent-write-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/high-concurrency-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when explaining TiDB data distribution and why high-concurrent write-heavy workloads depend on avoiding write hotspots across Regions and Region Leaders.
- Retrieval Keywords: Highly Concurrent Write Best Practices, highly-concurrent write-intensive scenario, write-heavy workloads, Data distribution principles in TiDB, Regions, 96M by default, Raft Group, Region Leader, Placement Driver, PD, Follower-Read, linearly scale read and write capacities, write hotspot, AUTO_INCREMENT primary key, monotonically increasing index
- Follow-up Guidance: The note defines no write hotspot as a write scenario without any `AUTO_INCREMENT` primary key or monotonically increasing index.
- Classification Note: This chunk is classified as architecture because it describes TiDB Region, Raft Group, and PD scheduling principles for distributing read and write pressure.

## Official Source Content

# Highly Concurrent Write Best Practices

This document describes best practices for handling highly-concurrent write-heavy workloads in TiDB, which can help to facilitate your application development.
## Target audience

This document assumes that you have a basic understanding of TiDB. It is recommended that you first read the following three blog articles that explain TiDB fundamentals, and [TiDB Best Practices](https://www.pingcap.com/blog/tidb-best-practice/):

+ [Data Storage](https://www.pingcap.com/blog/tidb-internal-data-storage/)
+ [Computing](https://www.pingcap.com/blog/tidb-internal-computing/)
+ [Scheduling](https://www.pingcap.com/blog/tidb-internal-scheduling/)
## Highly-concurrent write-intensive scenario

The highly concurrent write scenario often occurs when you perform batch tasks in applications, such as clearing and settlement. This scenario has the following features:

+ A huge volume of data
+ The need to import historical data into database in a short time
+ The need to read a huge volume of data from database in a short time

These features pose these challenges to TiDB:

+ The write or read capacity must be linearly scalable.
+ Database performance is stable and does not decrease as a huge volume of data is written concurrently.

For a distributed database, it is important to make full use of the capacity of all nodes and to prevent a single node from becoming the bottleneck.
## Data distribution principles in TiDB

To address the above challenges, it is necessary to start with the data segmentation and scheduling principle of TiDB. Refer to [Scheduling](https://www.pingcap.com/blog/tidb-internal-scheduling/) for more details.

TiDB splits data into Regions, each representing a range of data with a size limit of 96M by default. Each Region has multiple replicas, and each group of replicas is called a Raft Group. In a Raft Group, the Region Leader executes the read and write tasks (TiDB supports [Follower-Read](https://docs.pingcap.com/tidb/stable/follower-read)) within the data range. The Region Leader is automatically scheduled by the Placement Driver (PD) component to different physical nodes evenly to distribute the read and write pressure.

![TiDB Data Overview](/media/best-practices/tidb-data-overview.png)

In theory, if an application has no write hotspot, TiDB, by the virtue of its architecture, can not only linearly scale its read and write capacities, but also make full use of the distributed resources. From this point of view, TiDB is especially suitable for the high-concurrent and write-intensive scenario.

However, the actual situation often differs from the theoretical assumption.

> **Note:**
>
> No write hotspot in an application means the write scenario does not have any `AUTO_INCREMENT` primary key or monotonically increasing index.
