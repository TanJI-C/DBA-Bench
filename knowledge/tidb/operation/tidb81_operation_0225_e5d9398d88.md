# IMPORT INTO FROM FILE output, job management, and examples

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-import-into.md`
- Source Title: `IMPORT INTO`
- Source Heading Path: `IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Output | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > View and manage import jobs | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Import a CSV file with headers | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Import a file asynchronously in the `DETACHED` mode | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Skip importing a specific field in your data file | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Import multiple data files using wildcards | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Import data files from Amazon S3 or GCS | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Calculate column values using SetClause | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Import a data file in the SQL format | IMPORT INTO > `IMPORT INTO ... FROM FILE` usage > Examples > Limit the write speed to TiKV`
- Source Line Ranges: `216-337`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `cloud`
- Topic Tags: `detached-mode`, `job-output`, `show-import`, `cancel-import-job`, `csv`, `wildcards`, `s3`, `gcs`, `set-clause`, `sql-format`, `write-speed-limit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0225_e5d9398d88`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-import-into.md#output`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `88b31e2bcd5baa0a136d5623aad92de3e2141505b6f17ee7c31e23675b17e3b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#output
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-import-into.md

## Retrieval Guidance

- Use When: Use this chunk when looking for `IMPORT INTO ... FROM FILE` job output fields, `DETACHED` mode behavior, import job inspection or cancellation, or example statements for CSV, wildcards, S3, GCS, SetClause, SQL format, and `MAX_WRITE_SPEED`.
- Retrieval Keywords: IMPORT INTO ... FROM FILE, DETACHED, SHOW IMPORT, SHOW IMPORT JOB, CANCEL IMPORT JOB <job-id>, skip_rows=1, wildcards, file-*.csv, file-0[13].csv, s3://bucket-name/test.csv, gs://import/test.csv, SET val=@1*100, FORMAT 'sql', FORMAT 'parquet', MAX_WRITE_SPEED='10MiB', job output, pending, finished
- Follow-up Guidance: The source provides example SQL for viewing progress with `SHOW IMPORT` and canceling a started job with `CANCEL IMPORT JOB <job-id>`.
- Classification Note: This is classified as operation content because it covers job output, asynchronous execution, job management, and concrete import command examples.

## Official Source Content

### Output

When `IMPORT INTO ... FROM FILE` completes the import or when the `DETACHED` mode is enabled, TiDB returns the current job information in the output, as shown in the following examples. For the description of each field, see [`SHOW IMPORT JOB(s)`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-import-job).

When `IMPORT INTO ... FROM FILE` completes the import, the example output is as follows:

```sql
IMPORT INTO t FROM '/path/to/small.csv';
+--------+--------------------+--------------+----------+-------+----------+------------------+---------------+----------------+----------------------------+----------------------------+----------------------------+------------+
| Job_ID | Data_Source        | Target_Table | Table_ID | Phase | Status   | Source_File_Size | Imported_Rows | Result_Message | Create_Time                | Start_Time                 | End_Time                   | Created_By |
+--------+--------------------+--------------+----------+-------+----------+------------------+---------------+----------------+----------------------------+----------------------------+----------------------------+------------+
|  60002 | /path/to/small.csv | `test`.`t`   |      363 |       | finished | 16B              |             2 |                | 2023-06-08 16:01:22.095698 | 2023-06-08 16:01:22.394418 | 2023-06-08 16:01:26.531821 | root@%     |
+--------+--------------------+--------------+----------+-------+----------+------------------+---------------+----------------+----------------------------+----------------------------+----------------------------+------------+
```

When the `DETACHED` mode is enabled, executing the `IMPORT INTO ... FROM FILE` statement will immediately return the job information in the output. From the output, you can see that the status of the job is `pending`, which means waiting for execution.

```sql
IMPORT INTO t FROM '/path/to/small.csv' WITH DETACHED;
+--------+--------------------+--------------+----------+-------+---------+------------------+---------------+----------------+----------------------------+------------+----------+------------+
| Job_ID | Data_Source        | Target_Table | Table_ID | Phase | Status  | Source_File_Size | Imported_Rows | Result_Message | Create_Time                | Start_Time | End_Time | Created_By |
+--------+--------------------+--------------+----------+-------+---------+------------------+---------------+----------------+----------------------------+------------+----------+------------+
|  60001 | /path/to/small.csv | `test`.`t`   |      361 |       | pending | 16B              |          NULL |                | 2023-06-08 15:59:37.047703 | NULL       | NULL     | root@%     |
+--------+--------------------+--------------+----------+-------+---------+------------------+---------------+----------------+----------------------------+------------+----------+------------+
```
### View and manage import jobs

For an import job with the `DETACHED` mode enabled, you can use [`SHOW IMPORT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-import-job) to view its current job progress.

After an import job is started, you can cancel it using [`CANCEL IMPORT JOB <job-id>`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-cancel-import-job).
### Examples
#### Import a CSV file with headers

```sql
IMPORT INTO t FROM '/path/to/file.csv' WITH skip_rows=1;
```
#### Import a file asynchronously in the `DETACHED` mode

```sql
IMPORT INTO t FROM '/path/to/file.csv' WITH DETACHED;
```
#### Skip importing a specific field in your data file

Assume that your data file is in the CSV format and its content is as follows:

```
id,name,age
1,Tom,23
2,Jack,44
```

And assume that the target table schema for the import is `CREATE TABLE t(id int primary key, name varchar(100))`. To skip importing the `age` field in the data file to the table `t`, you can execute the following SQL statement:

```sql
IMPORT INTO t(id, name, @1) FROM '/path/to/file.csv' WITH skip_rows=1;
```
#### Import multiple data files using wildcards

Assume that there are three files named `file-01.csv`, `file-02.csv`, and `file-03.csv` in the `/path/to/` directory. To import these three files into a target table `t` using `IMPORT INTO`, you can execute the following SQL statement:

```sql
IMPORT INTO t FROM '/path/to/file-*.csv';
```

If you only need to import `file-01.csv` and `file-03.csv` into the target table, execute the following SQL statement:

```sql
IMPORT INTO t FROM '/path/to/file-0[13].csv';
```
#### Import data files from Amazon S3 or GCS

- Import data files from Amazon S3:

    ```sql
    IMPORT INTO t FROM 's3://bucket-name/test.csv?access-key=XXX&secret-access-key=XXX';
    ```

- Import data files from GCS:

    ```sql
    IMPORT INTO t FROM 'gs://import/test.csv?credentials-file=${credentials-file-path}';
    ```

For details about the URI path configuration for Amazon S3 or GCS, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
#### Calculate column values using SetClause

Assume that your data file is in the CSV format and its content is as follows:

```
id,name,val
1,phone,230
2,book,440
```

And assume that the target table schema for the import is `CREATE TABLE t(id int primary key, name varchar(100), val int)`. If you want to multiply the `val` column values by 100 during the import, you can execute the following SQL statement:

```sql
IMPORT INTO t(id, name, @1) SET val=@1*100 FROM '/path/to/file.csv' WITH skip_rows=1;
```
#### Import a data file in the SQL format

```sql
IMPORT INTO t FROM '/path/to/file.sql' FORMAT 'sql';
```
#### Limit the write speed to TiKV

To limit the write speed to a TiKV node to 10 MiB/s, execute the following SQL statement:

```sql
IMPORT INTO t FROM 's3://bucket/path/to/file.parquet?access-key=XXX&secret-access-key=XXX' FORMAT 'parquet' WITH MAX_WRITE_SPEED='10MiB';
```
