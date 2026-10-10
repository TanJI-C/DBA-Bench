# SQL management of Pump and Drainer status

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/maintain-tidb-binlog-cluster.md`
- Source Title: `TiDB Binlog Cluster Operations`
- Source Heading Path: `TiDB Binlog Cluster Operations > Use SQL statements to manage Pump or Drainer`
- Source Line Ranges: `56-139`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `binlog`, `pump`, `drainer`, `sql`, `node-state`, `status-check`, `state-change`, `abnormal-situations`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0276_2ee702acd7`
- Source ID: `tidb-docs-8.1:tidb-binlog/maintain-tidb-binlog-cluster.md#use-sql-statements-to-manage-pump-or-drainer`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `59be48e9e18d1b21d70b2e19f0530d0edd979f68fa81ad08c88b6f607f8a1db7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/maintain-tidb-binlog-cluster#use-sql-statements-to-manage-pump-or-drainer
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/maintain-tidb-binlog-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need the SQL statements to check whether binlog is enabled, display Pump or Drainer status, or change a Pump or Drainer node state in abnormal situations.
- Retrieval Keywords: show variables like "log_bin";, log_bin, show pump status;, show drainer status;, change pump to node_state ='paused' for node_id 'pump1';, change drainer to node_state ='paused' for node_id 'drainer1';, update-pump, update-drainer, NodeID, Address, State, Max_Commit_Ts, Update_Time, abnormal situations
- Follow-up Guidance: The content notes that changing Pump or Drainer status only supports modifying the status stored in PD, and that to pause or close the node, use the binlogctl tool.
- Classification Note: This is classified as an operation chunk because the content provides SQL-based status inspection and status modification procedures for Pump and Drainer management.

## Official Source Content

## Use SQL statements to manage Pump or Drainer

To view or modify binlog related states, execute corresponding SQL statements in TiDB.

- Check whether binlog is enabled:

    ```sql
    show variables like "log_bin";
    ```

    ```
    +---------------+-------+
    | Variable_name | Value |
    +---------------+-------+
    | log_bin       |  0   |
    +---------------+-------+
    ```
    
    When the Value is `0`, binlog is enabled. When the Value is `1`, binlog is disabled.

- Check the status of all the Pump or Drainer nodes:

    ```sql
    show pump status;
    ```

    ```
    +--------|----------------|--------|--------------------|---------------------|
    | NodeID |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
    +--------|----------------|--------|--------------------|---------------------|
    | pump1  | 127.0.0.1:8250 | Online | 408553768673342237 | 2019-05-01 00:00:01 |
    +--------|----------------|--------|--------------------|---------------------|
    | pump2  | 127.0.0.2:8250 | Online | 408553768673342335 | 2019-05-01 00:00:02 |
    +--------|----------------|--------|--------------------|---------------------|
    ```

    ```sql
    show drainer status;
    ```

    ```
    +----------|----------------|--------|--------------------|---------------------|
    |  NodeID  |     Address    | State  |   Max_Commit_Ts    |    Update_Time      |
    +----------|----------------|--------|--------------------|---------------------|
    | drainer1 | 127.0.0.3:8249 | Online | 408553768673342532 | 2019-05-01 00:00:03 |
    +----------|----------------|--------|--------------------|---------------------|
    | drainer2 | 127.0.0.4:8249 | Online | 408553768673345531 | 2019-05-01 00:00:04 |
    +----------|----------------|--------|--------------------|---------------------|
    ```

- Modify the state of a Pump or Drainer node in abnormal situations

    ```sql
    change pump to node_state ='paused' for node_id 'pump1';
    ```

    ```
    Query OK, 0 rows affected (0.01 sec)
    ```

    ```sql
    change drainer to node_state ='paused' for node_id 'drainer1';
    ```

    ```
    Query OK, 0 rows affected (0.01 sec)
    ```

    Executing the above SQL statements works the same as the `update-pump` or `update-drainer` commands in binlogctl. Use the above SQL statements **only** when the Pump or Drainer node is in abnormal situations.

> **Note:**
>
> - Checking whether binlog is enabled and the running status of Pump or Drainer is supported in TiDB v2.1.7 and later versions.
> - Modifying the status of Pump or Drainer is supported in TiDB v3.0.0-rc.1 and later versions. This feature only supports modifying the status of Pump or Drainer nodes stored in PD. To pause or close the node, use the `binlogctl` tool.
