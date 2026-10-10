# TiKV overview, architecture, transactions, and coprocessor

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-overview.md`
- Source Title: `TiKV Overview`
- Source Heading Path: `TiKV Overview | TiKV Overview > Architecture Overview | TiKV Overview > Architecture Overview > Region and RocksDB | TiKV Overview > Architecture Overview > Region and Raft Consensus Algorithm | TiKV Overview > Distributed Transaction | TiKV Overview > TiKV Coprocessor`
- Source Line Ranges: `5-36`
- Source Scope: `shared`
- Primary Component: `tikv`
- Related Components: `pd`, `tidb`
- Topic Tags: `overview`, `architecture`, `region`, `rocksdb`, `raft`, `replication`, `leader`, `learner`, `scaling`, `transactions`, `two-phase-commit`, `coprocessor`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0114_e6950db9fc`
- Source ID: `tidb-docs-8.1:tikv-overview.md#tikv-overview`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6e8af9f35a95432a9fb8a8deb9ce0b81fde78e727a725ede0264f772ace7f66`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-overview#tikv-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to retrieve an official TiKV overview covering storage architecture, Region and Raft behavior, distributed transactions, and TiKV Coprocessor processing.
- Retrieval Keywords: TiKV Overview, Architecture Overview, Region, Store, RocksDB, Raft consensus algorithm, multi-raft-group replica mechanism, Peer, leader, Learner replica, Follower replica, Leader Transfer, PD component, horizontal scalability, distributed transaction, two-phase commit, ACID compliance, TiKV Coprocessor, each request sent to TiKV Coprocessor only involves the data of one Region, Region size 96 MiB, split threshold 144 MiB, merge threshold 20 MiB
- Follow-up Guidance: The source also points to TiDB Optimistic Transaction Model for details about two-phase commit in distributed transactions.
- Classification Note: This chunk is classified as architecture because it describes TiKV as the storage layer of TiDB and explains Regions, Raft replication, RocksDB layout, PD balancing, transaction support, and coprocessor execution.

## Official Source Content

# TiKV Overview

TiKV is a distributed and transactional key-value database, which provides transactional APIs with ACID compliance. With the implementation of the [Raft consensus algorithm](https://raft.github.io/raft.pdf) and consensus state stored in RocksDB, TiKV guarantees data consistency between multiple replicas and high availability. As the storage layer of the TiDB distributed database, TiKV provides the read and write service, and persist the written data from applications. It also stores the statistics data of the TiDB cluster.
## Architecture Overview

TiKV implements the multi-raft-group replica mechanism based on the design of Google Spanner. A Region is a basic unit of the key-value data movement and refers to a data range in a Store. Each Region is replicated to multiple nodes. These multiple replicas form a Raft group. A replica of a Region is called a Peer. Typically there are 3 peers in a Region. One of them is the leader, which provides the read and write services. The PD component balances all the Regions automatically to guarantee that the read and write throughput is balanced among all the nodes in the TiKV cluster. With PD and carefully designed Raft groups, TiKV excels in horizontal scalability and can easily scale to store more than 100 TBs of data.

![TiKV Architecture](/media/tikv-arch.png)
### Region and RocksDB

There is a RocksDB database within each Store and it stores data into the local disk. All the Region data are stored in the same RocksDB instance in each Store. All the logs used for the Raft consensus algorithm is stored in another RocksDB instance in each Store. This is because the performance of sequential I/O is better than random I/O. With different RocksDB instances storing raft logs and Region data, TiKV combines all the data write operations of raft logs and TiKV Regions into one I/O operation to improve the performance.
### Region and Raft Consensus Algorithm

Data consistency between replicas of a Region is guaranteed by the Raft Consensus Algorithm. Only the leader of the Region can provide the writing service, and only when the data is written to the majority of replicas of a Region, the write operation succeeds.

TiKV tries to keep an appropriate size for each Region in the cluster. The Region size is currently 96 MiB by default. This mechanism helps the PD component to balance Regions among nodes in a TiKV cluster. When the size of a Region exceeds a threshold (144 MiB by default), TiKV splits it into two or more Regions. When the size of a Region is smaller than the threshold (20 MiB by default), TiKV merges the two smaller adjacent Regions into one Region.

When PD moves a replica from one TiKV node to another, it firstly adds a Learner replica on the target node, after the data in the Learner replica is nearly the same as that in the Leader replica, PD changes it to a Follower replica and removes the Follower replica on the source node.

Moving Leader replica from one node to another has a similar mechanism. The difference is that after the Learner replica becomes the Follower replica, there is a "Leader Transfer" operation in which the Follower replica actively proposes an election to elect itself as the Leader. Finally, the new Leader removes the old Leader replica in the source node.
## Distributed Transaction

TiKV supports distributed transactions. Users (or TiDB) can write multiple key-value pairs without worrying about whether they belong to the same Region. TiKV uses two-phase commit to achieve ACID constraints. See [TiDB Optimistic Transaction Model](https://docs.pingcap.com/tidb/stable/optimistic-transaction) for details.
## TiKV Coprocessor

TiDB pushes some data computation logic to TiKV Coprocessor. TiKV Coprocessor processes the computation for each Region. Each request sent to TiKV Coprocessor only involves the data of one Region.
