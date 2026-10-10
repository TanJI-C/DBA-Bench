# TiDB Lightning FAQ basics, import behavior, validation, and operational constraints

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-faq.md`
- Source Title: `TiDB Lightning FAQs`
- Source Heading Path: `TiDB Lightning FAQs | TiDB Lightning FAQs > What is the minimum TiDB/TiKV/PD cluster version supported by TiDB Lightning? | TiDB Lightning FAQs > Does TiDB Lightning support importing multiple schemas (databases)? | TiDB Lightning FAQs > What are the privilege requirements for the target database? | TiDB Lightning FAQs > TiDB Lightning encountered an error when importing one table. Will it affect other tables? Will the process be terminated? | TiDB Lightning FAQs > How to properly restart TiDB Lightning? | TiDB Lightning FAQs > How to ensure the integrity of the imported data? | TiDB Lightning FAQs > What kinds of data source formats are supported by TiDB Lightning? | TiDB Lightning FAQs > Could TiDB Lightning skip creating schema and tables? | TiDB Lightning FAQs > How to prohibit importing invalid data? | TiDB Lightning FAQs > How to stop the `tidb-lightning` process? | TiDB Lightning FAQs > Can TiDB Lightning be used with 1-Gigabit network card? | TiDB Lightning FAQs > Why TiDB Lightning requires so much free space in the target TiKV cluster?`
- Source Line Ranges: `5-94`
- Source Scope: `shared`
- Primary Component: `lightning`
- Related Components: `dumpling`, `sql`, `tikv`, `pd`, `tidb`, `tiup`
- Topic Tags: `version-compatibility`, `multi-schema-import`, `privileges`, `error-isolation`, `restart`, `checksum`, `data-formats`, `schema-detection`, `strict-sql-mode`, `process-stop`, `network-bandwidth`, `storage-capacity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0938_cab322eddc`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-faq.md#tidb-lightning-faqs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `927163765b6ceb99ae8db2bb1af1debab5f6a5e511aafc6bd3f283f1a9dcbeed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#tidb-lightning-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering general TiDB Lightning FAQ questions about supported cluster versions, multi-schema import, target privileges, single-table error impact, restart behavior, checksum validation, supported source formats, schema creation behavior, strict SQL mode, stopping the process, network bandwidth limits, or TiKV free space requirements.
- Retrieval Keywords: minimum TiDB TiKV PD cluster version supported by TiDB Lightning, Local-backend earliest available version 4.0.0, Importer-backend earliest available version 2.0.9, TiDB-backend earliest available version 2.0.9, version of TiDB Lightning should be the same as the cluster, support importing multiple schemas databases, privilege requirements for the target database, one table error affect other tables, how to properly restart TiDB Lightning, nohup tiup tidb-lightning -config tidb-lightning.toml, ensure integrity of imported data, checksum mismatch process would be aborted, ADMIN CHECKSUM TABLE, supported data source formats, Dumpling CSV Apache Parquet Amazon Aurora Apache Hive Snowflake, local disk Amazon S3 storage, skip creating schema and tables, no-schema = true, CREATE TABLE invocations, recognize the schema and tables in the downstream, prohibit importing invalid data, Strict SQL Mode, sql-mode = "STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION", ONLY_FULL_GROUP_BY,NO_AUTO_CREATE_USER, how to stop the tidb-lightning process, ps aux | grep tidb-lightning, kill -2 ${PID}, 1-Gigabit network card, 10-Gigabit network card, PD is unable to be contacted anymore, space requirement 6 times the size of data source, 3 replicas, space amplification in RocksDB
- Follow-up Guidance: The chunk also points to Prerequisites for using TiDB Lightning for target database permissions and includes the exact `ADMIN CHECKSUM TABLE `schema`.`table`;` SQL example.
- Classification Note: This is classified as reference because the content is a broad FAQ covering fixed behaviors, commands, configuration names, and constraints of TiDB Lightning.

## Official Source Content

# TiDB Lightning FAQs

This document lists the frequently asked questions (FAQs) and answers about TiDB Lightning.
## What is the minimum TiDB/TiKV/PD cluster version supported by TiDB Lightning?

The version of TiDB Lightning should be the same as the cluster. If you use the Local-backend mode, the earliest available version is 4.0.0. If you use the Importer-backend mode or the TiDB-backend mode, the earliest available version is 2.0.9, but it is recommended to use the 3.0 stable version.
## Does TiDB Lightning support importing multiple schemas (databases)?

Yes.
## What are the privilege requirements for the target database?

For details about the permissions, see [Prerequisites for using TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements).
## TiDB Lightning encountered an error when importing one table. Will it affect other tables? Will the process be terminated?

If only one table has an error encountered, the rest will still be processed normally.
## How to properly restart TiDB Lightning?

1. [Stop the `tidb-lightning` process](#how-to-stop-the-tidb-lightning-process).
2. Start a new `tidb-lightning` task: execute the previous start command, such as `nohup tiup tidb-lightning -config tidb-lightning.toml`.
## How to ensure the integrity of the imported data?

TiDB Lightning by default performs checksum on the local data source and the imported tables. If there is checksum mismatch, the process would be aborted. These checksum information can be read from the log.

You could also execute the [`ADMIN CHECKSUM TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-checksum-table) SQL command on the target table to recompute the checksum of the imported data.

```sql
ADMIN CHECKSUM TABLE `schema`.`table`;
```

```
+---------+------------+---------------------+-----------+-------------+
| Db_name | Table_name | Checksum_crc64_xor  | Total_kvs | Total_bytes |
+---------+------------+---------------------+-----------+-------------+
| schema  | table      | 5505282386844578743 |         3 |          96 |
+---------+------------+---------------------+-----------+-------------+
1 row in set (0.01 sec)
```
## What kinds of data source formats are supported by TiDB Lightning?

TiDB Lightning supports:

- Importing files exported by [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview), CSV files, and [Apache Parquet files generated by Amazon Aurora](https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb), Apache Hive, and Snowflake.
- Reading data from a local disk or from the Amazon S3 storage.
## Could TiDB Lightning skip creating schema and tables?

Starting from v5.1, TiDB Lightning can automatically recognize the schema and tables in the downstream. If you use TiDB Lightning earlier than v5.1, you need to set `no-schema = true` in the `[mydumper]` section in `tidb-lightning.toml`. This makes TiDB Lightning skip the `CREATE TABLE` invocations and fetch the metadata directly from the target database. TiDB Lightning will exit with error if a table is actually missing.
## How to prohibit importing invalid data?

You can prohibit importing invalid data by enabling Strict SQL Mode.

By default, the [`sql_mode`](https://dev.mysql.com/doc/refman/8.0/en/sql-mode.html) used by TiDB Lightning is `"ONLY_FULL_GROUP_BY,NO_AUTO_CREATE_USER"`, which allows invalid data such as the date `1970-00-00`.

To prohibit importing invalid data, you need to change the `sql-mode` setting to `"STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION"` in the `[tidb]` section in `tidb-lightning.toml`.

```toml
...
[tidb]
sql-mode = "STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION"
...
```
## How to stop the `tidb-lightning` process?

To stop the `tidb-lightning` process, you can choose the corresponding operation according to your deployment method.

- For manual deployment: if `tidb-lightning` is running in foreground, press <kbd>Ctrl</kbd>+<kbd>C</kbd> to exit. Otherwise, obtain the process ID using the `ps aux | grep tidb-lightning` command and then terminate the process using the `kill -2 ${PID}` command.
## Can TiDB Lightning be used with 1-Gigabit network card?

TiDB Lightning is best used with a 10-Gigabit network card.

1-Gigabit network cards can only provide a total bandwidth of 120 MB/s, which has to be shared among all target TiKV stores. TiDB Lightning can easily saturate all bandwidth of the 1-Gigabit network in physical import mode and bring down the cluster because PD is unable to be contacted anymore.
## Why TiDB Lightning requires so much free space in the target TiKV cluster?

With the default settings of 3 replicas, the space requirement of the target TiKV cluster is 6 times the size of data source. The extra multiple of "2" is a conservative estimation because the following factors are not reflected in the data source:

- The space occupied by indices
- Space amplification in RocksDB
