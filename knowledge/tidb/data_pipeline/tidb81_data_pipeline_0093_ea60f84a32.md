# Optional dbt seed loading and verification in TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-dbt.md`
- Source Title: `Integrate TiDB Cloud with dbt`
- Source Heading Path: `Integrate TiDB Cloud with dbt > Step 4: (optional) Load CSV files`
- Source Line Ranges: `142-222`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`
- Topic Tags: `dbt`, `seed`, `csv`, `table-creation`, `data-loading`, `verification`, `sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0093_ea60f84a32`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-dbt.md#step-4-optional-load-csv-files`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `22a6a963d798e9221b8a4932f1e486b0b218cde562d878221d326ac337ff5c11`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-dbt#step-4-optional-load-csv-files
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-dbt.md

## Retrieval Guidance

- Use When: Use this chunk when loading CSV seed files into TiDB Cloud with dbt seed and checking the resulting analytics database and raw tables with SQL.
- Retrieval Keywords: dbt seed, analytics.raw_customers, analytics.raw_orders, analytics.raw_payments, SHOW DATABASES;, USE ANALYTICS;, SHOW TABLES;, SELECT * FROM raw_customers LIMIT 10;, Load CSV files, seed file analytics.raw_customers, seed file analytics.raw_orders, seed file analytics.raw_payments
- Follow-up Guidance: The chunk notes that this step is optional and can be skipped if the data for processing is already in the target database.
- Classification Note: This is classified as data_pipeline because the content covers loading CSV seed data into TiDB Cloud as tables and verifying the loaded database objects and sample rows.

## Official Source Content

## Step 4: (optional) Load CSV files

> **Note:**
>
> This step is optional. If the data for processing is already in the target database, you can skip this step.

Now that you have successfully created and configured the project, it’s time to load the CSV data and materialize the CSV as a table in the target database.

1. Load the CSV data and materialize the CSV as a table in the target database.

    ```shell
    dbt seed
    ```

    The following is an example output:

    ```shell
    Running with dbt=1.0.1
    Partial parse save file not found. Starting full parse.
    Found 5 models, 20 tests, 0 snapshots, 0 analyses, 172 macros, 0 operations, 3 seed files, 0 sources, 0 exposures, 0 metrics

    Concurrency: 1 threads (target='dev')

    1 of 3 START seed file analytics.raw_customers.................................. [RUN]
    1 of 3 OK loaded seed file analytics.raw_customers.............................. [INSERT 100 in 0.19s]
    2 of 3 START seed file analytics.raw_orders..................................... [RUN]
    2 of 3 OK loaded seed file analytics.raw_orders................................. [INSERT 99 in 0.14s]
    3 of 3 START seed file analytics.raw_payments................................... [RUN]
    3 of 3 OK loaded seed file analytics.raw_payments............................... [INSERT 113 in 0.24s]
    ```

    As you can see in the results, the seed file was started and loaded into three tables: `analytics.raw_customers`, `analytics.raw_orders`, and `analytics.raw_payments`.

2. Verify the results in TiDB Cloud.

    The `show databases` command lists the new `analytics` database that dbt has created. The `show tables` command indicates that there are three tables in the `analytics` database, corresponding to the ones you have created.

    ```sql
    mysql> SHOW DATABASES;
    +--------------------+
    | Database           |
    +--------------------+
    | INFORMATION_SCHEMA |
    | METRICS_SCHEMA     |
    | PERFORMANCE_SCHEMA |
    | analytics          |
    | io_replicate       |
    | mysql              |
    | test               |
    +--------------------+
    7 rows in set (0.00 sec)

    mysql> USE ANALYTICS;
    mysql> SHOW TABLES;
    +---------------------+
    | Tables_in_analytics |
    +---------------------+
    | raw_customers       |
    | raw_orders          |
    | raw_payments        |
    +---------------------+
    3 rows in set (0.00 sec)

    mysql> SELECT * FROM raw_customers LIMIT 10;
    +------+------------+-----------+
    | id   | first_name | last_name |
    +------+------------+-----------+
    |    1 | Michael    | P.        |
    |    2 | Shawn      | M.        |
    |    3 | Kathleen   | P.        |
    |    4 | Jimmy      | C.        |
    |    5 | Katherine  | R.        |
    |    6 | Sarah      | R.        |
    |    7 | Martin     | M.        |
    |    8 | Frank      | R.        |
    |    9 | Jennifer   | F.        |
    |   10 | Henry      | W.        |
    +------+------------+-----------+
    10 rows in set (0.10 sec)
    ```
