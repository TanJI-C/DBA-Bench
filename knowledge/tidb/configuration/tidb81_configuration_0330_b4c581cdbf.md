# Configure and use tidb_external_ts for historical reads

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-external-ts.md`
- Source Title: `Read Historical Data Using the `tidb_external_ts` Variable`
- Source Heading Path: `Read Historical Data Using the `tidb_external_ts` Variable | Read Historical Data Using the `tidb_external_ts` Variable > Scenarios | Read Historical Data Using the `tidb_external_ts` Variable > Feature description | Read Historical Data Using the `tidb_external_ts` Variable > Usage examples`
- Source Line Ranges: `5-113`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `ticdc`
- Topic Tags: `historical-read`, `system-variables`, `read-only`, `session-scope`, `global-scope`, `replication`, `usage-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0330_b4c581cdbf`
- Source ID: `tidb-docs-8.1:tidb-external-ts.md#read-historical-data-using-the-tidb-external-ts-variable`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1c9fc21bb64afc7d9e49a69dccf6644b01ff5f8e601c886914f5dd304903da5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-external-ts#read-historical-data-using-the-tidb-external-ts-variable
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-external-ts.md

## Retrieval Guidance

- Use When: Use this when you need official guidance on reading historical data at a specified timestamp by using `tidb_external_ts` and `tidb_enable_external_ts_read`, including session or global behavior and read-only effects.
- Retrieval Keywords: tidb_external_ts, tidb_enable_external_ts_read, historical read, read historical data, external ts read, read-only mode, ERROR 1836 (HY000): Running in read-only mode, @@tidb_current_ts, SET GLOBAL tidb_external_ts, SET tidb_enable_external_ts_read=ON, TiCDC, downstream TiDB, session scope, global scope
- Follow-up Guidance: The example shows `START TRANSACTION; SET GLOBAL tidb_external_ts=@@tidb_current_ts; COMMIT;` followed by `SET tidb_enable_external_ts_read=ON;` and a `SELECT * FROM t;` that returns only rows before the specified timestamp.
- Classification Note: This is classified as configuration because the content explains the system variables `tidb_external_ts` and `tidb_enable_external_ts_read`, their scope, and their effect on query behavior.

## Official Source Content

# Read Historical Data Using the `tidb_external_ts` Variable

To support reading the historical data, TiDB v6.4.0 introduces a system variable [`tidb_external_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_external_ts-new-in-v640). This document describes how to read historical data through this system variable, including detailed usage examples.
## Scenarios

Read historical data from a specified point in time is very useful for data replication tools such as TiCDC. After the data replication tool completes the data replication before a certain point in time, you can set the `tidb_external_ts` system variable of the downstream TiDB to read the data before that point in time. This prevents the data inconsistency caused by data replication.
## Feature description

The system variable [`tidb_external_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_external_ts-new-in-v640) specifies the timestamp of the historical data to be read when `tidb_enable_external_ts_read` is enabled.

The system variable [`tidb_enable_external_ts_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_external_ts_read-new-in-v640) controls whether to read historical data in the current session or globally. The default value is `OFF`, which means the feature of reading historical data is disabled, and the `tidb_external_ts` value is ignored. When `tidb_enable_external_ts_read` is set to `ON` globally, all queries read historical data before the time specified by `tidb_external_ts`. If `tidb_enable_external_ts_read` is set to `ON` only for a certain session, only queries in that session read historical data.

When the `tidb_enable_external_ts_read` is enabled, TiDB becomes read-only. All write queries will fail with an error like `ERROR 1836 (HY000): Running in read-only mode`.
## Usage examples

This section describes how to use the `tidb_external_ts` variable to read historical data with examples.

1. Create a table and insert some rows into the table:

    ```sql
    CREATE TABLE t (c INT);
    ```

    ```
    Query OK, 0 rows affected (0.01 sec)
    ```

    ```sql
    INSERT INTO t VALUES (1), (2), (3);
    ```

    ```
    Query OK, 3 rows affected (0.00 sec)
    ```

2. View the data in the table:

    ```sql
    SELECT * FROM t;
    ```

    ```
    +------+
    | c    |
    +------+
    |    1 |
    |    2 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

3. Set `tidb_external_ts` to `@@tidb_current_ts`:

    ```sql
    START TRANSACTION;
    SET GLOBAL tidb_external_ts=@@tidb_current_ts;
    COMMIT;
    ```

4. Insert a new row and confirm that it is inserted:

    ```sql
    INSERT INTO t VALUES (4);
    ```

    ```
    Query OK, 1 row affected (0.001 sec)
    ```

    ```sql
    SELECT * FROM t;
    ```

    ```
    +------+
    | id   |
    +------+
    |    1 |
    |    2 |
    |    3 |
    |    4 |
    +------+
    4 rows in set (0.00 sec)
    ```

5. Set `tidb_enable_external_ts_read` to `ON` and then view data in the table:

    ```sql
    SET tidb_enable_external_ts_read=ON;
    SELECT * FROM t;
    ```

    ```
    +------+
    | c    |
    +------+
    |    1 |
    |    2 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

    Because `tidb_external_ts` is set to the timestamp before the new row is inserted, the newly inserted row is not returned after the `tidb_enable_external_ts_read` is enabled.
