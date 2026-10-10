# Generated columns basics, JSON indexing usage, and validation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/generated-columns.md`
- Source Title: `Generated Columns`
- Source Heading Path: `Generated Columns | Generated Columns > Basic concepts | Generated Columns > Usage | Generated Columns > Validation of generated columns`
- Source Line Ranges: `5-104`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `generated-columns`, `virtual-columns`, `stored-columns`, `json`, `indexing`, `insert`, `update`, `validation`, `not-null`, `explain`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0361_9605a192c5`
- Source ID: `tidb-docs-8.1:generated-columns.md#generated-columns`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c09a3479c6b353460f6c12ec88735a7cbc635d2581598a663a67cbe8f1971017`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/generated-columns#generated-columns
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/generated-columns.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about generated columns basics, indexing JSON data through a generated column, or validation errors for virtual generated columns during INSERT or UPDATE.
- Retrieval Keywords: generated columns, virtual generated column, stored generated column, DEFAULT, JSON cannot be indexed directly, CREATE TABLE person, address_info JSON, JSON_UNQUOTE(JSON_EXTRACT(address_info, '$.city')), city VARCHAR(64) AS, KEY (city), SELECT name, id FROM person WHERE city = 'Beijing', EXPLAIN SELECT name, id FROM person WHERE city = 'Beijing', IndexLookUp, IndexRangeScan, table:person, index:city(city), NOT NULL, INSERT, UPDATE, ERROR 1048 (23000): Column 'city' cannot be null
- Follow-up Guidance: If no data exists at path `$.city`, `JSON_EXTRACT` returns `NULL`, and defining the generated column with `NOT NULL` causes `INSERT` and `UPDATE` validation to return an error for rows that do not pass validation.
- Classification Note: This is reference content because it defines virtual and stored generated columns, shows exact SQL syntax for JSON extraction and indexing, and documents validation behavior and error output.

## Official Source Content

# Generated Columns

This document introduces the concept and usage of generated columns.
## Basic concepts

Unlike general columns, the value of the generated column is calculated by the expression in the column definition. When inserting or updating a generated column, you cannot assign a value, but only use `DEFAULT`.

There are two kinds of generated columns: virtual and stored. A virtual generated column occupies no storage and is computed when it is read. A stored generated column is computed when it is written (inserted or updated) and occupies storage. Compared with the virtual generated columns, the stored generated columns have better read performance, but take up more disk space.

You can create an index on a generated column whether it is virtual or stored.
## Usage

One of the main usage of generated columns is to extract data from the JSON data type and indexing the data.

In both MySQL 8.0 and TiDB, columns of type JSON cannot be indexed directly. That is, the following table schema is **not supported**:

```sql
CREATE TABLE person (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address_info JSON,
    KEY (address_info)
);
```

To index a JSON column, you must extract it as a generated column first.

Using the `city` field in `address_info` as an example, you can create a virtual generated column and add an index for it:

```sql
CREATE TABLE person (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address_info JSON,
    city VARCHAR(64) AS (JSON_UNQUOTE(JSON_EXTRACT(address_info, '$.city'))), -- virtual generated column
    -- city VARCHAR(64) AS (JSON_UNQUOTE(JSON_EXTRACT(address_info, '$.city'))) VIRTUAL, -- virtual generated column
    -- city VARCHAR(64) AS (JSON_UNQUOTE(JSON_EXTRACT(address_info, '$.city'))) STORED, -- stored generated column
    KEY (city)
);
```

In this table, the `city` column is a **virtual generated column** and has an index. The following query can use the index to speed up the execution:

```sql
SELECT name, id FROM person WHERE city = 'Beijing';
```

```sql
EXPLAIN SELECT name, id FROM person WHERE city = 'Beijing';
```

```sql
+---------------------------------+---------+-----------+--------------------------------+-------------------------------------------------------------+
| id                              | estRows | task      | access object                  | operator info                                               |
+---------------------------------+---------+-----------+--------------------------------+-------------------------------------------------------------+
| Projection_4                    | 10.00   | root      |                                | test.person.name, test.person.id                            |
| └─IndexLookUp_10                | 10.00   | root      |                                |                                                             |
|   ├─IndexRangeScan_8(Build)     | 10.00   | cop[tikv] | table:person, index:city(city) | range:["Beijing","Beijing"], keep order:false, stats:pseudo |
|   └─TableRowIDScan_9(Probe)     | 10.00   | cop[tikv] | table:person                   | keep order:false, stats:pseudo                              |
+---------------------------------+---------+-----------+--------------------------------+-------------------------------------------------------------+
```

From the query execution plan, it can be seen that the `city` index is used to read the `HANDLE` of the row that meets the condition `city ='Beijing'`, and then it uses this `HANDLE` to read the data of the row.

If no data exists at path `$.city`, `JSON_EXTRACT` returns `NULL`. If you want to enforce a constraint that `city` must be `NOT NULL`, you can define the virtual generated column as follows:

```sql
CREATE TABLE person (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address_info JSON,
    city VARCHAR(64) AS (JSON_UNQUOTE(JSON_EXTRACT(address_info, '$.city'))) NOT NULL,
    KEY (city)
);
```
## Validation of generated columns

Both `INSERT` and `UPDATE` statements check virtual column definitions. Rows that do not pass validation return errors:

```sql
mysql> INSERT INTO person (name, address_info) VALUES ('Morgan', JSON_OBJECT('Country', 'Canada'));
ERROR 1048 (23000): Column 'city' cannot be null
```
