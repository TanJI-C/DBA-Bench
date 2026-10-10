# CREATE INDEX multi-valued indexes creation usage and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-index.md`
- Source Title: `CREATE INDEX | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE INDEX > Multi-valued indexes > Create multi-valued indexes | CREATE INDEX > Multi-valued indexes > Use multi-valued indexes | CREATE INDEX > Multi-valued indexes > Limitations`
- Source Line Ranges: `258-357`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `br`, `ticdc`, `lightning`
- Topic Tags: `create-index`, `multi-valued-indexes`, `expression-indexes`, `json-array`, `unique-indexes`, `composite-indexes`, `limitations`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0554_d5726df43d`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-index.md#create-multi-valued-indexes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `74f31c2306660b858ab7f74941756f42b25ae19f133e50a1a5393c56013a4d76`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#create-multi-valued-indexes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-index.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to define, use, or understand limitations and write-time errors of multi-valued indexes in CREATE INDEX on JSON arrays.
- Retrieval Keywords: CREATE INDEX multi-valued indexes, CAST(... AS ... ARRAY), expression index, JSON array, UNIQUE INDEX zips, composite index multi-valued part only once, ERROR 1062 Duplicate entry for key customers.zips, ERROR 1235 more than one multi-valued key part per index, ERROR 3752 Value is out of range for expression index, ERROR 3903 Invalid JSON value for CAST for expression index, empty JSON array no corresponding index record, cannot use multi-valued indexes for sorting, cannot be a primary key or a foreign key, BR TiCDC TiDB Lightning earlier than v6.6.0, Use multi-valued indexes
- Follow-up Guidance: For supported condition patterns and optimizer behavior, the source points to Index Selection - Use multi-valued indexes.
- Classification Note: This is reference content because it defines the CREATE INDEX syntax patterns, examples, exact errors, and documented limitations for multi-valued indexes.

## Official Source Content

### Create multi-valued indexes

You can create multi-valued indexes by using the [`CAST(... AS ... ARRAY)`](https://docs.pingcap.com/tidb/stable/functions-and-operators/cast-functions-and-operators#cast) function in the index definition, as creating an expression index.

```sql
mysql> CREATE TABLE customers (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name CHAR(10),
    custinfo JSON,
    INDEX zips((CAST(custinfo->'$.zipcode' AS UNSIGNED ARRAY)))
);
```

You can define a multi-valued index as a unique index.

```sql
mysql> CREATE TABLE customers (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name CHAR(10),
    custinfo JSON,
    UNIQUE INDEX zips( (CAST(custinfo->'$.zipcode' AS UNSIGNED ARRAY)))
);
```

When a multi-valued index is defined as a unique index, an error is reported if you try to insert duplicate data.

```sql
mysql> INSERT INTO customers VALUES (1, 'pingcap', '{"zipcode": [1,2]}');
Query OK, 1 row affected (0.01 sec)

mysql> INSERT INTO customers VALUES (1, 'pingcap', '{"zipcode": [2,3]}');
ERROR 1062 (23000): Duplicate entry '2' for key 'customers.zips'
```

The same record can have duplicate values, but when different records have duplicate values, an error is reported.

```sql
-- Insert succeeded
mysql> INSERT INTO t1 VALUES('[1,1,2]');
mysql> INSERT INTO t1 VALUES('[3,3,3,4,4,4]');

-- Insert failed
mysql> INSERT INTO t1 VALUES('[1,2]');
mysql> INSERT INTO t1 VALUES('[2,3]');
```

You can also define a multi-valued index as a composite index:

```sql
mysql> CREATE TABLE customers (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name CHAR(10),
    custinfo JSON,
    INDEX zips(name, (CAST(custinfo->'$.zipcode' AS UNSIGNED ARRAY)))
);
```

When a multi-valued index is defined as a composite index, the multi-valued part can appear in any position, but only once.

```sql
mysql> CREATE TABLE customers (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name CHAR(10),
    custinfo JSON,
    INDEX zips(name, (CAST(custinfo->'$.zipcode' AS UNSIGNED ARRAY)), (CAST(custinfo->'$.zipcode' AS UNSIGNED ARRAY)))
);
ERROR 1235 (42000): This version of TiDB doesn't yet support 'more than one multi-valued key part per index'.
```

The written data must exactly match the type defined by the multi-valued index; otherwise, the data write fails:

```sql
-- All elements in the zipcode field must be the UNSIGNED type.
mysql> INSERT INTO customers VALUES (1, 'pingcap', '{"zipcode": [-1]}');
ERROR 3752 (HY000): Value is out of range for expression index 'zips' at row 1

mysql> INSERT INTO customers VALUES (1, 'pingcap', '{"zipcode": ["1"]}'); -- Incompatible with MySQL
ERROR 3903 (HY000): Invalid JSON value for CAST for expression index 'zips'

mysql> INSERT INTO customers VALUES (1, 'pingcap', '{"zipcode": [1]}');
Query OK, 1 row affected (0.00 sec)
```
### Use multi-valued indexes

See [Index Selection - Use multi-valued indexes](https://docs.pingcap.com/tidb/stable/choose-index#use-multi-valued-indexes) for more details.
### Limitations

- For an empty JSON array, no corresponding index record is generated.
- The target type in `CAST(... AS ... ARRAY)` cannot be any of `BINARY`, `JSON`, `YEAR`, `FLOAT`, and `DECIMAL`. The source type must be JSON.
- You cannot use multi-valued indexes for sorting.
- You can only create multi-valued indexes on a JSON array.
- A multi-valued index cannot be a primary key or a foreign key.
- The extra storage space used by a multi-valued index = the average number of array elements per row * the space used by a normal secondary index.
- Compared with normal indexes, DML operations will modify more index records for multi-valued indexes, so multi-valued indexes will have a greater performance impact than normal indexes.
- Because multi-valued indexes are a special type of expression index, multi-valued indexes have the same limitations as expression indexes.
- If a table uses multi-valued indexes, you cannot back up, replicate, or import the table using BR, TiCDC, or TiDB Lightning to a TiDB cluster earlier than v6.6.0.
- For a query with complex conditions, TiDB might not be able to select multi-valued indexes. For information on the condition patterns supported by multi-valued indexes, refer to [Use multi-valued indexes](https://docs.pingcap.com/tidb/stable/choose-index#use-multi-valued-indexes).
