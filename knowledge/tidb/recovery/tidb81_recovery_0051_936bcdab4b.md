# Reparo usage, parameters, configuration, and recovery start example

## Knowledge Metadata

- Knowledge Type: `recovery`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-reparo.md`
- Source Title: `Reparo User Guide`
- Source Heading Path: `Reparo User Guide | Reparo User Guide > Reparo usage | Reparo User Guide > Reparo usage > Description of command line parameters | Reparo User Guide > Reparo usage > Description of the configuration file | Reparo User Guide > Reparo usage > Start example`
- Source Line Ranges: `5-133`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `reparo`, `tidb-binlog`, `incremental-recovery`, `binlog`, `command-line-parameters`, `configuration-file`, `safe-mode`, `start-tso`, `stop-tso`, `mysql-output`, `print-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_recovery_0051_936bcdab4b`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-reparo.md#reparo-user-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `956f34a28d8b9101633c9e705791c0467d4030786925fdf4748583c82888f940`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-reparo#reparo-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-reparo.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to run Reparo for incremental data recovery from Drainer protobuf binlog files, including command-line parameters, configuration file fields, and a basic startup example.
- Retrieval Keywords: Reparo User Guide, reparo, TiDB Binlog, recover the incremental data, Drainer, protobuf format, data-dir, dest-type, print, mysql, start-datetime, stop-datetime, start-tso, stop-tso, safe-mode, txn-batch, worker-count, replicate-do-db, replicate-do-table, dest-db, host, port, user, password, ./reparo -config reparo.toml
- Follow-up Guidance: The source also states that `start-datetime`/`stop-datetime` and `start-tso`/`stop-tso` specify the recovery range, `dest-type` can be `mysql` or `print`, and `[dest-db]` is required only when `dest-type` is `mysql`.
- Classification Note: This is classified as recovery for the ecosystem component because the content defines Reparo usage for restoring incremental binlog data into TiDB/MySQL from files output by Drainer.

## Official Source Content

# Reparo User Guide

Reparo is a TiDB Binlog tool, used to recover the incremental data. To back up the incremental data, you can use Drainer of TiDB Binlog to output the binlog data in the protobuf format to files. To restore the incremental data, you can use Reparo to parse the binlog data in the files and apply the binlog in TiDB/MySQL.

The Reparo installation package (`reparo`) is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).
## Reparo usage
### Description of command line parameters

```
Usage of Reparo:
-L string
    The level of the output information of logs
    Value: "debug"/"info"/"warn"/"error"/"fatal" ("info" by default)
-V Prints the version.
-c int
    The number of concurrencies in the downstream for the replication process (`16` by default). A higher value indicates a better throughput for the replication.
-config string
    The path of the configuration file
    If the configuration file is specified, Reparo reads the configuration data in this file.
    If the configuration data also exists in the command line parameters, Reparo uses the configuration data in the command line parameters to cover that in the configuration file.
-data-dir string
    The storage directory for the binlog file in the protobuf format that Drainer outputs ("data.drainer" by default)
-dest-type string
    The downstream service type
    Value: "print"/"mysql" ("print" by default)
    If it is set to "print", the data is parsed and printed to standard output while the SQL statement is not executed.
    If it is set to "mysql", you need to configure the "host", "port", "user" and "password" information in the configuration file.
-log-file string
    The path of the log file
-log-rotate string
    The switch frequency of log files
    Value: "hour"/"day"
-start-datetime string
    Specifies the time point for starting recovery.
    Format: "2006-01-02 15:04:05"
    If it is not set, the recovery process starts from the earliest binlog file.
-stop-datetime string
    Specifies the time point of finishing the recovery process.
    Format: "2006-01-02 15:04:05"
    If it is not set, the recovery process ends up with the last binlog file.
-safe-mode bool
    Specifies whether to enable safe mode. When enabled, it supports repeated replication.
-txn-batch int
    The number of SQL statements in a transaction that is output to the downstream database (`20` by default).
```
### Description of the configuration file

```toml
# The storage directory for the binlog file in the protobuf format that Drainer outputs
data-dir = "./data.drainer"

# The level of the output information of logs
# Value: "debug"/"info"/"warn"/"error"/"fatal" ("info" by default)
log-level = "info"

# Uses `start-datetime` and `stop-datetime` to specify the time range in which
# the binlog files are to be recovered.
# Format: "2006-01-02 15:04:05"
# start-datetime = ""
# stop-datetime = ""

# Correspond to `start-datetime` and `stop-datetime` respectively.
# They are used to specify the time range in which the binlog files are to be recovered.
# If `start-datetime` and `stop-datetime` are set, there is no need to set `start-tso` and `stop-tso`.
# When you perform a full recovery or resume an incremental recovery, set start-tso to tso + 1 or stop-tso + 1, respectively.
# start-tso = 0
# stop-tso = 0

# The downstream service type
# Value: "print"/"mysql" ("print" by default)
# If it is set to "print", the data is parsed and printed to standard output
# while the SQL statement is not executed.
# If it is set to "mysql", you need to configure `host`, `port`, `user` and `password` in [dest-db].
dest-type = "mysql"

# The number of SQL statements in a transaction that is output to the downstream database (`20` by default).
txn-batch = 20

# The number of concurrencies in the downstream for the replication process (`16` by default). A higher value indicates a better throughput for the replication.
worker-count = 16

# Safe-mode configuration
# Value: "true"/"false" ("false" by default)
# If it is set to "true", Reparo splits the `UPDATE` statement into a `DELETE` statement plus a `REPLACE` statement.
safe-mode = false

# `replicate-do-db` and `replicate-do-table` specify the database and table to be recovered.
# `replicate-do-db` has priority over `replicate-do-table`.
# You can use a regular expression for configuration. The regular expression should start with "~".
# The configuration method for `replicate-do-db` and `replicate-do-table` is
# the same with that for `replicate-do-db` and `replicate-do-table` of Drainer.
# replicate-do-db = ["~^b.*","s1"]
# [[replicate-do-table]]
# db-name ="test"
# tbl-name = "log"
# [[replicate-do-table]]
# db-name ="test"
# tbl-name = "~^a.*"

# If `dest-type` is set to `mysql`, `dest-db` needs to be configured.
[dest-db]
host = "127.0.0.1"
port = 3309
user = "root"
password = ""
```
### Start example

```
./reparo -config reparo.toml
```

> **Note:**
>
> * `data-dir` specifies the directory for the binlog file that Drainer outputs.
> * Both `start-datatime` and `start-tso` are used to specify the time point for starting recovery, but they are different in the time format. If they are not set, the recovery process starts from the earliest binlog file by default.
> * Both `stop-datetime` and `stop-tso` are used to specify the time point for finishing recovery, but they are different in the time format. If they are not set, the recovery process ends up with the last binlog file by default.
> * `dest-type` specifies the destination type. Its value can be "mysql" and "print."
>
>     * When it is set to `mysql`, the data can be recovered to MySQL or TiDB that uses or is compatible with the MySQL protocol. In this case, you need to specify the database information in `[dest-db]` of the configuration information.
>     * When it is set to `print`, only the binlog information is printed. It is generally used for debugging and checking the binlog information. In this case, there is no need to specify `[dest-db]`.
>
> * `replicate-do-db` specifies the database for recovery. If it is not set, all the databases are to be recovered.
> * `replicate-do-table` specifies the table for recovery. If it is not set, all the tables are to be recovered.
