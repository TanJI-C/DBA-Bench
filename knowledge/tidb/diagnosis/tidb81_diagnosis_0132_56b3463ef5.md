# Hotspot concepts and common hotspot patterns

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-hot-spot-issues.md`
- Source Title: `Troubleshoot Hotspot Issues`
- Source Heading Path: `Troubleshoot Hotspot Issues | Troubleshoot Hotspot Issues > Common hotspots | Troubleshoot Hotspot Issues > Common hotspots > TiDB encoding rules | Troubleshoot Hotspot Issues > Common hotspots > Table hotspots | Troubleshoot Hotspot Issues > Common hotspots > Index hotspots`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `hotspots`, `rowid`, `tableid`, `indexid`, `key-encoding`, `table-hotspots`, `index-hotspots`, `write-hotspots`, `read-hotspots`, `region-splitting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0132_56b3463ef5`
- Source ID: `tidb-docs-8.1:troubleshoot-hot-spot-issues.md#troubleshoot-hotspot-issues`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7626575c5e64da0a6f52568c7e95f64348bc618702ffc85d2414f903f0665f9e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-hot-spot-issues#troubleshoot-hotspot-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-hot-spot-issues.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB key encoding rules and the basic patterns that make table or index hotspots appear.
- Retrieval Keywords: Troubleshoot Hotspot Issues, Common hotspots, TiDB encoding rules, Table hotspots, Index hotspots, TableID, IndexID, RowID, tablePrefix{tableID}_recordPrefixSep{rowID}, tablePrefix{tableID}_indexPrefixSep{indexID}_indexedColumnsValue, non-unique index, INSERT operation, Region split, write hotspot, read hotspot
- Follow-up Guidance: See the related hotspot identification and mitigation sections for how TiDB locates and scatters hotspot tables.
- Classification Note: This chunk explains hotspot concepts, TiDB encoding rules, and why table and index data can form hotspots.

## Official Source Content

# Troubleshoot Hotspot Issues

This document describes how to locate and resolve the problem of read and write hotspots.

As a distributed database, TiDB has a load balancing mechanism to distribute the application loads as evenly as possible to different computing or storage nodes, to make better use of server resources. However, in certain scenarios, some application loads cannot be well distributed, which can affect the performance and form a single point of high load, also known as a hotspot.

TiDB provides a complete solution to troubleshooting, resolving or avoiding hotspots. By balancing load hotspots, overall performance can be improved, including improving QPS and reducing latency.
## Common hotspots

This section describes TiDB encoding rules, table hotspots, and index hotspots.
### TiDB encoding rules

TiDB assigns a TableID to each table, an IndexID to each index, and a RowID to each row. By default, if the table uses an integer primary key, the value of the primary key is treated as the RowID. Among these IDs, TableID is unique in the entire cluster, while IndexID and RowID are unique in the table. The type of all these IDs is int64.

Each row of data is encoded as a key-value pair according to the following rule:

```
Key: tablePrefix{tableID}_recordPrefixSep{rowID}
Value: [col1, col2, col3, col4]
```

The `tablePrefix` and `recordPrefixSep` of the key are specific string constants, used to distinguish from other data in the KV space.

For Index data, the key-value pair is encoded according to the following rule:

```
Key: tablePrefix{tableID}_indexPrefixSep{indexID}_indexedColumnsValue
Value: rowID
```

Index data has two types: the unique index and the non-unique index.

- For unique indexes, you can follow the coding rules above.
- For non-unique indexes, a unique key cannot be constructed through this encoding, because the `tablePrefix{tableID}_indexPrefixSep{indexID}` of the same index is the same and the `ColumnsValue` of multiple rows might be the same. The encoding rule for non-unique indexes is as follows:

    ```
    Key: tablePrefix{tableID}_indexPrefixSep{indexID}_indexedColumnsValue_rowID
    Value: null
    ```
### Table hotspots

According to TiDB coding rules, the data of the same table is in a range prefixed by the beginning of the TableID, and the data is arranged in the order of RowID values. When RowID values are incremented during table inserting, the inserted line can only be appended to the end. The Region will split after it reaches a certain size, and then it still can only be appended to the end of the range. The `INSERT` operation can only be executed on one Region, forming a hotspot.

The common auto-increment primary key is sequentially increasing. When the primary key is of the integer type, the value of the primary key is used as the RowID by default. At this time, the RowID is sequentially increasing, and a write hotspot of the table forms when a large number of `INSERT` operations exist.

Meanwhile, the RowID in TiDB is also sequentially auto-incremental by default. When the primary key is not an integer type, you might also encounter the problem of write hotspots.

In addition, when hotspots occur during the process of data writes (on a newly created table or partition) or data reads (periodic read hotspots in read-only scenarios), you can control the Region merge behavior using table attributes. For details, see [Control the Region merge behavior using table attributes](https://docs.pingcap.com/tidb/stable/table-attributes#control-the-region-merge-behavior-using-table-attributes).
### Index hotspots

Index hotspots are similar to table hotspots. Common index hotspots appear in fields that are monotonously increasing in time order, or `INSERT` scenarios with a large number of repeated values.
