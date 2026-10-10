# Full data export and import FAQs

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/migration-tidb-faq.md`
- Source Title: `Migration FAQs`
- Source Heading Path: `Migration FAQs | Migration FAQs > Full data export and import | Migration FAQs > Full data export and import > How to migrate an application running on MySQL to TiDB? | Migration FAQs > Full data export and import > Data import and export is slow, and many retries and EOF errors appear in the log of each component without other errors | Migration FAQs > Full data export and import > If I accidentally import the MySQL user table into TiDB, or forget the password and cannot log in, how to deal with it? | Migration FAQs > Full data export and import > How to export the data in TiDB? | Migration FAQs > Full data export and import > How to migrate from DB2 or Oracle to TiDB? | Migration FAQs > Full data export and import > Error: `java.sql.BatchUpdateException:statement count 5001 exceeds the transaction limitation` while using Sqoop to write data into TiDB in `batches` | Migration FAQs > Full data export and import > Why does Dumpling return `The local disk space is insufficient` error or cause the upstream database to run out of memory when exporting a table? | Migration FAQs > Full data export and import > Does TiDB have a function like the Flashback Query in Oracle? Does it support DDL?`
- Source Line Ranges: `5-131`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `dumpling`, `tidb`
- Topic Tags: `migration`, `full-import`, `full-export`, `network-troubleshooting`, `authentication`, `password-reset`, `oracle-migration`, `db2-migration`, `sqoop`, `transaction-limit`, `disk-space`, `flashback-query`, `historical-read`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0023_14cd813407`
- Source ID: `tidb-docs-8.1:faq/migration-tidb-faq.md#migration-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `56b64a2f1c8c7420fdaa387d52cb9deab1d3ed33845cd82ec56ea9199b05e236`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/migration-tidb-faq#migration-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/migration-tidb-faq.md

## Retrieval Guidance

- Use When: Use this chunk when answering FAQ-style questions about full data export and import in TiDB, including MySQL application migration compatibility, slow import/export with retries and EOF errors, password recovery after importing the MySQL user table, export methods, DB2 or Oracle migration approaches, Sqoop batch transaction limit errors, Dumpling disk space or memory issues, and Flashback Query-like historical reads.
- Retrieval Keywords: How to migrate an application running on MySQL to TiDB, Data import and export is slow, retries and EOF errors, network issues, iperf3 -s, iperf3 -c <server-IP>, If I accidentally import the MySQL user table into TiDB, -skip-grant-table=true, mysql.user table, How to export the data in TiDB, Dumpling, mysqldump, WHERE clause, select to a file, How to migrate from DB2 or Oracle to TiDB, OGG, Gateway, CDC, Load infile, third-party data migration tool, java.sql.BatchUpdateException:statement count 5001 exceeds the transaction limitation, Sqoop, --batch, -Dsqoop.export.records.per.statement=10, maximum number of statements allowed in a single TiDB transaction, The local disk space is insufficient, SHARD_ROW_ID_BITS, partitioned table, latest version of Dumpling, Flashback Query in Oracle, read historical data, supports DDL as well
- Follow-up Guidance: If the network metrics look good but retries and EOF errors persist after updating each component, the content says to get support from PingCAP or the community.
- Classification Note: This chunk is classified as data_pipeline because the official content focuses on migration, export, import, external migration tools, batch write limits, and Dumpling export behavior.

## Official Source Content

# Migration FAQs

This document summarizes the frequently asked questions (FAQs) related to TiDB data migration.

For the frequently asked questions about migration-related tools, click the corresponding links in the list below:

- [Backup & Restore FAQs](https://docs.pingcap.com/tidb/stable/faq/backup-and-restore-faq)
- [TiDB Binlog FAQ](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq)
- [TiDB Lightning FAQs](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq)
- [TiDB Data Migration (DM) FAQs](https://docs.pingcap.com/tidb/stable/dm/dm-faq)
- [TiCDC FAQs](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq)
## Full data export and import
### How to migrate an application running on MySQL to TiDB?

Because TiDB supports most MySQL syntax, generally you can migrate your applications to TiDB without changing a single line of code in most cases.
### Data import and export is slow, and many retries and EOF errors appear in the log of each component without other errors

If no other logical errors occur, retries and EOF errors might be caused by network issues. It is recommended to first use tools to check the network connectivity. In the following example, [iperf](https://iperf.fr/) is used for troubleshooting:

+ Execute the following command on the server-side node where the retries and EOF errors occur:

    ```shell
    iperf3 -s
    ```

+ Execute the following command on the client-side node where the retries and EOF errors occur:

    ```shell
    iperf3 -c <server-IP>
    ```

The following example is the output of a client node with a good network connection:

```shell
$ iperf3 -c 192.168.196.58
Connecting to host 192.168.196.58, port 5201
[  5] local 192.168.196.150 port 55397 connected to 192.168.196.58 port 5201
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-1.00   sec  18.0 MBytes   150 Mbits/sec
[  5]   1.00-2.00   sec  20.8 MBytes   175 Mbits/sec
[  5]   2.00-3.00   sec  18.2 MBytes   153 Mbits/sec
[  5]   3.00-4.00   sec  22.5 MBytes   188 Mbits/sec
[  5]   4.00-5.00   sec  22.4 MBytes   188 Mbits/sec
[  5]   5.00-6.00   sec  22.8 MBytes   191 Mbits/sec
[  5]   6.00-7.00   sec  20.8 MBytes   174 Mbits/sec
[  5]   7.00-8.00   sec  20.1 MBytes   168 Mbits/sec
[  5]   8.00-9.00   sec  20.8 MBytes   175 Mbits/sec
[  5]   9.00-10.00  sec  21.8 MBytes   183 Mbits/sec
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-10.00  sec   208 MBytes   175 Mbits/sec                  sender
[  5]   0.00-10.00  sec   208 MBytes   174 Mbits/sec                  receiver

iperf Done.
```

If the output shows low network bandwidth and high bandwidth fluctuations, a large number of retries and EOF errors might appear in each component log. In this case, you need to consult your network service provider to improve the network quality.

If the output of each metric looks good, try to update each component. If the problem persists after the updating, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
### If I accidentally import the MySQL user table into TiDB, or forget the password and cannot log in, how to deal with it?

Restart the TiDB service, add the `-skip-grant-table=true` parameter in the configuration file. Log into the cluster without password and recreate the user, or recreate the `mysql.user` table. For the specific table schema, search the official documentation.
### How to export the data in TiDB?

You can use the following methods to export the data in TiDB:

- Export data using Dumpling. For more information, see [Dumpling documentation](https://docs.pingcap.com/tidb/stable/dumpling-overview).
- Export data using mysqldump and the `WHERE` clause.
- Use the MySQL client to export the results of `select` to a file.
### How to migrate from DB2 or Oracle to TiDB?

To migrate all the data or migrate incrementally from DB2 or Oracle to TiDB, see the following solution:

- Use the official migration tool of Oracle, such as OGG, Gateway, CDC (Change Data Capture).
- Develop a program for importing and exporting data.
- Export Spool as text file, and import data using Load infile.
- Use a third-party data migration tool.

Currently, it is recommended to use OGG.
### Error: `java.sql.BatchUpdateException:statement count 5001 exceeds the transaction limitation` while using Sqoop to write data into TiDB in `batches`

In Sqoop, `--batch` means committing 100 `statement`s in each batch, but by default each `statement` contains 100 SQL statements. So, 100 * 100 = 10000 SQL statements, which exceeds 5000, the maximum number of statements allowed in a single TiDB transaction.

Two solutions:

- Add the `-Dsqoop.export.records.per.statement=10` option as follows:

    ```bash
    sqoop export \
        -Dsqoop.export.records.per.statement=10 \
        --connect jdbc:mysql://mysql.example.com/sqoop \
        --username sqoop ${user} \
        --password ${passwd} \
        --table ${tab_name} \
        --export-dir ${dir} \
        --batch
    ```

- You can also increase the limited number of statements in a single TiDB transaction, but this will consume more memory.
### Why does Dumpling return `The local disk space is insufficient` error or cause the upstream database to run out of memory when exporting a table?

This issue might have the following causes:

+ The database's primary keys are not evenly distributed (for example, when you enable [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits)).
+ The upstream database is TiDB and the exported table is a partitioned table.

For the above cases, Dumpling splits excessively large data chunk for the export and sends queries with excessively large results. To address the issue, you can get the latest version of Dumpling.
### Does TiDB have a function like the Flashback Query in Oracle? Does it support DDL?

 Yes, it does. And it supports DDL as well. For details, see [how TiDB reads data from history versions](https://docs.pingcap.com/tidb/stable/read-historical-data).
