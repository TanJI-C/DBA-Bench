# Bookshop database initialization SQL script

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-bookshop-schema-design.md`
- Source Title: `Bookshop Example Application`
- Source Heading Path: `Bookshop Example Application > Database initialization script `dbinit.sql``
- Source Line Ranges: `228-293`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tiflash`
- Topic Tags: `schema`, `sql-script`, `database-creation`, `table-creation`, `ddl`, `tiflash-replica`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0082_7e30a95fba`
- Source ID: `tidb-docs-8.1:develop/dev-guide-bookshop-schema-design.md#database-initialization-script-dbinit-sql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2f7d8485e42459f731fbad42cd11efebc5924497fddc7888852059b59e565137`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#database-initialization-script-dbinit-sql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-bookshop-schema-design.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Bookshop example application's dbinit.sql statements that create the bookshop database and its tables, including TiFlash replica configuration.
- Retrieval Keywords: dbinit.sql, CREATE DATABASE IF NOT EXISTS `bookshop`, CREATE TABLE `bookshop`.`books`, CREATE TABLE `bookshop`.`authors`, CREATE TABLE `bookshop`.`book_authors`, CREATE TABLE `bookshop`.`ratings`, ALTER TABLE `bookshop`.`ratings` SET TIFLASH REPLICA 1, CREATE TABLE `bookshop`.`users`, CREATE TABLE `bookshop`.`orders`, AUTO_RANDOM, PRIMARY KEY CLUSTERED, uniq_book_user_idx, orders_book_id_idx, utf8mb4_bin
- Follow-up Guidance: The script also includes DROP TABLE IF EXISTS statements before each CREATE TABLE statement for the Bookshop tables.
- Classification Note: This is reference content because it provides the exact SQL initialization script and schema definitions for the Bookshop example application.

## Official Source Content

## Database initialization script `dbinit.sql`

If you want to manually create database table structures in the Bookshop application, run the following SQL statements:

```sql
CREATE DATABASE IF NOT EXISTS `bookshop`;

DROP TABLE IF EXISTS `bookshop`.`books`;
CREATE TABLE `bookshop`.`books` (
  `id` bigint(20) AUTO_RANDOM NOT NULL,
  `title` varchar(100) NOT NULL,
  `type` enum('Magazine', 'Novel', 'Life', 'Arts', 'Comics', 'Education & Reference', 'Humanities & Social Sciences', 'Science & Technology', 'Kids', 'Sports') NOT NULL,
  `published_at` datetime NOT NULL,
  `stock` int(11) DEFAULT '0',
  `price` decimal(15,2) DEFAULT '0.0',
  PRIMARY KEY (`id`) CLUSTERED
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

DROP TABLE IF EXISTS `bookshop`.`authors`;
CREATE TABLE `bookshop`.`authors` (
  `id` bigint(20) AUTO_RANDOM NOT NULL,
  `name` varchar(100) NOT NULL,
  `gender` tinyint(1) DEFAULT NULL,
  `birth_year` smallint(6) DEFAULT NULL,
  `death_year` smallint(6) DEFAULT NULL,
  PRIMARY KEY (`id`) CLUSTERED
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

DROP TABLE IF EXISTS `bookshop`.`book_authors`;
CREATE TABLE `bookshop`.`book_authors` (
  `book_id` bigint(20) NOT NULL,
  `author_id` bigint(20) NOT NULL,
  PRIMARY KEY (`book_id`,`author_id`) CLUSTERED
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

DROP TABLE IF EXISTS `bookshop`.`ratings`;
CREATE TABLE `bookshop`.`ratings` (
  `book_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `score` tinyint NOT NULL,
  `rated_at` datetime NOT NULL DEFAULT NOW() ON UPDATE NOW(),
  PRIMARY KEY (`book_id`,`user_id`) CLUSTERED,
  UNIQUE KEY `uniq_book_user_idx` (`book_id`,`user_id`)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
ALTER TABLE `bookshop`.`ratings` SET TIFLASH REPLICA 1;

DROP TABLE IF EXISTS `bookshop`.`users`;
CREATE TABLE `bookshop`.`users` (
  `id` bigint AUTO_RANDOM NOT NULL,
  `balance` decimal(15,2) DEFAULT '0.0',
  `nickname` varchar(100) UNIQUE NOT NULL,
  PRIMARY KEY (`id`)
) DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

DROP TABLE IF EXISTS `bookshop`.`orders`;
CREATE TABLE `bookshop`.`orders` (
  `id` bigint(20) AUTO_RANDOM NOT NULL,
  `book_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `quality` tinyint(4) NOT NULL,
  `ordered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`) CLUSTERED,
  KEY `orders_book_id_idx` (`book_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin
```
