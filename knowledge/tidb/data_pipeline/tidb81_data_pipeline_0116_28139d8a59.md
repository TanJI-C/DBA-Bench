# Example 1 setup with Dumpling export and Lightning data source configuration

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-distributed-import.md`
- Source Title: `Use TiDB Lightning to Import Data in Parallel`
- Source Heading Path: `Use TiDB Lightning to Import Data in Parallel > Example 1: Use Dumpling + TiDB Lightning to Import Sharded Databases and Tables into TiDB in Parallel | Use TiDB Lightning to Import Data in Parallel > Example 1: Use Dumpling + TiDB Lightning to Import Sharded Databases and Tables into TiDB in Parallel > Step 1: Use Dumpling to export data | Use TiDB Lightning to Import Data in Parallel > Example 1: Use Dumpling + TiDB Lightning to Import Sharded Databases and Tables into TiDB in Parallel > Step 2: Configure TiDB Lightning data sources`
- Source Line Ranges: `68-115`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `dumpling`, `tidb`, `pd`
- Topic Tags: `sharded-tables`, `parallel-import`, `dumpling-export`, `data-source-dir`, `s3`, `gcs`, `local-backend`, `sorted-kv-dir`, `configuration-file`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0116_28139d8a59`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-distributed-import.md#example-1-use-dumpling-tidb-lightning-to-import-sharded-databases-and-tables-into-tidb-in-parallel`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2981e695fa1743f465ef4e222a6be853122df58be735f561917b1db86beb619a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-distributed-import#example-1-use-dumpling-tidb-lightning-to-import-sharded-databases-and-tables-into-tidb-in-parallel
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-distributed-import.md

## Retrieval Guidance

- Use When: Use this content when looking for the Example 1 setup for exporting sharded tables with Dumpling and configuring TiDB Lightning data sources for parallel import.
- Retrieval Keywords: Example 1, Dumpling, sharded tables, my_db, my_table_01, my_table_10, my_db.my_table, --filter, data-source-dir, parent directory, different sub-directories, tidb-lightning.toml, status-addr = ":8289", parallel-import = true, backend = "local", sorted-kv-dir, Amazon S3, GCS, tiup tidb-lightning, s3://my-bucket/sql-backup, URI Formats of External Storage Services
- Follow-up Guidance: For external storage such as Amazon S3 or GCS, the source includes an example `tiup tidb-lightning` command and points to URI Formats of External Storage Services for parameter details.
- Classification Note: This chunk is classified as a data pipeline topic because the official content covers Dumpling export layout and TiDB Lightning source configuration fields such as `data-source-dir`, `backend`, and `sorted-kv-dir` for a parallel import workflow.

## Official Source Content

## Example 1: Use Dumpling + TiDB Lightning to Import Sharded Databases and Tables into TiDB in Parallel

In this example, assume that the upstream is a MySQL cluster with 10 sharded tables, with a total size of 10 TiB. You can Use 5 TiDB Lightning instances to perform parallel import, and each instance imports 2 TiB. It is estimated that the total import time (excluding the time required for Dumpling export) can be reduced from about 40 hours to about 10 hours.

Assume that the upstream library is named `my_db`, and the name of each sharded table is `my_table_01` ~ `my_table_10`. You want to merge and import them into the downstream `my_db.my_table` table. The specific steps are described in the following sections.
### Step 1: Use Dumpling to export data

Export two sharded tables on the 5 nodes where TiDB Lightning is deployed:

- If the two sharded tables are in the same MySQL instance, you can use the `--filter` parameter of Dumpling to directly export them. When using TiDB Lightning to import, you can specify `data-source-dir` as the directory where Dumpling exports data to;
- If the data of the two sharded tables are distributed on different MySQL nodes, you need to use Dumpling to separately export them. The exported data needs to be placed in the same parent directory <b>but in different sub-directories</b>. When using TiDB Lightning to perform parallel import, you need to specify `data-source-dir` as the parent directory.

For more information on how to use Dumpling to export data, see [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview).
### Step 2: Configure TiDB Lightning data sources

Create a configuration file `tidb-lightning.toml`, and then add the following content:

```
[lightning]
status-addr = ":8289"

[mydumper]
# Specify the path for Dumpling to export data. If Dumpling performs several times and the data belongs to different directories, you can place all the exported data in the same parent directory and specify this parent directory here.
data-source-dir = "/path/to/source-dir"

[tikv-importer]
# Whether to allow importing data into tables that already have data. The default value is `false`.
# When using parallel import, because multiple TiDB Lightning instances import a table at the same time, this configuration item must be set to `true`.
parallel-import = true
# "local": The default mode. It applies to large dataset import, for example, greater than 1 TiB. However, during the import, downstream TiDB is not available to provide services.
# "tidb": You can use this mode for small dataset import, for example, smaller than 1 TiB. During the import, downstream TiDB is available to provide services.
backend = "local"

# Specify the path for local sorting data.
sorted-kv-dir = "/path/to/sorted-dir"
```

If the data source is stored in external storage such as Amazon S3 or GCS, you need to configure additional parameters for connection. You can specify parameters for such configuration. For example, the following example assumes that data is stored in Amazon S3:

```
tiup tidb-lightning --tidb-port=4000 --pd-urls=127.0.0.1:2379 --backend=local --sorted-kv-dir=/tmp/sorted-kvs \
    -d 's3://my-bucket/sql-backup'
```

For more parameter descriptions, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
