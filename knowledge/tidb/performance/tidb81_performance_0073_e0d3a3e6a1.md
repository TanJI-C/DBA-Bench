# Index selection overview and table access operators

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/choose-index.md`
- Source Title: `Index Selection`
- Source Heading Path: `Index Selection | Index Selection > Access tables | Index Selection > Access tables > Operators for accessing tables`
- Source Line Ranges: `5-30`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`, `tiflash`
- Topic Tags: `index-selection`, `table-access`, `operators`, `point-get`, `batch-point-get`, `tablereader`, `indexreader`, `indexlookupreader`, `indexmerge`, `tiflash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0073_e0d3a3e6a1`
- Source ID: `tidb-docs-8.1:choose-index.md#index-selection`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dd2c8e0288fc86a957ec0e5641889eba613a52d7d02e89a72eee3cc81c69f347`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/choose-index#index-selection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/choose-index.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which table access operator TiDB can choose and what trigger conditions, scenarios, and trade-offs apply for PointGet, BatchPointGet, TableReader, IndexReader, IndexLookupReader, and IndexMerge.
- Retrieval Keywords: Index Selection, Access tables, Operators for accessing tables, PointGet, BatchPointGet, TableReader, IndexReader, IndexLookupReader, IndexMerge, _tidb_rowid, TiKV, TiFlash, kvget interface, coprocessor interface, multi-valued index
- Follow-up Guidance: It also points to optimizer hints and the "Explain Statements Using Index Merge" document for more details on using IndexMerge.
- Classification Note: This is classified as performance because the content explains how different table access operators and index choices affect SQL execution efficiency when reading data from storage engines.

## Official Source Content

# Index Selection

Reading data from storage engines is one of the most time-consuming steps during the SQL execution. Currently, TiDB supports reading data from different storage engines and different indexes. Query execution performance depends largely on whether you select a suitable index or not.

This document introduces how to select an index to access a table, and some related ways to control index selection.
## Access tables

Before introducing index selection, it is important to understand the ways TiDB accesses tables, what triggers each way, what differences each way makes, and what the pros and cons are.
### Operators for accessing tables

| Operator | Trigger Conditions | Applicable Scenarios | Explanations |
| :------- | :------- | :------- | :---- |
| PointGet / BatchPointGet | When accessing tables in one or more single point ranges. | Any scenario | If triggered, it is usually considered as the fastest operator, since it calls the kvget interface directly to perform the calculations rather than calls the coprocessor interface.  |
| TableReader | None | Any scenario | This TableReader operator is for TiKV. It is generally considered as the least efficient operator that scans table data directly from the TiKV layer. It can be selected only if there is a range query on the `_tidb_rowid` column, or if there are no other operators for accessing tables to choose from. |
| TableReader | A table has a replica on the TiFlash node. | There are fewer columns to read, but many rows to evaluate.  | This TableReader operator is for TiFlash. TiFlash is column-based storage. If you need to calculate a small number of columns and a large number of rows, it is recommended to choose this operator. |
| IndexReader | A table has one or more indexes, and the columns needed for the calculation are included in the indexes. | When there is a smaller range query on the indexes, or when there is an order requirement for indexed columns. | When multiple indexes exist, a reasonable index is selected based on the cost estimation. |
| IndexLookupReader | A table has one or more indexes, and the columns needed for calculation are not completely included in the indexes. | Same as IndexReader. |  Since the index does not completely cover calculated columns, TiDB needs to retrieve rows from a table after reading indexes. There is an extra cost compared to the IndexReader operator. |
| IndexMerge | A table has multiple indexes or a multi-valued index. | When a multi-valued index or multiple indexes are used. | To use the operator, you can specify the [optimizer hints](https://docs.pingcap.com/tidb/stable/optimizer-hints), or let the optimizer to automatically select this operator based on cost estimation. For details, see [Explain Statements Using Index Merge](https://docs.pingcap.com/tidb/stable/explain-index-merge). |

> **Note:**
>
> The TableReader operator is based on the `_tidb_rowid` column index, and TiFlash uses a column storage index, so the selection of index is the selection of an operator for accessing tables.
