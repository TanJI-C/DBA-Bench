# Runtime Filter overview and working principles

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/runtime-filter.md`
- Source Title: `Runtime Filter`
- Source Heading Path: `Runtime Filter | Runtime Filter > Concepts | Runtime Filter > Working principles of Runtime Filter | Runtime Filter > Working principles of Runtime Filter > Example`
- Source Line Ranges: `5-78`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `runtime filter`, `hash join`, `mpp`, `build side`, `probe side`, `dynamic predicate`, `table scan`, `join performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0056_24fb39a0d4`
- Source ID: `tidb-docs-8.1:runtime-filter.md#runtime-filter`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e3a122675393f54d05da507d5cb1be63da255bb0d3355626f0ee9c66c61b6e0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/runtime-filter#runtime-filter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/runtime-filter.md

## Retrieval Guidance

- Use When: Use this chunk when explaining what Runtime Filter is, how it works with hash join in MPP scenarios, or why dynamic predicates can reduce TableFullScan work on the probe side.
- Retrieval Keywords: Runtime Filter, hash join, MPP scenarios, dynamic predicate, PhysicalHashJoin, TableFullScan, build side, probe side, Selection operator, filter out the join key data in advance, store_sales, date_dim, ss_date_sk = d_date_sk, d_year = 2001, reduce the amount of data scanning, join performance
- Follow-up Guidance: The example shows Runtime Filter generated from the build side of `date_dim` and sent to the `TableFullScan` of `store_sales` to reduce scanned rows before hash join matching.
- Classification Note: This chunk is classified as architecture because the official content defines Runtime Filter concepts and describes the execution principles between `PhysicalHashJoin`, filter generation, and `TableFullScan`.

## Official Source Content

# Runtime Filter

Runtime Filter is a new feature introduced in TiDB v7.3, which aims to improve the performance of hash join in MPP scenarios. By generating filters dynamically to filter the data of hash join in advance, TiDB can reduce the amount of data scanning and the amount of calculation of hash join at runtime, ultimately improving the query performance.
## Concepts

- Hash join: a way to implement the join relational algebra. It gets the result of Join by building a hash table on one side and continuously matching the hash table on the other side.
- Build side: one side of hash join used to build a hash table. In this document, the right table of hash join is called the build side by default.
- Probe side: one side of hash join used to continuously match the hash table. In this document, the left table of hash join is called the probe side by default.
- Filter: also known as predicate, which refers to the filter condition in this document.
## Working principles of Runtime Filter

Hash join performs the join operation by building a hash table based on the right table and continuously probing the hash table using the left table. If some join key values cannot hit the hash table during the probing process, it means that the data does not exist in the right table and will not appear in the final join result. Therefore, if TiDB can **filter out the join key data in advance** during scanning, it will reduce the scanning time and network overhead, thereby greatly improving the join efficiency.

Runtime Filter is a **dynamic predicate** generated during the query planning phase. This predicate has the same function as other predicates in the TiDB Selection operator. These predicates are all applied to the Table Scan operation to filter out rows that do not match the predicate. The only difference is that the parameter values in Runtime Filter come from the results generated during the hash join build process.
### Example

Assume that there is a join query between the `store_sales` table and the `date_dim` table, and the join method is hash join. `store_sales` is a fact table that mainly stores the sales data of stores, and the number of rows is 1 million. `date_dim` is a time dimension table that mainly stores date information. You want to query the sales data of the year 2001, so 365 rows of the `date_dim` table are involved in the join operation.

```sql
SELECT * FROM store_sales, date_dim
WHERE ss_date_sk = d_date_sk
    AND d_year = 2001;
```

The execution plan of hash join is usually as follows:

```
                 +-------------------+
                 | PhysicalHashJoin  |
        +------->|                   |<------+
        |        +-------------------+       |
        |                                    |
        |                                    |
  100w  |                                    | 365
        |                                    |
        |                                    |
+-------+-------+                   +--------+-------+
| TableFullScan |                   | TableFullScan  |
|  store_sales  |                   |    date_dim    |
+---------------+                   +----------------+
```

*(The above figure omits the exchange node and other nodes.)*

The execution process of Runtime Filter is as follows:

1. Scan the data of the `date_dim` table.
2. `PhysicalHashJoin` calculates a filter condition based on the data of the build side, such as `date_dim in (2001/01/01~2001/12/31)`.
3. Send the filter condition to the `TableFullScan` operator that is waiting to scan `store_sales`.
4. The filter condition is applied to `store_sales`, and the filtered data is passed to `PhysicalHashJoin`, thereby reducing the amount of data scanned by the probe side and the amount of calculation of matching the hash table.

```
                         2. Build RF values
            +-------->+-------------------+
            |         |PhysicalHashJoin   |<-----+
            |    +----+                   |      |
4. After RF |    |    +-------------------+      | 1. Scan T2
    5000    |    |3. Send RF                     |      365
            |    | filter data                   |
            |    |                               |
      +-----+----v------+                +-------+--------+
      |  TableFullScan  |                | TableFullScan  |
      |  store_sales    |                |    date_dim    |
      +-----------------+                +----------------+
```

*(RF is short for Runtime Filter)*

From the above two figures, you can see that the amount of data scanned by `store_sales` is reduced from 1 million to 5000. By reducing the amount of data scanned by `TableFullScan`, Runtime Filter can reduce the number of times to match the hash table, avoiding unnecessary I/O and network transmission, thus significantly improving the efficiency of the join operation.
