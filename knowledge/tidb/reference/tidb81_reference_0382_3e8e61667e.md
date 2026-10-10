# COLLATION_CHARACTER_SET_APPLICABILITY table reference

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-collation-character-set-applicability.md`
- Source Title: `COLLATION_CHARACTER_SET_APPLICABILITY`
- Source Heading Path: `COLLATION_CHARACTER_SET_APPLICABILITY | COLLATION_CHARACTER_SET_APPLICABILITY > See also`
- Source Line Ranges: `5-56`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `collation`, `character_set`, `table_schema`, `mysql_compatibility`, `sql_query`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0382_3e8e61667e`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-collation-character-set-applicability.md#collation-character-set-applicability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `354fca39d50d34424eddabb0b2c10e9bb3c9fd04c2a0ee758e3ec1651d04624b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collation-character-set-applicability#collation-character-set-applicability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-collation-character-set-applicability.md

## Retrieval Guidance

- Use When: Use this chunk when you need the INFORMATION_SCHEMA reference that maps a collation to its applicable character set name through the COLLATION_CHARACTER_SET_APPLICABILITY table.
- Retrieval Keywords: COLLATION_CHARACTER_SET_APPLICABILITY, INFORMATION_SCHEMA, COLLATION_NAME, CHARACTER_SET_NAME, DESC COLLATION_CHARACTER_SET_APPLICABILITY, SELECT * FROM COLLATION_CHARACTER_SET_APPLICABILITY WHERE character_set_name='utf8mb4', utf8mb4_bin, utf8mb4_general_ci, utf8mb4_unicode_ci, collation mapping, character set name, MySQL compatibility
- Follow-up Guidance: Related official references listed here are SHOW CHARACTER SET, SHOW COLLATION, INFORMATION_SCHEMA.CHARACTER_SETS, and INFORMATION_SCHEMA.COLLATIONS.
- Classification Note: This is a reference chunk because it defines the INFORMATION_SCHEMA table purpose, shows its schema, and provides an example query and result for collation-to-character-set mapping.

## Official Source Content

# COLLATION_CHARACTER_SET_APPLICABILITY

The `COLLATION_CHARACTER_SET_APPLICABILITY` table maps collations to the applicable character set name. Similar to the `COLLATIONS` table, it is included only for compatibility with MySQL.

```sql
USE INFORMATION_SCHEMA;
DESC COLLATION_CHARACTER_SET_APPLICABILITY;
```

The output is as follows:

```sql
+--------------------+-------------+------+------+---------+-------+
| Field              | Type        | Null | Key  | Default | Extra |
+--------------------+-------------+------+------+---------+-------+
| COLLATION_NAME     | varchar(32) | NO   |      | NULL    |       |
| CHARACTER_SET_NAME | varchar(32) | NO   |      | NULL    |       |
+--------------------+-------------+------+------+---------+-------+
2 rows in set (0.00 sec)
```

View the collation mapping for the `utf8mb4` character set in the `COLLATION_CHARACTER_SET_APPLICABILITY` table:

```sql
SELECT * FROM COLLATION_CHARACTER_SET_APPLICABILITY WHERE character_set_name='utf8mb4';
```

The output is as follows:

```sql
+--------------------+--------------------+
| COLLATION_NAME     | CHARACTER_SET_NAME |
+--------------------+--------------------+
| utf8mb4_bin        | utf8mb4            |
| utf8mb4_general_ci | utf8mb4            |
| utf8mb4_unicode_ci | utf8mb4            |
+--------------------+--------------------+
3 rows in set (0.00 sec)
```

The description of columns in the `COLLATION_CHARACTER_SET_APPLICABILITY` table is as follows:

* `COLLATION_NAME`: The name of the collation.
* `CHARACTER_SET_NAME`: The name of the character set which the collation belongs to.
## See also

- [`SHOW CHARACTER SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-character-set)
- [`SHOW COLLATION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-collation)
- [`INFORMATION_SCHEMA.CHARACTER_SETS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-character-sets)
- [`INFORMATION_SCHEMA.COLLATIONS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-collations)
