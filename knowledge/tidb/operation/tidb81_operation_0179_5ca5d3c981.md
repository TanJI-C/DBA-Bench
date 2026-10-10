# Update statistics for partitioned tables in dynamic pruning mode

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Restrictions and limitations on partitions > Dynamic pruning mode > Update statistics of partitioned tables in dynamic pruning mode`
- Source Line Ranges: `2024-2089`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `partitioning`, `dynamic-pruning`, `statistics`, `analyze-table`, `information-schema`, `batch-update`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0179_5ca5d3c981`
- Source ID: `tidb-docs-8.1:partitioned-table.md#update-statistics-of-partitioned-tables-in-dynamic-pruning-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d71eaa9166c5f0681e8ee8708de75a02caa9eb29fed6ada3b4d609750cd40078`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#update-statistics-of-partitioned-tables-in-dynamic-pruning-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when finding the documented SQL and shell commands to locate partitioned tables and batch-generate `ANALYZE TABLE` statements for dynamic pruning mode.
- Retrieval Keywords: Update statistics of partitioned tables in dynamic pruning mode, information_schema.PARTITIONS, TIDB_PARTITION_ID IS NOT NULL, SELECT DISTINCT CONCAT(TABLE_SCHEMA,'.', TABLE_NAME), ANALYZE TABLE, ALL COLUMNS, gatherGlobalStats.sql, mysql --host xxxx --port xxxx -u root -p -e, tee gatherGlobalStats.sql, sed -i, SET session tidb_partition_prune_mode = dynamic, source gatherGlobalStats.sql
- Follow-up Guidance: The content includes generating `ANALYZE TABLE schema.table ALL COLUMNS;` statements from `information_schema.PARTITIONS`, exporting them to `gatherGlobalStats.sql`, removing the header line with `sed -i`, and then running `SET session tidb_partition_prune_mode = dynamic;` followed by `source gatherGlobalStats.sql`.
- Classification Note: This is operation content because it provides a numbered procedure and concrete commands for batch updating statistics of partitioned tables in dynamic pruning mode.

## Official Source Content

#### Update statistics of partitioned tables in dynamic pruning mode

1. Locate all partitioned tables:

    ```sql
    SELECT DISTINCT CONCAT(TABLE_SCHEMA,'.', TABLE_NAME)
        FROM information_schema.PARTITIONS
        WHERE TIDB_PARTITION_ID IS NOT NULL
        AND TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA', 'mysql', 'sys', 'PERFORMANCE_SCHEMA', 'METRICS_SCHEMA');
    ```

    ```
    +-------------------------------------+
    | concat(TABLE_SCHEMA,'.',TABLE_NAME) |
    +-------------------------------------+
    | test.t                              |
    +-------------------------------------+
    1 row in set (0.02 sec)
    ```

2. Generate the statements for updating the statistics of all partitioned tables:

    ```sql
    SELECT DISTINCT CONCAT('ANALYZE TABLE ',TABLE_SCHEMA,'.',TABLE_NAME,' ALL COLUMNS;')
        FROM information_schema.PARTITIONS
        WHERE TIDB_PARTITION_ID IS NOT NULL
        AND TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA','mysql','sys','PERFORMANCE_SCHEMA','METRICS_SCHEMA');
    ```

    ```
    +----------------------------------------------------------------------+
    | concat('ANALYZE TABLE ',TABLE_SCHEMA,'.',TABLE_NAME,' ALL COLUMNS;') |
    +----------------------------------------------------------------------+
    | ANALYZE TABLE test.t ALL COLUMNS;                                    |
    +----------------------------------------------------------------------+
    1 row in set (0.01 sec)
    ```

    You can change `ALL COLUMNS` to the columns you need.

3. Export the batch update statements to a file:

    ```shell
    mysql --host xxxx --port xxxx -u root -p -e "SELECT DISTINCT CONCAT('ANALYZE TABLE ',TABLE_SCHEMA,'.',TABLE_NAME,' ALL COLUMNS;') \
        FROM information_schema.PARTITIONS \
        WHERE TIDB_PARTITION_ID IS NOT NULL \
        AND TABLE_SCHEMA NOT IN ('INFORMATION_SCHEMA','mysql','sys','PERFORMANCE_SCHEMA','METRICS_SCHEMA');" | tee gatherGlobalStats.sql
    ```

4. Execute a batch update:

    Process SQL statements before executing the `source` command:

    ```
    sed -i "" '1d' gatherGlobalStats.sql --- mac
    sed -i '1d' gatherGlobalStats.sql --- linux
    ```

    ```sql
    SET session tidb_partition_prune_mode = dynamic;
    source gatherGlobalStats.sql
    ```
