# Secondary index usage and query concurrency considerations

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/tidb-best-practices.md`
- Source Title: `TiDB Best Practices`
- Source Heading Path: `TiDB Best Practices > Basic concepts > Secondary index`
- Source Line Ranges: `81-137`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `secondary-indexes`, `global-indexes`, `covering-index`, `composite-indexes`, `query-concurrency`, `index-lookup`, `reverse-scan`, `optimizer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0066_49d73e5be5`
- Source ID: `tidb-docs-8.1:best-practices/tidb-best-practices.md#secondary-index`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0a2d7058880c883e102848eca987fa454865faffb91bf5aa11e58c246edb1aa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/tidb-best-practices#secondary-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/tidb-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB secondary index behavior, covering index and composite index design, index lookup versus table scan, query concurrency variables, ordered index reads, or reverse index scan overhead.
- Retrieval Keywords: secondary index, global indexes, covering index, composite index, Index cidx (c1, c2, c3), Index c12 (c1, c2), index lookup, row ID, tidb_distsql_scan_concurrency, tidb_index_lookup_size, tidb_index_lookup_concurrency, tidb_index_serial_scan_concurrency, reverse index scan, parallel + pipeline, primary key integer
- Follow-up Guidance: The source also points to the system variables `tidb_distsql_scan_concurrency`, `tidb_index_lookup_size`, `tidb_index_lookup_concurrency`, and `tidb_index_serial_scan_concurrency` for query concurrency behavior.
- Classification Note: This is classified as performance for SQL because the content explains how secondary indexes, index access patterns, and TiDB query concurrency settings affect query latency and optimizer behavior.

## Official Source Content

### Secondary index

TiDB supports the complete secondary indexes, which are also global indexes. Many queries can be optimized by index. Thus, it is important for applications to make good use of secondary indexes.

Lots of MySQL experience is also applicable to TiDB. It is noted that TiDB has its unique features. The following are a few notes when using secondary indexes in TiDB.

* The more secondary indexes, the better?

    Secondary indexes can speed up queries, but adding an index has side effects. The previous section introduces the storage model of indexes. For each additional index, there will be one more Key-Value when inserting a row. Therefore, the more indexes, the slower the writing speed and the more space it takes up.

    In addition, too many indexes affects the runtime of the optimizer, and inappropriate indexes mislead the optimizer. Thus, more secondary indexes does not mean better performance.

* Which columns should create indexes?

    As is mentioned above, index is important but the number of indexes should be proper. You must create appropriate indexes according to the application characteristics. In principle, you need to create an index on the columns involved in the query to improve the performance. The following are situations that need to create indexes:

    - For columns with a high degree of differentiation, filtered rows are remarkably reduced through indexes.
    - If there are multiple query criteria, you can choose composite indexes. Note to put the columns with the equivalent condition before composite indexes.

    For example, if a commonly used query is `select * from t where c1 = 10 and c2 = 100 and c3 > 10`, you can create a composite index `Index cidx (c1, c2, c3)`. In this way, you can use the query condition to create an index prefix and then scan.

* The difference between querying through indexes and directly scanning the table

    TiDB has implemented global indexes, so indexes and data of the table are not necessarily on the same data sharding. When querying through indexes, it should firstly scan indexes to get the corresponding row ID and then use the row ID to get the data. Thus, this method involves two network requests and has a certain performance overhead.

    If the query involves lots of rows, scanning index proceeds concurrently. When the first batch of results is returned, getting the data of the table can then proceed. Therefore, this is a parallel + pipeline model. Though the two accesses create overhead, the latency is not high.

    The following two conditions do not have the problem of two accesses:

    - Columns of the index have already met the query requirement. Assume that the `c` column on the `t` table has an index and the query is `select c from t where c > 10;`. At this time, all needed data can be obtained if you access the index. This situation is called `Covering Index`. But if you focus more on the query performance, you can put into index a portion of columns that do not need to be filtered but need to be returned in the query result, creating composite index. Take `select c1, c2 from t where c1 > 10;` as an example. You can optimize this query by creating composite index `Index c12 (c1, c2)`.

    - The primary key of the table is integer. In this case, TiDB uses the value of the primary key as row ID. Thus, if the query condition is on the primary key, you can directly construct the range of the row ID, scan the table data, and get the result.

* Query concurrency

    As data is distributed across many Regions, queries run in TiDB concurrently. But the concurrency by default is not high in case it consumes lots of system resources. Besides, the OLTP query usually does not involve a large amount of data and the low concurrency is enough. But for the OLAP query, the concurrency is high and TiDB modifies the query concurrency through the following system variables:

    - [`tidb_distsql_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_distsql_scan_concurrency):

        The concurrency of scanning data, including scanning the table and index data.

    - [`tidb_index_lookup_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_index_lookup_size):

        If it needs to access the index to get row IDs before accessing the table data, it uses a batch of row IDs as a single request to access the table data. This parameter sets the size of a batch. The larger batch increases latency, while the smaller one might lead to more queries. The proper size of this parameter is related to the amount of data that the query involves. Generally, no modification is required.

    - [`tidb_index_lookup_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_index_lookup_concurrency):

        If it needs to access the index to get row IDs before accessing the table data, the concurrency of getting data through row IDs every time is modified through this parameter.

* Ensure the order of results through indexes

    You can use indexes to filter or sort data. Firstly, get row IDs according to the index order. Then, return the row content according to the return order of row IDs. In this way, the returned results are ordered according to the index column. It has been mentioned earlier that the model of scanning index and getting row is parallel + pipeline. If the row is returned according to the index order, a high concurrency between two queries does not reduce latency. Thus, the concurrency is low by default, but it can be modified through the [`tidb_index_serial_scan_concurrency`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_index_serial_scan_concurrency) variable.

* Reverse index scan

    TiDB supports scanning an ascending index in reverse order, at a speed slower than normal scan by 20%. If the data is changed frequently and thus too many versions exist, the performance overhead might be higher. It is recommended to avoid reverse index scans as much as possible.
