# Export full shard data with Dumpling

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB > Step1. Use Dumpling to export full data`
- Source Line Ranges: `72-116`
- Source Scope: `self_managed`
- Primary Component: `dumpling`
- Related Components: `lightning`, `dm`, `tidb`
- Topic Tags: `full-export`, `mysql-shards`, `table-filter`, `output-directory`, `metadata`, `binlog-position`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0042_256279fe24`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-shards-to-tidb.md#step1-use-dumpling-to-export-full-data`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `de3a0988767c47fd77b627900393f8a92ffdd5d9ea1dbd7753dee8688042ba5c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-shards-to-tidb#step1-use-dumpling-to-export-full-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Dumpling commands and parameters for exporting full data from multiple MySQL shard tables and locating the metadata files that contain binlog positions for incremental replication.
- Retrieval Keywords: Step1. Use Dumpling to export full data, tiup dumpling, -f parameter of Dumpling, my_db1.table[12], my_db2.table[34], -B my_db1, -B my_db2, -o ${data-path}/my_db1, -o ${data-path}/my_db2, -t 16, -r 200000, -F 256MB, table-filter, external storage URI, metadata files, binlog locations, incremental replication, same parent directory, ${data-path}
- Follow-up Guidance: The source states that the starting position information for incremental replication is in the `metadata` files under the `my_db1` and `my_db2` sub-directories of `${data-path}`.
- Classification Note: This is classified as data_pipeline because the content covers full-data export from source MySQL shards, export layout, and export metadata used by later replication steps.

## Official Source Content

## Step1. Use Dumpling to export full data

If those multiple sharded tables to be exported are in the same upstream MySQL instance, you can directly use the `-f` parameter of Dumpling to export them in a single operation.

If the sharded tables are stored in different MySQL instances, you can use Dumpling to export them respectively and place the exported results in the same parent directory.

In the following example, both methods are used, and then the exported data is stored in the same parent directory.

First, run the following command to use Dumpling to export `table1` and `table2` from `my_db1`:

```shell
tiup dumpling -h ${ip} -P 3306 -u root -t 16 -r 200000 -F 256MB -B my_db1 -f 'my_db1.table[12]' -o ${data-path}/my_db1
```

The following table describes parameters in the command above. For more information about Dumpling parameters, see [Dumpling Overview](https://docs.pingcap.com/tidb/stable/dumpling-overview).

| Parameter       |   Description |
|-                |-              |
| `-u` or `--user`       |   Specifies the user name to be used.  |
| `-p` or `--password`   |   Specifies the password to be used. |
| `-p` or `--port`       |   Specifies the port to be used.|
| `-h` or `--host`       |   Specifies the IP address of the data source.  |
| `-t` or `--thread`     |   Specifies the number of threads for the export. Increasing the number of threads improves the concurrency of Dumpling and the export speed, and increases the database's memory consumption. Therefore, it is not recommended to set the number too large. Usually, it's less than 64.|
| `-o` or `--output`     |  Specifies the export directory of the storage, which supports a local file path or an [external storage URI](https://docs.pingcap.com/tidb/stable/external-storage-uri).|
| `-r` or `--row`        | Specifies the maximum number of rows in a single file. If you use this parameter, Dumpling enables the in-table concurrency to speed up the export and reduce the memory usage.|
| `-F` |  Specifies the maximum size of a single file. The unit is `MiB`. It is recommended to keep the value to 256 MiB. |
| `-B` or `--database`   | Specifies databases to be exported. |
| `-f` or `--filter`     |  Exports tables that match the filter pattern. For the filter syntax, see [table-filter](https://docs.pingcap.com/tidb/stable/table-filter). |

Ensure that there is enough free space in `${data-path}`. It is strongly recommended to use the `-F` option to avoid interruptions in the backup process due to oversized single tables.

Then, run the following command to use Dumpling to export `table3` and `table4` from `my_db2`. Note that the path is `${data-path}/my_db2` instead of `${data-path}/my_db1`.

```shell
tiup dumpling -h ${ip} -P 3306 -u root -t 16 -r 200000 -F 256MB -B my_db2 -f 'my_db2.table[34]' -o ${data-path}/my_db2
```

After the preceding procedures, all source data tables are now exported to the `${data-path}` directory. Putting all the exported data on the same directory makes subsequent import by TiDB Lightning convenient.

The starting position information needed for incremental replication is in the `metadata` files in `my_db1` and `my_db2` sub-directories of `${data-path}` directory respectively. They are meta-information files automatically generated by Dumpling. To perform incremental replication, you need to record the binlog locations information in these files.
