# Old and new collation support frameworks

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/character-set-and-collation.md`
- Source Title: `Character Set and Collation`
- Source Heading Path: `Character Set and Collation > Collation support framework | Character Set and Collation > Collation support framework > Old framework for collations | Character Set and Collation > Collation support framework > New framework for collations`
- Source Line Ranges: `439-569`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `collation-framework`, `new-collations`, `old-collations`, `bootstrap-configuration`, `mysql-compatibility`, `string-comparison`, `padding-behavior`, `version-dependence`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0039_dfabc63f9c`
- Source ID: `tidb-docs-8.1:character-set-and-collation.md#collation-support-framework`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ab82ad88add673633f73fa1fd263364299defd59aa7e298126db29c83ef852a8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/character-set-and-collation#collation-support-framework
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/character-set-and-collation.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official distinction between the old and new collation frameworks, how `new_collations_enabled_on_first_bootstrap` affects syntax and semantic support, and how to verify the actual setting in an initialized cluster.
- Retrieval Keywords: Collation support framework, new_collations_enabled_on_first_bootstrap, new_collation_enabled, mysql.tidb, SELECT VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME='new_collation_enabled', old framework for collations, new framework for collations, utf8mb4_general_ci, utf8mb4_unicode_ci, utf8mb4_0900_ai_ci, gbk_chinese_ci, Duplicate entry 'a', PADDING behavior
- Follow-up Guidance: The content also lists the collations supported under the new framework and shows the case-insensitive and padding-related duplicate key behavior differences compared with the old framework.
- Classification Note: This is reference content because it explains configuration-controlled collation semantics, compatibility behavior, supported collations, and the exact SQL query used to inspect the effective setting.

## Official Source Content

## Collation support framework

The syntax support and semantic support for the collation are influenced by the [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap) configuration item. The syntax support and semantic support are different. The former indicates that TiDB can parse and set collations. The latter indicates that TiDB can correctly use collations when comparing strings.

Before v4.0, TiDB provides only the [old framework for collations](#old-framework-for-collations). In this framework, TiDB supports syntactically parsing most of the MySQL collations but semantically takes all collations as binary collations.

Since v4.0, TiDB supports a [new framework for collations](#new-framework-for-collations). In this framework, TiDB semantically parses different collations and strictly follows the collations when comparing strings.
### Old framework for collations

Before v4.0, you can specify most of the MySQL collations in TiDB, and these collations are processed according to the default collations, which means that the byte order determines the character order. Different from MySQL, TiDB does not handle the trailing spaces of a character, which causes the following behavior differences:

```sql
CREATE TABLE t(a varchar(20) charset utf8mb4 collate utf8mb4_general_ci PRIMARY KEY);
```

```sql
Query OK, 0 rows affected
```

```sql
INSERT INTO t VALUES ('A');
```

```sql
Query OK, 1 row affected
```

```sql
INSERT INTO t VALUES ('a');
```

```sql
Query OK, 1 row affected
```

In TiDB, the preceding statement is successfully executed. In MySQL, because `utf8mb4_general_ci` is case-insensitive, the `Duplicate entry 'a'` error is reported.

```sql
INSERT INTO t1 VALUES ('a ');
```

```sql
Query OK, 1 row affected
```

In TiDB, the preceding statement is successfully executed. In MySQL, because comparison is performed after the spaces are filled in, the `Duplicate entry 'a '` error is returned.
### New framework for collations

Since TiDB v4.0, a complete framework for collations is introduced.

This new framework supports semantically parsing collations and introduces the `new_collations_enabled_on_first_bootstrap` configuration item to decide whether to enable the new framework when a cluster is first initialized. To enable the new framework, set `new_collations_enabled_on_first_bootstrap` to `true`. For details, see [`new_collations_enabled_on_first_bootstrap`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#new_collations_enabled_on_first_bootstrap).

For a TiDB cluster that is already initialized, you can check whether the new collation is enabled through the `new_collation_enabled` variable in the `mysql.tidb` table:

> **Note:**
>
> If the query result of the `mysql.tidb` table is different from the value of `new_collations_enabled_on_first_bootstrap`, the result of the `mysql.tidb` table is the actual value.

```sql
SELECT VARIABLE_VALUE FROM mysql.tidb WHERE VARIABLE_NAME='new_collation_enabled';
```

```sql
+----------------+
| VARIABLE_VALUE |
+----------------+
| True           |
+----------------+
1 row in set (0.00 sec)
```

This new framework supports semantically parsing collations. TiDB enables the new framework by default when a cluster is first initialized.

Under the new framework, TiDB supports the `utf8_general_ci`, `utf8mb4_general_ci`, `utf8_unicode_ci`, `utf8mb4_unicode_ci`, `utf8mb4_0900_bin`, `utf8mb4_0900_ai_ci`, `gbk_chinese_ci`, and `gbk_bin` collations, which is compatible with MySQL.

When one of `utf8_general_ci`, `utf8mb4_general_ci`, `utf8_unicode_ci`, `utf8mb4_unicode_ci`, `utf8mb4_0900_ai_ci` and `gbk_chinese_ci` is used, the string comparison is case-insensitive and accent-insensitive. At the same time, TiDB also corrects the collation's `PADDING` behavior:

```sql
CREATE TABLE t(a varchar(20) charset utf8mb4 collate utf8mb4_general_ci PRIMARY KEY);
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
INSERT INTO t VALUES ('A');
```

```sql
Query OK, 1 row affected (0.00 sec)
```

```sql
INSERT INTO t VALUES ('a');
```

```sql
ERROR 1062 (23000): Duplicate entry 'a' for key 't.PRIMARY' -- TiDB is compatible with the case-insensitive collation of MySQL.
```

```sql
INSERT INTO t VALUES ('a ');
```

```sql
ERROR 1062 (23000): Duplicate entry 'a ' for key 't.PRIMARY' -- TiDB modifies the `PADDING` behavior to be compatible with MySQL.
```

> **Note:**
>
> The implementation of padding in TiDB is different from that in MySQL. In MySQL, padding is implemented by filling in spaces. In TiDB, padding is implemented by cutting out the spaces at the end. The two approaches are the same in most cases. The only exception is when the end of the string contains characters that are less than spaces (0x20). For example, the result of `'a' < 'a\t'` in TiDB is `1`, but in MySQL, `'a' < 'a\t'` is equivalent to `'a ' < 'a\t'`, and the result is `0`.
