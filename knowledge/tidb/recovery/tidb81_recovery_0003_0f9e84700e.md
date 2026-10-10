# BR batch create table for restore

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-batch-create-table.md`
- Source Title: `Batch Create Table`
- Source Heading Path: `Batch Create Table | Batch Create Table > Usage scenario | Batch Create Table > Use Batch Create Table | Batch Create Table > Implementation | Batch Create Table > Feature test`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tidb`, `tikv`, `pd`, `tiup`
- Topic Tags: `restore`, `table-creation`, `batch-ddl`, `ddl-batch-size`, `serial-execution`, `performance-testing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0003_0f9e84700e`
- Source ID: `tidb-docs-8.1:br/br-batch-create-table.md#batch-create-table`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d93343f54dd50f7fe78e58ef3df948d4348abde16dbe98b9b6a563f3132062ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-batch-create-table#batch-create-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-batch-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how BR speeds up restore table creation for a large number of tables and how `--ddl-batch-size` affects Batch Create Table versus serial execution.
- Retrieval Keywords: Batch Create Table, BR restore full, --ddl-batch-size, --ddl-batch-size=128, --ddl-batch-size=1, serial execution, create tables in batches, TiDB DDL owner, schema version changes once, 50000 tables, tiup br restore full
- Follow-up Guidance: The source also includes the implementation difference between serial execution and batch create table, plus a feature test with cluster configuration and restore speed results.
- Classification Note: This is classified as recovery for the BR component because the content describes table creation behavior and configuration during BR restore in a self-managed TiDB cluster.

## Official Source Content

# Batch Create Table

When restoring data, Backup & Restore (BR) creates databases and tables in the target TiDB cluster and then restores the backup data to the tables. In versions earlier than TiDB v6.0.0, BR uses the [serial execution](#implementation) implementation to create tables in the restore process. However, when BR restores data with a large number of tables (nearly 50000), this implementation takes much time on creating tables.

To speed up the table creation process and reduce the time for restoring data, the Batch Create Table feature is introduced in TiDB v6.0.0. This feature is enabled by default.

> **Note:**
>
> - To use the Batch Create Table feature, both TiDB and BR are expected to be of v6.0.0 or later. If either TiDB or BR is earlier than v6.0.0, BR uses the serial execution implementation.
> - Suppose that you use a cluster management tool (for example, TiUP), and your TiDB and BR are of v6.0.0 or later versions, or your TiDB and BR are upgraded from a version earlier than v6.0.0 to v6.0.0 or later.
## Usage scenario

If you need to restore data with a massive amount of tables, for example, 50000 tables, you can use the Batch Create Table feature to speed up the restore process.

For the detailed effect, see [Test for the Batch Create Table Feature](#feature-test).
## Use Batch Create Table

BR enables the Batch Create Table feature by default, with the default configuration of `--ddl-batch-size=128` in v6.0.0 or later to speed up the restore process. Therefore, you do not need to configure this parameter. `--ddl-batch-size=128` means creating tables in batches, each batch with 128 tables.

To disable this feature, you can set `--ddl-batch-size` to `1`. See the following example command:

```shell
tiup br restore full \
--storage local:///br_data/ --pd "${PD_IP}:2379" --log-file restore.log \
--ddl-batch-size=1
```

After this feature is disabled, BR uses the [serial execution implementation](#implementation) instead.
## Implementation

- Serial execution implementation before v6.0.0:

    When restoring data, BR creates databases and tables in the target TiDB cluster and then restores the backup data to the tables. To create tables, BR calls TiDB internal API first, and then processes table creation tasks, which works similarly to executing the `Create Table` statement. The TiDB DDL owner creates tables sequentially. Once the DDL owner creates a table, the DDL schema version changes correspondingly and each version change is synchronized to other TiDB DDL workers (including BR). Therefore, when restoring a large number of tables, the serial execution implementation is time-consuming.

- Batch create table implementation since v6.0.0:

    By default, BR creates tables in multiple batches, and each batch has 128 tables. Using this implementation, when BR creates one batch of tables, the TiDB schema version only changes once. This implementation significantly increases the speed of table creation.
## Feature test

This section describes the test information about the Batch Create Table feature. The test environment is as follows:

- Cluster configurations:

    - 15 TiKV instances. Each TiKV instance is equipped with 16 CPU cores, 80 GB memory, and 16 threads to process RPC requests ([`import.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads) = 16).
    - 3 TiDB instances. Each TiDB instance is equipped with 16 CPU cores, 32 GB memory.
    - 3 PD instances. Each PD instance is equipped with 16 CPU cores, 32 GB memory.

- The size of data to be restored: 16.16 TB

The test result is as follows:

```
'[2022/03/12 22:37:49.060 +08:00] [INFO] [collector.go:67] ["Full restore success summary"] [total-ranges=751760] [ranges-succeed=751760] [ranges-failed=0] [split-region=1h33m18.078448449s] [restore-ranges=542693] [total-take=1h41m35.471476438s] [restore-data-size(after-compressed)=8.337TB] [Size=8336694965072] [BackupTS=431773933856882690] [total-kv=148015861383] [total-kv-size=16.16TB] [average-speed=2.661GB/s]'
```

From the test result, you can see that the average speed of restoring one TiKV instance is as high as 181.65 MB/s (which equals to `average-speed`/`tikv_count`).
