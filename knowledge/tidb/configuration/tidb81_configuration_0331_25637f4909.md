# Enable Global Sort and configure cloud storage URI

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-global-sort.md`
- Source Title: `TiDB Global Sort`
- Source Heading Path: `TiDB Global Sort > Usage`
- Source Line Ranges: `36-68`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `shared`, `cloud`
- Topic Tags: `enablement`, `system-variables`, `tidb-enable-dist-task`, `tidb-cloud-storage-uri`, `s3`, `import-into`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0331_25637f4909`
- Source ID: `tidb-docs-8.1:tidb-global-sort.md#usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c075e7950ecb9953b4f2bd366089d20b04a79d27c5085668c06729bde2af1425`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-global-sort#usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-global-sort.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to enable Global Sort or how to configure the cloud storage URI used by Global Sort or IMPORT INTO.
- Retrieval Keywords: Usage, enable Global Sort, tidb_enable_dist_task, SET GLOBAL tidb_enable_dist_task = ON, tidb_cloud_storage_uri, SET GLOBAL tidb_cloud_storage_uri, s3://my-bucket/test-data?role-arn=, CLOUD_STORAGE_URI, IMPORT INTO, cloud storage path
- Follow-up Guidance: The source states that for IMPORT INTO, CLOUD_STORAGE_URI takes effect when both tidb_cloud_storage_uri and CLOUD_STORAGE_URI are configured with a valid cloud storage path.
- Classification Note: This chunk is classified as configuration because it provides the system variables, SQL statements, and option precedence used to enable Global Sort and set its cloud storage location.

## Official Source Content

## Usage

To enable Global Sort, follow these steps:

1. Enable the DXF by setting the value of [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) to `ON`. Starting from v8.1.0, this variable is enabled by default. For newly created clusters of v8.1.0 or later versions, you can skip this step.

    ```sql
    SET GLOBAL tidb_enable_dist_task = ON;
    ```

2. Set [`tidb_cloud_storage_uri`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cloud_storage_uri-new-in-v740) to a correct cloud storage path. See [an example](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages).

    ```sql
    SET GLOBAL tidb_cloud_storage_uri = 's3://my-bucket/test-data?role-arn=arn:aws:iam::888888888888:role/my-role'
    ```

2. Set [`tidb_cloud_storage_uri`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cloud_storage_uri-new-in-v740) to a correct cloud storage path. See [an example](https://docs.pingcap.com/tidb/stable/backup-and-restore-storages).

    ```sql
    SET GLOBAL tidb_cloud_storage_uri = 's3://my-bucket/test-data?role-arn=arn:aws:iam::888888888888:role/my-role'
    ```

> **Note:**
>
> For [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into), you can also specify the cloud storage path using the [`CLOUD_STORAGE_URI`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#withoptions) option. If both [`tidb_cloud_storage_uri`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_cloud_storage_uri-new-in-v740) and `CLOUD_STORAGE_URI` are configured with a valid cloud storage path, the configuration of `CLOUD_STORAGE_URI` takes effect for [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).
