# TiDB architecture and component FAQs

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/tidb-faq.md`
- Source Title: `TiDB Architecture FAQs`
- Source Heading Path: `TiDB Architecture FAQs | TiDB Architecture FAQs > TiDB introduction and architecture | TiDB Architecture FAQs > TiDB introduction and architecture > What is TiDB? | TiDB Architecture FAQs > TiDB introduction and architecture > What is TiDB's architecture? | TiDB Architecture FAQs > TiDB introduction and architecture > Is TiDB based on MySQL? | TiDB Architecture FAQs > TiDB introduction and architecture > What is the respective responsibility of TiDB, TiKV and PD (Placement Driver)? | TiDB Architecture FAQs > TiDB introduction and architecture > Is it easy to use TiDB? | TiDB Architecture FAQs > TiDB introduction and architecture > How is TiDB compatible with MySQL? | TiDB Architecture FAQs > TiDB introduction and architecture > Does TiDB support distributed transactions? | TiDB Architecture FAQs > TiDB introduction and architecture > What programming language can I use to work with TiDB? | TiDB Architecture FAQs > TiDB introduction and architecture > Can I use other Key-Value storage engines with TiDB? | TiDB Architecture FAQs > TiDB introduction and architecture > In addition to the TiDB documentation, are there any other ways to acquire TiDB knowledge? | TiDB Architecture FAQs > TiDB introduction and architecture > What is the length limit for the TiDB user name? | TiDB Architecture FAQs > TiDB introduction and architecture > What are the limits on the number of columns and row size in TiDB? | TiDB Architecture FAQs > TiDB introduction and architecture > Does TiDB support XA? | TiDB Architecture FAQs > TiDB introduction and architecture > How could TiDB support high concurrent `INSERT` or `UPDATE` operations to the columnar storage engine (TiFlash) without hurting performance? | TiDB Architecture FAQs > TiDB introduction and architecture > What kind of consistency does TiFlash provide? | TiDB Architecture FAQs > TiDB techniques | TiDB Architecture FAQs > TiDB techniques > TiKV for data storage | TiDB Architecture FAQs > TiDB techniques > TiDB for data computing | TiDB Architecture FAQs > TiDB techniques > PD for scheduling`
- Source Line Ranges: `5-131`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `sql`
- Topic Tags: `architecture`, `mysql-compatibility`, `distributed-transactions`, `storage-engines`, `component-roles`, `limits`, `xa`, `tiflash`, `consistency`, `learning-resources`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0038_a29c5b53b0`
- Source ID: `tidb-docs-8.1:faq/tidb-faq.md#tidb-architecture-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5178ca1edd206950e5139a938632b2ef94531bc0eafd1bee94a0167a37509551`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/tidb-faq#tidb-architecture-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/tidb-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering general TiDB architecture and compatibility questions, including component roles, distributed transactions, supported storage engines, TiFlash consistency, XA support, and documented limits such as username length, column count, and row size.
- Retrieval Keywords: What is TiDB, TiDB architecture, TiDB server, PD Placement Driver, TiKV server, SQL computing layer, distributed Key-Value storage engine, cluster manager, allocates timestamps, data placement and load balancing, MySQL compatible, majority of MySQL 8.0 syntax, does not support triggers stored procedures user-defined functions, distributed transactions, two-phase commit, Percolator, timestamp allocator, multi-data centers, supported storage engines, ./bin/tidb-server -h, -store string, tikv, mocktikv, unistore, TiDB user name length limit, 32 characters, maximum number of columns 1017, up to 4096, maximum size of a single row 6 MB, up to 120 MB, Does TiDB support XA, Atomikos, com.mysql.jdbc.jdbc2.optional.MysqlXADataSource, JTA/XA, TiFlash, DeltaTree, learner role, Raft group, DML operations do not have to wait for the acknowledgment of TiFlash, strong data consistency, TSO check
- Follow-up Guidance: For more details referenced in this FAQ, the content points to TiDB architecture, TiDB storage, TiDB computing, TiDB scheduling, Compatibility with MySQL, TiDB Limitations, and TiFlash overview pages.
- Classification Note: This chunk is classified as architecture because the official content explains what TiDB is, how TiDB, TiKV, PD, and TiFlash function, and what core compatibility and transaction properties the system provides.

## Official Source Content

# TiDB Architecture FAQs

This document lists the Most Frequently Asked Questions about TiDB.
## TiDB introduction and architecture
### What is TiDB?

[TiDB](https://github.com/pingcap/tidb) is an open-source distributed SQL database that supports Hybrid Transactional and Analytical Processing (HTAP) workloads. It is MySQL compatible and features horizontal scalability, strong consistency, and high availability. The goal of TiDB is to provide users with a one-stop database solution that covers OLTP (Online Transactional Processing), OLAP (Online Analytical Processing), and HTAP services. TiDB is suitable for various use cases that require high availability and strong consistency with large-scale data.
### What is TiDB's architecture?

The TiDB cluster has three components: the TiDB server, the PD (Placement Driver) server, and the TiKV server. For more details, see [TiDB architecture](https://docs.pingcap.com/tidb/stable/tidb-architecture), [TiDB storage](https://docs.pingcap.com/tidb/stable/tidb-storage), [TiDB computing](https://docs.pingcap.com/tidb/stable/tidb-computing), and [TiDB scheduling](https://docs.pingcap.com/tidb/stable/tidb-scheduling).
### Is TiDB based on MySQL?

No. TiDB supports MySQL syntax and protocol, but it is a new open source database that is developed and maintained by PingCAP, Inc.
### What is the respective responsibility of TiDB, TiKV and PD (Placement Driver)?

- TiDB works as the SQL computing layer, mainly responsible for parsing SQL, specifying query plan, and generating executor.
- TiKV works as a distributed Key-Value storage engine, used to store the real data. In short, TiKV is the storage engine of TiDB.
- PD works as the cluster manager of TiDB, which manages TiKV metadata, allocates timestamps, and makes decisions for data placement and load balancing.
### Is it easy to use TiDB?

Yes, it is. When all the required services are started, you can use TiDB as easily as a MySQL server. You can replace MySQL with TiDB to power your applications without changing a single line of code in most cases. You can also manage TiDB using the popular MySQL management tools.
### How is TiDB compatible with MySQL?

Currently, TiDB supports the majority of MySQL 8.0 syntax, but does not support triggers, stored procedures, and user-defined functions. For more details, see [Compatibility with MySQL](https://docs.pingcap.com/tidb/stable/mysql-compatibility).
### Does TiDB support distributed transactions?

Yes. TiDB distributes transactions across your cluster, whether it is a few nodes in a single location or many [nodes across multiple data centers](https://docs.pingcap.com/tidb/stable/multi-data-centers-in-one-city-deployment).

Inspired by Google's Percolator, the transaction model in TiDB is mainly a two-phase commit protocol with some practical optimizations. This model relies on a timestamp allocator to assign the monotone increasing timestamp for each transaction, so conflicts can be detected. [PD](https://docs.pingcap.com/tidb/stable/tidb-architecture#placement-driver-pd-server) works as the timestamp allocator in a TiDB cluster.
### What programming language can I use to work with TiDB?

Any language supported by MySQL client or driver.
### Can I use other Key-Value storage engines with TiDB?

Yes. In addition to TiKV, TiDB supports standalone storage engines such as UniStore and MockTiKV. Note that in later TiDB releases, MockTiKV might NO LONGER be supported.

To check all TiDB-supported storage engines, use the following command:

```shell
./bin/tidb-server -h
```

The output is as follows:

```shell
Usage of ./bin/tidb-server:
  -L string
        log level: info, debug, warn, error, fatal (default "info")
  -P string
        tidb server port (default "4000")
  -V    print version information and exit (default false)
.........
  -store string
        registered store name, [tikv, mocktikv, unistore] (default "unistore")
  ......
```
### In addition to the TiDB documentation, are there any other ways to acquire TiDB knowledge?

- [TiDB documentation](https://docs.pingcap.com/): the most important and timely way to get TiDB related knowledge.
- [TiDB blogs](https://www.pingcap.com/blog/): learn technical articles, product insights, and case studies.
- [PingCAP Education](https://www.pingcap.com/education/?from=en): take online courses and certification programs.
### What is the length limit for the TiDB user name?

32 characters at most.
### What are the limits on the number of columns and row size in TiDB?

- The maximum number of columns in TiDB defaults to 1017. You can adjust the number up to 4096.
- The maximum size of a single row defaults to 6 MB. You can increase the number up to 120 MB.

For more information, see [TiDB Limitations](https://docs.pingcap.com/tidb/stable/tidb-limitations).
### Does TiDB support XA?

No. The JDBC driver of TiDB is MySQL Connector/J. When using Atomikos, set the data source to `type="com.mysql.jdbc.jdbc2.optional.MysqlXADataSource"`. TiDB does not support the connection with MySQL JDBC XADataSource. MySQL JDBC XADataSource only works for MySQL (for example, using DML to modify the `redo` log).

After you configure the two data sources of Atomikos, set the JDBC drives to XA. When Atomikos operates TM and RM (DB), Atomikos sends the command including XA to the JDBC layer. Taking MySQL for an example, when XA is enabled in the JDBC layer, JDBC will send a series of XA logic operations to InnoDB, including using DML to change the `redo` log. This is the operation of the two-phase commit. The current TiDB version does not support the upper application layer JTA/XA and does not parse XA operations sent by Atomikos.

As a standalone database, MySQL can only implement across-database transactions using XA; while TiDB supports distributed transactions using Google Percolator transaction model and its performance stability is higher than XA, so TiDB does not support JTA/XA and there is no need for TiDB to support XA.
### How could TiDB support high concurrent `INSERT` or `UPDATE` operations to the columnar storage engine (TiFlash) without hurting performance?

- [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview) introduces a special structure named DeltaTree to process the modification of the columnar engine.
- TiFlash acts as the learner role in a Raft group, so it does not vote for the log commit or writes. This means that DML operations do not have to wait for the acknowledgment of TiFlash, which is why TiFlash does not slow down the OLTP performance. In addition, TiFlash and TiKV work in separate instances, so they do not affect each other.
### What kind of consistency does TiFlash provide?

TiFlash maintains strong data consistency by default. The raft learner process updates the data. There is also a TSO check to ensure the data in queries is fully consistent with the transaction. For more information, see [Asynchronous replication](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#asynchronous-replication) and [Consistency](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#consistency).
## TiDB techniques
### TiKV for data storage

See [TiDB Internal (I) - Data Storage](https://www.pingcap.com/blog/tidb-internal-data-storage/?from=en).
### TiDB for data computing

See [TiDB Internal (II) - Computing](https://www.pingcap.com/blog/tidb-internal-computing/?from=en).
### PD for scheduling

See [TiDB Internal (III) - Scheduling](https://www.pingcap.com/blog/tidb-internal-scheduling/?from=en).
