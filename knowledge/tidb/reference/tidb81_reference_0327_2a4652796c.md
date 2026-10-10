# Miscellaneous SQL functions: IP, UUID, naming, sleep, values, and unsupported functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/miscellaneous-functions.md`
- Source Title: `Miscellaneous Functions`
- Source Heading Path: `Miscellaneous Functions > Supported functions > IS_IPV4_COMPAT() | Miscellaneous Functions > Supported functions > IS_IPV4_MAPPED() | Miscellaneous Functions > Supported functions > IS_IPV6() | Miscellaneous Functions > Supported functions > IS_UUID() | Miscellaneous Functions > Supported functions > NAME_CONST() | Miscellaneous Functions > Supported functions > SLEEP() | Miscellaneous Functions > Supported functions > UUID() | Miscellaneous Functions > Supported functions > UUID_TO_BIN | Miscellaneous Functions > Supported functions > VALUES() | Miscellaneous Functions > Unsupported functions`
- Source Line Ranges: `244-419`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `sql-functions`, `ip-addresses`, `uuid`, `column-aliases`, `query-execution`, `insert`, `duplicate-key`, `unsupported-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0327_2a4652796c`
- Source ID: `tidb-docs-8.1:functions-and-operators/miscellaneous-functions.md#is-ipv4-compat`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5f64243b6673facec91480c2808404367f0065904c37cc0f7110bec7031a289f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions#is-ipv4-compat
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/miscellaneous-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking up miscellaneous SQL functions for IP address checks, UUID validation or generation, column naming, query sleeping, INSERT ... ON DUPLICATE KEY UPDATE value references, or the unsupported UUID_SHORT() function.
- Retrieval Keywords: IS_IPV4_COMPAT(), IS_IPV4_MAPPED(), IS_IPV6(), IS_UUID(), NAME_CONST(), SLEEP(), UUID(), UUID_TO_BIN, VALUES(col_name), ON DUPLICATE KEY UPDATE, INSERT, UUID_SHORT(), IPv4-compatible address, IPv4-mapped address, IPv6 address, RFC 4122, column aliases, pause the execution of queries, unsupported functions
- Follow-up Guidance: The source also points from UUID_TO_BIN to BIN_TO_UUID() and links UUID() and IS_UUID() related usage to Best practices for UUID.
- Classification Note: This is reference content because it defines supported and unsupported miscellaneous SQL functions and shows exact SQL examples and outputs for each function.

## Official Source Content

### IS_IPV4_COMPAT()

The `IS_IPV4_COMPAT()` function tests whether the given argument is an IPv4-compatible address.

```sql
SELECT IS_IPV4_COMPAT(INET6_ATON('::127.0.0.1'));
```

```
+-------------------------------------------+
| IS_IPV4_COMPAT(INET6_ATON('::127.0.0.1')) |
+-------------------------------------------+
|                                         1 |
+-------------------------------------------+
1 row in set (0.00 sec)
```
### IS_IPV4_MAPPED()

The `IS_IPV4_MAPPED()` function tests whether the given argument is an IPv4-mapped address.

```sql
SELECT IS_IPV4_MAPPED(INET6_ATON('::ffff:127.0.0.1'));
```

```
+------------------------------------------------+
| IS_IPV4_MAPPED(INET6_ATON('::ffff:127.0.0.1')) |
+------------------------------------------------+
|                                              1 |
+------------------------------------------------+
1 row in set (0.00 sec)
```
### IS_IPV6()

The `IS_IPV6()` function tests whether the given argument is an IPv6 address.

```sql
SELECT IS_IPV6('::1');
```

```
+----------------+
| IS_IPV6('::1') |
+----------------+
|              1 |
+----------------+
1 row in set (0.00 sec)
```
### IS_UUID()

The `IS_UUID()` function tests whether the given argument is a [UUID](https://docs.pingcap.com/tidb/stable/best-practices/uuid).

```sql
SELECT IS_UUID('eb48c08c-eb71-11ee-bacf-5405db7aad56');
```

```
+-------------------------------------------------+
| IS_UUID('eb48c08c-eb71-11ee-bacf-5405db7aad56') |
+-------------------------------------------------+
|                                               1 |
+-------------------------------------------------+
1 row in set (0.00 sec)
```
### NAME_CONST()

The `NAME_CONST()` function is used to name columns. It is recommended to use column aliases instead.

```sql
SELECT NAME_CONST('column name', 'value') UNION ALL SELECT 'another value';
```

```
+---------------+
| column name   |
+---------------+
| another value |
| value         |
+---------------+
2 rows in set (0.00 sec)
```

The preceding statement uses `NAME_CONST()` and the following statement uses the recommended way of aliasing columns.

```sql
SELECT 'value' AS 'column name' UNION ALL SELECT 'another value';
```

```
+---------------+
| column name   |
+---------------+
| value         |
| another value |
+---------------+
2 rows in set (0.00 sec)
```
### SLEEP()

The `SLEEP()` function is used to pause the execution of queries for a specified number of seconds.

```sql
SELECT SLEEP(1.5);
```

```
+------------+
| SLEEP(1.5) |
+------------+
|          0 |
+------------+
1 row in set (1.50 sec)
```
### UUID()

The `UUID()` function returns a universally unique identifier (UUID) version 1 as defined in [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122).

```sql
SELECT UUID();
```

```
+--------------------------------------+
| UUID()                               |
+--------------------------------------+
| cb4d5ae6-eb6b-11ee-bacf-5405db7aad56 |
+--------------------------------------+
1 row in set (0.00 sec)
```

See also [Best practices for UUID](https://docs.pingcap.com/tidb/stable/best-practices/uuid).
### UUID_TO_BIN

See [BIN_TO_UUID()](#bin_to_uuid).
### VALUES()

The `VALUES(col_name)` function is used to reference the value of a specific column in the `ON DUPLICATE KEY UPDATE` clause of an [`INSERT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert) statement.

```sql
CREATE TABLE t1 (id INT PRIMARY KEY, c1 INT);
Query OK, 0 rows affected (0.17 sec)

INSERT INTO t1 VALUES (1,51),(2,52),(3,53),(4,54),(5,55);
Query OK, 5 rows affected (0.01 sec)
Records: 5  Duplicates: 0  Warnings: 0

INSERT INTO t1 VALUES(2,22),(4,44) ON DUPLICATE KEY UPDATE c1=VALUES(id)+100;
Query OK, 4 rows affected (0.01 sec)
Records: 2  Duplicates: 2  Warnings: 0

TABLE t1;
+----+------+
| id | c1   |
+----+------+
|  1 |   51 |
|  2 |  102 |
|  3 |   53 |
|  4 |  104 |
|  5 |   55 |
+----+------+
5 rows in set (0.00 sec)
```
## Unsupported functions

| Name | Description  |
|:------------|:-----------------------------------------------------------------------------------------------|
| [`UUID_SHORT()`](https://dev.mysql.com/doc/refman/8.0/en/miscellaneous-functions.html#function_uuid-short)            | Provides a UUID that is unique given certain assumptions not present in TiDB [TiDB #4620](https://github.com/pingcap/tidb/issues/4620) |
