# Glossary terms across TiDB ecosystem concepts

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/glossary.md`
- Source Title: `Glossary`
- Source Heading Path: `Glossary | Glossary > A | Glossary > A > ACID | Glossary > B | Glossary > B > Batch Create Table | Glossary > B > Baseline Capturing | Glossary > B > Bucket | Glossary > C | Glossary > C > Cached Table | Glossary > C > Coalesce Partition | Glossary > C > Continuous Profiling | Glossary > D | Glossary > D > Dynamic Pruning | Glossary > I | Glossary > I > Index Merge | Glossary > I > In-Memory Pessimistic Lock | Glossary > L | Glossary > L > leader/follower/learner | Glossary > M | Glossary > M > MPP | Glossary > M > Multi-version concurrency control (MVCC) | Glossary > O | Glossary > O > Old value | Glossary > O > Operator | Glossary > O > Operator step | Glossary > P | Glossary > P > Partitioning | Glossary > P > pending/down | Glossary > P > Point Get | Glossary > P > Predicate columns | Glossary > Q | Glossary > Q > Quota Limiter | Glossary > R | Glossary > R > Raft Engine | Glossary > R > Region/peer/Raft group | Glossary > R > Region split | Glossary > R > restore | Glossary > S | Glossary > S > scheduler | Glossary > S > Store | Glossary > T | Glossary > T > Top SQL | Glossary > T > TSO`
- Source Line Ranges: `5-174`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `br`, `dashboard`, `pd`, `sql`, `ticdc`, `tidb`, `tiflash`, `tikv`
- Topic Tags: `glossary`, `transactions`, `partitioning`, `scheduling`, `storage`, `replication`, `query-optimization`, `profiling`, `backup-restore`, `timestamp-oracle`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0363_cc1c773589`
- Source ID: `tidb-docs-8.1:glossary.md#glossary`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1125b2ac1f895db56305449b1dee8e1757559754aa8031be8bdd198b01c2b480`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/glossary#glossary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/glossary.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs definitions of TiDB ecosystem glossary terms such as ACID, MVCC, MPP, Region, peer, Raft group, scheduler, TSO, Top SQL, or BR restore terminology.
- Retrieval Keywords: ACID, atomicity consistency isolation durability, Batch Create Table, Baseline Capturing, Bucket, Cached Table, Coalesce Partition, Continuous Profiling, Dynamic Pruning, Index Merge, In-Memory Pessimistic Lock, leader follower learner, MPP, Multi-version concurrency control, MVCC, Old value, Operator, Operator step, TransferLeader, AddPeer, RemovePeer, AddLearner, PromoteLearner, SplitRegion, Partitioning, pending down, Point Get, Predicate columns, Quota Limiter, Raft Engine, Region peer Raft group, Region split, restore, scheduler, balance-leader-scheduler, balance-region-scheduler, hot-region-scheduler, evict-leader-{store-id}, Store, tikv-server, Top SQL, TSO, Timestamp Oracle
- Follow-up Guidance: The glossary entry points to related detailed documents for topics such as Batch Create Table, TiDB transaction isolation levels, Continuous Profiling, TiFlash MPP mode, partitioned tables, statistics, Top SQL, and quota-related configuration items.
- Classification Note: This chunk is classified as reference content because it provides concise glossary definitions and exact term names across shared TiDB, TiKV, PD, TiFlash, TiCDC, BR, Dashboard, and SQL concepts.

## Official Source Content

# Glossary
## A
### ACID

ACID refers to the four key properties of a transaction: atomicity, consistency, isolation, and durability. Each of these properties is described below.

- **Atomicity** means that either all the changes of an operation are performed, or none of them are. TiDB ensures the atomicity of the [Region](#regionpeerraft-group) that stores the Primary Key to achieve the atomicity of transactions.

- **Consistency** means that transactions always bring the database from one consistent state to another. In TiDB, data consistency is ensured before writing data to the memory.

- **Isolation** means that a transaction in process is invisible to other transactions until it completes. This allows concurrent transactions to read and write data without sacrificing consistency. For more information, see [TiDB transaction isolation levels](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#tidb-transaction-isolation-levels).

- **Durability** means that once a transaction is committed, it remains committed even in the event of a system failure. TiKV uses persistent storage to ensure durability.
## B
### Batch Create Table

Batch Create Table is a feature introduced in TiDB v6.0.0. This feature is enabled default. When restoring data with a large number of tables (nearly 50000) using BR (Backup & Restore), the feature can greatly speed up the restore process by creating tables in batches. For details, see [Batch Create Table](https://docs.pingcap.com/tidb/stable/br/br-batch-create-table).
### Baseline Capturing

Baseline Capturing captures queries that meet capturing conditions and create bindings for them. It is used for [preventing regression of execution plans during an upgrade](https://docs.pingcap.com/tidb/stable/sql-plan-management#prevent-regression-of-execution-plans-during-an-upgrade).
### Bucket

A [Region](#regionpeerraft-group) is logically divided into several small ranges called bucket. TiKV collects query statistics by buckets and reports the bucket status to PD. For details, see the [Bucket design doc](https://github.com/tikv/rfcs/blob/master/text/0082-dynamic-size-region.md#bucket).
## C
### Cached Table

With the cached table feature, TiDB loads the data of an entire table into the memory of the TiDB server, and TiDB directly gets the table data from the memory without accessing TiKV, which improves the read performance.
### Coalesce Partition

Coalesce Partition is a way of decreasing the number of partitions in a Hash or Key partitioned table. For more information, see [Manage Hash and Key partitions](https://docs.pingcap.com/tidb/stable/partitioned-table#manage-hash-and-key-partitions).
### Continuous Profiling

Introduced in TiDB 5.3.0, Continuous Profiling is a way to observe resource overhead at the system call level. With the support of Continuous Profiling, TiDB provides performance insight as clear as directly looking into the database source code, and helps R&D and operation and maintenance personnel to locate the root cause of performance problems using a flame graph. For details, see [TiDB Dashboard Instance Profiling - Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling).
## D
### Dynamic Pruning

Dynamic pruning mode is one of the modes that TiDB accesses partitioned tables. In dynamic pruning mode, each operator supports direct access to multiple partitions. Therefore, TiDB no longer uses Union. Omitting the Union operation can improve the execution efficiency and avoid the problem of Union concurrent execution.
## I
### Index Merge

Index Merge is a method introduced in TiDB v4.0 to access tables. Using this method, the TiDB optimizer can use multiple indexes per table and merge the results returned by each index. In some scenarios, this method makes the query more efficient by avoiding full table scans. Since v5.4, Index Merge has become a GA feature.
### In-Memory Pessimistic Lock

The in-memory pessimistic lock is a new feature introduced in TiDB v6.0.0. When this feature is enabled, pessimistic locks are usually stored in the memory of the Region leader only, and are not persisted to disk or replicated through Raft to other replicas. This feature can greatly reduce the overhead of acquiring pessimistic locks and improve the throughput of pessimistic transactions.
## L
### leader/follower/learner

Leader/Follower/Learner each corresponds to a role in a Raft group of [peers](#regionpeerraft-group). The leader services all client requests and replicates data to the followers. If the group leader fails, one of the followers will be elected as the new leader. Learners are non-voting followers that only serves in the process of replica addition.
## M
### MPP

Starting from v5.0, TiDB introduces Massively Parallel Processing (MPP) architecture through TiFlash nodes, which shares the execution workloads of large join queries among TiFlash nodes. When the MPP mode is enabled, TiDB, based on cost, determines whether to use the MPP framework to perform the calculation. In the MPP mode, the join keys are redistributed through the Exchange operation while being calculated, which distributes the calculation pressure to each TiFlash node and speeds up the calculation. For more information, see [Use TiFlash MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode).
### Multi-version concurrency control (MVCC)

[MVCC](https://en.wikipedia.org/wiki/Multiversion_concurrency_control) is a concurrency control mechanism in TiDB and other databases. It processes the memory read by transactions to achieve concurrent access to TiDB, thereby avoiding blocking caused by conflicts between concurrent reads and writes.
## O
### Old value

The "original value" in the incremental change log output by TiCDC. You can specify whether the incremental change log output by TiCDC contains the "original value".
### Operator

An operator is a collection of actions that applies to a Region for scheduling purposes. Operators perform scheduling tasks such as "migrate the leader of Region 2 to Store 5" and "migrate replicas of Region 2 to Store 1, 4, 5".

An operator can be computed and generated by a [scheduler](#scheduler), or created by an external API.
### Operator step

An operator step is a step in the execution of an operator. An operator normally contains multiple Operator steps.

Currently, available steps generated by PD include:

- `TransferLeader`: Transfers leadership to a specified member
- `AddPeer`: Adds peers to a specified store
- `RemovePeer`: Removes a peer of a Region
- `AddLearner`: Adds learners to a specified store
- `PromoteLearner`: Promotes a specified learner to a voting member
- `SplitRegion`: Splits a specified Region into two
## P
### Partitioning

[Partitioning](https://docs.pingcap.com/tidb/stable/partitioned-table) refers to physically dividing a table into smaller table partitions, which can be done by partition methods such as RANGE, LIST, HASH, and KEY partitioning.
### pending/down

"Pending" and "down" are two special states of a peer. Pending indicates that the Raft log of followers or learners is vastly different from that of leader. Followers in pending cannot be elected as leader. "Down" refers to a state that a peer ceases to respond to leader for a long time, which usually means the corresponding node is down or isolated from the network.
### Point Get

Point get means reading a single row of data by a unique index or primary index, the returned resultset is up to one row.
### Predicate columns

In most cases, when executing SQL statements, the optimizer only uses statistics of some columns (such as columns in the `WHERE`, `JOIN`, `ORDER BY`, and `GROUP BY` statements). These used columns are called predicate columns. For details, see [Collect statistics on some columns](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-on-some-columns).
## Q
### Quota Limiter

Quota Limiter is an experimental feature introduced in TiDB v6.0.0. If the machine on which TiKV is deployed has limited resources, for example, with only 4v CPU and 16 G memory, and the foreground of TiKV processes too many read and write requests, the CPU resources used by the background are occupied to help process such requests, which affects the performance stability of TiKV. To avoid this situation, the [quota-related configuration items](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#quota) can be set to limit the CPU resources to be used by the foreground.
## R
### Raft Engine

Raft Engine is an embedded persistent storage engine with a log-structured design. It is built for TiKV to store multi-Raft logs. Since v5.4, TiDB supports using Raft Engine as the log storage engine. For details, see [Raft Engine](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#raft-engine).
### Region/peer/Raft group

Region is the minimal piece of data storage in TiKV, each representing a range of data (96 MiB by default). Each Region has three replicas by default. A replica of a Region is called a peer. Multiple peers of the same Region replicate data via the Raft consensus algorithm, so peers are also members of a Raft instance. TiKV uses Multi-Raft to manage data. That is, for each Region, there is a corresponding, isolated Raft group.
### Region split

Regions are generated as data writes increase. The process of splitting is called Region split.

The mechanism of Region split is to use one initial Region to cover the entire key space, and generate new Regions through splitting existing ones every time the size of the Region or the number of keys has reached a threshold.
### restore

Restore is the reverse of the backup operation. It is the process of bringing back the system to an earlier state by retrieving data from a prepared backup.
## S
### scheduler

Schedulers are components in PD that generate scheduling tasks. Each scheduler in PD runs independently and serves different purposes. The commonly used schedulers are:

- `balance-leader-scheduler`: Balances the distribution of leaders
- `balance-region-scheduler`: Balances the distribution of peers
- `hot-region-scheduler`: Balances the distribution of hot Regions
- `evict-leader-{store-id}`: Evicts all leaders of a node (often used for rolling upgrades)
### Store

A store refers to the storage node in the TiKV cluster (an instance of `tikv-server`). Each store has a corresponding TiKV instance.
## T
### Top SQL

Top SQL helps locate SQL queries that contribute to a high load of a TiDB or TiKV node in a specified time range. For details, see [Top SQL user document](https://docs.pingcap.com/tidb/stable/dashboard/top-sql).
### TSO

Because TiKV is a distributed storage system, it requires a global timing service, Timestamp Oracle (TSO), to assign a monotonically increasing timestamp. In TiKV, such a feature is provided by PD, and in Google [Spanner](http://static.googleusercontent.com/media/research.google.com/en//archive/spanner-osdi2012.pdf), this feature is provided by multiple atomic clocks and GPS.
