# Create Snowflake table replicas from TiDB change logs

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/integrate-confluent-using-ticdc.md`
- Source Title: `Integrate Data with Confluent Cloud and Snowflake`
- Source Heading Path: `Integrate Data with Confluent Cloud and Snowflake > Integrate data with Snowflake > Create data replicas of TiDB tables in Snowflake`
- Source Line Ranges: `194-316`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `ecosystem`, `sql`
- Topic Tags: `snowflake`, `replication`, `changefeed`, `etl`, `stream`, `task`, `merge`, `cdc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0063_df7687257c`
- Source ID: `tidb-docs-8.1:ticdc/integrate-confluent-using-ticdc.md#create-data-replicas-of-tidb-tables-in-snowflake`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `008101d9ed8a9bff462ebd7de914efa3cdeb5e55f00c8c70b5ec823bc0a7ad74`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/integrate-confluent-using-ticdc#create-data-replicas-of-tidb-tables-in-snowflake
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/integrate-confluent-using-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when you need Snowflake SQL patterns to turn TiCDC change logs replicated by Confluent into a table replica with INSERT, UPDATE, and DELETE handling.
- Retrieval Keywords: Snowflake, TiCDC, Confluent Snowflake Sink Connector, TIDB_TEST_ITEM, TEST_ITEM, TEST_ITEM_STREAM, append_only=true, MERGE INTO, RECORD_METADATA:key, RECORD_CONTENT:val, IS_NULL_VALUE(v), STREAM_TO_ITEM, system$stream_has_data, SCHEDULED TASK, TRUNCATE_TIDB_TEST_ITEM, TRUNCATE table TIDB_TEST_ITEM
- Follow-up Guidance: The chunk also includes a scheduled cleanup task that truncates `TIDB_TEST_ITEM` every two hours when `system$stream_has_data('TIDB_TEST_ITEM')` is true.
- Classification Note: This is classified as a data pipeline chunk because it describes ETL-style replication of TiDB incremental change logs into Snowflake using streams, merge logic, and scheduled tasks.

## Official Source Content

### Create data replicas of TiDB tables in Snowflake

In the previous section, the change logs of TiDB incremental data have been replicated to Snowflake. This section describes how to process these change logs using the TASK and STREAM features of Snowflake according to the event type of `INSERT`, `UPDATE`, and `DELETE`, and then write them to a table with the same structure as that in upstream, thereby creating a data replica of the TiDB table in Snowflake. The following takes the `ITEM` table as an example.

The structure of the `ITEM` table is as follows:

```
CREATE TABLE `item` (
  `i_id` int(11) NOT NULL,
  `i_im_id` int(11) DEFAULT NULL,
  `i_name` varchar(24) DEFAULT NULL,
  `i_price` decimal(5,2) DEFAULT NULL,
  `i_data` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`i_id`)
);
```

In Snowflake, there is a table named `TIDB_TEST_ITEM`, which is automatically created by the Confluent Snowflake Sink Connector. The table structure is as follows:

```
create or replace TABLE TIDB_TEST_ITEM (
        RECORD_METADATA VARIANT,
        RECORD_CONTENT VARIANT
);
```

1. In Snowflake, create a table with the same structure as that in TiDB:

    ```
    create or replace table TEST_ITEM (
        i_id INTEGER primary key,
        i_im_id INTEGER,
        i_name VARCHAR,
        i_price DECIMAL(36,2),
        i_data VARCHAR
    );
    ```

2. Create a stream for `TIDB_TEST_ITEM` and set `append_only` to `true` as follows.

    ```
    create or replace stream TEST_ITEM_STREAM on table TIDB_TEST_ITEM append_only=true;
    ```

    In this way, the created stream captures only `INSERT` events in real time. Specifically, when a new change log is generated for `ITEM` in TiDB, the change log will be inserted into `TIDB_TEST_ITEM` and be captured by the stream.

3. Process the data in the stream. According to the event type, insert, update, or delete the stream data in the `TEST_ITEM` table.

    ```
    --Merge data into the TEST_ITEM table
    merge into TEST_ITEM n
      using
          -- Query TEST_ITEM_STREAM
          (SELECT RECORD_METADATA:key as k, RECORD_CONTENT:val as v from TEST_ITEM_STREAM) stm
          -- Match the stream with table on the condition that i_id is equal
          on k:i_id = n.i_id
      -- If the TEST_ITEM table contains a record that matches i_id and v is empty, delete this record
      when matched and IS_NULL_VALUE(v) = true then
          delete

      -- If the TEST_ITEM table contains a record that matches i_id and v is not empty, update this record
      when matched and IS_NULL_VALUE(v) = false then
          update set n.i_data = v:i_data, n.i_im_id = v:i_im_id, n.i_name = v:i_name, n.i_price = v:i_price

      -- If the TEST_ITEM table does not contain a record that matches i_id, insert this record
      when not matched then
          insert
              (i_data, i_id, i_im_id, i_name, i_price)
          values
              (v:i_data, v:i_id, v:i_im_id, v:i_name, v:i_price)
    ;
    ```

    In the preceding example, the `MERGE INTO` statement of Snowflake is used to match the stream and the table on a specific condition, and then execute corresponding operations, such as deleting, updating, or inserting a record. In this example, three `WHERE` clauses are used for the following three scenarios:

    - Delete the record in the table when the stream and the table match and the data in the stream is empty.
    - Update the record in the table when the stream and the table match and the data in the stream is not empty.
    - Insert the record in the table when the stream and the table do not match.

4. Periodically execute the statement in Step 3 to ensure that data is always up-to-date. You can also use the `SCHEDULED TASK` feature of Snowflake:

    ```
    -- Create a TASK to periodically execute the MERGE INTO statement
    create or replace task STREAM_TO_ITEM
        warehouse = test
        -- Execute the TASK every minute
        schedule = '1 minute'
    when
        -- Skip the TASK when there is no data in TEST_ITEM_STREAM
        system$stream_has_data('TEST_ITEM_STREAM')
    as
    -- Merge data into the TEST_ITEM table. The statement is the same as that in the preceding example
    merge into TEST_ITEM n
      using
          (select RECORD_METADATA:key as k, RECORD_CONTENT:val as v from TEST_ITEM_STREAM) stm
          on k:i_id = n.i_id
      when matched and IS_NULL_VALUE(v) = true then
          delete
      when matched and IS_NULL_VALUE(v) = false then
          update set n.i_data = v:i_data, n.i_im_id = v:i_im_id, n.i_name = v:i_name, n.i_price = v:i_price
      when not matched then
          insert
              (i_data, i_id, i_im_id, i_name, i_price)
          values
              (v:i_data, v:i_id, v:i_im_id, v:i_name, v:i_price)
    ;
    ```

At this time, you have established a data channel with certain ETL capabilities. Through this data channel, you can replicate TiDB's incremental data change logs to Snowflake, maintain a data replica of TiDB, and use the data in Snowflake.

The last step is to regularly clean up the useless data in the `TIDB_TEST_ITEM` table:

```
-- Clean up the TIDB_TEST_ITEM table every two hours
create or replace task TRUNCATE_TIDB_TEST_ITEM
    warehouse = test
    schedule = '120 minute'
when
    system$stream_has_data('TIDB_TEST_ITEM')
as
    TRUNCATE table TIDB_TEST_ITEM;
```
