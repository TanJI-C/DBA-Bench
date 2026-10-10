# tidb_snapshot historical reads and example usage

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/read-historical-data.md`
- Source Title: `Read Historical Data Using the System Variable `tidb_snapshot``
- Source Heading Path: `Read Historical Data Using the System Variable `tidb_snapshot` | Read Historical Data Using the System Variable `tidb_snapshot` > Feature description | Read Historical Data Using the System Variable `tidb_snapshot` > How TiDB reads data from history versions | Read Historical Data Using the System Variable `tidb_snapshot` > How TiDB manages the data versions | Read Historical Data Using the System Variable `tidb_snapshot` > Example`
- Source Line Ranges: `5-160`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`
- Topic Tags: `historical-read`, `snapshot`, `session-variable`, `mvcc`, `gc`, `safe-point`, `sql-example`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0203_b4177f4cc2`
- Source ID: `tidb-docs-8.1:read-historical-data.md#read-historical-data-using-the-system-variable-tidb-snapshot`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bea916c15044b25d1f419c6c535019667138cdf71b3f1ff8c84db9632e715214`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/read-historical-data#read-historical-data-using-the-system-variable-tidb-snapshot
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/read-historical-data.md

## Retrieval Guidance

- Use When: Use this chunk when you need to read historical data in TiDB with the session system variable `tidb_snapshot`, understand its timestamp formats and scope, or check how GC safe points affect snapshot reads.
- Retrieval Keywords: tidb_snapshot, Read Historical Data Using the System Variable tidb_snapshot, historical read, history versions, snapshot read, SESSION scope, SET @@tidb_snapshot, TSO, Timestamp Oracle, PD, datetime format 2016-10-08 16:45:26.999, MVCC, Garbage Collection GC, tidb_gc_life_time, mysql.tidb, tikv_gc_safe_point, safePoint, set @@tidb_snapshot="", old table structure, SELECT from Snapshot
- Follow-up Guidance: After reading historical data, you can return to the latest version by ending the current Session or setting `tidb_snapshot` to an empty string, and you can check `SELECT * FROM mysql.tidb WHERE variable_name = 'tikv_gc_safe_point'` for the current readable historical boundary.
- Classification Note: The official content is classified as an operation topic because it explains how to use the session variable `tidb_snapshot` to perform historical reads, including syntax, behavior, and an SQL example.

## Official Source Content

# Read Historical Data Using the System Variable `tidb_snapshot`

This document describes how to read data from the history versions using the system variable `tidb_snapshot`, including specific usage examples and strategies for saving historical data.

> **Note:**
>
> You can also use the [Stale Read](https://docs.pingcap.com/tidb/stable/stale-read) feature to read historical data, which is more recommended.
## Feature description

TiDB implements a feature to read history data using the standard SQL interface directly without special clients or drivers.

> **Note:**
>
> - Even when data is updated or removed, its history versions can be read using the SQL interface.
> - When reading historical data, TiDB returns the data with the old table structure even if the current table structure is different.
## How TiDB reads data from history versions

The [`tidb_snapshot`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_snapshot) system variable is introduced to support reading history data. About the `tidb_snapshot` variable:

- The variable is valid in the `SESSION` scope.
- Its value can be modified using the `SET` statement.
- The data type for the variable is text.
- The variable accepts TSO (Timestamp Oracle) and datetime. TSO is a globally unique time service, which is obtained from PD. The acceptable datetime format is "2016-10-08 16:45:26.999". Generally, the datetime can be set using second precision, for example "2016-10-08 16:45:26".
- When the variable is set, TiDB creates a Snapshot using its value as the timestamp, just for the data structure and there is no any overhead. After that, all the `SELECT` operations will read data from this Snapshot.

> **Note:**
>
> Because the timestamp in TiDB transactions is allocated by Placement Driver (PD), the version of the stored data is also marked based on the timestamp allocated by PD. When a Snapshot is created, the version number is based on the value of the `tidb_snapshot` variable. If there is a large difference between the local time of the TiDB server and the PD server, use the time of the PD server.

After reading data from history versions, you can read data from the latest version by ending the current Session or using the `SET` statement to set the value of the `tidb_snapshot` variable to "" (empty string).
## How TiDB manages the data versions

TiDB implements Multi-Version Concurrency Control (MVCC) to manage data versions. The history versions of data are kept because each update/removal creates a new version of the data object instead of updating/removing the data object in-place. But not all the versions are kept. If the versions are older than a specific time, they will be removed completely to reduce the storage occupancy and the performance overhead caused by too many history versions.

In TiDB, Garbage Collection (GC) runs periodically to remove the obsolete data versions. For GC details, see [TiDB Garbage Collection (GC)](https://docs.pingcap.com/tidb/stable/garbage-collection-overview)

Pay special attention to the following:

- [`tidb_gc_life_time`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_life_time-new-in-v50): This system variable is used to configure the retention time of earlier modifications (default: `10m0s`).
- The output of `SELECT * FROM mysql.tidb WHERE variable_name = 'tikv_gc_safe_point'`. This is the current `safePoint` where you can read historical data up to. It is updated every time the garbage collection process is run.
## Example

1. At the initial stage, create a table and insert several rows of data:

    ```sql
    mysql> create table t (c int);
    Query OK, 0 rows affected (0.01 sec)

    mysql> insert into t values (1), (2), (3);
    Query OK, 3 rows affected (0.00 sec)
    ```

2. View the data in the table:

    ```sql
    mysql> select * from t;
    +------+
    | c    |
    +------+
    |    1 |
    |    2 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

3. View the timestamp of the table:

    ```sql
    mysql> select now();
    +---------------------+
    | now()               |
    +---------------------+
    | 2016-10-08 16:45:26 |
    +---------------------+
    1 row in set (0.00 sec)
    ```

4. Update the data in one row:

    ```sql
    mysql> update t set c=22 where c=2;
    Query OK, 1 row affected (0.00 sec)
    ```

5. Make sure the data is updated:

    ```sql
    mysql> select * from t;
    +------+
    | c    |
    +------+
    |    1 |
    |   22 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

6. Set the `tidb_snapshot` variable whose scope is Session. The variable is set so that the latest version before the value can be read.

    > **Note:**
    >
    > In this example, the value is set to be the time before the update operation.

    ```sql
    mysql> set @@tidb_snapshot="2016-10-08 16:45:26";
    Query OK, 0 rows affected (0.00 sec)
    ```

    > **Note:**
    >
    > You should use `@@` instead of `@` before `tidb_snapshot` because `@@` is used to denote the system variable while `@` is used to denote the user variable.

    **Result:** The read from the following statement is the data before the update operation, which is the history data.

    ```sql
    mysql> select * from t;
    +------+
    | c    |
    +------+
    |    1 |
    |    2 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

7. Set the `tidb_snapshot` variable to be "" (empty string) and you can read the data from the latest version:

    ```sql
    mysql> set @@tidb_snapshot="";
    Query OK, 0 rows affected (0.00 sec)
    ```

    ```sql
    mysql> select * from t;
    +------+
    | c    |
    +------+
    |    1 |
    |   22 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

    > **Note:**
    >
    > You should use `@@` instead of `@` before `tidb_snapshot` because `@@` is used to denote the system variable while `@` is used to denote the user variable.
