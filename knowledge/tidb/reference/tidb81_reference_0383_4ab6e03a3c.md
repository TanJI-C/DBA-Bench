# INFORMATION_SCHEMA COLLATIONS table reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-collations.md`
- Source Title: `COLLATIONS`
- Source Heading Path: `COLLATIONS | COLLATIONS > See also`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `information_schema`, `collations`, `character-sets`, `schema-reference`, `mysql-compatibility`, `sql-queries`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0383_4ab6e03a3c`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-collations.md#collations`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `06034394695bce2da1532f7b3705e2b380da5e9b7450bae8af8bb07065ce835a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collations#collations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-collations.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the INFORMATION_SCHEMA `COLLATIONS` table schema, example queries on `collations`, or the mapping between collations and character sets such as `utf8mb4`.
- Retrieval Keywords: INFORMATION_SCHEMA COLLATIONS, COLLATIONS table, DESC collations, SELECT * FROM collations WHERE character_set_name='utf8mb4', COLLATION_NAME, CHARACTER_SET_NAME, IS_DEFAULT, IS_COMPILED, SORTLEN, utf8mb4_bin, utf8mb4_general_ci, utf8mb4_unicode_ci, MySQL compatibility
- Follow-up Guidance: Related identifiers in this source are `SHOW CHARACTER SET`, `SHOW COLLATION`, `INFORMATION_SCHEMA.CHARACTER_SETS`, and `INFORMATION_SCHEMA.COLLATION_CHARACTER_SET_APPLICABILITY`.
- Classification Note: This is a SQL reference chunk because it defines the `INFORMATION_SCHEMA.COLLATIONS` table, shows its columns and example query results, and notes it is included for MySQL compatibility.

## Official Source Content

# COLLATIONS

The `COLLATIONS` table provides a list of collations that correspond to character sets in the `CHARACTER_SETS` table. Currently, this table is included only for compatibility with MySQL.

```sql
USE information_schema;
DESC collations;
```

```sql
+--------------------+-------------+------+------+---------+-------+
| Field              | Type        | Null | Key  | Default | Extra |
+--------------------+-------------+------+------+---------+-------+
| COLLATION_NAME     | varchar(32) | YES  |      | NULL    |       |
| CHARACTER_SET_NAME | varchar(32) | YES  |      | NULL    |       |
| ID                 | bigint(11)  | YES  |      | NULL    |       |
| IS_DEFAULT         | varchar(3)  | YES  |      | NULL    |       |
| IS_COMPILED        | varchar(3)  | YES  |      | NULL    |       |
| SORTLEN            | bigint(3)   | YES  |      | NULL    |       |
+--------------------+-------------+------+------+---------+-------+
6 rows in set (0.00 sec)
```

```sql
SELECT * FROM collations WHERE character_set_name='utf8mb4';
```

```sql
+--------------------+--------------------+------+------------+-------------+---------+
| COLLATION_NAME     | CHARACTER_SET_NAME | ID   | IS_DEFAULT | IS_COMPILED | SORTLEN |
+--------------------+--------------------+------+------------+-------------+---------+
| utf8mb4_bin        | utf8mb4            |   46 | Yes        | Yes         |       1 |
| utf8mb4_general_ci | utf8mb4            |   45 |            | Yes         |       1 |
| utf8mb4_unicode_ci | utf8mb4            |  224 |            | Yes         |       1 |
+--------------------+--------------------+------+------------+-------------+---------+
3 rows in set (0.001 sec)
```

The description of columns in the `COLLATIONS` table is as follows:

* `COLLATION_NAME`: The name of the collation.
* `CHARACTER_SET_NAME`: The name of the character set which the collation belongs to.
* `ID`: The ID of the collation.
* `IS_DEFAULT`: Whether this collation is the default collation of the character set it belongs to.
* `IS_COMPILED`: Whether the character set is compiled into the server.
* `SORTLEN`: The minimum length of memory allocated when the collation sorts characters.
## See also

- [`SHOW CHARACTER SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set)
- [`SHOW COLLATION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation)
- [`INFORMATION_SCHEMA.CHARACTER_SETS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-character-sets)
- [`INFORMATION_SCHEMA.COLLATION_CHARACTER_SET_APPLICABILITY`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collation-character-set-applicability)
