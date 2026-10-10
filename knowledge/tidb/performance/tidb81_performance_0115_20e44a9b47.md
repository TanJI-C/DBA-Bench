# TiDB testing FAQs: benchmarking, scaling, and MySQL comparison

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > TiDB testing | TiDB Cluster Management FAQs > TiDB testing > What is the performance test result for TiDB using Sysbench? | TiDB Cluster Management FAQs > TiDB testing > What's the relationship between the TiDB cluster capacity (QPS) and the number of nodes? How does TiDB compare to MySQL? | TiDB Cluster Management FAQs > TiDB testing > The performance test of MySQL and TiDB by our DBA shows that the performance of a standalone TiDB is not as good as MySQL`
- Source Line Ranges: `423-445`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `tikv`, `shared`
- Topic Tags: `benchmarking`, `sysbench`, `qps`, `tps`, `horizontal-scaling`, `mysql-comparison`, `distributed-transactions`, `pushdown`, `workload-fit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0115_20e44a9b47`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#tidb-testing`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43bbc59d05050b17e78a4a41b6b7ba1c8ba67199a863e48a8f0dece6f57c4dd0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#tidb-testing
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering testing or benchmarking questions about Sysbench results, TiDB QPS or TPS scaling with node count, or why standalone TiDB can perform worse than MySQL in small-table workloads.
- Retrieval Keywords: TiDB testing, Performance test result for TiDB using Sysbench, Sysbench, QPS, TPS, Insert TPS, within 10 nodes, 40% linear increase, MySQL comparison, standalone TiDB, strong consistency, complete distributed transactions, pushing down computing to the storage nodes, small size tables, below ten million level, counter table, Region, sharding
- Follow-up Guidance: The chunk points to the Performance test result for TiDB using Sysbench and explains that scenario differences matter more than spending too much time on benchmark comparison.
- Classification Note: This is classified as TiDB performance content because the official content discusses benchmark interpretation, scaling characteristics, throughput comparisons, and workload suitability.

## Official Source Content

## TiDB testing

This section describes common problems you might encounter during TiDB testing, their causes, and solutions.
### What is the performance test result for TiDB using Sysbench?

At the beginning, many users tend to do a benchmark test or a comparison test between TiDB and MySQL. We have also done a similar official test and find the test result is consistent at large, although the test data has some bias. Because the architecture of TiDB differs greatly from MySQL, it is hard to find a benchmark point. The suggestions are as follows:

- Do not spend too much time on the benchmark test. Pay more attention to the difference of scenarios using TiDB.
- See [Performance test result for TiDB using Sysbench](https://docs.pingcap.com/tidb/stable/benchmark/v3.0-performance-benchmarking-with-sysbench).
### What's the relationship between the TiDB cluster capacity (QPS) and the number of nodes? How does TiDB compare to MySQL?

- Within 10 nodes, the relationship between TiDB write capacity (Insert TPS) and the number of nodes is roughly 40% linear increase. Because MySQL uses single-node write, its write capacity cannot be scaled.
- In MySQL, the read capacity can be increased by adding secondary database, but the write capacity cannot be increased except using sharding, which has many problems.
- In TiDB, both the read and write capacity can be easily increased by adding more nodes.
### The performance test of MySQL and TiDB by our DBA shows that the performance of a standalone TiDB is not as good as MySQL

TiDB is designed for scenarios where sharding is used because the capacity of a MySQL standalone is limited, and where strong consistency and complete distributed transactions are required. One of the advantages of TiDB is pushing down computing to the storage nodes to execute concurrent computing.

TiDB is not suitable for tables of small size (such as below ten million level), because its strength in concurrency cannot be shown with a small size of data and limited Regions. A typical example is the counter table, in which records of a few lines are updated high frequently. In TiDB, these lines become several Key-Value pairs in the storage engine, and then settle into a Region located on a single node. The overhead of background replication to guarantee strong consistency and operations from TiDB to TiKV leads to a poorer performance than a MySQL standalone.
