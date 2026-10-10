# INFORMATION_SCHEMA CHARACTER_SETS table reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-character-sets.md`
- Source Title: `CHARACTER_SETS`
- Source Heading Path: `CHARACTER_SETS | CHARACTER_SETS > See also`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `character_sets`, `collation`, `schema_reference`, `sql_query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0374_3e01955b90`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-character-sets.md#character-sets`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `11741ca1ab20c7269ec5d9212586caebab59ea209ccdd6f35d45dd1278f25a65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-character-sets#character-sets
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-character-sets.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the INFORMATION_SCHEMA.CHARACTER_SETS table schema, its columns, or example query output for supported character sets and default collations in TiDB.
- Retrieval Keywords: INFORMATION_SCHEMA.CHARACTER_SETS, CHARACTER_SETS table, DESC CHARACTER_SETS, SELECT * FROM CHARACTER_SETS, CHARACTER_SET_NAME, DEFAULT_COLLATE_NAME, DESCRIPTION, MAXLEN, ascii, binary, gbk, latin1, utf8, utf8mb4, SHOW CHARACTER SET, SHOW COLLATION, INFORMATION_SCHEMA.COLLATIONS, INFORMATION_SCHEMA.COLLATION_CHARACTER_SET_APPLICABILITY
- Follow-up Guidance: Related references include SHOW CHARACTER SET, SHOW COLLATION, INFORMATION_SCHEMA.COLLATIONS, and INFORMATION_SCHEMA.COLLATION_CHARACTER_SET_APPLICABILITY.
- Classification Note: This is a SQL reference chunk because it defines the INFORMATION_SCHEMA CHARACTER_SETS table structure, sample contents, and column meanings.

## Official Source Content

# CHARACTER_SETS

The `CHARACTER_SETS` table provides information about [character sets](https://docs.pingcap.com/tidb/stable/character-set-and-collation). Currently, TiDB only supports some of the character sets.

```sql
USE INFORMATION_SCHEMA;
DESC CHARACTER_SETS;
```

The output is as follows:

```
+----------------------+-------------+------+------+---------+-------+
| Field                | Type        | Null | Key  | Default | Extra |
+----------------------+-------------+------+------+---------+-------+
| CHARACTER_SET_NAME   | varchar(32) | YES  |      | NULL    |       |
| DEFAULT_COLLATE_NAME | varchar(32) | YES  |      | NULL    |       |
| DESCRIPTION          | varchar(60) | YES  |      | NULL    |       |
| MAXLEN               | bigint(3)   | YES  |      | NULL    |       |
+----------------------+-------------+------+------+---------+-------+
4 rows in set (0.00 sec)
```

View the `CHARACTER_SETS` table:

```sql
SELECT * FROM `CHARACTER_SETS`;
```

The output is as follows:

```sql
+--------------------+----------------------+-------------------------------------+--------+
| CHARACTER_SET_NAME | DEFAULT_COLLATE_NAME | DESCRIPTION                         | MAXLEN |
+--------------------+----------------------+-------------------------------------+--------+
| ascii              | ascii_bin            | US ASCII                            |      1 |
| binary             | binary               | binary                              |      1 |
| gbk                | gbk_chinese_ci       | Chinese Internal Code Specification |      2 |
| latin1             | latin1_bin           | Latin1                              |      1 |
| utf8               | utf8_bin             | UTF-8 Unicode                       |      3 |
| utf8mb4            | utf8mb4_bin          | UTF-8 Unicode                       |      4 |
+--------------------+----------------------+-------------------------------------+--------+
6 rows in set (0.00 sec)
```

The description of columns in the `CHARACTER_SETS` table is as follows:

* `CHARACTER_SET_NAME`: The name of the character set.
* `DEFAULT_COLLATE_NAME` The default collation name of the character set.
* `DESCRIPTION` The description of the character set.
* `MAXLEN` The maximum length required to store a character in this character set.
## See also

- [`SHOW CHARACTER SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set)
- [`SHOW COLLATION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation)
- [`INFORMATION_SCHEMA.COLLATIONS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collations)
- [`INFORMATION_SCHEMA.COLLATION_CHARACTER_SET_APPLICABILITY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collation-character-set-applicability)
