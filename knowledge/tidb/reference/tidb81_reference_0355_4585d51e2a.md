# DDL owner, TSO parsing, and row checksum functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/tidb-functions.md`
- Source Title: `TiDB Specific Functions`
- Source Heading Path: `TiDB Specific Functions > TIDB_IS_DDL_OWNER | TiDB Specific Functions > TIDB_PARSE_TSO | TiDB Specific Functions > TIDB_PARSE_TSO_LOGICAL | TiDB Specific Functions > TIDB_ROW_CHECKSUM`
- Source Line Ranges: `374-483`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`
- Topic Tags: `ddl-owner`, `tso`, `physical-timestamp`, `logical-counter`, `row-checksum`, `fastplan`, `session-reconnect`, `system-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0355_4585d51e2a`
- Source ID: `tidb-docs-8.1:functions-and-operators/tidb-functions.md#tidb-is-ddl-owner`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5a1efb253707c69d286fcd8a8e96ca4a76ae432611422ae09f6a2e58fee9c14`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb-is-ddl-owner
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/tidb-functions.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB-specific functions that check DDL owner status, parse the physical or logical parts of a TSO timestamp, or return a row checksum under FastPlan conditions.
- Retrieval Keywords: TIDB_IS_DDL_OWNER, DDL owner, TIDB_PARSE_TSO, TIDB_PARSE_TSO_LOGICAL, TSO, Time Stamp Oracle, PD, Placement Driver, physical timestamp, logical counter, @@tidb_current_ts, tidb_current_ts, TIDB_ROW_CHECKSUM, FastPlan, SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id = ?, SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id IN (?, ?, ...), tidb_enable_row_level_checksum, SET GLOBAL tidb_enable_row_level_checksum = ON, reconnect to TiDB
- Follow-up Guidance: The source notes that enabling tidb_enable_row_level_checksum only takes effect for newly created sessions, so reconnect to TiDB before using TIDB_ROW_CHECKSUM.
- Classification Note: This is a reference chunk because it documents the purpose, constraints, system variable dependency, and examples for the TiDB-specific functions TIDB_IS_DDL_OWNER, TIDB_PARSE_TSO, TIDB_PARSE_TSO_LOGICAL, and TIDB_ROW_CHECKSUM.

## Official Source Content

## TIDB_IS_DDL_OWNER

The `TIDB_IS_DDL_OWNER()` function returns `1` if the instance you are connected to is the DDL owner.

```sql
SELECT TIDB_IS_DDL_OWNER();
```

```
+---------------------+
| TIDB_IS_DDL_OWNER() |
+---------------------+
|                   1 |
+---------------------+
1 row in set (0.00 sec)
```
## TIDB_PARSE_TSO

The `TIDB_PARSE_TSO()` function extracts the physical timestamp from a TiDB TSO timestamp. [TSO](https://docs.pingcap.com/tidb/stable/tso) stands for Time Stamp Oracle and is a monotonically increasing timestamp given out by PD (Placement Driver) for every transaction.

A TSO is a number that consists of two parts:

- A physical timestamp
- A logical counter

```sql
BEGIN;
SELECT TIDB_PARSE_TSO(@@tidb_current_ts);
ROLLBACK;
```

```sql
+-----------------------------------+
| TIDB_PARSE_TSO(@@tidb_current_ts) |
+-----------------------------------+
| 2021-05-26 11:33:37.776000        |
+-----------------------------------+
1 row in set (0.0012 sec)
```

Here `TIDB_PARSE_TSO` is used to extract the physical timestamp from the timestamp number that is available in the `tidb_current_ts` session variable. Because timestamps are given out per transaction, this function is running in a transaction.
## TIDB_PARSE_TSO_LOGICAL

The `TIDB_PARSE_TSO_LOGICAL(tso)` function returns the logical part of a [TSO](https://docs.pingcap.com/tidb/stable/tso) timestamp.

```sql
SELECT TIDB_PARSE_TSO_LOGICAL(450456244814610433);
```

```
+--------------------------------------------+
| TIDB_PARSE_TSO_LOGICAL(450456244814610433) |
+--------------------------------------------+
|                                          1 |
+--------------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT TIDB_PARSE_TSO_LOGICAL(450456244814610434);
```

```
+--------------------------------------------+
| TIDB_PARSE_TSO_LOGICAL(450456244814610434) |
+--------------------------------------------+
|                                          2 |
+--------------------------------------------+
1 row in set (0.00 sec)
```
## TIDB_ROW_CHECKSUM

The `TIDB_ROW_CHECKSUM()` function is used to query the checksum value of a row. This function can only be used in `SELECT` statements within the FastPlan process. That is, you can query through statements like `SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id = ?` or `SELECT TIDB_ROW_CHECKSUM() FROM t WHERE id IN (?, ?, ...)`.

To enable the checksum feature of single-row data in TiDB (controlled by the system variable [`tidb_enable_row_level_checksum`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_row_level_checksum-new-in-v710)), run the following statement:

```sql
SET GLOBAL tidb_enable_row_level_checksum = ON;
```

This configuration only takes effect for newly created sessions, so you need to reconnect to TiDB.

Create table `t` and insert data:

```sql
USE test;
CREATE TABLE t (id INT PRIMARY KEY, k INT, c CHAR(1));
INSERT INTO t VALUES (1, 10, 'a');
```

The following statement shows how to query the checksum value of the row where `id = 1` in table `t`:

```sql
SELECT *, TIDB_ROW_CHECKSUM() FROM t WHERE id = 1;
```

The output is as follows:

```sql
+----+------+------+---------------------+
| id | k    | c    | TIDB_ROW_CHECKSUM() |
+----+------+------+---------------------+
|  1 |   10 | a    | 3813955661          |
+----+------+------+---------------------+
1 row in set (0.000 sec)
```
