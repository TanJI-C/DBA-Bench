# TiFlash computation layer incompatibility cases

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-compatibility.md`
- Source Title: `TiFlash Compatibility Notes`
- Source Heading Path: `TiFlash Compatibility Notes`
- Source Line Ranges: `5-39`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`, `sql`
- Topic Tags: `compatibility`, `computation-layer`, `overflow`, `window-functions`, `pushdown`, `tikv-read`, `sum`, `string-cast`, `decimal-division`, `query-results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0951_f2946507ad`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-compatibility.md#tiflash-compatibility-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f0bfd2c744e4a80d17bc91a70ca1e6b8e833d92af94b24a24e9959c0a3ff4dc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-compatibility#tiflash-compatibility-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiFlash computation layer incompatibilities that can cause different query behavior from TiDB, such as overflow handling, unsupported pushdown, TiKV reads, SUM on string arguments, or decimal division result differences.
- Retrieval Keywords: TiFlash Compatibility Notes, TiFlash computation layer, BIGINT value is out of range, 9223372036854775807 + 9223372036854775807, overflow value of -2, window functions pushdown, TiFlash supported pushdown calculations, Reading data from TiKV is not supported, SUM(string_col), [FLASH:Coprocessor:Unimplemented] CastStringAsReal is not supported., SELECT SUM(CAST(string_col AS double)) FROM t, decimal division, tidb_isolation_read_engines='tikv', tidb_isolation_read_engines='tiflash', DECIMAL(7,4), SELECT a/b, a/b + 0.0000000000001 FROM t WHERE a/b
- Follow-up Guidance: The content includes an example workaround for the `SUM` string-type argument case by changing `SELECT SUM(string_col) FROM t` to `SELECT SUM(CAST(string_col AS double)) FROM t`.
- Classification Note: This is reference content because it lists documented incompatibility cases in the TiFlash computation layer and gives exact errors, SQL examples, and behavior differences.

## Official Source Content

# TiFlash Compatibility Notes

TiFlash is incompatible with TiDB in the following situations:

* In the TiFlash computation layer:
    * Checking overflowed [numerical values](https://docs.pingcap.com/tidb/stable/data-type-numeric) is not supported. For example, adding two maximum values of the `BIGINT` type `9223372036854775807 + 9223372036854775807`. The expected behavior of this calculation in TiDB is to return the `ERROR 1690 (22003): BIGINT value is out of range` error. However, if this calculation is performed in TiFlash, an overflow value of `-2` is returned without any error.
    * Not all [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions) are supported for [pushdown](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations).
    * Reading data from TiKV is not supported.
    * Currently, the [`SUM`](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions#supported-aggregate-functions) function in TiFlash does not support the string-type argument. But TiDB cannot identify whether any string-type argument has been passed into the `SUM` function during the compiling. Therefore, when you execute statements similar to `SELECT SUM(string_col) FROM t`, TiFlash returns the `[FLASH:Coprocessor:Unimplemented] CastStringAsReal is not supported.` error. To avoid such an error in this case, you need to modify this SQL statement to `SELECT SUM(CAST(string_col AS double)) FROM t`.
    * Currently, TiFlash's decimal division calculation is incompatible with that of TiDB. For example, when dividing decimal, TiFlash performs the calculation always using the type inferred from the compiling. However, TiDB performs this calculation using a type that is more precise than that inferred from the compiling. Therefore, some SQL statements involving the decimal division return different execution results when executed in TiDB + TiKV and in TiDB + TiFlash. For example:

        ```sql
        mysql> CREATE TABLE t (a DECIMAL(3,0), b DECIMAL(10, 0));
        Query OK, 0 rows affected (0.07 sec)
        mysql> INSERT INTO t VALUES (43, 1044774912);
        Query OK, 1 row affected (0.03 sec)
        mysql> ALTER TABLE t SET TIFLASH REPLICA 1;
        Query OK, 0 rows affected (0.07 sec)
        mysql> SET SESSION tidb_isolation_read_engines='tikv';
        Query OK, 0 rows affected (0.00 sec)
        mysql> SELECT a/b, a/b + 0.0000000000001 FROM t WHERE a/b;
        +--------+-----------------------+
        | a/b    | a/b + 0.0000000000001 |
        +--------+-----------------------+
        | 0.0000 |       0.0000000410001 |
        +--------+-----------------------+
        1 row in set (0.00 sec)
        mysql> SET SESSION tidb_isolation_read_engines='tiflash';
        Query OK, 0 rows affected (0.00 sec)
        mysql> SELECT a/b, a/b + 0.0000000000001 FROM t WHERE a/b;
        Empty set (0.01 sec)
        ```

        In the preceding example, `a/b`'s inferred type from the compiling is `DECIMAL(7,4)` both in TiDB and in TiFlash. Constrained by `DECIMAL(7,4)`, `a/b`'s returned type is `0.0000`. In TiDB, `a/b`'s runtime precision is higher than `DECIMAL(7,4)`, so the original table data is not filtered by the `WHERE a/b` condition. However, in TiFlash, the calculation of `a/b` uses `DECIMAL(7,4)` as the result type, so the original table data is filtered by the `WHERE a/b` condition.
