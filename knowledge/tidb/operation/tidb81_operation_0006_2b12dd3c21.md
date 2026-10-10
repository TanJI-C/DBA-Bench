# Sysbench benchmark workflow, data import, warmup, and test commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-tidb-using-sysbench.md`
- Source Title: `How to Test TiDB Using Sysbench`
- Source Heading Path: `How to Test TiDB Using Sysbench > Test process | How to Test TiDB Using Sysbench > Test process > Sysbench configuration | How to Test TiDB Using Sysbench > Test process > Data import | How to Test TiDB Using Sysbench > Test process > Warming data and collecting statistics | How to Test TiDB Using Sysbench > Test process > Point select test command | How to Test TiDB Using Sysbench > Test process > Update index test command | How to Test TiDB Using Sysbench > Test process > Read-only test command`
- Source Line Ranges: `56-166`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `sysbench`, `benchmarking`, `configuration-file`, `data-import`, `transaction-retry`, `prewarm`, `statistics`, `point-select`, `update-index`, `read-only`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0006_2b12dd3c21`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-tidb-using-sysbench.md#test-process`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8891321606ede5815c2d429d551310d1370e74d651f75a94270c14bd1ea5ff00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-sysbench#test-process
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-tidb-using-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the documented Sysbench benchmark workflow, including config file fields, data import steps, optional import optimization, prewarm, and run commands for point select, update index, and read-only tests.
- Retrieval Keywords: sysbench --config-file=config, mysql-host={TIDB_HOST}, threads={8, 16, 32, 64, 128, 256}, set global tidb_disable_txn_auto_retry = off;, create database sbtest;, oltp_common.lua, sysbench 1.0.20, oltp_point_select prepare, prewarm, oltp_point_select --db-ps-mode=auto --rand-type=uniform run, oltp_update_index --db-ps-mode=auto --rand-type=uniform run, oltp_read_only --db-ps-mode=auto --rand-type=uniform run
- Follow-up Guidance: The source notes that the test was performed without load balancing tools such as HAproxy and that different tool versions and parameters might impact performance.
- Classification Note: This is classified as operation because the content gives procedural benchmark steps, commands, and configuration examples for running Sysbench against TiDB.

## Official Source Content

## Test process

> **Note:**
>
> The test in this document was performed without load balancing tools such as HAproxy. We run the Sysbench test on individual TiDB node and added the results up. The load balancing tools and the parameters of different versions might also impact the performance.
### Sysbench configuration

This is an example of the Sysbench configuration file:

```txt
mysql-host={TIDB_HOST}
mysql-port=4000
mysql-user=root
mysql-password=password
mysql-db=sbtest
time=600
threads={8, 16, 32, 64, 128, 256}
report-interval=10
db-driver=mysql
```

The above parameters can be adjusted according to actual needs. Among them, `TIDB_HOST` is the IP address of the TiDB server (because we cannot include multiple addresses in the configuration file), `threads` is the number of concurrent connections in the test, which can be adjusted in "8, 16, 32, 64, 128, 256". When importing data, it is recommended to set threads = 8 or 16. After adjusting `threads`, save the file named **config**.

See the following as a sample **config** file:

```txt
mysql-host=172.16.30.33
mysql-port=4000
mysql-user=root
mysql-password=password
mysql-db=sbtest
time=600
threads=16
report-interval=10
db-driver=mysql
```
### Data import

> **Note:**
>
> If you enable the optimistic transaction model (TiDB uses the pessimistic transaction mode by default), TiDB rolls back transactions when a concurrency conflict is found. Setting `tidb_disable_txn_auto_retry` to `off` turns on the automatic retry mechanism after meeting a transaction conflict, which can prevent Sysbench from quitting because of the transaction conflict error.

Before importing the data, it is necessary to make some settings to TiDB. Execute the following command in MySQL client:

```sql
set global tidb_disable_txn_auto_retry = off;
```

Then exit the client.

Restart MySQL client and execute the following SQL statement to create a database `sbtest`:

```sql
create database sbtest;
```

Adjust the order in which Sysbench scripts create indexes. Sysbench imports data in the order of "Build Table -> Insert Data -> Create Index", which takes more time for TiDB to import data. Users can adjust the order to speed up the import of data. Suppose that you use the Sysbench version [1.0.20](https://github.com/akopytov/sysbench/tree/1.0.20). You can adjust the order in either of the following two ways:

- Download the modified [oltp_common.lua](https://raw.githubusercontent.com/pingcap/tidb-bench/master/sysbench/sysbench-patch/oltp_common.lua) file for TiDB and overwrite the `/usr/share/sysbench/oltp_common.lua` file with it.
- In `/usr/share/sysbench/oltp_common.lua`, move the lines [235-240](https://github.com/akopytov/sysbench/blob/1.0.20/src/lua/oltp_common.lua#L235-L240) to be right behind the line 198.

> **Note:**
>
> This operation is optional and is only to save the time consumed by data import.

At the command line, enter the following command to start importing data. The config file is the one configured in the previous step:

```bash
sysbench --config-file=config oltp_point_select --tables=32 --table-size=10000000 prepare
```
### Warming data and collecting statistics

To warm data, we load data from disk into the block cache of memory. The warmed data has significantly improved the overall performance of the system. It is recommended to warm data once after restarting the cluster.

```bash
sysbench --config-file=config oltp_point_select --tables=32 --table-size=10000000 prewarm
```
### Point select test command

```bash
sysbench --config-file=config oltp_point_select --tables=32 --table-size=10000000 --db-ps-mode=auto --rand-type=uniform run
```
### Update index test command

```bash
sysbench --config-file=config oltp_update_index --tables=32 --table-size=10000000 --db-ps-mode=auto --rand-type=uniform run
```
### Read-only test command

```bash
sysbench --config-file=config oltp_read_only --tables=32 --table-size=10000000 --db-ps-mode=auto --rand-type=uniform run
```
