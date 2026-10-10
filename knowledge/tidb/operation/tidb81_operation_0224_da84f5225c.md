# IMPORT INTO FROM FILE usage and compressed files

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-import-into.md`
- Source Title: `IMPORT INTO`
- Source Heading Path: `IMPORT INTO > `IMPORT INTO ... FROM FILE` usage | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Compressed files`
- Source Line Ranges: `162-187`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `cloud`, `lightning`
- Topic Tags: `from-file`, `storage-support`, `dxf`, `distributed-execution`, `local-storage`, `proxy-limitations`, `compressed-files`, `gzip`, `zstd`, `snappy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0224_da84f5225c`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-import-into.md#import-into-from-file-usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `26bbbc3a12a5012af1a745dad2cd248ac9c2a2daf31d9b3b8c7cb44d6a9ab583`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#import-into-from-file-usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-import-into.md

## Retrieval Guidance

- Use When: Use this chunk when you need deployment-specific support and execution behavior for `IMPORT INTO ... FROM FILE`, including DXF behavior, local-storage limitations, proxy restrictions, and supported compressed file extensions.
- Retrieval Keywords: IMPORT INTO FROM FILE usage, TiDB Self-Managed, TiDB Cloud Dedicated, Starter, Essential, Amazon S3, GCS, Alibaba Cloud OSS, TiDB Distributed eXecution Framework, DXF, tidb_enable_dist_task, local storage, proxy or load balancer, compressed files, .gz, .gzip, .zstd, .zst, .snappy, official Snappy format, 256 MiB after decompression
- Follow-up Guidance: This content also identifies the follow-up distinction between DXF enabled versus disabled execution and notes compressed file handling limits tied to TiDB Lightning decompression behavior.
- Classification Note: This is operational content because it describes where `IMPORT INTO ... FROM FILE` can run, how execution changes with DXF, and practical constraints for local and compressed files.

## Official Source Content

## `IMPORT INTO ... FROM FILE` usage

For TiDB Self-Managed, `IMPORT INTO ... FROM FILE` supports importing data from files stored in Amazon S3, GCS, and the TiDB local storage. For [TiDB Cloud Dedicated](https://docs.pingcap.com/tidbcloud/select-cluster-tier#tidb-cloud-dedicated), `IMPORT INTO ... FROM FILE` supports importing data from files stored in Amazon S3 and GCS. For [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential), `IMPORT INTO ... FROM FILE` supports importing data from files stored in Amazon S3 and Alibaba Cloud OSS.

- For data files stored in Amazon S3 or GCS, `IMPORT INTO ... FROM FILE` supports running in the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework).

    - When the DXF is enabled ([tidb_enable_dist_task](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) is `ON`), `IMPORT INTO` splits a data import job into multiple sub-jobs and distributes these sub-jobs to different TiDB nodes for execution to improve the import efficiency.
    - When the DXF is disabled, `IMPORT INTO ... FROM FILE` only supports running on the TiDB node where the current user is connected.

- For data files stored locally in TiDB, `IMPORT INTO ... FROM FILE` only supports running on the TiDB node where the current user is connected. Therefore, the data files need to be placed on the TiDB node where the current user is connected. If you access TiDB through a proxy or load balancer, you cannot import data files stored locally in TiDB.
### Compressed files

`IMPORT INTO ... FROM FILE` supports importing compressed `CSV` and `SQL` files. It can automatically determine whether a file is compressed and the compression format based on the file extension:

| Extension | Compression format |
|:---|:---|
| `.gz`, `.gzip` | gzip compression format |
| `.zstd`, `.zst` | ZStd compression format |
| `.snappy` | snappy compression format |

> **Note:**
>
> - The Snappy compressed file must be in the [official Snappy format](https://github.com/google/snappy). Other variants of Snappy compression are not supported.
> - Because TiDB Lightning cannot concurrently decompress a single large compressed file, the size of the compressed file affects the import speed. It is recommended that a source file is no greater than 256 MiB after decompression.
