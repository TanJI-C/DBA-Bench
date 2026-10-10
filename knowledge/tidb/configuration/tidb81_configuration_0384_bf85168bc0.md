# Backup, HDFS backup, and log-backup settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > backup | TiKV Configuration File > backup > `num-threads` | TiKV Configuration File > backup > `batch-size` | TiKV Configuration File > backup > `sst-max-size` | TiKV Configuration File > backup > `enable-auto-tune` <span class="version-mark">New in v5.4.0</span> | TiKV Configuration File > backup > `s3-multi-part-size` <span class="version-mark">New in v5.3.2</span> | TiKV Configuration File > backup.hadoop | TiKV Configuration File > backup.hadoop > `home` | TiKV Configuration File > backup.hadoop > `linux-user` | TiKV Configuration File > log-backup | TiKV Configuration File > log-backup > `enable` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > log-backup > `file-size-limit` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > log-backup > `initial-scan-pending-memory-quota` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > log-backup > `initial-scan-rate-limit` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > log-backup > `max-flush-interval` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > log-backup > `num-threads` <span class="version-mark">New in v6.2.0</span> | TiKV Configuration File > log-backup > `temp-path` <span class="version-mark">New in v6.2.0</span>`
- Source Line Ranges: `2283-2374`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `br`
- Topic Tags: `backup`, `br`, `log-backup`, `hdfs`, `s3`, `threads`, `rate-limit`, `external-storage`, `deprecated`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0384_bf85168bc0`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#backup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1a0441d7e6b25d28e495d158ce711983d8233d923cc6cab3637b69ce5356a4ac`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#backup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiKV configuration items for BR backup, HDFS backup command settings, or log-backup thread, rate limit, file size, and temporary storage parameters.
- Retrieval Keywords: backup, BR backup, backup.num-threads, batch-size, sst-max-size, enable-auto-tune, s3-multi-part-size, backup.hadoop, home, linux-user, log-backup, enable, file-size-limit, initial-scan-pending-memory-quota, initial-scan-rate-limit, max-flush-interval, num-threads, temp-path, external storage, multipart upload to S3
- Follow-up Guidance: The content notes that `s3-multi-part-size` is deprecated from v6.1.1 and no longer recommended.
- Classification Note: This is classified as configuration because the content lists TiKV backup, backup.hadoop, and log-backup configuration items with defaults, ranges, and behavior descriptions.

## Official Source Content

## backup

Configuration items related to BR backup.
### `num-threads`

+ The number of worker threads to process backup
+ Default value: `MIN(CPU * 0.5, 8)`
+ Value range: `[1, CPU]`
+ Minimum value: `1`
### `batch-size`

+ The number of data ranges to back up in one batch
+ Default value: `8`
### `sst-max-size`

+ The threshold of the backup SST file size. If the size of a backup file in a TiKV Region exceeds this threshold, the file is backed up to several files with the TiKV Region split into multiple Region ranges. Each of the files in the split Regions is the same size as `sst-max-size` (or slightly larger).
+ For example, when the size of a backup file in the Region of `[a,e)` is larger than `sst-max-size`, the file is backed up to several files with regions `[a,b)`, `[b,c)`, `[c,d)` and `[d,e)`, and the size of `[a,b)`, `[b,c)`, `[c,d)` is the same as that of `sst-max-size` (or slightly larger).
+ Default value: `"144MiB"`
### `enable-auto-tune` New in v5.4.0

+ Controls whether to limit the resources used by backup tasks to reduce the impact on the cluster when the cluster resource utilization is high. For more information, refer to [BR Auto-Tune](https://docs.pingcap.com/tidb/stable/br/br-auto-tune).
+ Default value: `true`
### `s3-multi-part-size` New in v5.3.2

> **Note:**
>
> This configuration is introduced to address backup failures caused by S3 rate limiting. This problem has been fixed by [refining the backup data storage structure](https://docs.pingcap.com/tidb/stable/br/br-snapshot-architecture#structure-of-backup-files). Therefore, this configuration is deprecated from v6.1.1 and is no longer recommended.

+ The part size used when you perform multipart upload to S3 during backup. You can adjust the value of this configuration to control the number of requests sent to S3.
+ If data is backed up to S3 and the backup file is larger than the value of this configuration item, [multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/API/API_UploadPart.html) is automatically enabled. Based on the compression ratio, the backup file generated by a 96-MiB Region is approximately 10 MiB to 30 MiB.
+ Default value: 5MiB
## backup.hadoop
### `home`

+ Specifies the location of the HDFS shell command and allows TiKV to find the shell command. This configuration item has the same effect as the environment variable `$HADOOP_HOME`.
+ Default value: `""`
### `linux-user`

+ Specifies the Linux user with which TiKV runs HDFS shell commands.
+ If this configuration item is not set, TiKV uses the current linux user.
+ Default value: `""`
## log-backup

Configuration items related to log backup.
### `enable` New in v6.2.0

+ Determines whether to enable log backup.
+ Default value: `true`
### `file-size-limit` New in v6.2.0

+ The size limit on backup log data to be stored.
+ Default value: 256MiB
+ Note: Generally, the value of `file-size-limit` is greater than the backup file size displayed in external storage. This is because the backup files are compressed before being uploaded to external storage.
### `initial-scan-pending-memory-quota` New in v6.2.0

+ The quota of cache used for storing incremental scan data during log backup.
+ Default value: `min(Total machine memory * 10%, 512 MiB)`
### `initial-scan-rate-limit` New in v6.2.0

+ The rate limit on throughput in an incremental data scan during log backup, which means the maximum amount of data that can be read from the disk per second. Note that if you only specify a number (for example, `60`), the unit is Byte instead of KiB.
+ Default value: 60MiB
+ Minimum value: 1MiB
### `max-flush-interval` New in v6.2.0

+ The maximum interval for writing backup data to external storage in log backup.
+ Default value: 3min
### `num-threads` New in v6.2.0

+ The number of threads used in log backup.
+ Default value: CPU * 0.5
+ Value range: [2, 12]
### `temp-path` New in v6.2.0

+ The temporary path to which log files are written before being flushed to external storage.
+ Default value: `${deploy-dir}/data/log-backup-temp`
