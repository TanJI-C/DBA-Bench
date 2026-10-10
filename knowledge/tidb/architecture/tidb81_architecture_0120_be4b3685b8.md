# TSO structure and parsing in TiDB

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tso.md`
- Source Title: `TimeStamp Oracle (TSO) in TiDB`
- Source Heading Path: `TimeStamp Oracle (TSO) in TiDB`
- Source Line Ranges: `5-96`
- Source Scope: `all`
- Primary Component: `pd`
- Related Components: `tidb`, `tiup`
- Topic Tags: `tso`, `timestamps`, `pd`, `mvcc`, `transactions`, `percolator`, `physical-timestamp`, `logical-timestamp`, `sql-functions`, `bitwise-operations`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0120_be4b3685b8`
- Source ID: `tidb-docs-8.1:tso.md#timestamp-oracle-tso-in-tidb`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `38c9fe1b477efeea152edc36f211914169cd6162f3e521838bac226138ead620`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tso#timestamp-oracle-tso-in-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tso.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how TiDB TSO is structured, how to obtain the current TSO, or how to parse its physical and logical parts in SQL or via the PD CLI.
- Retrieval Keywords: TimeStamp Oracle (TSO) in TiDB, Placement Driver (PD), @@tidb_current_ts, BEGIN; SET @ts := @@tidb_current_ts; ROLLBACK;, TIDB_PARSE_TSO(), TIDB_PARSE_TSO_LOGICAL(), @ts >> 18, @ts & 0x3FFFF, physical timestamp, logical timestamp, FROM_UNIXTIME((@ts >> 18)/1000), UNIX timestamp in milliseconds, Percolator, MVCC, tiup ctl:v7.1.0 pd tso
- Follow-up Guidance: The source also shows that TSO timestamps are assigned per transaction and includes SQL examples using bitwise right shift and mask operations plus a `tiup ctl:v7.1.0 pd tso` example to display `system:` and `logic:` values.
- Classification Note: This chunk is classified as architecture for PD because it explains PD's role in allocating TSO timestamps and describes the timestamp format used for MVCC and transaction management in TiDB.

## Official Source Content

# TimeStamp Oracle (TSO) in TiDB

In TiDB, the Placement Driver (PD) plays a pivotal role in allocating timestamps to various components within a cluster. These timestamps are instrumental in the assignment of temporal markers to transactions and data, a mechanism crucial for enabling the [Percolator](https://research.google/pubs/large-scale-incremental-processing-using-distributed-transactions-and-notifications/) model within TiDB. The Percolator model is used to support [Multi-Version Concurrency Control (MVCC)](https://docs.pingcap.com/tidb/stable/glossary#multi-version-concurrency-control-mvcc) and [transaction management](https://docs.pingcap.com/tidb/stable/transaction-overview).

The following example shows how to get the current TSO in TiDB:

```sql
BEGIN; SET @ts := @@tidb_current_ts; ROLLBACK;
Query OK, 0 rows affected (0.0007 sec)
Query OK, 0 rows affected (0.0002 sec)
Query OK, 0 rows affected (0.0001 sec)

SELECT @ts;
+--------------------+
| @ts                |
+--------------------+
| 443852055297916932 |
+--------------------+
1 row in set (0.00 sec)
```

Note that this is done in a transaction with `BEGIN; ...; ROLLBACK` because TSO timestamps are assigned per transaction.

The TSO timestamp you get from the preceding example is a decimal number. You can use the following SQL functions to parse the timestamp:

- [`TIDB_PARSE_TSO()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_parse_tso)
- [`TIDB_PARSE_TSO_LOGICAL()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions)

```sql
SELECT TIDB_PARSE_TSO(443852055297916932);
+------------------------------------+
| TIDB_PARSE_TSO(443852055297916932) |
+------------------------------------+
| 2023-08-27 20:33:41.687000         |
+------------------------------------+
1 row in set (0.00 sec)
```

```sql
SELECT TIDB_PARSE_TSO_LOGICAL(443852055297916932);
+--------------------------------------------+
| TIDB_PARSE_TSO_LOGICAL(443852055297916932) |
+--------------------------------------------+
|                                          4 |
+--------------------------------------------+
1 row in set (0.00 sec)
```

The following example shows what a TSO timestamp looks like in binary:

```shell
0000011000101000111000010001011110111000110111000000000000000100  ← This is 443852055297916932 in binary
0000011000101000111000010001011110111000110111                    ← The first 46 bits are the physical timestamp
                                              000000000000000100  ← The last 18 bits are the logical timestamp
```

There are two parts in a TSO timestamp:

- The physical timestamp: a UNIX timestamp in milliseconds since 1 January 1970.
- The logical timestamp: an incrementing counter, used in scenarios requiring multiple timestamps within the same millisecond, or in cases where certain events might trigger a reversal of the clock's progression. In such cases, the physical timestamp remains unchanged while the logical timestamp steadily advances. This mechanism ensures the integrity of the TSO timestamp, which always moves forward and never regresses.

With this knowledge, you can inspect the TSO timestamp a bit more in SQL:

```sql
SELECT @ts, UNIX_TIMESTAMP(NOW(6)), (@ts >> 18)/1000, FROM_UNIXTIME((@ts >> 18)/1000), NOW(6), @ts & 0x3FFFF\G
*************************** 1. row ***************************
                            @ts: 443852055297916932
         UNIX_TIMESTAMP(NOW(6)): 1693161835.502954
               (@ts >> 18)/1000: 1693161221.6870
FROM_UNIXTIME((@ts >> 18)/1000): 2023-08-27 20:33:41.6870
                         NOW(6): 2023-08-27 20:43:55.502954
                  @ts & 0x3FFFF: 4
1 row in set (0.00 sec)
```

The `>> 18` operation signifies a bitwise [right shift](https://docs.pingcap.com/tidb/stable/functions-and-operators/bit-functions-and-operators#-right-shift) by 18 bits, which is used to extract the physical timestamp. Because the physical timestamp is expressed in milliseconds, deviating from the more common UNIX timestamp format measured in seconds, you need to divide it by 1000 to convert it into a format compatible with [`FROM_UNIXTIME()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/date-and-time-functions). This process aligns with the functionality of `TIDB_PARSE_TSO()`.

You can also extract the logical timestamp `000000000000000100` in binary, which is equivalent to `4` in decimal.

You can also parse the timestamp via the CLI tool as follows:

```shell
$ tiup ctl:v7.1.0 pd tso 443852055297916932
```

```
system:  2023-08-27 20:33:41.687 +0200 CEST
logic:   4
```

Here you can see the physical timestamp in the line that starts with `system:` and the logical timestamp in the line that starts with `logic:`.
