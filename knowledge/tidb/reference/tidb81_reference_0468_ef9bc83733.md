# Key partitioning syntax behavior and version note

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partitioning types > Key partitioning`
- Source Line Ranges: `623-714`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partitioning`, `key-partitioning`, `create-table`, `partition-keys`, `primary-key`, `unique-key`, `version-dependent-behavior`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0468_ef9bc83733`
- Source ID: `tidb-docs-8.1:partitioned-table.md#key-partitioning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `257f7b22359c7bb2cff598598291029613fc047eb41b95377a388fae9f763280`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#key-partitioning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Key partitioning syntax, support starting from v7.0.0, allowed partition column lists, empty `KEY()` behavior, or examples using primary key or unique key as the partitioning key.
- Retrieval Keywords: Key partitioning, Starting from v7.0.0, PARTITION BY KEY(store_id), PARTITION BY KEY(fname), PARTITION BY KEY(fname, store_id), PARTITION BY KEY(), primary key `id` as the partitioning key, UNIQUE KEY (id), default number of partitions is 1, BLOB JSON GEOMETRY
- Follow-up Guidance: This chunk also states that for versions earlier than v7.0.0, creating a Key partitioned table results in a non-partitioned table with a warning, and that a unique key used by `KEY()` must be defined as `NOT NULL`.
- Classification Note: The content is reference material because it documents Key partitioning semantics, version-dependent behavior, supported column types, and exact SQL examples.

## Official Source Content

### Key partitioning

Starting from v7.0.0, TiDB supports Key partitioning. For TiDB versions earlier than v7.0.0, if you try creating a Key partitioned table, TiDB creates it as a non-partitioned table and returns a warning.

Both Key partitioning and Hash partitioning can evenly distribute data into a certain number of partitions. The difference is that Hash partitioning only supports distributing data based on a specified integer expression or an integer column, while Key partitioning supports distributing data based on a column list, and partitioning columns of Key partitioning are not limited to the integer type. The Hash algorithm of TiDB for Key partitioning is different from that of MySQL, so the table data distribution is also different.

To create a Key partitioned table, you need to append a `PARTITION BY KEY (columnList)` clause to the `CREATE TABLE` statement. `columnList` is a column list with one or more column names. The data type of each column in the list can be any type except `BLOB`, `JSON`, and `GEOMETRY` (Note that TiDB does not support `GEOMETRY`). In addition, you might also need to append `PARTITIONS num` (where `num` is a positive integer indicating how many partitions a table is divided into), or append the definition of the partition names. For example, adding `(PARTITION p0, PARTITION p1)` means dividing the table into two partitions named `p0` and `p1`.

The following operation creates a Key partitioned table, which is divided into 4 partitions by `store_id`:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    fname VARCHAR(30),
    lname VARCHAR(30),
    hired DATE NOT NULL DEFAULT '1970-01-01',
    separated DATE DEFAULT '9999-12-31',
    job_code INT,
    store_id INT
)

PARTITION BY KEY(store_id)
PARTITIONS 4;
```

If `PARTITIONS num` is not specified, the default number of partitions is 1.

You can also create a Key partitioned table based on non-integer columns such as VARCHAR. For example, you can partition a table by the `fname` column:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    fname VARCHAR(30),
    lname VARCHAR(30),
    hired DATE NOT NULL DEFAULT '1970-01-01',
    separated DATE DEFAULT '9999-12-31',
    job_code INT,
    store_id INT
)

PARTITION BY KEY(fname)
PARTITIONS 4;
```

You can also create a Key partitioned table based on multiple columns. For example, you can divide a table into 4 partitions based on `fname` and `store_id`:

```sql
CREATE TABLE employees (
    id INT NOT NULL,
    fname VARCHAR(30),
    lname VARCHAR(30),
    hired DATE NOT NULL DEFAULT '1970-01-01',
    separated DATE DEFAULT '9999-12-31',
    job_code INT,
    store_id INT
)

PARTITION BY KEY(fname, store_id)
PARTITIONS 4;
```

Similar to MySQL, TiDB supports creating Key partitioned tables with an empty partition column list specified in `PARTITION BY KEY`. For example, the following statement creates a partitioned table using the primary key `id` as the partitioning key:

```sql
CREATE TABLE employees (
    id INT NOT NULL PRIMARY KEY,
    fname VARCHAR(30),
    lname VARCHAR(30),
    hired DATE NOT NULL DEFAULT '1970-01-01',
    separated DATE DEFAULT '9999-12-31',
    job_code INT,
    store_id INT
)

PARTITION BY KEY()
PARTITIONS 4;
```

If the table lacks a primary key but contains a unique key, the unique key is used as the partitioning key:

```sql
CREATE TABLE k1 (
    id INT NOT NULL,
    name VARCHAR(20),
    UNIQUE KEY (id)
)
PARTITION BY KEY()
PARTITIONS 2;
```

However, the previous statement will fail if the unique key column is not defined as `NOT NULL`.
