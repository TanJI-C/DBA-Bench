# TiDB Control installation and core schema decoding commands

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-control.md`
- Source Title: `TiDB Control User Guide`
- Source Heading Path: `TiDB Control User Guide | TiDB Control User Guide > Get TiDB Control | TiDB Control User Guide > Get TiDB Control > Install TiDB Control using TiUP | TiDB Control User Guide > Get TiDB Control > Compile from source code | TiDB Control User Guide > Usage introduction | TiDB Control User Guide > Usage introduction > Get help | TiDB Control User Guide > Usage introduction > Global options | TiDB Control User Guide > Usage introduction > The `schema` command | TiDB Control User Guide > Usage introduction > The `schema` command > The `in` subcommand | TiDB Control User Guide > Usage introduction > The `schema` command > The `tid` subcommand | TiDB Control User Guide > Usage introduction > The `schema` command > The `base64decode` command | TiDB Control User Guide > Usage introduction > The `decoder` command`
- Source Line Ranges: `5-257`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `tiup`
- Topic Tags: `debugging`, `installation`, `source-build`, `usage`, `help`, `global-options`, `schema`, `table-id`, `base64`, `key-decoding`, `tls`, `status-port`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0931_99896b80fc`
- Source ID: `tidb-docs-8.1:tidb-control.md#tidb-control-user-guide`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d5e2c6fa7a690d0a1679e9e64589a2ae0c436636813359e6ee976c8032084816`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-control#tidb-control-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-control.md

## Retrieval Guidance

- Use When: Use this when looking for how to obtain or use TiDB Control for debugging, including installation, global connection options, schema lookup, base64 decoding, or key decoding commands.
- Retrieval Keywords: TiDB Control, tidb-ctl, tiup ctl:v<CLUSTER_VERSION> tidb, make, make doc, tidb-ctl -h, --host, --port, --pdhost, --pdport, --ca, --ssl-key, --ssl-cert, tidb-ctl schema in, tidb-ctl schema tid -i, table_id, base64decode, decoder, http://$IP:10080/mvcc/index, http://$IP:10080/mvcc/key
- Follow-up Guidance: The content also shows that `schema` has `in` and `tid` subcommands, `base64decode` can decode handle id or row data using `db_name.table_name` or `table_id`, and `decoder` examples decode a row key and an index value.
- Classification Note: This is classified as reference because the official content mainly lists TiDB Control commands, options, installation methods, and example outputs for schema and decoding usage.

## Official Source Content

# TiDB Control User Guide

TiDB Control is a command-line tool of TiDB, usually used to obtain the status information of TiDB for debugging. This document introduces the features of TiDB Control and how to use these features.

> **Note:**
>
> TiDB Control is specifically designed for debugging purposes and might not be fully compatible with future capabilities introduced in TiDB. It's not recommended to include this tool in applications or utilities development to get information.
## Get TiDB Control

You can get TiDB Control by installing it using TiUP or by compiling it from source code.

> **Note:**
>
> It is recommended that the version of the Control tool you use is consistent with the version of the cluster.
### Install TiDB Control using TiUP

After installing TiUP, you can use `tiup ctl:v<CLUSTER_VERSION> tidb` command to get and execute TiDB Control.
### Compile from source code

- Compilation environment requirement: [Go](https://golang.org/) 1.21 or later
- Compilation procedures: Go to the root directory of the [TiDB Control project](https://github.com/pingcap/tidb-ctl), use the `make` command to compile, and generate `tidb-ctl`.
- Compilation documentation: you can find the help files in the `doc` directory; if the help files are lost or you want to update them, use the `make doc` command to generate the help files.
## Usage introduction

This section describes how to use commands, subcommands, options, and flags in `tidb-ctl`.

- command: characters without `-` or `--`
- subcommand: characters without `-` or `--` that follow a command
- option: characters with `-` or `--`
- flag: characters exactly following a command/subcommand or option, passing value to the command/subcommand or option

Usage example: `tidb-ctl schema in mysql -n db`

- `schema`: the command
- `in`: the subcommand of `schema`
- `mysql`: the flag of `in`
- `-n`: the option
- `db`: the flag of `-n`

Currently, TiDB Control has the following subcommands:

- `tidb-ctl base64decode`: used for `BASE64` decoding
- `tidb-ctl decoder`: used for `KEY` decoding
- `tidb-ctl etcd`: used for operating etcd
- `tidb-ctl log`: used to format the log file to expand the single-line stack information
- `tidb-ctl mvcc`: used to get the MVCC information
- `tidb-ctl region`: used to get the Region information
- `tidb-ctl schema`: used to get the schema information
- `tidb-ctl table`: used to get the table information
### Get help

Use `tidb-ctl -h/--help` to get usage information.

TiDB Control consists of multiple layers of commands. You can use `-h/--help` after each command/subcommand to get its respective usage information.

The following example shows how to obtain the schema information:

Use `tidb-ctl schema -h` to get usage details. The `schema` command itself has two subcommands: `in` and `tid`.

- `in` is used to obtain the table schema of all tables in the database through the database name.
- `tid` is used to obtain the table schema by using the unique `table_id` in the whole database.
### Global options

`tidb-ctl` has the following connection-related global options:

- `--host`: TiDB Service address (default 127.0.0.1)
- `--port`: TiDB status port (default 10080)
- `--pdhost`: PD Service address (default 127.0.0.1)
- `--pdport`: PD Service port (default 2379)
- `--ca`: The CA file path used for the TLS connection
- `--ssl-key`: The key file path used for the TLS connection
- `--ssl-cert`: The certificate file path used for the TLS connection

`--pdhost` and `--pdport` are mainly used in the `etcd` subcommand. For example, `tidb-ctl etcd ddlinfo`. If you do not specify the address and the port, the following default value is used:

- The default service address of TiDB and PD: `127.0.0.1`. The service address must be an IP address.
- The default service port of TiDB: `10080`.
- The default service port of PD: `2379`.
### The `schema` command
#### The `in` subcommand

`in` is used to obtain the table schema of all tables in the database through the database name.

```bash
tidb-ctl schema in <database name>
```

For example, running `tidb-ctl schema in mysql` returns the following result:

```json
[
    {
        "id": 13,
        "name": {
            "O": "columns_priv",
            "L": "columns_priv"
        },
              ...
        "update_timestamp": 399494726837600268,
        "ShardRowIDBits": 0,
        "Partition": null
    }
]
```

The result is displayed in the JSON format. (The above output is truncated.)

- If you want to specify the table name, use `tidb-ctl schema in <database> -n <table name>` to filter.

    For example, `tidb-ctl schema in mysql -n db` returns the table schema of the `db` table in the `mysql` database:

    ```json
    {
        "id": 9,
        "name": {
            "O": "db",
            "L": "db"
        },
        ...
        "Partition": null
    }
    ```

    (The above output is also truncated.)

    If you do not want to use the default TiDB service address and port, use the `--host` and `--port` options to configure. For example, `tidb-ctl --host 172.16.55.88 --port 8898 schema in mysql -n db`.
#### The `tid` subcommand

`tid` is used to obtain the table schema by using the unique `table_id` in the whole database. You can use the `in` subcommand to get all table IDs of certain schema and use the `tid` subcommand to get the detailed table information.

For example, the table ID of `mysql.stat_meta` is `21`. You can use `tidb-ctl schema tid -i 21` to obtain the detail of `mysql.stat_meta`.

```json
{
 "id": 21,
 "name": {
  "O": "stats_meta",
  "L": "stats_meta"
 },
 "charset": "utf8mb4",
 "collate": "utf8mb4_bin",
  ...
}
```

Like the `in` subcommand, if you do not want to use the default TiDB service address and status port, use the `--host` and `--port` options to specify the host and port.
#### The `base64decode` command

`base64decode` is used to decode `base64` data.

```shell
tidb-ctl base64decode [base64_data]
tidb-ctl base64decode [db_name.table_name] [base64_data]
tidb-ctl base64decode [table_id] [base64_data]
```

1. Execute the following SQL statement to prepare the environment:

    ```sql
    use test;
    create table t (a int, b varchar(20),c datetime default current_timestamp , d timestamp default current_timestamp, unique index(a));
    insert into t (a,b,c) values(1,"哈哈 hello",NULL);
    alter table t add column e varchar(20);
    ```

2. Obtain MVCC data using the HTTP API interface:

    ```shell
    $ curl "http://$IP:10080/mvcc/index/test/t/a/1?a=1"
    {
     "info": {
      "writes": [
       {
        "start_ts": 407306449994645510,
        "commit_ts": 407306449994645513,
        "short_value": "AAAAAAAAAAE="    # The unique index a stores the handle id of the corresponding row.
       }
      ]
     }
    }%

    $ curl "http://$IP:10080/mvcc/key/test/t/1"
    {
     "info": {
      "writes": [
       {
        "start_ts": 407306588892692486,
        "commit_ts": 407306588892692489,
        "short_value": "CAIIAggEAhjlk4jlk4ggaGVsbG8IBgAICAmAgIDwjYuu0Rk="  # Row data that handle id is 1.
       }
      ]
     }
    }%
    ```

3. Decode ```handle id (uint64) using `base64decode` ```.

    ```shell
    $ tidb-ctl base64decode AAAAAAAAAAE=
    hex: 0000000000000001
    uint64: 1
    ```

4. Decode row data using `base64decode`.

    ```shell
    $ ./tidb-ctl base64decode test.t CAIIAggEAhjlk4jlk4ggaGVsbG8IBgAICAmAgIDwjYuu0Rk=
    a:      1
    b:      哈哈 hello
    c is NULL
    d:      2019-03-28 05:35:30
    e not found in data

    # if the table id of test.t is 60, you can also use below command to do the same thing.
    $ ./tidb-ctl base64decode 60 CAIIAggEAhjlk4jlk4ggaGVsbG8IBgAICAmAgIDwjYuu0Rk=
    a:      1
    b:      哈哈 hello
    c is NULL
    d:      2019-03-28 05:35:30
    e not found in data
    ```
### The `decoder` command

- The following example shows how to decode the row key, similar to decoding the index key.

    ```shell
    $ ./tidb-ctl decoder "t\x00\x00\x00\x00\x00\x00\x00\x1c_r\x00\x00\x00\x00\x00\x00\x00\xfa"
    format: table_row
    table_id: -9223372036854775780      table_id: -9223372036854775780
    row_id: -9223372036854775558        row_id: -9223372036854775558
    ```

- The following example shows how to decode `value`.

    ```shell
    $ ./tidb-ctl decoder AhZoZWxsbyB3b3JsZAiAEA==
    format: index_value
    type: bigint, value: 1024       index_value[0]: {type: bytes, value: hello world}
    index_value[1]: {type: bigint, value: 1024}
    ```
