# Import data from Amazon S3 examples

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-data-source.md`
- Source Title: `TiDB Lightning Data Sources`
- Source Heading Path: `TiDB Lightning Data Sources > Import data from Amazon S3 | TiDB Lightning Data Sources > More resources`
- Source Line Ranges: `405-447`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `cloud`, `pd`, `tiup`
- Topic Tags: `amazon-s3`, `external-storage`, `iam-role`, `access-keys`, `session-token`, `path-style`, `command-examples`, `resources`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0453_85f8ba294c`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-data-source.md#import-data-from-amazon-s3`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a30136b5603cb9dd5e8263692ee83a4da2f3a8f76ea151b11931bd0876423eee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#import-data-from-amazon-s3
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-data-source.md

## Retrieval Guidance

- Use When: Use this chunk when you need example tiup tidb-lightning commands for importing data from Amazon S3 with local permissions, force-path-style and endpoint parameters, role-arn, access_key and secret_access_key, or session-token.
- Retrieval Keywords: Import data from Amazon S3, tiup tidb-lightning, -d 's3://my-bucket/sql-backup', force-path-style=true, endpoint=http://10.154.10.132:8088, role-arn, access_key, secret_access_key, session-token, --tidb-port=4000, --pd-urls=127.0.0.1:2379, --backend=local, --sorted-kv-dir=/tmp/sorted-kvs, URI Formats of External Storage Services
- Follow-up Guidance: For more parameter configurations, the source points to URI Formats of External Storage Services.
- Classification Note: The classification is operation because the content provides command-line examples for running TiDB Lightning against Amazon S3 with different authentication and request-style parameters.

## Official Source Content

## Import data from Amazon S3

The following examples show how to import data from Amazon S3 using TiDB Lightning. For more parameter configurations, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).

+ Use the locally configured permissions to access S3 data:

    ```bash
    tiup tidb-lightning --tidb-port=4000 --pd-urls=127.0.0.1:2379 --backend=local --sorted-kv-dir=/tmp/sorted-kvs \
        -d 's3://my-bucket/sql-backup'
    ```

+ Use the path-style request to access S3 data:

    ```bash
    tiup tidb-lightning --tidb-port=4000 --pd-urls=127.0.0.1:2379 --backend=local --sorted-kv-dir=/tmp/sorted-kvs \
        -d 's3://my-bucket/sql-backup?force-path-style=true&endpoint=http://10.154.10.132:8088'
    ```

+ Use a specific AWS IAM role ARN to access S3 data:

    ```bash
    tiup tidb-lightning --tidb-port=4000 --pd-urls=127.0.0.1:2379 --backend=local --sorted-kv-dir=/tmp/sorted-kvs \
        -d 's3://my-bucket/test-data?role-arn=arn:aws:iam::888888888888:role/my-role'
    ```

* Use access keys of an AWS IAM user to access S3 data:

    ```bash
    tiup tidb-lightning --tidb-port=4000 --pd-urls=127.0.0.1:2379 --backend=local --sorted-kv-dir=/tmp/sorted-kvs \
        -d 's3://my-bucket/test-data?access_key={my_access_key}&secret_access_key={my_secret_access_key}'
    ```

* Use the combination of AWS IAM role access keys and session tokens to access S3 data:

    ```bash
    tiup tidb-lightning --tidb-port=4000 --pd-urls=127.0.0.1:2379 --backend=local --sorted-kv-dir=/tmp/sorted-kvs \
        -d 's3://my-bucket/test-data?access_key={my_access_key}&secret_access_key={my_secret_access_key}&session-token={my_session_token}'
    ```
## More resources

- [Export to CSV files Using Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-to-csv-files)
- [`LOAD DATA`](https://dev.mysql.com/doc/refman/8.0/en/load-data.html)
