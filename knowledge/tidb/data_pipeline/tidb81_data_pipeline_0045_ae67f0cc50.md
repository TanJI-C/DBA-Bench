# Import full data to TiDB with Lightning local backend

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-large-mysql-to-tidb.md`
- Source Title: `Migrate Large Datasets from MySQL to TiDB`
- Source Heading Path: `Migrate Large Datasets from MySQL to TiDB > Step 2. Import full data to TiDB`
- Source Line Ranges: `108-169`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `pd`, `shared`
- Topic Tags: `migration`, `import`, `full-load`, `local-backend`, `s3`, `configuration`, `progress`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0045_ae67f0cc50`
- Source ID: `tidb-docs-8.1:migrate-large-mysql-to-tidb.md#step-2-import-full-data-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3249c0a2d704c9932fdc4b2185e51f060f599f28e56397de3784cbb7cd920985`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-large-mysql-to-tidb#step-2-import-full-data-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-large-mysql-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when configuring and running TiDB Lightning to import full data, especially with backend = "local", sorted-kv-dir, S3 credentials, progress checks, and success verification from the log.
- Retrieval Keywords: Step 2. Import full data to TiDB, tidb-lightning.toml, [lightning], [tikv-importer], backend = "local", backend = "tidb", sorted-kv-dir, [mydumper], data-source-dir, [tidb], status-port, pd-addr, TiDB Lightning Configuration, tiup tidb-lightning -config tidb-lightning.toml, SIGHUP, nohup, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ~/.aws/credentials, progress, monitoring dashboard, TiDB Lightning web interface, tidb-lightning.log, the whole procedure completed, tidb lightning exit, TiDB Lightning FAQ
- Follow-up Guidance: The source explains that import progress can be checked by grepping progress in the log, using the monitoring dashboard, or using the TiDB Lightning web interface, and that success is confirmed by the log line the whole procedure completed.
- Classification Note: This is classified as data_pipeline for Lightning because it describes the full-load import configuration, runtime requirements for local backend, execution method, monitoring, and completion checks.

## Official Source Content

## Step 2. Import full data to TiDB

1. Create the `tidb-lightning.toml` configuration file:

    ```toml
    [lightning]
    # log.
    level = "info"
    file = "tidb-lightning.log"

    [tikv-importer]
    # "local": Default backend. The local backend is recommended to import large volumes of data (1 TiB or more). During the import, the target TiDB cluster cannot provide any service.
    # "tidb": The "tidb" backend is recommended to import data less than 1 TiB. During the import, the target TiDB cluster can provide service normally. For more information on the backends, refer to https://docs.pingcap.com/tidb/stable/tidb-lightning-backends.
    backend = "local"
    # Sets the temporary storage directory for the sorted Key-Value files. The directory must be empty, and the storage space must be greater than the size of the dataset to be imported. For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage, which can use I/O exclusively.
    sorted-kv-dir = "${sorted-kv-dir}"

    [mydumper]
    # The data source directory. The same directory where Dumpling exports data in "Step 1. Export all data from MySQL".
    data-source-dir = "${data-path}" # A local path or S3 path. For example, 's3://my-bucket/sql-backup'.

    [tidb]
    # The target TiDB cluster information.
    host = ${host}                # e.g.: 172.16.32.1
    port = ${port}                # e.g.: 4000
    user = "${user_name}"         # e.g.: "root"
    password = "${password}"      # e.g.: "rootroot"
    status-port = ${status-port}  # During the import, TiDB Lightning needs to obtain the table schema information from the TiDB status port. e.g.: 10080
    pd-addr = "${ip}:${port}"     # The address of the PD cluster, e.g.: 172.16.31.3:2379. TiDB Lightning obtains some information from PD. When backend = "local", you must specify status-port and pd-addr correctly. Otherwise, the import will be abnormal.
    ```

    For more information on TiDB Lightning configuration, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).

2. Start the import by running `tidb-lightning`. If you launch the program directly in the command line, the process might exit unexpectedly after receiving a SIGHUP signal. It is not recommended to directly use `nohup` to start a process from the command line. Instead, edit the following script content, for example:

    If you import data from S3, pass the SecretKey and AccessKey that have access to the S3 storage path as environment variables to the TiDB Lightning node. You can also read the credentials from `~/.aws/credentials`.

    ```shell
    #!/bin/bash
    export AWS_ACCESS_KEY_ID=${access_key}
    export AWS_SECRET_ACCESS_KEY=${secret_key}
    nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out 2>&1 &
    ```

    Then use the script to start TiDB Lightning.

3. After the import starts, you can check the progress of the import by one of the following methods:

    - `grep` the keyword `progress` in the log. The progress is updated every 5 minutes by default.
    - Check progress in [the monitoring dashboard](https://docs.pingcap.com/tidb/stable/tidb-lightning/monitor-tidb-lightning).
    - Check progress in [the TiDB Lightning web interface](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-web-interface).

4. After TiDB Lightning completes the import, it exits automatically. Check whether `tidb-lightning.log` contains `the whole procedure completed` in the last lines. If yes, the import is successful. If no, the import encounters an error. Address the error as instructed in the error message.

> **Note:**
>
> Whether the import is successful or not, the last line of the log shows `tidb lightning exit`. It means that TiDB Lightning exits normally, but does not necessarily mean that the import is successful.

If the import fails, refer to [TiDB Lightning FAQ](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq) for troubleshooting.
