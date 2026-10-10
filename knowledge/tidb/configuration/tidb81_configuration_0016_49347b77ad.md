# Database and table character set and collation configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-and-collation.md`
- Source Title: `Character Set and Collation`
- Source Heading Path: `Character Set and Collation > Character set and collation in different layers | Character Set and Collation > Character set and collation in different layers > Database character set and collation | Character Set and Collation > Character set and collation in different layers > Table character set and collation`
- Source Line Ranges: `211-339`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `character-set`, `collation`, `database-schema`, `table-schema`, `default-values`, `information-schema`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0016_49347b77ad`
- Source ID: `tidb-docs-8.1:character-set-and-collation.md#character-set-and-collation-in-different-layers`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c7b82ea3692e9e4267ae5b008539c3fbd6ac1c78b368ac0f45dca313c311169`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-and-collation#character-set-and-collation-in-different-layers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-and-collation.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to set or inspect database-level or table-level character set and collation defaults in TiDB.
- Retrieval Keywords: CREATE DATABASE db_name [[DEFAULT] CHARACTER SET charset_name] [[DEFAULT] COLLATE collation_name], ALTER DATABASE db_name [[DEFAULT] CHARACTER SET charset_name] [[DEFAULT] COLLATE collation_name], CREATE SCHEMA, ALTER DATABASE, DATABASE can be replaced with SCHEMA, @@character_set_database, @@collation_database, INFORMATION_SCHEMA.SCHEMATA, DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME, CREATE TABLE tbl_name (column_list) [[DEFAULT] CHARACTER SET charset_name] [COLLATE collation_name], ALTER TABLE tbl_name [[DEFAULT] CHARACTER SET charset_name] [COLLATE collation_name], default_collation_for_utf8mb4, table character set and collation, database character set and collation, utf8mb4_general_ci, latin1_bin
- Follow-up Guidance: The chunk explains that if a table does not specify character set and collation, it inherits the database defaults, and if only utf8mb4 is specified, the collation is determined by default_collation_for_utf8mb4.
- Classification Note: This is configuration content because it shows the SQL syntax and related system and information schema variables used to configure and inspect database and table character set and collation settings.

## Official Source Content

## Character set and collation in different layers

The character set and collation can be set at different layers.
### Database character set and collation

Each database has a character set and a collation. You can use the following statements to specify the database character set and collation:

```sql
CREATE DATABASE db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name]

ALTER DATABASE db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name]
```

`DATABASE` can be replaced with `SCHEMA` here.

Different databases can use different character sets and collations. Use the `character_set_database` and `collation_database` to see the character set and collation of the current database:

```sql
CREATE SCHEMA test1 CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

```sql
Query OK, 0 rows affected (0.09 sec)
```

```sql
USE test1;
```

```sql
Database changed
```

```sql
SELECT @@character_set_database, @@collation_database;
```

```sql
+--------------------------|----------------------+
| @@character_set_database | @@collation_database |
+--------------------------|----------------------+
| utf8mb4                  | utf8mb4_general_ci   |
+--------------------------|----------------------+
1 row in set (0.00 sec)
```

```sql
CREATE SCHEMA test2 CHARACTER SET latin1 COLLATE latin1_bin;
```

```sql
Query OK, 0 rows affected (0.09 sec)
```

```sql
USE test2;
```

```sql
Database changed
```

```sql
SELECT @@character_set_database, @@collation_database;
```

```sql
+--------------------------|----------------------+
| @@character_set_database | @@collation_database |
+--------------------------|----------------------+
| latin1                   | latin1_bin           |
+--------------------------|----------------------+
1 row in set (0.00 sec)
```

You can also see the two values in `INFORMATION_SCHEMA`:

```sql
SELECT DEFAULT_CHARACTER_SET_NAME, DEFAULT_COLLATION_NAME
FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'db_name';
```
### Table character set and collation

You can use the following statement to specify the character set and collation for tables:

```sql
CREATE TABLE tbl_name (column_list)
    [[DEFAULT] CHARACTER SET charset_name]
    [COLLATE collation_name]]

ALTER TABLE tbl_name
    [[DEFAULT] CHARACTER SET charset_name]
    [COLLATE collation_name]
```

For example:

```sql
CREATE TABLE t1(a int) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```

```sql
Query OK, 0 rows affected (0.08 sec)
```

If the table character set and collation are not specified, the database character set and collation are used as their default values. If you only specify the character set as `utf8mb4` without specifying the collation, the collation is determined by the value of the system variable [`default_collation_for_utf8mb4`](https://docs.pingcap.com/tidb/stable/system-variables#default_collation_for_utf8mb4-new-in-v740).
