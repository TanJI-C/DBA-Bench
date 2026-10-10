# AUTO_RANDOM overview, usage, and value structure

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/auto-random.md`
- Source Title: `AUTO_RANDOM`
- Source Heading Path: `AUTO_RANDOM <span class="version-mark">New in v3.1.0</span> | AUTO_RANDOM <span class="version-mark">New in v3.1.0</span> > User scenario | AUTO_RANDOM <span class="version-mark">New in v3.1.0</span> > Basic concepts`
- Source Line Ranges: `5-119`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `auto_random`, `primary-key`, `bigint`, `write-hotspot`, `auto_increment`, `insert`, `show-create-table`, `regions`, `shard-bits`, `id-allocation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0008_63cba00c0d`
- Source ID: `tidb-docs-8.1:auto-random.md#auto-random-span-class-version-mark-new-in-v3-1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6de12b669260e659917e6e6799b8c4136effe441df83a7e277674c7073095042`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/auto-random#auto-random-span-class-version-mark-new-in-v3-1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/auto-random.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the AUTO_RANDOM column attribute, how it differs from AUTO_INCREMENT for avoiding write hotspot, or how AUTO_RANDOM values are structured and shown in SQL examples.
- Retrieval Keywords: AUTO_RANDOM, AUTO_INCREMENT, write hotspot, BIGINT PRIMARY KEY AUTO_RANDOM, ALTER TABLE t MODIFY COLUMN id BIGINT AUTO_RANDOM(5);, AUTO_RANDOM_BASE, CREATE TABLE, INSERT, SHOW CREATE TABLE, SHOW TABLE t REGIONS, PRE_SPLIT_REGIONS, AUTO_RANDOM(5, 54), shard bits, auto-increment bits, random and unique, TiDB specific comment syntax
- Follow-up Guidance: The chunk also includes example CREATE TABLE, INSERT, SHOW CREATE TABLE, and SHOW TABLE t REGIONS output, plus the bit layout and parameter ranges for AUTO_RANDOM(S, R).
- Classification Note: This is reference content because it defines AUTO_RANDOM semantics, SQL syntax, examples, and the 64-bit value structure for a TiDB SQL feature.

## Official Source Content

# AUTO_RANDOM New in v3.1.0
## User scenario

Since the value of `AUTO_RANDOM` is random and unique, `AUTO_RANDOM` is often used in place of [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) to avoid write hotspot in a single storage node caused by TiDB assigning consecutive IDs. If the current `AUTO_INCREMENT` column is a primary key and the type is `BIGINT`, you can execute the `ALTER TABLE t MODIFY COLUMN id BIGINT AUTO_RANDOM(5);` statement to switch from `AUTO_INCREMENT` to `AUTO_RANDOM`.

For more information about how to handle highly concurrent write-heavy workloads in TiDB, see [Highly concurrent write best practices](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices).

The `AUTO_RANDOM_BASE` parameter in the [CREATE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) statement is used to set the initial incremental part value of `auto_random`. This option can be considered as a part of the internal interface. You can ignore this parameter.
## Basic concepts

`AUTO_RANDOM` is a column attribute that is used to automatically assign values to a `BIGINT` column. Values assigned automatically are **random** and **unique**.

To create a table with an `AUTO_RANDOM` column, you can use the following statements. The `AUTO_RANDOM` column must be included in a primary key, and the `AUTO_RANDOM` column is the first column in the primary key.

```sql
CREATE TABLE t (a BIGINT AUTO_RANDOM, b VARCHAR(255), PRIMARY KEY (a));
CREATE TABLE t (a BIGINT PRIMARY KEY AUTO_RANDOM, b VARCHAR(255));
CREATE TABLE t (a BIGINT AUTO_RANDOM(6), b VARCHAR(255), PRIMARY KEY (a));
CREATE TABLE t (a BIGINT AUTO_RANDOM(5, 54), b VARCHAR(255), PRIMARY KEY (a));
CREATE TABLE t (a BIGINT AUTO_RANDOM(5, 54), b VARCHAR(255), PRIMARY KEY (a, b));
```

You can wrap the keyword `AUTO_RANDOM` in an executable comment. For more details, refer to [TiDB specific comment syntax](https://docs.pingcap.com/tidb/stable/comment-syntax#tidb-specific-comment-syntax).

```sql
CREATE TABLE t (a bigint /*T![auto_rand] AUTO_RANDOM */, b VARCHAR(255), PRIMARY KEY (a));
CREATE TABLE t (a bigint PRIMARY KEY /*T![auto_rand] AUTO_RANDOM */, b VARCHAR(255));
CREATE TABLE t (a BIGINT /*T![auto_rand] AUTO_RANDOM(6) */, b VARCHAR(255), PRIMARY KEY (a));
CREATE TABLE t (a BIGINT  /*T![auto_rand] AUTO_RANDOM(5, 54) */, b VARCHAR(255), PRIMARY KEY (a));
```

When you execute an `INSERT` statement:

- If you explicitly specify the value of the `AUTO_RANDOM` column, it is inserted into the table as is.
- If you do not explicitly specify the value of the `AUTO_RANDOM` column, TiDB generates a random value and inserts it into the table.
```sql
tidb> CREATE TABLE t (a BIGINT PRIMARY KEY AUTO_RANDOM, b VARCHAR(255)) /*T! PRE_SPLIT_REGIONS=2 */ ;
Query OK, 0 rows affected, 1 warning (0.01 sec)

tidb> INSERT INTO t(a, b) VALUES (1, 'string');
Query OK, 1 row affected (0.00 sec)

tidb> SELECT * FROM t;
+---+--------+
| a | b      |
+---+--------+
| 1 | string |
+---+--------+
1 row in set (0.01 sec)

tidb> INSERT INTO t(b) VALUES ('string2');
Query OK, 1 row affected (0.00 sec)

tidb> INSERT INTO t(b) VALUES ('string3');
Query OK, 1 row affected (0.00 sec)

tidb> SELECT * FROM t;
+---------------------+---------+
| a                   | b       |
+---------------------+---------+
|                   1 | string  |
| 1152921504606846978 | string2 |
| 4899916394579099651 | string3 |
+---------------------+---------+
3 rows in set (0.00 sec)

tidb> SHOW CREATE TABLE t;
+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Table | Create Table                                                                                                                                                                                                                                                    |
+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| t     | CREATE TABLE `t` (
  `a` bigint(20) NOT NULL /*T![auto_rand] AUTO_RANDOM(5) */,
  `b` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`a`) /*T![clustered_index] CLUSTERED */
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T! PRE_SPLIT_REGIONS=2 */ |
+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.00 sec)

tidb> SHOW TABLE t REGIONS;
+-----------+-----------------------------+-----------------------------+-----------+-----------------+---------------------+------------+---------------+------------+----------------------+------------------+------------------------+------------------+
| REGION_ID | START_KEY                   | END_KEY                     | LEADER_ID | LEADER_STORE_ID | PEERS               | SCATTERING | WRITTEN_BYTES | READ_BYTES | APPROXIMATE_SIZE(MB) | APPROXIMATE_KEYS | SCHEDULING_CONSTRAINTS | SCHEDULING_STATE |
+-----------+-----------------------------+-----------------------------+-----------+-----------------+---------------------+------------+---------------+------------+----------------------+------------------+------------------------+------------------+
|     62798 | t_158_                      | t_158_r_2305843009213693952 |     62810 |              28 | 62811, 62812, 62810 |          0 |           151 |          0 |                    1 |                0 |                        |                  |
|     62802 | t_158_r_2305843009213693952 | t_158_r_4611686018427387904 |     62803 |               1 | 62803, 62804, 62805 |          0 |            39 |          0 |                    1 |                0 |                        |                  |
|     62806 | t_158_r_4611686018427387904 | t_158_r_6917529027641081856 |     62813 |               4 | 62813, 62814, 62815 |          0 |           160 |          0 |                    1 |                0 |                        |                  |
|      9289 | t_158_r_6917529027641081856 | 78000000                    |     48268 |               1 | 48268, 58951, 62791 |          0 |         10628 |      43639 |                    2 |             7999 |                        |                  |
+-----------+-----------------------------+-----------------------------+-----------+-----------------+---------------------+------------+---------------+------------+----------------------+------------------+------------------------+------------------+
4 rows in set (0.00 sec)
```

The `AUTO_RANDOM(S, R)` column value automatically assigned by TiDB has a total of 64 bits:

- `S` is the number of shard bits. The value ranges from `1` to `15`. The default value is `5`.
- `R` is the total length of the automatic allocation range. The value ranges from `32` to `64`. The default value is `64`.

The structure of an `AUTO_RANDOM` value with a signed bit is as follows:

| Signed bit | Reserved bits | Shard bits | Auto-increment bits |
|---------|-------------|--------|--------------|
| 1 bit | `64-R` bits | `S` bits | `R-1-S` bits |

The structure of an `AUTO_RANDOM` value without a signed bit is as follows:

| Reserved bits | Shard bits | Auto-increment bits |
|-------------|--------|--------------|
| `64-R` bits | `S` bits | `R-S` bits |
