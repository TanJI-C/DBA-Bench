# tidb_read_staleness overview and usage examples

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-read-staleness.md`
- Source Title: `Read Historical Data Using the `tidb_read_staleness` System Variable`
- Source Heading Path: `Read Historical Data Using the `tidb_read_staleness` System Variable | Read Historical Data Using the `tidb_read_staleness` System Variable > Feature description | Read Historical Data Using the `tidb_read_staleness` System Variable > Usage examples`
- Source Line Ranges: `5-171`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `stale-read`, `historical-data`, `session-variable`, `read-consistency`, `sql-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0347_7fe8399eba`
- Source ID: `tidb-docs-8.1:tidb-read-staleness.md#read-historical-data-using-the-tidb-read-staleness-system-variable`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `58c18e1c1b67b8b149bc6b5abe65def05aae4c9bb91d9062a8a97a44808b5527`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-read-staleness#read-historical-data-using-the-tidb-read-staleness-system-variable
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-read-staleness.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to read historical data in a TiDB session with the `tidb_read_staleness` system variable and how to switch back to latest reads.
- Retrieval Keywords: tidb_read_staleness, Read Historical Data Using the `tidb_read_staleness` System Variable, SESSION scope, historical data, stale read, set @@tidb_read_staleness="-5", set @@tidb_read_staleness="", latest version data before the time set by the value, Use @@ instead of @, interactive transaction still read the latest data, DML operations are not affected by `tidb_read_staleness`, advance-ts-interval, select * from t, update t set c=22 where c=2
- Follow-up Guidance: The content notes that after reading historical data, you can read the latest data by starting a new session or by setting `tidb_read_staleness` to `""`, and it also references the TiKV `advance-ts-interval` configuration item for reducing Stale Read latency.
- Classification Note: This is classified as configuration content because it defines the `tidb_read_staleness` SESSION system variable, its effect on read timestamps, and the exact SQL syntax used to enable and unset it.

## Official Source Content

# Read Historical Data Using the `tidb_read_staleness` System Variable

To support reading the historical data, in v5.4, TiDB introduces a new system variable `tidb_read_staleness`. This document describes how to read historical data through this system variable, including detailed operating procedures.
## Feature description

The `tidb_read_staleness` system variable is used to set the time range of historical data that TiDB can read in the current session. The data type of this variable is int type, and the scope of it is `SESSION`. After setting the value, TiDB selects a timestamp as new as possible from the range allowed by this variable, and all subsequent read operations are performed against this timestamp. For example, if the value of this variable is set to `-5`, on the condition that TiKV has the corresponding historical version's data, TiDB selects a timestamp as new as possible within a 5-second time range.

After enabling `tidb_read_staleness`, you still can perform the following operations:

- Insert, modify, delete data or perform DML operations in the current session. These statements are not affected by `tidb_read_staleness`.
- Start an interactive transaction in the current session. Queries within this transaction still read the latest data.

After reading the historical data, you can read the latest data in the following two ways:

- Start a new session.
- Set the value of the `tidb_read_staleness` variable to `""` using the `SET` statement.

> **Note:**
>
> To reduce the latency and improve the timeliness of the Stale Read data, you can modify the TiKV `advance-ts-interval` configuration item. See [Reduce Stale Read latency](https://docs.pingcap.com/tidb/stable/stale-read#reduce-stale-read-latency) for details.
## Usage examples

This section describes how to use `tidb_read_staleness` with examples.

1. Create a table, and insert a few rows of data into the table:

    ```sql
    create table t (c int);
    ```

    ```
    Query OK, 0 rows affected (0.01 sec)
    ```

    ```sql
    insert into t values (1), (2), (3);
    ```

    ```
    Query OK, 3 rows affected (0.00 sec)
    ```

2. Check out the data in the table:

    ```sql
    select * from t;
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

3. Update the data in a row:

    ```sql
    update t set c=22 where c=2;
    ```

    ```
    Query OK, 1 row affected (0.00 sec)
    ```

4. Confirm that the data has been updated:

    ```sql
    select * from t;
    ```

    ```
    +------+
    | c    |
    +------+
    |    1 |
    |   22 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```

5. Set the `tidb_read_staleness` system variable.

    The scope of this variable is `SESSION`. After setting its value, TiDB reads the latest version data before the time set by the value.

    The following setting indicates that TiDB selects a timestamp as new as possible within the time range from 5 seconds ago to now and uses it as the timestamp for reading historical data:

    ```sql
    set @@tidb_read_staleness="-5";
    ```

    ```
    Query OK, 0 rows affected (0.00 sec)
    ```

    > **Note:**
    >
    >  - Use `@@` instead of `@` before `tidb_read_staleness`. `@@` means system variables, and `@` means user variables.
    >  - You need to set the historical time range (the value of `tidb_read_staleness`) according to the total time that you spent in step 3 and step 4. Otherwise, the latest data will be displayed in the query results, not the historical data. Therefore, you need to adjust this time range according to the time you spent on operations. For example, in this example, since the set time range is 5 seconds, you need to complete step 3 and step 4 within 5 seconds.

    The data read here is the data before the update, that is, the historical data:

    ```sql
    select * from t;
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

6. After un-setting this variable as follows, TiDB can read the latest data:

    ```sql
    set @@tidb_read_staleness="";
    ```

    ```
    Query OK, 0 rows affected (0.00 sec)
    ```

    ```sql
    select * from t;
    ```

    ```
    +------+
    | c    |
    +------+
    |    1 |
    |   22 |
    |    3 |
    +------+
    3 rows in set (0.00 sec)
    ```
