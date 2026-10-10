# Export full data from MySQL with Dumpling

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-to-tidb.md`
- Source Title: `Migrate Large Datasets from MySQL to TiDB`
- Source Heading Path: `Migrate Large Datasets from MySQL to TiDB > Step 1. Export all data from MySQL`
- Source Line Ranges: `70-107`
- Source Scope: `self_managed`
- Primary Component: `dumpling`
- Related Components: `shared`
- Topic Tags: `migration`, `export`, `mysql`, `full-load`, `metadata`, `binlog-position`, `s3`, `table-filter`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0044_3479dfb47f`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-to-tidb.md#step-1-export-all-data-from-mysql`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66b637f204b982a68cd97dd69c4c9112d2366a742f2175d0d3bc62cbb66ff9c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-to-tidb#step-1-export-all-data-from-mysql
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the Dumpling command example and parameter meanings for exporting full MySQL data, including file splitting, table filters, output to S3, and recording binlog position metadata.
- Retrieval Keywords: Step 1. Export all data from MySQL, tiup dumpling, -h ${ip} -P 3306 -u root -t 16 -r 200000 -F 256MiB -B my_db1 -f 'my_db1.table[12]' -o 's3://my-bucket/sql-backup', --filetype, --user, --password, --port, --host, --thread, --output, external storage URI, --row, -F 256MiB, --database, --filter, table-filter, metadata file, SHOW MASTER STATUS, Log: mysql-bin.000004, Pos: 109227, GTID, binlog position information
- Follow-up Guidance: The source says to view the Dumpling-generated metadata file in the data directory and record the SHOW MASTER STATUS binlog position for incremental replication in Step 3.
- Classification Note: This is classified as data_pipeline for Dumpling because it focuses on the full-load export step, Dumpling CLI options, export storage location, and export metadata.

## Official Source Content

## Step 1. Export all data from MySQL

1. Export all data from MySQL by running the following command:

    ```shell
    tiup dumpling -h ${ip} -P 3306 -u root -t 16 -r 200000 -F 256MiB -B my_db1 -f 'my_db1.table[12]' -o 's3://my-bucket/sql-backup'
    ```

    Dumpling exports data in SQL files by default. You can specify a different file format by adding the `--filetype` option.

    The parameters used above are as follows. For more Dumpling parameters, refer to [Dumpling Overview](https://docs.pingcap.com/tidb/stable/dumpling-overview).

    |parameters             |Description|
    |-                      |-|
    |`-u` or `--user`       |MySQL user|
    |`-p` or `--password`   |MySQL user password|
    |`-P` or `--port`       |MySQL port|
    |`-h` or `--host`       |MySQL IP address|
    |`-t` or `--thread`     |The number of threads used for export|
    |`-o` or `--output`     |The directory that stores the exported file. Supports a local path or an [external storage URI](https://docs.pingcap.com/tidb/stable/external-storage-uri)|
    |`-r` or `--row`        |The maximum number of rows in a single file|
    |`-F`                   |The maximum size of a single file, in MiB. Recommended value: 256 MiB.|
    |-`B` or `--database`   |Specifies a database to be exported|
    |`-f` or `--filter`     |Exports tables that match the pattern. Refer to [table-filter](https://docs.pingcap.com/tidb/stable/table-filter) for the syntax.|

    Make sure `${data-path}` has the space to store all exported upstream tables. To calculate the required space, see [Downstream storage space requirements](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#storage-space-of-the-target-database). To prevent the export from being interrupted by a large table consuming all the spaces, it is strongly recommended to use the `-F` option to limit the size of a single file.

2. View the `metadata` file in the `${data-path}` directory. This is a Dumpling-generated metadata file. Record the binlog position information, which is required for the incremental replication in Step 3.

    ```
    SHOW MASTER STATUS:
    Log: mysql-bin.000004
    Pos: 109227
    GTID:
    ```
