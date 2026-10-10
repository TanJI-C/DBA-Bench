# Bookshop table schema reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-bookshop-schema-design.md`
- Source Title: `Bookshop Example Application`
- Source Heading Path: `Bookshop Example Application > Description of the tables | Bookshop Example Application > Description of the tables > `books` table | Bookshop Example Application > Description of the tables > `authors` table | Bookshop Example Application > Description of the tables > `users` table | Bookshop Example Application > Description of the tables > `ratings` table | Bookshop Example Application > Description of the tables > `book_authors` table | Bookshop Example Application > Description of the tables > `orders` table`
- Source Line Ranges: `157-227`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `schema`, `tables`, `books`, `authors`, `users`, `ratings`, `book-authors`, `orders`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0081_5abb9b314a`
- Source ID: `tidb-docs-8.1:develop/dev-guide-bookshop-schema-design.md#description-of-the-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `baefce5cae39ae590dd40ef53da5c50103756c8bce67a24a9252bda654b45ca8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#description-of-the-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-bookshop-schema-design.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official reference for the Bookshop table definitions, including table purposes, field names, data types, and table relationships.
- Retrieval Keywords: Description of the tables, books table, authors table, users table, ratings table, book_authors table, orders table, books id title type stock price published_at, authors id name gender birth_year death_year, users id balance nickname, ratings book_id user_id score rated_at, book_authors book_id author_id, orders id book_id user_id quantity ordered_at, Bookshop schema
- Follow-up Guidance: 
- Classification Note: The chunk is classified as a reference because it describes the Bookshop schema by listing each table and its fields, types, and meanings.

## Official Source Content

## Description of the tables

This section describes the database tables of the Bookshop application in detail.
### `books` table

This table stores the basic information of books.

| Field name   | Type          | Description                                                          |
|--------------|---------------|------------------------------------------------------------------|
| id           | bigint(20)    | Unique ID of a book                                            |
| title        | varchar(100)  | Title of a book                                                       |
| type         | enum          | Type of a book (for example, magazine, animation, or teaching aids) |
| stock        | bigint(20)    | Stock                                                            |
| price        | decimal(15,2) | Price                                                            |
| published_at | datetime      | Date of publish                                                  |
### `authors` table

This table stores basic information of authors.

| Field name | Type         | Description                                               |
|------------|--------------|-------------------------------------------------------|
| id         | bigint(20)   | Unique ID of an author                               |
| name       | varchar(100) | Name of an author                                                 |
| gender     | tinyint(1)   | Biological gender (0: female, 1: male, NULL: unknown) |
| birth_year | smallint(6)  | Year of birth                                     |
| death_year | smallint(6)  | Year of death                                     |
### `users` table

This table stores information of Bookshop users.

| Field name | Type          | Description               |
|------------|---------------|-----------------------|
| id         | bigint(20)    | Unique ID of a user |
| balance    | decimal(15,2) | Balance               |
| nickname   | varchar(100)  | Nickname              |
### `ratings` table

This table stores records of user ratings on books.

| Field name | Type     | Description                                                    |
|------------|----------|------------------------------------------------------------|
| book_id    | bigint   | Unique ID of a book (linked to [books](#books-table))    |
| user_id    | bigint   | User's unique identifier (linked to [users](#users-table)) |
| score      | tinyint  | User rating (1-5)                                          |
| rated_at   | datetime | Rating time                                                |
### `book_authors` table

An author may write multiple books, and a book may involve more than one author. This table stores the correspondence between books and authors.

| Field name | Type       | Description                                                      |
|------------|------------|--------------------------------------------------------------|
| book_id    | bigint(20) | Unique ID of a book (linked to [books](#books-table))      |
| author_id  | bigint(20) | Unique ID of an author（Link to [authors](#authors-table)） |
### `orders` table

This table stores user purchase information.

| Field name | Type       | Description                                                        |
|------------|------------|----------------------------------------------------------------|
| id         | bigint(20) | Unique ID of an order                                     |
| book_id    | bigint(20) | Unique ID of a book (linked to [books](#books-table))        |
| user_id    | bigint(20) | User unique identifier (associated with [users](#users-table)) |
| quantity   | tinyint(4) | Purchase quantity                                              |
| ordered_at | datetime   | Purchase time                                                  |
