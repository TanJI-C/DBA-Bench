# Miscellaneous SQL functions: overview and supported examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/miscellaneous-functions.md`
- Source Title: `Miscellaneous Functions`
- Source Heading Path: `Miscellaneous Functions | Miscellaneous Functions > Supported functions | Miscellaneous Functions > Supported functions > ANY_VALUE() | Miscellaneous Functions > Supported functions > BIN_TO_UUID() | Miscellaneous Functions > Supported functions > DEFAULT() | Miscellaneous Functions > Supported functions > GROUPING() | Miscellaneous Functions > Supported functions > INET_ATON() | Miscellaneous Functions > Supported functions > INET_NTOA() | Miscellaneous Functions > Supported functions > INET6_ATON() | Miscellaneous Functions > Supported functions > INET6_NTOA() | Miscellaneous Functions > Supported functions > IS_IPV4()`
- Source Line Ranges: `5-243`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `miscellaneous-functions`, `mysql-compatibility`, `group-by`, `uuid`, `default-values`, `ip-addresses`, `ipv4`, `ipv6`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0326_2deca12dcb`
- Source ID: `tidb-docs-8.1:functions-and-operators/miscellaneous-functions.md#miscellaneous-functions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e8857baf5f3fab64500c427644c491eabb9146dcf15357d23ed927cd01de3394`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions#miscellaneous-functions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/miscellaneous-functions.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB miscellaneous SQL functions such as ANY_VALUE(), BIN_TO_UUID(), DEFAULT(), GROUPING(), INET_ATON(), INET_NTOA(), INET6_ATON(), INET6_NTOA(), and IS_IPV4(), including examples and the ONLY_FULL_GROUP_BY error context.
- Retrieval Keywords: miscellaneous functions, MySQL 8.0 miscellaneous functions, ANY_VALUE(), ONLY_FULL_GROUP_BY, ERROR 1055 (42000), GROUP BY clause, GROUP_CONCAT(id), BIN_TO_UUID(), UUID_TO_BIN(), UUID(), DEFAULT(), GROUPING(), INET_ATON(), INET_NTOA(), INET6_ATON(), INET6_NTOA(), IS_IPV4(), IPv4 address, IPv6 address, dotted-quad notation
- Follow-up Guidance: The content also points to the GROUP BY modifiers page for GROUPING() and to UUID() and Best practices for UUID for related UUID information.
- Classification Note: This is reference content because it lists supported miscellaneous SQL functions and shows exact SQL statements, outputs, and error text for each function.

## Official Source Content

# Miscellaneous Functions

TiDB supports most of the [miscellaneous functions](https://dev.mysql.com/doc/refman/8.0/en/miscellaneous-functions.html) available in MySQL 8.0.
## Supported functions

| Name | Description  |
|:------------|:-----------------------------------------------------------------------------------------------|
| [`ANY_VALUE()`](#any_value)              | Suppress `ONLY_FULL_GROUP_BY` value rejection     |
| [`BIN_TO_UUID()`](#bin_to_uuid)          | Convert UUID from binary format to text format    |
| [`DEFAULT()`](#default)                  | Returns the default value for a table column      |
| [`GROUPING()`](#grouping)                | Modifier for `GROUP BY` operations                |
| [`INET_ATON()`](#inet_aton)              | Return the numeric value of an IP address         |
| [`INET_NTOA()`](#inet_ntoa)              | Return the IP address from a numeric value        |
| [`INET6_ATON()`](#inet6_aton)            | Return the numeric value of an IPv6 address       |
| [`INET6_NTOA()`](#inet6_ntoa)            | Return the IPv6 address from a numeric value      |
| [`IS_IPV4()`](#is_ipv4)                  | Whether argument is an IPv4 address               |
| [`IS_IPV4_COMPAT()`](#is_ipv4_compat)    | Whether argument is an IPv4-compatible address    |
| [`IS_IPV4_MAPPED()`](#is_ipv4_mapped)    | Whether argument is an IPv4-mapped address        |
| [`IS_IPV6()`](#is_ipv6)                  | Whether argument is an IPv6 address               |
| [`IS_UUID()`](#is_uuid)                  | Whether argument is an UUID                       |
| [`NAME_CONST()`](#name_const)            | Can be used to rename a column name               |
| [`SLEEP()`](#sleep)                      | Sleep for a number of seconds. Note that for [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters, the `SLEEP()` function has a limitation wherein it can only support a maximum sleep time of 300 seconds.       |
| [`UUID()`](#uuid)                        | Return a Universal Unique Identifier (UUID)       |
| [`UUID_TO_BIN()`](#uuid_to_bin)          | Convert UUID from text format to binary format    |
| [`VALUES()`](#values)                    | Defines the values to be used during an INSERT    |
### ANY_VALUE()

The `ANY_VALUE()` function returns any value from a group of values. Typically, it is used in scenarios where you need to include non-aggregated columns in your `SELECT` statement along with a `GROUP BY` clause.

```sql
CREATE TABLE fruits (id INT PRIMARY KEY, name VARCHAR(255));
Query OK, 0 rows affected (0.14 sec)

INSERT INTO fruits VALUES (1,'apple'),(2,'apple'),(3,'pear'),(4,'banana'),(5, 'pineapple');
Query OK, 5 rows affected (0.01 sec)
Records: 5  Duplicates: 0  Warnings: 0

SELECT id,name FROM fruits GROUP BY name;
ERROR 1055 (42000): Expression #1 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'test.fruits.id' which is not functionally dependent on columns in GROUP BY clause; this is incompatible with sql_mode=only_full_group_by

SELECT ANY_VALUE(id),GROUP_CONCAT(id),name FROM fruits GROUP BY name;
+---------------+------------------+-----------+
| ANY_VALUE(id) | GROUP_CONCAT(id) | name      |
+---------------+------------------+-----------+
|             1 | 1,2              | apple     |
|             3 | 3                | pear      |
|             4 | 4                | banana    |
|             5 | 5                | pineapple |
+---------------+------------------+-----------+
4 rows in set (0.00 sec)
```

In the preceding example, TiDB returns an error for the first `SELECT` statement because the `id` column is non-aggregated and not included in the `GROUP BY` clause. To address the issue, the second `SELECT` query uses `ANY_VALUE()` to get any value from each group and uses `GROUP_CONCAT()` to concatenate all values of the `id` column within each group into a single string. This approach enables you to get one value from each group and all values of the group without changing the SQL mode for non-aggregated columns.
### BIN_TO_UUID()

`BIN_TO_UUID()` and `UUID_TO_BIN()` can be used to convert between a textual format UUID and a binary format. Both functions accept two arguments.

- The first argument specifies the value to be converted.
- The second argument (optional) controls the ordering of the fields in the binary format.

```sql
SET @a := UUID();
Query OK, 0 rows affected (0.00 sec)

SELECT @a;
+--------------------------------------+
| @a                                   |
+--------------------------------------+
| 9a17b457-eb6d-11ee-bacf-5405db7aad56 |
+--------------------------------------+
1 row in set (0.00 sec)

SELECT UUID_TO_BIN(@a);
+------------------------------------+
| UUID_TO_BIN(@a)                    |
+------------------------------------+
| 0x9A17B457EB6D11EEBACF5405DB7AAD56 |
+------------------------------------+
1 row in set (0.00 sec)

SELECT BIN_TO_UUID(0x9A17B457EB6D11EEBACF5405DB7AAD56);
+-------------------------------------------------+
| BIN_TO_UUID(0x9A17B457EB6D11EEBACF5405DB7AAD56) |
+-------------------------------------------------+
| 9a17b457-eb6d-11ee-bacf-5405db7aad56            |
+-------------------------------------------------+
1 row in set (0.00 sec)

SELECT UUID_TO_BIN(@a, 1);
+----------------------------------------+
| UUID_TO_BIN(@a, 1)                     |
+----------------------------------------+
| 0x11EEEB6D9A17B457BACF5405DB7AAD56     |
+----------------------------------------+
1 row in set (0.00 sec)

SELECT BIN_TO_UUID(0x11EEEB6D9A17B457BACF5405DB7AAD56, 1);
+----------------------------------------------------+
| BIN_TO_UUID(0x11EEEB6D9A17B457BACF5405DB7AAD56, 1) |
+----------------------------------------------------+
| 9a17b457-eb6d-11ee-bacf-5405db7aad56               |
+----------------------------------------------------+
1 row in set (0.00 sec)
```

See also [UUID()](#uuid) and [Best practices for UUID](https://docs.pingcap.com/tidb/stable/best-practices/uuid).
### DEFAULT()

The `DEFAULT()` function is used to get the default value of a column.

```sql
CREATE TABLE t1 (id INT PRIMARY KEY, c1 INT DEFAULT 5);
Query OK, 0 rows affected (0.15 sec)

INSERT INTO t1 VALUES (1, 1);
Query OK, 1 row affected (0.01 sec)

UPDATE t1 SET c1=DEFAULT(c1)+3;
Query OK, 1 row affected (0.02 sec)
Rows matched: 1  Changed: 1  Warnings: 0

TABLE t1;
+----+------+
| id | c1   |
+----+------+
|  1 |    8 |
+----+------+
1 row in set (0.00 sec)
```

In the preceding example, the `UPDATE` statement sets the value of the `c1` column to the default value of the column (which is `5`) plus `3`, resulting in a new value of `8`.
### GROUPING()

See [`GROUP BY` modifiers](https://docs.pingcap.com/tidb/stable/functions-and-operators/group-by-modifier).
### INET_ATON()

The `INET_ATON()` function converts an IPv4 address in dotted-quad notation into a binary version that can be stored efficiently.

```sql
SELECT INET_ATON('127.0.0.1');
```

```
+------------------------+
| INET_ATON('127.0.0.1') |
+------------------------+
|             2130706433 |
+------------------------+
1 row in set (0.00 sec)
```
### INET_NTOA()

The `INET_NTOA()` function converts a binary IPv4 address into a dotted-quad notation.

```sql
SELECT INET_NTOA(2130706433);
```

```
+-----------------------+
| INET_NTOA(2130706433) |
+-----------------------+
| 127.0.0.1             |
+-----------------------+
1 row in set (0.00 sec)
```
### INET6_ATON()

The `INET6_ATON()` function is similar to [`INET_ATON()`](#inet_aton), but `INET6_ATON()` can also handle IPv6 addresses.

```sql
SELECT INET6_ATON('::1');
```

```
+--------------------------------------+
| INET6_ATON('::1')                    |
+--------------------------------------+
| 0x00000000000000000000000000000001   |
+--------------------------------------+
1 row in set (0.00 sec)
```
### INET6_NTOA()

The `INET6_NTOA()` function is similar to [`INET_NTOA()`](#inet_ntoa), but `INET6_NTOA()` can also handle IPv6 addresses.

```sql
SELECT INET6_NTOA(0x00000000000000000000000000000001);
```

```
+------------------------------------------------+
| INET6_NTOA(0x00000000000000000000000000000001) |
+------------------------------------------------+
| ::1                                            |
+------------------------------------------------+
1 row in set (0.00 sec)
```
### IS_IPV4()

The `IS_IPV4()` function tests whether the given argument is an IPv4 address or not.

```sql
SELECT IS_IPV4('127.0.0.1');
```

```
+----------------------+
| IS_IPV4('127.0.0.1') |
+----------------------+
|                    1 |
+----------------------+
1 row in set (0.00 sec)
```

```sql
SELECT IS_IPV4('300.0.0.1');
```

```
+----------------------+
| IS_IPV4('300.0.0.1') |
+----------------------+
|                    0 |
+----------------------+
1 row in set (0.00 sec)
```
