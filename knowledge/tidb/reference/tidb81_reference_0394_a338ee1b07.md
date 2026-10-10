# KEYWORDS INFORMATION_SCHEMA table

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-keywords.md`
- Source Title: `KEYWORDS`
- Source Heading Path: `KEYWORDS`
- Source Line Ranges: `5-48`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `keywords`, `reserved-words`, `sql-reference`, `metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0394_a338ee1b07`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-keywords.md#keywords`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `524d783c78a356fbf8757102068ab8412fdeed32db6f8aef20dad477266f856a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-keywords#keywords
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-keywords.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the INFORMATION_SCHEMA metadata table that lists TiDB keywords and indicates whether a keyword is reserved.
- Retrieval Keywords: INFORMATION_SCHEMA.KEYWORDS, KEYWORDS table, DESC keywords, WORD, RESERVED, reserved keyword, non-reserved keyword, SELECT * FROM INFORMATION_SCHEMA.KEYWORDS WHERE WORD IN ('ADD','USER'), ADD, USER
- Follow-up Guidance: The content includes example SQL statements to describe the KEYWORDS table and to query whether ADD and USER are reserved keywords.
- Classification Note: This is reference content because it defines the KEYWORDS INFORMATION_SCHEMA table schema, field meanings, and example query results.

## Official Source Content

# KEYWORDS

Starting from v7.5.3 and v7.6.0, TiDB provides the `KEYWORDS` table. You can use this table to get information about [keywords](https://docs.pingcap.com/tidb/stable/keywords) in TiDB.

```sql
USE INFORMATION_SCHEMA;
DESC keywords;
```

The output is as follows:

```
+----------+--------------+------+------+---------+-------+
| Field    | Type         | Null | Key  | Default | Extra |
+----------+--------------+------+------+---------+-------+
| WORD     | varchar(128) | YES  |      | NULL    |       |
| RESERVED | int(11)      | YES  |      | NULL    |       |
+----------+--------------+------+------+---------+-------+
2 rows in set (0.00 sec)
```

Field description:

- `WORD`: The keyword.
- `RESERVED`: Whether the keyword is reserved.

The following statement queries the information about `ADD` and `USER` keywords:

```sql
SELECT * FROM INFORMATION_SCHEMA.KEYWORDS WHERE WORD IN ('ADD','USER');
```

From the output, you can see that `ADD` is a reserved keyword and `USER` is a non-reserved keyword.

```
+------+----------+
| WORD | RESERVED |
+------+----------+
| ADD  |        1 |
| USER |        0 |
+------+----------+
2 rows in set (0.00 sec)
```
