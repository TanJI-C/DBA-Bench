# Secondary index example with EXPLAIN and SHOW INDEXES

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-secondary-indexes.md`
- Source Title: `Create a Secondary Index`
- Source Heading Path: `Create a Secondary Index > Example`
- Source Line Ranges: `68-170`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `secondary-index`, `explain`, `execution-plan`, `tablefullscan`, `indexrangescan`, `show-indexes`, `cbo`, `sql-tuning`, `optimizer-hints`, `spm`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0091_96008bcf4d`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-secondary-indexes.md#example`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `00b11c89e79499307ef24faa14e461d9c4524d89de094bd9cb528ae4cc652f54`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes#example
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-secondary-indexes.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an example of creating a secondary index for a query, checking the execution plan with EXPLAIN, or listing indexes with SHOW INDEXES.
- Retrieval Keywords: EXPLAIN, SHOW INDEXES, books, published_at, SELECT * FROM `bookshop`.`books` WHERE `published_at` >= '2022-01-01 00:00:00' AND `published_at` < '2023-01-01 00:00:00', CREATE INDEX `idx_book_published_at` ON `bookshop`.`books` (`bookshop`.`books`.`published_at`), TableFullScan, IndexRangeScan, IndexLookUp, TableRowIDScan, Cost-Based Optimization, CBO, operators, execution plan, query all books published in a given year, SHOW INDEXES FROM `bookshop`.`books`
- Follow-up Guidance: The source notes that execution plans can vary because TiDB uses Cost-Based Optimization and also mentions Optimizer Hints and SQL Plan Management (SPM) as related ways to control index use.
- Classification Note: This chunk is performance-focused because it shows how a secondary index on published_at changes the execution plan from TableFullScan to IndexRangeScan for the example query.

## Official Source Content

## Example

Suppose you want the `bookshop` application to support **searching for all books published in a given year**.

The fields in the `books` table are as follows:

| Field name   | Type          | Field description                                                          |
|--------------|---------------|------------------------------------------------------------------|
| id           | bigint(20)    | Unique ID of the book                                            |
| title        | varchar(100)  | Book title                                                       |
| type         | enum          | Types of books (for example, magazines, animations, and teaching aids) |
| stock        | bigint(20)    | Stock                                                            |
| price        | decimal(15,2) | Price                                                            |
| published_at | datetime      | Date of publishing                                                  |

The `books` table is created using the following SQL statement:

```sql
CREATE TABLE `bookshop`.`books` (
  `id` bigint(20) AUTO_RANDOM NOT NULL,
  `title` varchar(100) NOT NULL,
  `type` enum('Magazine', 'Novel', 'Life', 'Arts', 'Comics', 'Education & Reference', 'Humanities & Social Sciences', 'Science & Technology', 'Kids', 'Sports') NOT NULL,
  `published_at` datetime NOT NULL,
  `stock` int(11) DEFAULT '0',
  `price` decimal(15,2) DEFAULT '0.0',
  PRIMARY KEY (`id`) CLUSTERED
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
```

To support the searching by year feature, you need to write a SQL statement to **search for all books published in a given year**. Taking 2022 as an example, write a SQL statement as follows:

```sql
SELECT * FROM `bookshop`.`books` WHERE `published_at` >= '2022-01-01 00:00:00' AND `published_at` < '2023-01-01 00:00:00';
```

To check the execution plan of the SQL statement, you can use the [`EXPLAIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) statement.

```sql
EXPLAIN SELECT * FROM `bookshop`.`books` WHERE `published_at` >= '2022-01-01 00:00:00' AND `published_at` < '2023-01-01 00:00:00';
```

The following is an example output of the execution plan:

```
+-------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------+
| id                      | estRows  | task      | access object | operator info                                                                                                            |
+-------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------+
| TableReader_7           | 346.32   | root      |               | data:Selection_6                                                                                                         |
| └─Selection_6           | 346.32   | cop[tikv] |               | ge(bookshop.books.published_at, 2022-01-01 00:00:00.000000), lt(bookshop.books.published_at, 2023-01-01 00:00:00.000000) |
|   └─TableFullScan_5     | 20000.00 | cop[tikv] | table:books   | keep order:false                                                                                                         |
+-------------------------+----------+-----------+---------------+--------------------------------------------------------------------------------------------------------------------------+
3 rows in set (0.61 sec)
```

In the example output, **TableFullScan** is displayed in the `id` column, which means that TiDB is ready to do a full table scan on the `books` table in this query. In the case of a large amount of data, however, a full table scan might be quite slow and cause a fatal impact.

To avoid such impact, you can add an index for the `published_at` column to the `books` table as follows:

```sql
CREATE INDEX `idx_book_published_at` ON `bookshop`.`books` (`bookshop`.`books`.`published_at`);
```

After adding the index, execute the `EXPLAIN` statement again to check the execution plan.

The following is an example output.

```
+-------------------------------+---------+-----------+--------------------------------------------------------+-------------------------------------------------------------------+
| id                            | estRows | task      | access object                                          | operator info                                                     |
+-------------------------------+---------+-----------+--------------------------------------------------------+-------------------------------------------------------------------+
| IndexLookUp_10                | 146.01  | root      |                                                        |                                                                   |
| ├─IndexRangeScan_8(Build)     | 146.01  | cop[tikv] | table:books, index:idx_book_published_at(published_at) | range:[2022-01-01 00:00:00,2023-01-01 00:00:00), keep order:false |
| └─TableRowIDScan_9(Probe)     | 146.01  | cop[tikv] | table:books                                            | keep order:false                                                  |
+-------------------------------+---------+-----------+--------------------------------------------------------+-------------------------------------------------------------------+
3 rows in set (0.18 sec)
```

In the output, **IndexRangeScan** is displayed instead of **TableFullScan**, which means that TiDB is ready to use indexes to do this query.

The words such as **TableFullScan** and **IndexRangeScan** in the execution plan are [operators](https://docs.pingcap.com/tidb/stable/explain-overview#operator-overview) in TiDB. For more information about execution plans and operators, see [TiDB Query Execution Plan Overview](https://docs.pingcap.com/tidb/stable/explain-overview).

The execution plan does not return the same operator every time. This is because TiDB uses a **Cost-Based Optimization (CBO)** approach, in which an execution plan depends on both rules and data distribution. For more information about TiDB SQL performance, see [SQL Tuning Overview](https://docs.pingcap.com/tidb/stable/sql-tuning-overview).

The execution plan does not return the same operator every time. This is because TiDB uses a **Cost-Based Optimization (CBO)** approach, in which an execution plan depends on both rules and data distribution. For more information about TiDB SQL performance, see [SQL Tuning Overview](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-sql-tuning-overview).

> **Note:**
>
> TiDB also supports explicit use of indexes when querying, and you can use [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) or [SQL Plan Management (SPM)](https://docs.pingcap.com/tidb/stable/sql-plan-management) to artificially control the use of indexes. But if you do not know well about indexes, optimizer hints, or SPM, **DO NOT** use this feature to avoid any unexpected results.

To query the indexes on a table, you can use the [SHOW INDEXES](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-indexes) statement:

```sql
SHOW INDEXES FROM `bookshop`.`books`;
```
