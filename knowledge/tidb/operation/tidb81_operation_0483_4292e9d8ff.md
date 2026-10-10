# TTL overview and table syntax

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/time-to-live.md`
- Source Title: `Periodically Delete Data Using TTL (Time to Live)`
- Source Heading Path: `Periodically Delete Expired Data Using TTL (Time to Live) | Periodically Delete Expired Data Using TTL (Time to Live) > Syntax | Periodically Delete Expired Data Using TTL (Time to Live) > Syntax > Create a table with a TTL attribute | Periodically Delete Expired Data Using TTL (Time to Live) > Syntax > Modify the TTL attribute of a table | Periodically Delete Expired Data Using TTL (Time to Live) > Syntax > TTL and the default values of data types | Periodically Delete Expired Data Using TTL (Time to Live) > Syntax > TTL and generated columns`
- Source Line Ranges: `5-128`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `ttl`, `table-attributes`, `create-table`, `alter-table`, `ttl-enable`, `default-values`, `generated-columns`, `json`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0483_4292e9d8ff`
- Source ID: `tidb-docs-8.1:time-to-live.md#periodically-delete-expired-data-using-ttl-time-to-live`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6f96ef921840c792f51227c1b21865367af3355cc692e64b5c4ff5619415eaa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/time-to-live#periodically-delete-expired-data-using-ttl-time-to-live
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/time-to-live.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL syntax and behavior for configuring table TTL attributes, enabling or disabling TTL cleanup, removing TTL, or combining TTL with default values, generated columns, or JSON-based generated columns.
- Retrieval Keywords: Time to live (TTL), CREATE TABLE ... TTL = `created_at` + INTERVAL 3 MONTH, ALTER TABLE t1 TTL = `created_at` + INTERVAL 1 MONTH, ALTER TABLE t1 TTL_ENABLE = 'OFF', ALTER TABLE t1 REMOVE TTL, TTL_ENABLE, DEFAULT CURRENT_TIMESTAMP, ON UPDATE CURRENT_TIMESTAMP, generated columns, JSON_EXTRACT(order_info, '$.created_at'), /*T![ttl] TTL = `created_at` + INTERVAL 3 MONTH TTL_ENABLE = 'OFF'*/
- Follow-up Guidance: The content also states that TTL cleanup runs in background jobs across TiDB nodes and expired rows might still be readable for some time until deletion occurs.
- Classification Note: This is classified as an operation chunk because the official content focuses on SQL statements and table attributes used to create, modify, enable, disable, and remove TTL behavior.

## Official Source Content

# Periodically Delete Expired Data Using TTL (Time to Live)

Time to live (TTL) is a feature that allows you to manage TiDB data lifetime at the row level. For a table with the TTL attribute, TiDB automatically checks data lifetime and deletes expired data at the row level. This feature can effectively save storage space and enhance performance in some scenarios.

The following are some common scenarios for TTL:

* Regularly delete verification codes and short URLs.
* Regularly delete unnecessary historical orders.
* Automatically delete intermediate results of calculations.

TTL is designed to help users clean up unnecessary data periodically and in a timely manner without affecting the online read and write workloads. TTL concurrently dispatches different jobs to different TiDB nodes to delete data in parallel in the unit of table. TTL does not guarantee that all expired data is deleted immediately, which means that even if some data is expired, the client might still read that data some time after the expiration time until that data is deleted by the background TTL job.
## Syntax

You can configure the TTL attribute of a table using the [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) or [`ALTER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table) statement.
### Create a table with a TTL attribute

- Create a table with a TTL attribute:

    ```sql
    CREATE TABLE t1 (
        id int PRIMARY KEY,
        created_at TIMESTAMP
    ) TTL = `created_at` + INTERVAL 3 MONTH;
    ```

    The preceding example creates a table `t1` and specifies `created_at` as the TTL timestamp column, which indicates the creation time of the data. The example also sets the longest time that a row is allowed to live in the table to 3 months through `INTERVAL 3 MONTH`. Data that lives longer than this value will be deleted later.

- Set the `TTL_ENABLE` attribute to enable or disable the feature of cleaning up expired data:

    ```sql
    CREATE TABLE t1 (
        id int PRIMARY KEY,
        created_at TIMESTAMP
    ) TTL = `created_at` + INTERVAL 3 MONTH TTL_ENABLE = 'OFF';
    ```

    If `TTL_ENABLE` is set to `OFF`, even if other TTL options are set, TiDB does not automatically clean up expired data in this table. For a table with the TTL attribute, `TTL_ENABLE` is `ON` by default.

- To be compatible with MySQL, you can set a TTL attribute using a comment:

    ```sql
    CREATE TABLE t1 (
        id int PRIMARY KEY,
        created_at TIMESTAMP
    ) /*T![ttl] TTL = `created_at` + INTERVAL 3 MONTH TTL_ENABLE = 'OFF'*/;
    ```

    In TiDB, using the table TTL attribute or using comments to configure TTL is equivalent. In MySQL, the comment is ignored and an ordinary table is created.
### Modify the TTL attribute of a table

- Modify the TTL attribute of a table:

    ```sql
    ALTER TABLE t1 TTL = `created_at` + INTERVAL 1 MONTH;
    ```

    You can use the preceding statement to modify a table with an existing TTL attribute or to add a TTL attribute to a table without a TTL attribute.

- Modify the value of `TTL_ENABLE` for a table with the TTL attribute:

    ```sql
    ALTER TABLE t1 TTL_ENABLE = 'OFF';
    ```

- To remove all TTL attributes of a table:

    ```sql
    ALTER TABLE t1 REMOVE TTL;
    ```
### TTL and the default values of data types

You can use TTL together with [default values of the data types](https://docs.pingcap.com/tidb/stable/data-type-default-values). The following are two common usage examples:

* Use `DEFAULT CURRENT_TIMESTAMP` to specify the default value of a column as the current creation time and use this column as the TTL timestamp column. Records that were created 3 months ago are expired:

    ```sql
    CREATE TABLE t1 (
        id int PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) TTL = `created_at` + INTERVAL 3 MONTH;
    ```

* Specify the default value of a column as the creation time or the latest update time and use this column as the TTL timestamp column. Records that have not been updated for 3 months are expired:

    ```sql
    CREATE TABLE t1 (
        id int PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) TTL = `created_at` + INTERVAL 3 MONTH;
    ```
### TTL and generated columns

You can use TTL together with [generated columns](https://docs.pingcap.com/tidb/stable/generated-columns) to configure complex expiration rules. For example:

```sql
CREATE TABLE message (
    id int PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    image bool,
    expire_at TIMESTAMP AS (IF(image,
            created_at + INTERVAL 5 DAY,
            created_at + INTERVAL 30 DAY
    ))
) TTL = `expire_at` + INTERVAL 0 DAY;
```

The preceding statement uses the `expire_at` column as the TTL timestamp column and sets the expiration time according to the message type. If the message is an image, it expires in 5 days. Otherwise, it expires in 30 days.

You can use TTL together with the [JSON type](https://docs.pingcap.com/tidb/stable/data-type-json). For example:

```sql
CREATE TABLE orders (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_info JSON,
    created_at DATE AS (JSON_EXTRACT(order_info, '$.created_at')) VIRTUAL
) TTL = `created_at` + INTERVAL 3 month;
```
