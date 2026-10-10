# Export with Dumpling and import with TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/backup-and-restore-using-dumpling-lightning.md`
- Source Title: `Back up and Restore Data Using Dumpling and TiDB Lightning`
- Source Heading Path: `Back up and Restore Data Using Dumpling and TiDB Lightning > Use Dumpling to back up full data | Back up and Restore Data Using Dumpling and TiDB Lightning > Use TiDB Lightning to restore full data`
- Source Line Ranges: `84-149`
- Source Scope: `self_managed`
- Primary Component: `dumpling`
- Related Components: `lightning`, `pd`, `tidb`, `tiup`
- Topic Tags: `backup`, `restore`, `export`, `import`, `s3`, `configuration`, `local-backend`, `tidb-backend`, `credentials`, `nohup`, `progress`, `verification`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0004_b256548c40`
- Source ID: `tidb-docs-8.1:backup-and-restore-using-dumpling-lightning.md#use-dumpling-to-back-up-full-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `56c046dc10ad58baf9b75a7f5fe83629ce472350e126d42c51d6d044ff139f1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/backup-and-restore-using-dumpling-lightning#use-dumpling-to-back-up-full-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/backup-and-restore-using-dumpling-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official example for exporting full data with Dumpling and restoring it with TiDB Lightning, including S3 paths, configuration fields, startup commands, and log-based verification.
- Retrieval Keywords: tiup dumpling -h ${ip} -P 3306 -u root -t 16 -r 200000 -F 256MiB -B my_db1 -f 'my_db1.table[12]' -o 's3://my-bucket/sql-backup', --filetype, Option list of Dumpling, tidb-lightning.toml, [tikv-importer], backend = "local", backend = "tidb", sorted-kv-dir, [mydumper], data-source-dir, [tidb], status-port, pd-addr, nohup tiup tidb-lightning -config tidb-lightning.toml, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ~/.aws/credentials, grep progress, the whole procedure completed, tidb lightning exit, TiDB Lightning FAQ
- Follow-up Guidance: The chunk also explains how to supply S3 credentials, monitor import progress with the progress log keyword, and distinguish a successful import from a normal TiDB Lightning process exit.
- Classification Note: This is classified as an operation chunk because the content provides executable export and import procedures, concrete configuration examples, and runtime verification details for Dumpling and TiDB Lightning.

## Official Source Content

## Use Dumpling to back up full data

1. Run the following command to export full data from TiDB to `s3://my-bucket/sql-backup` in Amazon S3:

    ```shell
    tiup dumpling -h ${ip} -P 3306 -u root -t 16 -r 200000 -F 256MiB -B my_db1 -f 'my_db1.table[12]' -o 's3://my-bucket/sql-backup'
    ```

    Dumpling exports data in SQL files by default. You can specify a different file format by adding the `--filetype` option.

    For more configurations of Dumpling, see [Option list of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling).

2. After the export is completed, you can view the backup files in the directory `s3://my-bucket/sql-backup`.
## Use TiDB Lightning to restore full data

1. Edit the `tidb-lightning.toml` file to import full data backed up using Dumpling from `s3://my-bucket/sql-backup` to the target TiDB cluster:

    ```toml
    [lightning]
    # log
    level = "info"
    file = "tidb-lightning.log"

    [tikv-importer]
    # "local": Default backend. The local backend is recommended to import large volumes of data (1 TiB or more). During the import, the target TiDB cluster cannot provide any service.
    # "tidb": The "tidb" backend is recommended to import data less than 1 TiB. During the import, the target TiDB cluster can provide service normally. For more information on the backends, refer to https://docs.pingcap.com/tidb/stable/tidb-lightning-backends.
    backend = "local"
    # Sets the temporary storage directory for the sorted Key-Value files. The directory must be empty, and the storage space must be greater than the size of the dataset to be imported. For better import performance, it is recommended to use a directory different from `data-source-dir` and use flash storage, which can use I/O exclusively.
    sorted-kv-dir = "${sorted-kv-dir}"

    [mydumper]
    # The data source directory. The same directory where Dumpling exports data in "Use Dumpling to back up full data".
    data-source-dir = "${data-path}" #  A local path or S3 path. For example, 's3://my-bucket/sql-backup'

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

2. Start the import by running `tidb-lightning`. If you launch the program directly in the command line, the process might exit unexpectedly after receiving a `SIGHUP` signal. In this case, it is recommended to run the program using a `nohup` or `screen` tool. For example:

    If you import data from S3, pass the SecretKey and AccessKey that have access to the S3 storage path as environment variables to the TiDB Lightning node. You can also read the credentials from `~/.aws/credentials`.

    ```shell
    export AWS_ACCESS_KEY_ID=${access_key}
    export AWS_SECRET_ACCESS_KEY=${secret_key}
    nohup tiup tidb-lightning -config tidb-lightning.toml > nohup.out 2>&1 &
    ```

3. After the import starts, you can `grep` the keyword `progress` in the log to check the progress of the import. The progress is updated every 5 minutes by default.

4. After TiDB Lightning completes the import, it exits automatically. Check whether `tidb-lightning.log` contains `the whole procedure completed` in the last lines. If yes, the import is successful. If no, the import encounters an error. Address the error as instructed in the error message.

> **Note:**
>
> Whether the import is successful or not, the last line of the log shows `tidb lightning exit`. It means that TiDB Lightning exits normally, but does not necessarily mean that the import is successful.

If the import fails, refer to [TiDB Lightning FAQ](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq) for troubleshooting.
