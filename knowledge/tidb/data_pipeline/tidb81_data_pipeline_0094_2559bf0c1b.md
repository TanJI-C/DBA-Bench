# Run dbt transformations, verify results, and generate docs

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-dbt.md`
- Source Title: `Integrate TiDB Cloud with dbt`
- Source Heading Path: `Integrate TiDB Cloud with dbt > Step 5: Transform data | Integrate TiDB Cloud with dbt > Step 6: Generate the document`
- Source Line Ranges: `223-319`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`
- Topic Tags: `dbt`, `transformation`, `verification`, `tables`, `views`, `documentation`, `local-server`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0094_2559bf0c1b`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-dbt.md#step-5-transform-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dbf3d156ab0a8922aa6090505612d40efd8e16e80e9e3e02b968f6da84d22545`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-dbt#step-5-transform-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-dbt.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to run dbt transformations against TiDB Cloud, verify the created tables and views with SQL, or generate and serve dbt project documentation locally.
- Retrieval Keywords: dbt run, dbt docs generate, dbt docs serve, USE ANALYTICS, SHOW TABLES, SELECT * FROM customers LIMIT 10, analytics.customers, analytics.orders, analytics.stg_customers, analytics.stg_orders, analytics.stg_payments, http://localhost:8080, Completed successfully, PASS=5 WARN=0 ERROR=0 SKIP=0 TOTAL=5
- Follow-up Guidance: The chunk also shows example verification output in TiDB Cloud and the local URL for viewing generated dbt docs at http://localhost:8080.
- Classification Note: This is classified as data_pipeline because the content covers running dbt transformations, checking transformed tables and views, and generating project documentation.

## Official Source Content

## Step 5: Transform data

Now you are ready to run the configured project and finish the data transformation.

1. Run the dbt project to finish the data transformation:

    ```shell
    dbt run
    ```

    The following is an example output:

    ```shell
    Running with dbt=1.0.1
    Found 5 models, 20 tests, 0 snapshots, 0 analyses, 170 macros, 0 operations, 3 seed files, 0 sources, 0 exposures, 0 metrics

    Concurrency: 1 threads (target='dev')

    1 of 5 START view model analytics.stg_customers................................. [RUN]
    1 of 5 OK created view model analytics.stg_customers............................ [SUCCESS 0 in 0.31s]
    2 of 5 START view model analytics.stg_orders.................................... [RUN]
    2 of 5 OK created view model analytics.stg_orders............................... [SUCCESS 0 in 0.23s]
    3 of 5 START view model analytics.stg_payments.................................. [RUN]
    3 of 5 OK created view model analytics.stg_payments............................. [SUCCESS 0 in 0.29s]
    4 of 5 START table model analytics.customers.................................... [RUN]
    4 of 5 OK created table model analytics.customers............................... [SUCCESS 0 in 0.76s]
    5 of 5 START table model analytics.orders....................................... [RUN]
    5 of 5 OK created table model analytics.orders.................................. [SUCCESS 0 in 0.63s]

    Finished running 3 view models, 2 table models in 2.27s.

    Completed successfully

    Done. PASS=5 WARN=0 ERROR=0 SKIP=0 TOTAL=5
    ```

    The result shows that two tables (`analytics.customers` and `analytics.orders`), and three views (`analytics.stg_customers`, `analytics.stg_orders`, and `analytics.stg_payments`) are created successfully.

2. Go to TiDB Cloud to verify that the transformation is successful.

    ```sql
    mysql> USE ANALYTICS;
    mysql> SHOW TABLES;
    +---------------------+
    | Tables_in_analytics |
    +---------------------+
    | customers           |
    | orders              |
    | raw_customers       |
    | raw_orders          |
    | raw_payments        |
    | stg_customers       |
    | stg_orders          |
    | stg_payments        |
    +---------------------+
    8 rows in set (0.00 sec)

    mysql> SELECT * FROM customers LIMIT 10;
    +-------------+------------+-----------+-------------+-------------------+------------------+-------------------------+
    | customer_id | first_name | last_name | first_order | most_recent_order | number_of_orders | customer_lifetime_value |
    +-------------+------------+-----------+-------------+-------------------+------------------+-------------------------+
    |           1 | Michael    | P.        | 2018-01-01  | 2018-02-10        |                2 |                 33.0000 |
    |           2 | Shawn      | M.        | 2018-01-11  | 2018-01-11        |                1 |                 23.0000 |
    |           3 | Kathleen   | P.        | 2018-01-02  | 2018-03-11        |                3 |                 65.0000 |
    |           4 | Jimmy      | C.        | NULL        | NULL              |             NULL |                    NULL |
    |           5 | Katherine  | R.        | NULL        | NULL              |             NULL |                    NULL |
    |           6 | Sarah      | R.        | 2018-02-19  | 2018-02-19        |                1 |                  8.0000 |
    |           7 | Martin     | M.        | 2018-01-14  | 2018-01-14        |                1 |                 26.0000 |
    |           8 | Frank      | R.        | 2018-01-29  | 2018-03-12        |                2 |                 45.0000 |
    |           9 | Jennifer   | F.        | 2018-03-17  | 2018-03-17        |                1 |                 30.0000 |
    |          10 | Henry      | W.        | NULL        | NULL              |             NULL |                    NULL |
    +-------------+------------+-----------+-------------+-------------------+------------------+-------------------------+
    10 rows in set (0.00 sec)
    ```

    The output shows that five more tables or views have been added, and the data in the tables or views has been transformed. Only part of the data from the customer table is shown in this example.
## Step 6: Generate the document

dbt lets you generate visual documents that display the overall structure of the project and describe all the tables and views.

To generate visual documents, take the following steps:

1. Generate the document:

    ```shell
    dbt docs generate
    ```

2. Start the server:

    ```shell
    dbt docs serve
    ```

3. To access the document from your browser, go to [http://localhost:8080](http://localhost:8080).
