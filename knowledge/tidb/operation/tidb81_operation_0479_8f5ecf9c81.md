# TiFlash query result materialization overview, restrictions, and example

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-results-materialization.md`
- Source Title: `TiFlash Query Result Materialization`
- Source Heading Path: `TiFlash Query Result Materialization | TiFlash Query Result Materialization > Typical and recommended usage scenarios | TiFlash Query Result Materialization > Execution process | TiFlash Query Result Materialization > Restrictions | TiFlash Query Result Materialization > Example`
- Source Line Ranges: `5-129`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `insert-into-select`, `materialization`, `mpp`, `sql-mode`, `transactions`, `acid`, `memory-quota`, `concurrency`, `bi`, `reporting`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0479_8f5ecf9c81`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-results-materialization.md#tiflash-query-result-materialization`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea5fa236e3b14de04a7b17405c678e3adbe981379eb233e77efc93164b507de5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-results-materialization#tiflash-query-result-materialization
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-results-materialization.md

## Retrieval Guidance

- Use When: Use this chunk when you need information about TiFlash query result materialization with `INSERT INTO SELECT`, including pushdown conditions, restrictions, concurrency guidance, and the daily-to-monthly analysis example.
- Retrieval Keywords: TiFlash Query Result Materialization, INSERT INTO SELECT, TiFlash query result materialization, tidb_allow_mpp, tidb_enforce_mpp, sql_mode, STRICT_TRANS_TABLES, STRICT_ALL_TABLES, ACID properties, tidb_mem_quota_query, txn-total-size-limit, TiDB memory control, TiFlash concurrency limit, 100 QPS, write transaction close to 1 GiB, write transaction less than 100 MiB, ALTER TABLE SET TIFLASH REPLICA, daily_data, detail_data, SELECT DATE(ts), customer_id, sum(detail_fee)
- Follow-up Guidance: The source includes an example that creates `detail_data` and `daily_data`, sets `TIFLASH REPLICA 2`, materializes daily results with `INSERT INTO daily_data ... SELECT ... GROUP BY`, and then queries monthly aggregates from `daily_data`.
- Classification Note: This is classified as an operation topic because the content explains how `INSERT INTO SELECT` executes with TiFlash, its restrictions and concurrency considerations, and shows a concrete SQL workflow for saving query results into a TiDB table.

## Official Source Content

# TiFlash Query Result Materialization

This document introduces how to save the TiFlash query result to a specified TiDB table in an `INSERT INTO SELECT` transaction.

Starting from v6.5.0, TiDB supports saving TiFlash query results in a table, that is, TiFlash query result materialization. During the execution of the `INSERT INTO SELECT` statement, if TiDB pushes down the `SELECT` subquery to TiFlash, the TiFlash query result can be saved to a TiDB table specified in the `INSERT INTO` clause. For TiDB versions earlier than v6.5.0, the TiFlash query results are read-only, so if you want to save TiFlash query results, you have to obtain them from the application level, and then save them in a separate transaction or process.

> **Note:**
>
> By default ([`tidb_allow_mpp = ON`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50)), the optimizer intelligently decides whether to push a query down to TiFlash based on the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) and the cost estimates of the TiFlash replica. 
>
> - If the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) of the current session is not strict (which means the `sql_mode` value does not contain `STRICT_TRANS_TABLES`' and `STRICT_ALL_TABLES`), the optimizer intelligently decides whether to push the `SELECT` subquery in `INSERT INTO SELECT` down to TiFlash based on the cost estimates of the TiFlash replica. In this mode, if you want to ignore the cost estimates of the optimizer and enforce that the queries are pushed down to TiFlash, you can set the [`tidb_enforce_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enforce_mpp-new-in-v51) system variable to `ON`. 
> - If the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) of the current session is strict (which means the `sql_mode` value contains either `STRICT_TRANS_TABLES` or `STRICT_ALL_TABLES`), the `SELECT` subquery in `INSERT INTO SELECT` cannot be pushed down to TiFlash.

The syntax of `INSERT INTO SELECT` is as follows.

```sql
INSERT [LOW_PRIORITY | HIGH_PRIORITY] [IGNORE]
    [INTO] tbl_name
    [PARTITION (partition_name [, partition_name] ...)]
    [(col_name [, col_name] ...)]
    SELECT ...
    [ON DUPLICATE KEY UPDATE assignment_list]value:
    {expr | DEFAULT}

assignment:
    col_name = valueassignment_list:
    assignment [, assignment] ...
```

For example, you can save the query result from table `t1` in the `SELECT` clause to table `t2` using the following `INSERT INTO SELECT` statement:

```sql
INSERT INTO t2 (name, country)
SELECT app_name, country FROM t1;
```
## Typical and recommended usage scenarios

- Efficient BI solutions

    For many BI applications, the analysis query requests are very heavy. For example, when a lot of users access and refresh a report at the same time, a BI application needs to handle a lot of concurrent query requests. To deal with this situation effectively, you can use `INSERT INTO SELECT` to save the query results of the report in a TiDB table. Then, the end users can query data directly from the result table when the report is refreshed, which avoids multiple repeated computations and analyses. Similarly, by saving historical analysis results, you can further reduce the computation volume for long-time historical data analysis. For example, if you have a report `A` that is used to analyze daily sales profit, you can save the results of report `A` to a result table `T` using `INSERT INTO SELECT`. Then, when you need to generate a report `B` to analyze the sales profit of the past month, you can directly use the daily analysis results in table `T`. This way not only greatly reduces the computation volume but also improves the query response speed and reduces the system load.

- Serving online applications with TiFlash

    The number of concurrent requests supported by TiFlash depends on the volume of data and complexity of the queries, but it typically does not exceed 100 QPS. You can use `INSERT INTO SELECT` to save TiFlash query results, and then use the query result table to support highly concurrent online requests. The data in the result table can be updated in the background at a low frequency (for example, at an interval of 0.5 second), which is well below the TiFlash concurrency limit, while still maintaining a high level of data freshness.
## Execution process

* During the execution of the `INSERT INTO SELECT` statement, TiFlash first returns the query results of the `SELECT` clause to a TiDB server in the cluster, and then writes the results to the target table, which can have a TiFlash replica.
* The execution of the `INSERT INTO SELECT` statement guarantees ACID properties.
## Restrictions

* The TiDB memory limit on the `INSERT INTO SELECT` statement can be adjusted using the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query). Starting from v6.5.0, it is not recommended to use [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit) to control transaction memory size.

    For more information, see [TiDB memory control](https://docs.pingcap.com/tidb/stable/configure-memory-usage).

* The TiDB memory limit on the `INSERT INTO SELECT` statement can be adjusted using the system variable [`tidb_mem_quota_query`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_query). Starting from v6.5.0, it is not recommended to use [`txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit) to control transaction memory size.

    For more information, see [TiDB memory control](https://docs.pingcap.com/tidb/stable/configure-memory-usage).

* TiDB has no hard limit on the concurrency of the `INSERT INTO SELECT` statement, but it is recommended to consider the following practices:

    * When a "write transaction" is large, such as close to 1 GiB, it is recommended to control concurrency to no more than 10.
    * When a "write transaction" is small, such as less than 100 MiB, it is recommended to control concurrency to no more than 30.
    * Determine the concurrency based on testing results and specific circumstances.
## Example

Data definition:

```sql
CREATE TABLE detail_data (
    ts DATETIME,                -- Fee generation time
    customer_id VARCHAR(20),    -- Customer ID
    detail_fee DECIMAL(20,2));  -- Amount of fee

CREATE TABLE daily_data (
    rec_date DATE,              -- Date when data is collected
    customer_id VARCHAR(20),    -- Customer ID
    daily_fee DECIMAL(20,2));   -- Amount of fee for per day

ALTER TABLE detail_data SET TIFLASH REPLICA 2;
ALTER TABLE daily_data SET TIFLASH REPLICA 2;

-- ... (detail_data table continues updating)
INSERT INTO detail_data(ts,customer_id,detail_fee) VALUES
('2023-1-1 12:2:3', 'cus001', 200.86),
('2023-1-2 12:2:3', 'cus002', 100.86),
('2023-1-3 12:2:3', 'cus002', 2200.86),
('2023-1-4 12:2:3', 'cus003', 2020.86),
('2023-1-5 12:2:3', 'cus003', 1200.86),
('2023-1-6 12:2:3', 'cus002', 20.86),
('2023-1-7 12:2:3', 'cus004', 120.56),
('2023-1-8 12:2:3', 'cus005', 320.16);

-- Execute the following SQL statement 13 times to insert a cumulative total of 65,536 rows into the table.
INSERT INTO detail_data SELECT * FROM detail_data;
```

Save daily analysis results:

```sql
SET @@sql_mode='NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO';

INSERT INTO daily_data (rec_date, customer_id, daily_fee)
SELECT DATE(ts), customer_id, sum(detail_fee) FROM detail_data WHERE DATE(ts) > DATE('2023-1-1 12:2:3') GROUP BY DATE(ts), customer_id;
```

Analyze monthly data based on daily analysis data:

```sql
SELECT MONTH(rec_date), customer_id, sum(daily_fee) FROM daily_data GROUP BY MONTH(rec_date), customer_id;
```

The preceding example materializes the daily analysis results and saves them to the daily result table, based on which the monthly data analysis is accelerated, thus improving data analysis efficiency.
