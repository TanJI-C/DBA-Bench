# AUTO_RANDOM concepts, allocation rules, and restrictions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/auto-random.md`
- Source Title: `AUTO_RANDOM`
- Source Heading Path: `AUTO_RANDOM <span class="version-mark">New in v3.1.0</span> > Basic concepts | AUTO_RANDOM <span class="version-mark">New in v3.1.0</span> > Implicit allocation rules of IDs | AUTO_RANDOM <span class="version-mark">New in v3.1.0</span> > Restrictions`
- Source Line Ranges: `120-177`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `auto_random`, `primary-key`, `id-allocation`, `shard-bits`, `range-bits`, `last-insert-id`, `show-warnings`, `system-variables`, `restrictions`, `pre-split-regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0009_a211740e50`
- Source ID: `tidb-docs-8.1:auto-random.md#basic-concepts`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a09bb2f5e3bcdcba60d41b1e4835e0124c3b8618857d550218e86fdad1931748`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/auto-random#basic-concepts
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/auto-random.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB AUTO_RANDOM bit layout, implicit ID allocation behavior, visibility commands, and documented restrictions on primary keys and inserts.
- Retrieval Keywords: AUTO_RANDOM, AUTO_RANDOM(10), AUTO_RANDOM(5, 54), AUTO_RANDOM(5, 53), PRE_SPLIT_REGIONS, last_insert_id(), SELECT last_insert_id (), SHOW CREATE TABLE, SHOW WARNINGS, information_schema.tables, TIDB_ROW_ID_SHARDING_INFO, PK_AUTO_RANDOM_BITS=x, auto_increment_increment, auto_increment_offset, @@allow_auto_random_explicit_insert, Failed to read auto-increment value from storage engine, Available implicit allocation times, BIGINT, NONCLUSTERED, AUTO_INCREMENT, DEFAULT, ALTER TABLE
- Follow-up Guidance: The source also states that implicit AUTO_RANDOM values affect last_insert_id(), that SHOW WARNINGS can display Available implicit allocation times, and that shard bits can be checked through SHOW CREATE TABLE or information_schema.tables.TIDB_ROW_ID_SHARDING_INFO.
- Classification Note: This is reference content because it defines AUTO_RANDOM concepts, exact allocation rules, SQL-visible identifiers, system variables, value ranges, and explicit usage restrictions from the official documentation.

## Official Source Content

- Whether a value has a signed bit depends on whether the corresponding column has the `UNSIGNED` attribute.
- The length of the sign bit is determined by the existence of an `UNSIGNED` attribute. If there is an `UNSIGNED` attribute, the length is `0`. Otherwise, the length is `1`.
- The length of the reserved bits is `64-R`. The reserved bits are always `0`.
- The content of the shard bits is obtained by calculating the hash value of the starting time of the current transaction. To use a different length of shard bits (such as 10), you can specify `AUTO_RANDOM(10)` when creating the table.
- The value of the auto-increment bits is stored in the storage engine and allocated sequentially. Each time a new value is allocated, the value is incremented by 1. The auto-increment bits ensure that the values of `AUTO_RANDOM` are unique globally. When the auto-increment bits are exhausted, an error `Failed to read auto-increment value from storage engine` is reported when the value is allocated again.
- Value range: the maximum number of bits for the final generated value = shard bits + auto-increment bits. The range of a signed column is `[-(2^(R-1))+1, (2^(R-1))-1]`, and the range of an unsigned column is `[0, (2^R)-1]`.
- You can use `AUTO_RANDOM` with `PRE_SPLIT_REGIONS`. When a table is created successfully, `PRE_SPLIT_REGIONS` pre-splits data in the table into the number of Regions as specified by `2^(PRE_SPLIT_REGIONS)`.

> **Note:**
>
> Selection of shard bits (`S`):
>
> - Since there is a total of 64 available bits, the shard bits length affects the auto-increment bits length. That is, as the shard bits length increases, the length of auto-increment bits decreases, and vice versa. Therefore, you need to balance the randomness of allocated values and available space.
> - The best practice is to set the shard bits as `log(2, x)`, in which `x` is the current number of storage engines. For example, if there are 16 TiKV nodes in a TiDB cluster, you can set the shard bits as `log(2, 16)`, that is `4`. After all regions are evenly scheduled to each TiKV node, the load of bulk writes can be uniformly distributed to different TiKV nodes to maximize resource utilization.
>
> Selection of range (`R`):
>
> - Typically, the `R` parameter needs to be set when the numeric type of the application cannot represent a full 64-bit integer.
> - For example, the range of JSON number is `[-(2^53)+1, (2^53)-1]`. TiDB can easily assign an integer beyond this range to a column defined as `AUTO_RANDOM(5)`, causing unexpected behaviors when the application reads the column. In such cases, you can replace `AUTO_RANDOM(5)` with `AUTO_RANDOM(5, 54)` for signed columns, and replace `AUTO_RANDOM(5)` with `AUTO_RANDOM(5, 53)` for unsigned columns, ensuring that TiDB does not assign integers greater than `9007199254740991` (2^53-1) to the column.

Values allocated implicitly to the `AUTO_RANDOM` column affect `last_insert_id()`. To get the ID that TiDB last implicitly allocates, you can use the `SELECT last_insert_id ()` statement.

To view the shard bits number of the table with an `AUTO_RANDOM` column, you can execute the `SHOW CREATE TABLE` statement. You can also see the value of the `PK_AUTO_RANDOM_BITS=x` mode in the `TIDB_ROW_ID_SHARDING_INFO` column in the `information_schema.tables` system table. `x` is the number of shard bits.

After creating a table with an `AUTO_RANDOM` column, you can use `SHOW WARNINGS` to view the maximum implicit allocation times:

```sql
CREATE TABLE t (a BIGINT AUTO_RANDOM, b VARCHAR(255), PRIMARY KEY (a));
SHOW WARNINGS;
```

The output is as follows:

```sql
+-------+------+---------------------------------------------------------+
| Level | Code | Message                                                 |
+-------+------+---------------------------------------------------------+
| Note  | 1105 | Available implicit allocation times: 288230376151711743 |
+-------+------+---------------------------------------------------------+
1 row in set (0.00 sec)
```
## Implicit allocation rules of IDs

TiDB implicitly allocates values to `AUTO_RANDOM` columns similarly to `AUTO_INCREMENT` columns. They are also controlled by the session-level system variables [`auto_increment_increment`](https://docs.pingcap.com/tidb/stable/system-variables#auto_increment_increment) and [`auto_increment_offset`](https://docs.pingcap.com/tidb/stable/system-variables#auto_increment_offset). The auto-increment bits (ID) of implicitly allocated values conform to the equation `(ID - auto_increment_offset) % auto_increment_increment == 0`.
## Restrictions

Pay attention to the following restrictions when you use `AUTO_RANDOM`:

- To insert values explicitly, you need to set the value of the `@@allow_auto_random_explicit_insert` system variable to `1` (`0` by default). It is **not** recommended that you explicitly specify a value for the column with the `AUTO_RANDOM` attribute when you insert data. Otherwise, the numeral values that can be automatically allocated for this table might be used up in advance.
- Specify this attribute for the primary key column **ONLY** as the `BIGINT` type. Otherwise, an error occurs. In addition, when the attribute of the primary key is `NONCLUSTERED`, `AUTO_RANDOM` is not supported even on the integer primary key. For more details about the primary key of the `CLUSTERED` type, refer to [clustered index](https://docs.pingcap.com/tidb/stable/clustered-indexes).
- You cannot use `ALTER TABLE` to modify the `AUTO_RANDOM` attribute, including adding or removing this attribute.
- You cannot use `ALTER TABLE` to change from `AUTO_INCREMENT` to `AUTO_RANDOM` if the maximum value is close to the maximum value of the column type.
- You cannot change the column type of the primary key column that is specified with `AUTO_RANDOM` attribute.
- You cannot specify `AUTO_RANDOM` and `AUTO_INCREMENT` for the same column at the same time.
- You cannot specify `AUTO_RANDOM` and `DEFAULT` (the default value of a column) for the same column at the same time.
- When`AUTO_RANDOM` is used on a column, it is difficult to change the column attribute back to `AUTO_INCREMENT` because the auto-generated values might be very large.
