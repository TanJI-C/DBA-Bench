# TIDB_HOT_REGIONS_HISTORY schema and query scenarios

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-tidb-hot-regions-history.md`
- Source Title: `TIDB_HOT_REGIONS_HISTORY`
- Source Heading Path: `TIDB_HOT_REGIONS_HISTORY | TIDB_HOT_REGIONS_HISTORY > Common user scenarios`
- Source Line Ranges: `5-132`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`, `tidb`
- Topic Tags: `information_schema`, `hot-regions`, `history`, `schema`, `columns`, `pd-recording`, `query-examples`, `time-range`, `region-distribution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0417_3790ceec4c`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-tidb-hot-regions-history.md#tidb-hot-regions-history`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d8e1cf274f3dbce704f17b980808f8064c5d9d8d18a4ff546f4673906fa7cca`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-hot-regions-history#tidb-hot-regions-history
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-tidb-hot-regions-history.md

## Retrieval Guidance

- Use When: Use this when you need the schema, column meanings, availability note, or example queries for historical hot Regions recorded by PD in INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY.
- Retrieval Keywords: TIDB_HOT_REGIONS_HISTORY, INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY, history hot Regions, PD periodically recorded locally, hot-regions-write-interval, hot-regions-reserved-days, DESC tidb_hot_regions_history, UPDATE_TIME, REGION_ID, STORE_ID, PEER_ID, IS_LEARNER, IS_LEADER, TYPE, HOT_DEGREE, FLOW_BYTES, KEY_RATE, QUERY_RATE, time range, Query hot Regions within a specific period of time, Query the distribution of hot Regions, Query the distribution of hot Leader Regions, Query the distribution of hot Index Regions, FROM_UNIXTIME, TIMESTAMP
- Follow-up Guidance: The source notes that UPDATE_TIME, REGION_ID, STORE_ID, PEER_ID, IS_LEARNER, IS_LEADER, and TYPE are pushed down to the PD servers for execution, and it gives an example that specifies a time range and additional conditions such as store_id and type='write'.
- Classification Note: This is reference content because it defines the TIDB_HOT_REGIONS_HISTORY table schema, explains each field, and lists grounded query scenarios and SQL examples.

## Official Source Content

# TIDB_HOT_REGIONS_HISTORY

The `TIDB_HOT_REGIONS_HISTORY` table provides information about history hot Regions that are periodically recorded locally by PD.

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

You can specify the record interval by configuring [`hot-regions-write-interval`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#hot-regions-write-interval-new-in-v540). The default value is 10 minutes. You can specify the period for reserving history information about hot Regions by configuring [`hot-regions-reserved-days`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#hot-regions-reserved-days-new-in-v540). The default value is 7 days. See [PD configuration file description](https://docs.pingcap.com/tidb/stable/pd-configuration-file#hot-regions-write-interval-new-in-v540) for details.

By default, the record interval is 10 minutes, and the period for reserving history information about hot Regions is 7 days.

```sql
USE information_schema;
DESC tidb_hot_regions_history;
```

```sql
+-------------+--------------+------+------+---------+-------+
| Field       | Type         | Null | Key  | Default | Extra |
+-------------+--------------+------+------+---------+-------+
| UPDATE_TIME | timestamp(6) | YES  |      | NULL    |       |
| DB_NAME     | varchar(64)  | YES  |      | NULL    |       |
| TABLE_NAME  | varchar(64)  | YES  |      | NULL    |       |
| TABLE_ID    | bigint(21)   | YES  |      | NULL    |       |
| INDEX_NAME  | varchar(64)  | YES  |      | NULL    |       |
| INDEX_ID    | bigint(21)   | YES  |      | NULL    |       |
| REGION_ID   | bigint(21)   | YES  |      | NULL    |       |
| STORE_ID    | bigint(21)   | YES  |      | NULL    |       |
| PEER_ID     | bigint(21)   | YES  |      | NULL    |       |
| IS_LEARNER  | tinyint(1)   | NO   |      | 0       |       |
| IS_LEADER   | tinyint(1)   | NO   |      | 0       |       |
| TYPE        | varchar(64)  | YES  |      | NULL    |       |
| HOT_DEGREE  | bigint(21)   | YES  |      | NULL    |       |
| FLOW_BYTES  | double       | YES  |      | NULL    |       |
| KEY_RATE    | double       | YES  |      | NULL    |       |
| QUERY_RATE  | double       | YES  |      | NULL    |       |
+-------------+--------------+------+------+---------+-------+
16 rows in set (0.00 sec)
```

The fields in the `TIDB_HOT_REGIONS_HISTORY` table are described as follows:

* UPDATE_TIME: The update time of the hot Region.
* DB_NAME: The database name of the object in which the hot Region is located.
* TABLE_ID: The ID of the table in which the hot Region is located.
* TABLE_NAME: The name of the table in which the hot Region is located.
* INDEX_NAME: The name of the index in which the hot Region is located.
* INDEX_ID: The ID of the index in which the hot Region is located.
* REGION_ID: The ID of the hot Region.
* STORE_ID: The ID of the store in which the hot Region is located.
* PEER_ID: The ID of the Peer corresponding to the hot Region.
* IS_LEARNER: Whether the PEER is the LEARNER.
* IS_LEADER: Whether the PEER is the LEADER.
* TYPE: The type of the hot Region.
* HOT_DEGREE: The hot degree of the hot Region.
* FLOW_BYTES: The number of bytes written and read in the Region.
* KEY_RATE: The number of keys written and read in the Region.
* QUERY_RATE: The number of queries written and read in the Region.

> **Note:**
>
> `UPDATE_TIME`, `REGION_ID`, `STORE_ID`, `PEER_ID`, `IS_LEARNER`, `IS_LEADER` and `TYPE` fields are pushed down to the PD servers for execution. To reduce the overhead of using the table, you must specify the time range for the search, and specify as many conditions as possible. For example, `select * from tidb_hot_regions_history where store_id = 11 and update_time > '2020-05-18 20:40:00' and update_time < '2020-05-18 21:40:00' and type='write'`.
## Common user scenarios

* Query hot Regions within a specific period of time. Replace `update_time` with your actual time.

    ```sql
    SELECT * FROM INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY WHERE update_time >'2021-08-18 21:40:00' and update_time <'2021-09-19 00:00:00';
    ```

    > **Note:**
    >
    > `UPDATE_TIME` also supports Unix timestamps. For example, `update_time >TIMESTAMP('2021-08-18 21:40:00')` or `update_time > FROM_UNIXTIME(1629294000.000)`.

* Query hot Regions in a table within a specific period of time. Replace `update_time` and `table_name` with your actual values.

    ```SQL
    SELECT * FROM INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY WHERE update_time >'2021-08-18 21:40:00' and update_time <'2021-09-19 00:00:00' and TABLE_NAME = 'table_name';
    ```

* Query the distribution of hot Regions within a specific period of time. Replace `update_time` and `table_name` with your actual values.

    ```sql
    SELECT count(region_id) cnt, store_id FROM INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY WHERE update_time >'2021-08-18 21:40:00' and update_time <'2021-09-19 00:00:00' and table_name = 'table_name' GROUP BY STORE_ID ORDER BY cnt DESC;
    ```

* Query the distribution of hot Leader Regions within a specific period of time. Replace `update_time` and `table_name` with your actual values.

    ```sql
    SELECT count(region_id) cnt, store_id FROM INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY WHERE update_time >'2021-08-18 21:40:00' and update_time <'2021-09-19 00:00:00' and table_name = 'table_name' and is_leader=1 GROUP BY STORE_ID ORDER BY cnt DESC;
    ```

* Query the distribution of hot Index Regions within a specific period of time. Replace `update_time` and `table_name` with your actual values.

    ```sql
    SELECT count(region_id) cnt, index_name, store_id FROM INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY WHERE update_time >'2021-08-18 21:40:00' and update_time <'2021-09-19 00:00:00' and table_name = 'table_name' group by index_name, store_id order by index_name,cnt desc;
    ```

* Query the distribution of hot Index Leader Regions within a specific period of time. Replace `update_time` and `table_name` with your actual values.

    ```sql
    SELECT count(region_id) cnt, index_name, store_id FROM INFORMATION_SCHEMA.TIDB_HOT_REGIONS_HISTORY WHERE update_time >'2021-08-18 21:40:00' and update_time <'2022-09-19 00:00:00' and table_name = 'table_name' and is_leader=1 group by index_name, store_id order by index_name,cnt desc;
    ```
