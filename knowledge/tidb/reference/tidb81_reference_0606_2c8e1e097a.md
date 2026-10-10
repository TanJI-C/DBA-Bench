# LOAD DATA statement syntax, parameters, storage sources, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-load-data.md`
- Source Title: `LOAD DATA | TiDB SQL Statement Reference`
- Source Heading Path: `LOAD DATA | LOAD DATA > Synopsis | LOAD DATA > Parameters | LOAD DATA > Parameters > `LOCAL` | LOAD DATA > Parameters > `REPLACE` and `IGNORE` | LOAD DATA > Parameters > S3 and GCS storage | LOAD DATA > Parameters > `Fields`, `Lines`, and `Ignore Lines` | LOAD DATA > Examples`
- Source Line Ranges: `5-181`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `cloud`, `shared`
- Topic Tags: `load data`, `sql syntax`, `local infile`, `s3`, `gcs`, `duplicate handling`, `field delimiters`, `null parsing`, `ignore lines`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0606_2c8e1e097a`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-load-data.md#load-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0b8c2169c233f3f5313e6795a53f064fe02721e4177aa9aedc0b7d6148f735da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data#load-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-load-data.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the syntax, parameters, storage paths, duplicate handling, field and line format options, NULL parsing rules, TiDB Cloud local infile notes, or examples for the `LOAD DATA` statement.
- Retrieval Keywords: LOAD DATA, LOAD DATA INFILE, LOAD DATA LOCAL INFILE, LocalOpt, DuplicateOpt, FIELDS TERMINATED BY, FIELDS ENCLOSED BY, ESCAPED BY, DEFINED NULL BY, OPTIONALLY ENCLOSED, LINES TERMINATED BY, IGNORE 1 LINES, REPLACE, IGNORE, S3, GCS, external storage, s3://<bucket-name>/path/to/data/*, wildcard character *, ERROR 1148 (42000): the used command is not allowed with this TiDB version, --local-infile, hexadecimal ASCII character expressions, binary ASCII character expressions, x'2c', b'100010'
- Follow-up Guidance: If the user encounters `ERROR 1148 (42000): the used command is not allowed with this TiDB version`, the source says to refer to the error-codes troubleshooting entry for that message.
- Classification Note: This is reference content because the official text defines `LOAD DATA` syntax, parameter behavior, supported file source forms, default parsing rules, and example statements.

## Official Source Content

# LOAD DATA

The `LOAD DATA` statement batch loads data into a TiDB table.

Starting from TiDB v7.0.0, the `LOAD DATA` SQL statement supports the following features:

- Support importing data from S3 and GCS
- Add a new parameter `FIELDS DEFINED NULL BY`

> **Warning:**
>
> The new parameter `FIELDS DEFINED NULL BY` and support for importing data from S3 and GCS are experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

> **Note:**
>
> For the `LOAD DATA INFILE` statement, TiDB Cloud Dedicated supports `LOAD DATA LOCAL INFILE`, and `LOAD DATA INFILE` from Amazon S3 or Google Cloud Storage, while [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) only support `LOAD DATA LOCAL INFILE`.
## Synopsis

```ebnf+diagram
LoadDataStmt ::=
    'LOAD' 'DATA' LocalOpt 'INFILE' stringLit DuplicateOpt 'INTO' 'TABLE' TableName CharsetOpt Fields Lines IgnoreLines ColumnNameOrUserVarListOptWithBrackets LoadDataSetSpecOpt

LocalOpt ::= ('LOCAL')?

DuplicateOpt ::=
    ( 'IGNORE' | 'REPLACE' )?

Fields ::=
    ('TERMINATED' 'BY' stringLit
    | ('OPTIONALLY')? 'ENCLOSED' 'BY' stringLit
    | 'ESCAPED' 'BY' stringLit
    | 'DEFINED' 'NULL' 'BY' stringLit ('OPTIONALLY' 'ENCLOSED')?)?
```
## Parameters
### `LOCAL`

You can use `LOCAL` to specify data files on the client to be imported, where the file parameter must be the file system path on the client.

If you are using TiDB Cloud, to use the `LOAD DATA` statement to load local data files, you need to add the `--local-infile` option to the connection string when you connect to TiDB Cloud.

- The following is an example connection string for {{{ .starter }}}:

    ```
    mysql --connect-timeout 15 -u '<user_name>' -h <host_name> -P 4000 -D test --ssl-mode=VERIFY_IDENTITY --ssl-ca=/etc/ssl/cert.pem -p<your_password> --local-infile
    ```

- The following is an example connection string for TiDB Cloud Dedicated:

    ```
    mysql --connect-timeout 15 --ssl-mode=VERIFY_IDENTITY --ssl-ca=<CA_path> --tls-version="TLSv1.2" -u root -h <host_name> -P 4000 -D test -p<your_password> --local-infile
    ```
### `REPLACE` and `IGNORE`

You can use `REPLACE` and `IGNORE` to specify how duplicate data is handled. 

- `REPLACE`: existing data is overwritten.
- `IGNORE`: duplicate rows are ignored, keeping existing data.

By default, duplicate data leads to errors.
### S3 and GCS storage

If you do not specify `LOCAL`, the file parameter must be a valid S3 or GCS path, as detailed in [external storage](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages).

If you do not specify `LOCAL`, the file parameter must be a valid S3 or GCS path, as detailed in [external storage](https://docs.pingcap.com/tidb/stable/backup-and-restore-storages).

When the data files are stored on S3 or GCS, you can import individual files or use the wildcard character `*` to match multiple files to be imported. Note that wildcards do not recursively process files in subdirectories. The following are some examples:

- Import a single file: `s3://<bucket-name>/path/to/data/foo.csv`
- Import all files in the specified path: `s3://<bucket-name>/path/to/data/*`
- Import all files ending with `.csv` under the specified path: `s3://<bucket-name>/path/to/data/*.csv`
- Import all files prefixed with `foo` under the specified path: `s3://<bucket-name>/path/to/data/foo*`
- Import all files prefixed with `foo` and ending with `.csv` under the specified path: `s3://<bucket-name>/path/to/data/foo*.csv`
### `Fields`, `Lines`, and `Ignore Lines`

You can use the `Fields` and `Lines` parameters to specify how to handle the data format.

- `FIELDS TERMINATED BY`: specifies the data delimiter.
- `FIELDS ENCLOSED BY`: specifies the enclosing character of the data.
- `LINES TERMINATED BY`: specifies the line terminator, if you want to end a line with a certain character.

You can use `DEFINED NULL BY` to specify how NULL values are represented in the data file.

- Consistent with MySQL behavior, if `ESCAPED BY` is not null, for example, if the default value `\` is used, then `\N` will be considered a NULL value.
- If you use `DEFINED NULL BY`, such as `DEFINED NULL BY 'my-null'`, `my-null` is considered a NULL value.
- If you use `DEFINED NULL BY ... OPTIONALLY ENCLOSED`, such as `DEFINED NULL BY 'my-null' OPTIONALLY ENCLOSED`, `my-null` and `"my-null"` (assuming `ENCLOSED BY '"`) are considered NULL values.
- If you do not use `DEFINED NULL BY` or `DEFINED NULL BY ... OPTIONALLY ENCLOSED`, but use `ENCLOSED BY`, such as `ENCLOSED BY '"'`, then `NULL` is considered a NULL value. This behavior is consistent with MySQL.
- In other cases, it is not considered a NULL value.

Take the following data format as an example:

```
"bob","20","street 1"\r\n
"alice","33","street 1"\r\n
```

If you want to extract `bob`, `20`, and `street 1`, specify the field delimiter as `','`, and the enclosing character as `'\"'`:

```sql
FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n'
```

If you do not specify the preceding parameters, the imported data is processed in the following way by default:

```sql
FIELDS TERMINATED BY '\t' ENCLOSED BY '' ESCAPED BY '\\'
LINES TERMINATED BY '\n' STARTING BY ''
```

You can ignore the first `number` lines of a file by configuring the `IGNORE <number> LINES` parameter. For example, if you configure `IGNORE 1 LINES`, the first line of a file is ignored.
## Examples

The following example imports data using `LOAD DATA`. Comma is specified as the field delimiter. The double quotation marks that enclose the data are ignored. The first line of the file is ignored.

If you see `ERROR 1148 (42000): the used command is not allowed with this TiDB version`, refer to [ERROR 1148 (42000): the used command is not allowed with this TiDB version](https://docs.pingcap.com/tidb/stable/error-codes#mysql-native-error-messages) for troubleshooting.

If you see `ERROR 1148 (42000): the used command is not allowed with this TiDB version`, refer to [ERROR 1148 (42000): the used command is not allowed with this TiDB version](https://docs.pingcap.com/tidb/stable/error-codes#mysql-native-error-messages) for troubleshooting.

```sql
LOAD DATA LOCAL INFILE '/mnt/evo970/data-sets/bikeshare-data/2017Q4-capitalbikeshare-tripdata.csv' INTO TABLE trips FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (duration, start_date, end_date, start_station_number, start_station, end_station_number, end_station, bike_number, member_type);
```

```sql
Query OK, 815264 rows affected (39.63 sec)
Records: 815264  Deleted: 0  Skipped: 0  Warnings: 0
```

`LOAD DATA` also supports using hexadecimal ASCII character expressions or binary ASCII character expressions as the parameters for `FIELDS ENCLOSED BY` and `FIELDS TERMINATED BY`. See the following example:

```sql
LOAD DATA LOCAL INFILE '/mnt/evo970/data-sets/bikeshare-data/2017Q4-capitalbikeshare-tripdata.csv' INTO TABLE trips FIELDS TERMINATED BY x'2c' ENCLOSED BY b'100010' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (duration, start_date, end_date, start_station_number, start_station, end_station_number, end_station, bike_number, member_type);
```

In the above example, `x'2c'` is the hexadecimal representation of the `,` character, and `b'100010'` is the binary representation of the `"` character.

The following example shows how to import data into a TiDB Cloud Dedicated cluster from Amazon S3 using the `LOAD DATA INFILE` statement:

```sql
LOAD DATA INFILE 's3://<your-bucket-name>/your-file.csv?role_arn=<The ARN of the IAM role you created for TiDB Cloud import>&external_id=<TiDB Cloud external ID (optional)>'
INTO TABLE <your-db-name>.<your-table-name>
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES;
```
