# Backup statistics options and backup data encryption

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-snapshot-manual.md`
- Source Title: `TiDB Snapshot Backup and Restore Command Manual`
- Source Heading Path: `TiDB Snapshot Backup and Restore Command Manual > Back up statistics | TiDB Snapshot Backup and Restore Command Manual > Encrypt the backup data`
- Source Line Ranges: `113-164`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `tiup`
- Topic Tags: `statistics-backup`, `ignore-stats`, `load-stats`, `backupmeta`, `encryption`, `crypter`, `experimental`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0012_92b40340c5`
- Source ID: `tidb-docs-8.1:br/br-snapshot-manual.md#back-up-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f90150bac59bbcd8b3c32063cac0a3a76daee03ab342e1117c60fef021cfa62c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-snapshot-manual.md

## Retrieval Guidance

- Use When: Use this chunk when looking for BR options for backing up and restoring table statistics or for encrypting backup data with crypter parameters.
- Retrieval Keywords: --ignore-stats, --load-stats, backupmeta, LOAD STATS, statistics in JSON format, tiup br backup full --ignore-stats=false, tiup br restore full, Encrypt the backup data, --crypter.method, --crypter.key, --crypter.key-file, aes128-ctr, aes192-ctr, aes256-ctr, plaintext, experimental feature
- Follow-up Guidance: It notes that statistics restore is automatic when statistics are included in the backup, and that encrypted backup data cannot be restored on clusters earlier than v5.3.0.
- Classification Note: This is classified as a configuration chunk because the content centers on configurable BR parameters such as `--ignore-stats`, `--load-stats`, and the `--crypter.*` encryption settings and their documented behavior.

## Official Source Content

## Back up statistics

Starting from TiDB v7.5.0, the `br` command-line tool introduces the `--ignore-stats` parameter. When you set this parameter to `false`, the `br` command-line tool supports backing up statistics of columns, indexes, and tables. In this case, you do not need to manually run the statistics collection task for the TiDB database restored from the backup, or wait for the completion of the automatic collection task. This feature simplifies the database maintenance work and improves the query performance.

If you do not set this parameter to `false`, the `br` command-line tool uses the default setting `--ignore-stats=true`, which means statistics are not backed up during data backup.

The following is an example of backing up cluster snapshot data and backing up table statistics with `--ignore-stats=false`:

```shell
tiup br backup full \
--storage local:///br_data/ --pd "${PD_IP}:2379" --log-file restore.log \
--ignore-stats=false
```

After backing up data with the preceding configuration, when you restore data, the `br` command-line tool automatically restores table statistics if table statistics are included in the backup (Starting from v8.0.0, the `br` command-line tool introduces the `--load-stats` parameter, which controls whether to restore backup statistics. The default behavior is to restore backup statistics. There is no need to set it to `false` in most cases):

```shell
tiup br restore full \
--storage local:///br_data/ --pd "${PD_IP}:2379" --log-file restore.log
```

When the backup and restore feature backs up data, it stores statistics in JSON format within the `backupmeta` file. When restoring data, it loads statistics in JSON format into the cluster. For more information, see [LOAD STATS](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-stats).
## Encrypt the backup data

> **Warning:**
>
> This is an experimental feature. It is not recommended that you use it in the production environment.

BR supports encrypting backup data at the backup side and [at the storage side when backing up to Amazon S3](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#amazon-s3-server-side-encryption). You can choose either encryption method as required.

Since TiDB v5.3.0, you can encrypt backup data by configuring the following parameters:

- `--crypter.method`: Encryption algorithm, which can be `aes128-ctr`, `aes192-ctr`, or `aes256-ctr`. The default value is `plaintext`, indicating that data is not encrypted.
- `--crypter.key`: Encryption key in hexadecimal string format. It is a 128-bit (16 bytes) key for the algorithm `aes128-ctr`, a 24-byte key for the algorithm `aes192-ctr`, and a 32-byte key for the algorithm `aes256-ctr`.
- `--crypter.key-file`: The key file. You can directly pass in the file path where the key is stored as a parameter without passing in the `crypter.key`.

The following is an example:

```shell
tiup br backup full\
    --pd ${PD_IP}:2379 \
    --storage "s3://${backup_collection_addr}/snapshot-${date}?access-key=${access-key}&secret-access-key=${secret-access-key}" \
    --crypter.method aes128-ctr \
    --crypter.key 0123456789abcdef0123456789abcdef
```

> **Note:**
>
> - If the key is lost, the backup data cannot be restored to the cluster.
> - The encryption feature needs to be used on `br` and TiDB clusters v5.3.0 or later versions. The encrypted backup data cannot be restored on clusters earlier than v5.3.0.
