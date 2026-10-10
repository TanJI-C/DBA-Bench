# Export and import table statistics

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Export and import statistics | Introduction to Statistics > Export and import statistics > Export statistics | Introduction to Statistics > Export and import statistics > Import statistics`
- Source Line Ranges: `511-562`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `statistics`, `export`, `import`, `json`, `http`, `load-stats`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0232_98c5e8e7d7`
- Source ID: `tidb-docs-8.1:statistics.md#export-and-import-statistics`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6afff05b4543a5ccb0f1baef70b2ec53a070dfe174e7b9bb47d490f012aa7c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#export-and-import-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to export table statistics as JSON through the TiDB status port or import statistics with the LOAD STATS statement.
- Retrieval Keywords: Export and import statistics, /stats/dump/${db_name}/${table_name}, /stats/dump/${db_name}/${table_name}/${yyyyMMddHHmmss}, JSON format statistics, LOAD STATS, LOAD STATS 'file_name';, --local-infile=1, tidb-server-status-port, curl -s http://127.0.0.1:10080/stats/dump/test/t1 -o /tmp/t1.json
- Follow-up Guidance: It includes the HTTP export paths for current and specific-time table statistics and notes that the MySQL client should be started with --local-infile=1 for import.
- Classification Note: This is classified as operation for TiDB because the content describes the operational interfaces and SQL statement used to export and import table statistics.

## Official Source Content

## Export and import statistics

This section describes how to export and import statistics.

> **Note:**
>
> This section is not applicable to TiDB Cloud.
### Export statistics

The interface to export statistics is as follows:

+ To obtain the JSON format statistics of the `${table_name}` table in the `${db_name}` database:

    ```
    http://${tidb-server-ip}:${tidb-server-status-port}/stats/dump/${db_name}/${table_name}
    ```

    For example:

    ```shell
    curl -s http://127.0.0.1:10080/stats/dump/test/t1 -o /tmp/t1.json
    ```

+ To obtain the JSON format statistics of the `${table_name}` table in the `${db_name}` database at specific time:

    ```
    http://${tidb-server-ip}:${tidb-server-status-port}/stats/dump/${db_name}/${table_name}/${yyyyMMddHHmmss}
    ```
### Import statistics

> **Note:**
>
> When you start the MySQL client, use the `--local-infile=1` option.

Generally, the imported statistics refer to the JSON file obtained using the export interface.

Loading statistics can be done with the [`LOAD STATS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-stats) statement.

For example:

```sql
LOAD STATS 'file_name';
```

`file_name` is the file name of the statistics to be imported.
