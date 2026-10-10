# Stale Read overview and introductory example

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-use-stale-read.md`
- Source Title: `Stale Read`
- Source Heading Path: `Stale Read | Stale Read > Introduction`
- Source Line Ranges: `5-70`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `stale-read`, `historical-data`, `replica-read`, `read-latency`, `consistency`, `bookshop-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0102_96e376f660`
- Source ID: `tidb-docs-8.1:develop/dev-guide-use-stale-read.md#stale-read`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f88f167073839da6be16cdea6a4e1fbf8c6353f6a428d0c0081331895a00dc49`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-stale-read#stale-read
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-use-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about what Stale Read is, why it can reduce read latency by reading historical data from randomly selected replicas, or the Bookshop example showing an older book price after an update.
- Retrieval Keywords: Stale Read, historical versions of data, specific time, specified time range, latency caused by data replication, randomly selects a replica, all replicas are available for data reading, statement level, transaction level, session level, Bookshop, books, SELECT id, title, type, price FROM books ORDER BY published_at DESC LIMIT 5, UPDATE books SET price = 150 WHERE id = 3181093216, The Story of Droolius Caesar, non-real-time data
- Follow-up Guidance: The next section shows statement-level Stale Read with the `AS OF TIMESTAMP` clause and examples using exact timestamps and bounded staleness.
- Classification Note: This is classified as performance because the content explains that Stale Read can avoid latency caused by data replication during strongly consistent reads and improve application throughput when non-real-time data is acceptable.

## Official Source Content

# Stale Read

Stale Read is a mechanism that TiDB applies to read historical versions of data stored in TiDB. Using this mechanism, you can read the corresponding historical data at a specific time or within a specified time range, and thus save the latency caused by data replication between storage nodes. When you are using Stale Read, TiDB randomly selects a replica for data reading, which means that all replicas are available for data reading.

In practice, consider carefully whether it is appropriate to enable Stale Read in TiDB based on the [usage scenarios](https://docs.pingcap.com/tidb/stable/stale-read#usage-scenarios-of-stale-read). Do not enable Stale Read if your application cannot tolerate reading non-real-time data.

TiDB provides three levels of Stale Read: statement level, transaction level, and session level.
## Introduction

In the [Bookshop](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design) application, you can query the latest published books and their prices through the following SQL statement:

```sql
SELECT id, title, type, price FROM books ORDER BY published_at DESC LIMIT 5;
```

The result is as follows:

```
+------------+------------------------------+-----------------------+--------+
| id         | title                        | type                  | price  |
+------------+------------------------------+-----------------------+--------+
| 3181093216 | The Story of Droolius Caesar | Novel                 | 100.00 |
| 1064253862 | Collin Rolfson               | Education & Reference |  92.85 |
| 1748583991 | The Documentary of cat       | Magazine              | 159.75 |
|  893930596 | Myrl Hills                   | Education & Reference | 356.85 |
| 3062833277 | Keven Wyman                  | Life                  | 477.91 |
+------------+------------------------------+-----------------------+--------+
5 rows in set (0.02 sec)
```

In the list at this time (2022-04-20 15:20:00), the price of *The Story of Droolius Caesar* is 100.0.

At the same time, the seller found that the book was very popular and raised the price of the book to 150.0 through the following SQL statement:

```sql
UPDATE books SET price = 150 WHERE id = 3181093216;
```

The result is as follows:

```
Query OK, 1 row affected (0.00 sec)
Rows matched: 1  Changed: 1  Warnings: 0
```

By querying the latest books list, you can see that the price of this book has increased.

```
+------------+------------------------------+-----------------------+--------+
| id         | title                        | type                  | price  |
+------------+------------------------------+-----------------------+--------+
| 3181093216 | The Story of Droolius Caesar | Novel                 | 150.00 |
| 1064253862 | Collin Rolfson               | Education & Reference |  92.85 |
| 1748583991 | The Documentary of cat       | Magazine              | 159.75 |
|  893930596 | Myrl Hills                   | Education & Reference | 356.85 |
| 3062833277 | Keven Wyman                  | Life                  | 477.91 |
+------------+------------------------------+-----------------------+--------+
5 rows in set (0.01 sec)
```

If it is not necessary to use the latest data, you can query with Stale Read, which might return outdated data, to avoid the latency caused by data replication during a strongly consistent read.

Assuming that in the Bookshop application, the real-time price of a book is not required on the book lists page but only required on the book details and order pages. Stale Read can be used to improve throughout of the application.
