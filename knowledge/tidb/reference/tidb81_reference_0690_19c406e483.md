# Split Region syntax and table region splitting

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-split-region.md`
- Source Title: `Split Region`
- Source Heading Path: `Split Region | Split Region > Synopsis | Split Region > Usage of Split Region | Split Region > Usage of Split Region > Split Table Region | Split Region > Usage of Split Region > Split Table Region > Even Split | Split Region > Usage of Split Region > Split Table Region > Uneven split | Split Region > Usage of Split Region > Split index Region`
- Source Line Ranges: `5-136`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `split-region`, `syntax`, `table-region`, `index-region`, `row-id`, `session-variables`, `scatter`, `hotspot`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0690_19c406e483`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-split-region.md#split-region`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `faf2cc3ea28e535df0f6c2b4f02df2bb7b590a567114b1bf9ce130d022713a1c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#split-region
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-split-region.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the SPLIT TABLE or SPLIT REGION syntax, table or index Region pre-splitting behavior, result columns, or session variables that affect scattering and timeout.
- Retrieval Keywords: SPLIT TABLE table_name [INDEX index_name] BETWEEN (lower_value) AND (upper_value) REGIONS region_num, SPLIT TABLE table_name [INDEX index_name] BY (value_list), SplitRegionStmt, TOTAL_SPLIT_REGION, SCATTER_FINISH_RATIO, tidb_wait_split_region_finish, tidb_wait_split_region_timeout, split-table, row_id, t[table_id]_r[row_id], t[table_id]_i[index_id][index_value], Split Table Region, Split index Region, hotspot, scatter
- Follow-up Guidance: The source also explains even and uneven split examples for table row data and introduces how index keys are encoded for index Region splits.
- Classification Note: This is reference content because it defines SPLIT REGION syntax, result fields, session variables, and table or index key concepts used to split Regions.

## Official Source Content

# Split Region

For each new table created in TiDB, one [Region](https://docs.pingcap.com/tidb/stable/tidb-storage#region) is segmented by default to store the data of this table. This default behavior is controlled by `split-table` in the TiDB configuration file. When the data in this Region exceeds the default Region size limit, the Region starts to split into two.

In the above case, because there is only one Region at the beginning, all write requests occur on the TiKV where the Region is located. If there are a large number of writes for the newly created table, hotspots are caused.

To solve the hotspot problem in the above scenario, TiDB introduces the pre-split function, which can pre-split multiple Regions for a certain table according to the specified parameters and scatter them to each TiKV node.

> **Note:**
>
> This feature is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.
## Synopsis

```ebnf+diagram
SplitRegionStmt ::=
    "SPLIT" SplitSyntaxOption "TABLE" TableName PartitionNameList? ("INDEX" IndexName)? SplitOption

SplitSyntaxOption ::=
    ("REGION" "FOR")? "PARTITION"?

TableName ::=
    (SchemaName ".")? Identifier

PartitionNameList ::=
    "PARTITION" "(" PartitionName ("," PartitionName)* ")"

SplitOption ::=
    ("BETWEEN" RowValue "AND" RowValue "REGIONS" NUM
|   "BY" RowValue ("," RowValue)* )

RowValue ::=
    "(" ValuesOpt ")"
```
## Usage of Split Region

There are two types of Split Region syntax:

- The syntax of even split:

    ```sql
    SPLIT TABLE table_name [INDEX index_name] BETWEEN (lower_value) AND (upper_value) REGIONS region_num
    ```

    `BETWEEN lower_value AND upper_value REGIONS region_num` defines the upper boundary, the lower boundary, and the Region amount. Then the current region will be evenly spilt into the number of regions (as specified in `region_num`) between the upper and lower boundaries.

- The syntax of uneven split:

    ```sql
    SPLIT TABLE table_name [INDEX index_name] BY (value_list) [, (value_list)] ...
    ```

    `BY value_list…` specifies a series of points manually, based on which the current Region is spilt. It is suitable for scenarios with unevenly distributed data.

The following example shows the result of the `SPLIT` statement:

```sql
+--------------------+----------------------+
| TOTAL_SPLIT_REGION | SCATTER_FINISH_RATIO |
+--------------------+----------------------+
| 4                  | 1.0                  |
+--------------------+----------------------+
```

* `TOTAL_SPLIT_REGION`: the number of newly split Regions.
* `SCATTER_FINISH_RATIO`: the completion rate of scattering for newly split Regions. `1.0` means that all Regions are scattered. `0.5` means that only half of the Regions are scattered and the rest are being scattered.

> **Note:**
>
> The following two session variables might affect the behavior of the `SPLIT` statement:
>
> - `tidb_wait_split_region_finish`: It might take a while to scatter the Regions. This duration depends on PD scheduling and TiKV loads. This variable is used to control when executing the `SPLIT REGION` statement whether to return the results to the client until all Regions are scattered. If its value is set to `1` (by default), TiDB returns the results only after the scattering is completed. If its value is set to `0`, TiDB returns the results regardless of the scattering status.
> - `tidb_wait_split_region_timeout`: This variable is to set the execution timeout of the `SPLIT REGION` statement, in seconds. The default value is 300s. If the `split` operation is not completed within the duration, TiDB returns a timeout error.
### Split Table Region

The key of row data in each table is encoded by `table_id` and `row_id`. The format is as follows:

```go
t[table_id]_r[row_id]
```

For example, when `table_id` is 22 and `row_id` is 11:

```go
t22_r11
```

Row data in the same table have the same `table_id`, but each row has its unique `row_id` that can be used for Region split.
#### Even Split

Because `row_id` is an integer, the value of the key to be split can be calculated according to the specified `lower_value`, `upper_value`, and `region_num`. TiDB first calculates the step value (`step = (upper_value - lower_value)/region_num`). Then split will be done evenly per each "step" between `lower_value` and `upper_value` to generate the number of Regions as specified by `region_num`.

For example, if you want 16 evenly split Regions split from key range`minInt64`~`maxInt64` for table t, you can use this statement:

```sql
SPLIT TABLE t BETWEEN (-9223372036854775808) AND (9223372036854775807) REGIONS 16;
```

This statement splits table t into 16 Regions between minInt64 and maxInt64. If the given primary key range is smaller than the specified one, for example, 0~1000000000, you can use 0 and 1000000000 take place of minInt64 and maxInt64 respectively to split Regions.

```sql
SPLIT TABLE t BETWEEN (0) AND (1000000000) REGIONS 16;
```
#### Uneven split

If the known data is unevenly distributed, and you want a Region to be split respectively in key ranges -inf ~ 10000, 10000 ~ 90000, and 90000 ~ +inf, you can achieve this by setting fixed points, as shown below:

```sql
SPLIT TABLE t BY (10000), (90000);
```
### Split index Region

The key of the index data in the table is encoded by `table_id`, `index_id`, and the value of the index column. The format is as follows:

```go
t[table_id]_i[index_id][index_value]
```

For example, when `table_id` is 22, `index_id` is 5, and `index_value` is abc:

```go
t22_i5abc
```

The `table_id` and `index_id` of the same index data in one table is the same. To split index Regions, you need to split Regions based on `index_value`.
