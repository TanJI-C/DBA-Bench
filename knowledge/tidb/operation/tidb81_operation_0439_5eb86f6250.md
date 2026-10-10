# Full-text search SQL quickstart

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-full-text-search-sql.md`
- Source Title: `Full-Text Search with SQL`
- Source Heading Path: `Full-Text Search with SQL | Full-Text Search with SQL > Get started | Full-Text Search with SQL > Get started > Create a full-text index | Full-Text Search with SQL > Get started > Insert text data | Full-Text Search with SQL > Get started > Perform a full-text search`
- Source Line Ranges: `6-154`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `full-text search`, `sql functions`, `fulltext index`, `multilingual parser`, `text insertion`, `relevance ranking`, `bm25`, `serverless regions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0439_5eb86f6250`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-full-text-search-sql.md#full-text-search-with-sql`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `318b02246b4b1af32e5b2000943b82ec44abac42c401af7338f0afd4edcfffc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-sql#full-text-search-with-sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-full-text-search-sql.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the SQL quickstart for TiDB Cloud full-text search, including creating a FULLTEXT INDEX, inserting multilingual text, and querying with relevance ranking.
- Retrieval Keywords: Full-Text Search with SQL, TiDB Cloud Serverless, Frankfurt (eu-central-1), Singapore (ap-southeast-1), CREATE TABLE stock_items, FULLTEXT INDEX (title) WITH PARSER MULTILINGUAL, ALTER TABLE stock_items ADD FULLTEXT INDEX (title) WITH PARSER MULTILINGUAL ADD_COLUMNAR_REPLICA_ON_DEMAND, WITH PARSER STANDARD, WITH PARSER MULTILINGUAL, INSERT INTO stock_items, FTS_MATCH_WORD(), fts_match_word("bluetoothイヤホン", title), fts_match_word("蓝牙耳机", title), ORDER BY fts_match_word, BM25 ranking, COUNT(*) FROM stock_items WHERE fts_match_word
- Follow-up Guidance: The page also links to Full-Text Search with Python and Hybrid Search for related usage patterns.
- Classification Note: This is classified as an operation chunk because it provides step-by-step SQL usage for creating a full-text index, inserting data, and performing full-text search queries.

## Official Source Content

# Full-Text Search with SQL

Unlike [Vector Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-overview), which focuses on semantic similarity, full-text search lets you retrieve documents for exact keywords. In Retrieval-Augmented Generation (RAG) scenarios, you can use full-text search together with vector search to improve the retrieval quality.

The full-text search feature in TiDB provides the following capabilities:

- **Query text data directly**: you can search any string columns directly without the embedding process.

- **Support for multiple languages**: no need to specify the language for high-quality search. The text analyzer in TiDB supports documents in multiple languages mixed in the same table and automatically chooses the best analyzer for each document.

- **Order by relevance**: the search result can be ordered by relevance using the widely adopted [BM25 ranking](https://en.wikipedia.org/wiki/Okapi_BM25) algorithm.

- **Fully compatible with SQL**: all SQL features, such as pre-filtering, post-filtering, grouping, and joining, can be used with full-text search.

> **Tip:**
>
> For Python usage, see [Full-Text Search with Python](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-python).
>
> To use full-text search and vector search together in your AI apps, see [Hybrid Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-hybrid-search).
## Get started

Full-text search is still in the early stages, and we are continuously rolling it out to more customers. Currently, Full-text search is only available for the following product option and regions:

- TiDB Cloud Serverless: `Frankfurt (eu-central-1)` and `Singapore (ap-southeast-1)`

Before using full-text search, make sure your TiDB Cloud Serverless cluster is created in a supported region. If you don't have one, follow [Creating a TiDB Cloud Serverless cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud) to create it.

To perform a full-text search, follow these steps:

1. [**Create a full-text index**](#create-a-full-text-index): create a table with a full-text index, or add a full-text index to an existing table.

2. [**Insert text data**](#insert-text-data): insert text data into the table.

3. [**Perform a full-text search**](#perform-a-full-text-search): perform a full-text search using text queries and full-text search functions.
### Create a full-text index

To perform full-text search, a full-text index is required as it provides the necessary data structure for efficient searching and ranking. Full-text indexes can be created on new tables or added to existing tables.

Create a table with a full-text index:

```sql
CREATE TABLE stock_items(
    id INT,
    title TEXT,
    FULLTEXT INDEX (title) WITH PARSER MULTILINGUAL
);
```

Or add a full-text index to an existing table:

```sql
CREATE TABLE stock_items(
    id INT,
    title TEXT
);

-- You might insert some data here.
-- The full-text index can be created even if data is already in the table.

ALTER TABLE stock_items ADD FULLTEXT INDEX (title) WITH PARSER MULTILINGUAL ADD_COLUMNAR_REPLICA_ON_DEMAND;
```

The following parsers are accepted in the `WITH PARSER <PARSER_NAME>` clause:

- `STANDARD`: fast, works for English contents, splitting words by spaces and punctuation.

- `MULTILINGUAL`: supports multiple languages, including English, Chinese, Japanese, and Korean.
### Insert text data

Inserting data into a table with a full-text index is identical to inserting data into any other tables.

For example, you can execute the following SQL statements to insert data in multiple languages. The multilingual parser in TiDB automatically processes the text.

```sql
INSERT INTO stock_items VALUES (1, "イヤホン bluetooth ワイヤレスイヤホン ");
INSERT INTO stock_items VALUES (2, "完全ワイヤレスイヤホン/ウルトラノイズキャンセリング 2.0 ");
INSERT INTO stock_items VALUES (3, "ワイヤレス ヘッドホン Bluetooth 5.3 65時間再生 ヘッドホン 40mm HD ");
INSERT INTO stock_items VALUES (4, "楽器用 オンイヤーヘッドホン 密閉型【国内正規品】");
INSERT INTO stock_items VALUES (5, "ワイヤレスイヤホン ハイブリッドANC搭載 40dBまでアクティブノイズキャンセル");
INSERT INTO stock_items VALUES (6, "Lightweight Bluetooth Earbuds with 48 Hours Playtime");
INSERT INTO stock_items VALUES (7, "True Wireless Noise Cancelling Earbuds - Compatible with Apple & Android, Built-in Microphone");
INSERT INTO stock_items VALUES (8, "In-Ear Earbud Headphones with Mic, Black");
INSERT INTO stock_items VALUES (9, "Wired Headphones, HD Bass Driven Audio, Lightweight Aluminum Wired in Ear Earbud Headphones");
INSERT INTO stock_items VALUES (10, "LED Light Bar, Music Sync RGB Light Bar, USB Ambient Lamp");
INSERT INTO stock_items VALUES (11, "无线消噪耳机-黑色 手势触控蓝牙降噪 主动降噪头戴式耳机（智能降噪 长久续航）");
INSERT INTO stock_items VALUES (12, "专业版USB7.1声道游戏耳机电竞耳麦头戴式电脑网课办公麦克风带线控");
INSERT INTO stock_items VALUES (13, "投影仪家用智能投影机便携卧室手机投影");
INSERT INTO stock_items VALUES (14, "无线蓝牙耳机超长续航42小时快速充电 流光金属耳机");
INSERT INTO stock_items VALUES (15, "皎月银 国家补贴 心率血氧监测 蓝牙通话 智能手表 男女表");
```
### Perform a full-text search

To perform a full-text search, you can use the `FTS_MATCH_WORD()` function.

**Example: search for most relevant 10 documents**

```sql
SELECT * FROM stock_items
    WHERE fts_match_word("bluetoothイヤホン", title)
    ORDER BY fts_match_word("bluetoothイヤホン", title)
    DESC LIMIT 10;

-- Results are ordered by relevance, with the most relevant documents first.

+------+-----------------------------------------------------------------------------------------------------------+
| id   | title                                                                                                     |
+------+-----------------------------------------------------------------------------------------------------------+
|    1 | イヤホン bluetooth ワイヤレスイヤホン                                                                         |
|    6 | Lightweight Bluetooth Earbuds with 48 Hours Playtime                                                      |
|    2 | 完全ワイヤレスイヤホン/ウルトラノイズキャンセリング 2.0                                                           |
|    3 | ワイヤレス ヘッドホン Bluetooth 5.3 65時間再生 ヘッドホン 40mm HD                                               |
|    5 | ワイヤレスイヤホン ハイブリッドANC搭載 40dBまでアクティブノイズキャンセル                                            |
+------+-----------------------------------------------------------------------------------------------------------+

-- Try searching in another language:
SELECT * FROM stock_items
    WHERE fts_match_word("蓝牙耳机", title)
    ORDER BY fts_match_word("蓝牙耳机", title)
    DESC LIMIT 10;

-- Results are ordered by relevance, with the most relevant documents first.

+------+---------------------------------------------------------------------------------------------------------------+
| id   | title                                                                                                         |
+------+---------------------------------------------------------------------------------------------------------------+
|   14 | 无线蓝牙耳机超长续航42小时快速充电 流光金属耳机                                                                      |
|   11 | 无线消噪耳机-黑色 手势触控蓝牙降噪 主动降噪头戴式耳机（智能降噪 长久续航）                                                |
|   15 | 皎月银 国家补贴 心率血氧监测 蓝牙通话 智能手表 男女表                                                                 |
+------+---------------------------------------------------------------------------------------------------------------+
```

**Example: count the number of documents matching the user query**

```sql
SELECT COUNT(*) FROM stock_items
    WHERE fts_match_word("bluetoothイヤホン", title);

+----------+
| COUNT(*) |
+----------+
|        5 |
+----------+
```
