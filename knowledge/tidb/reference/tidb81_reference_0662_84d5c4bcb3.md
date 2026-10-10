# SHOW IMPORT syntax, privileges, output columns, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-show-import-job.md`
- Source Title: `SHOW IMPORT`
- Source Heading Path: `SHOW IMPORT | SHOW IMPORT > Required privileges | SHOW IMPORT > Synopsis | SHOW IMPORT > Example | SHOW IMPORT > MySQL compatibility | SHOW IMPORT > See also`
- Source Line Ranges: `5-78`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `show import`, `import jobs`, `privileges`, `syntax`, `output columns`, `job status`, `mysql compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0662_84d5c4bcb3`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-show-import-job.md#show-import`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8d9eed0c1426f088ef15fdd358321ff129cead275a1ab64be686ed378294eaed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-import-job#show-import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-show-import-job.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to view IMPORT jobs or a specific IMPORT job in TiDB, including required privileges, syntax, result columns, statuses, phases, or example output.
- Retrieval Keywords: SHOW IMPORT, SHOW IMPORT JOBS, SHOW IMPORT JOB <job-id>, SHOW IMPORT JOB 60001, SHOW IMPORT syntax, Required privileges, SUPER privilege, current user, Job_ID, Data_Source, Target_Table, Phase, importing, validating, add-index, Status, pending, running, canceled, failed, finished, Source_File_Size, Imported_Rows, Result_Message, Create_Time, Start_Time, End_Time, Created_By, TiDB extension to MySQL syntax
- Follow-up Guidance: The source also points to related statements `IMPORT INTO` and `CANCEL IMPORT JOB`.
- Classification Note: This is reference content because it defines the `SHOW IMPORT` statement with privilege rules, formal syntax, output field meanings, examples, and MySQL compatibility notes.

## Official Source Content

# SHOW IMPORT

The `SHOW IMPORT` statement is used to show the IMPORT jobs created in TiDB. This statement can only show jobs created by the current user.
## Required privileges

- `SHOW IMPORT JOBS`: if a user has the `SUPER` privilege, this statement shows all import jobs in TiDB. Otherwise, this statement only shows jobs created by the current user.
- `SHOW IMPORT JOB <job-id>`: only the creator of an import job or users with the `SUPER` privilege can use this statement to view a specific job.
## Synopsis

```ebnf+diagram
ShowImportJobsStmt ::=
    'SHOW' 'IMPORT' 'JOBS'

ShowImportJobStmt ::=
    'SHOW' 'IMPORT' 'JOB' JobID
```

The output fields of the `SHOW IMPORT` statement are described as follows:

| Column           | Description             |
|------------------|-------------------------|
| Job_ID           | The ID of the task                  |
| Data_Source      | Information about the data source                  |
| Target_Table     | The name of the target table                     |
| Phase            | The current phase of the job, including `importing`, `validating`, and `add-index` |
| Status           | The current status of the job, including `pending` (means created but not started yet), `running`, `canceled`, `failed`, and `finished` |
| Source_File_Size | The size of the source file  |
| Imported_Rows | The number of data rows that have been read and written to the target table  |
| Result_Message   | If the import fails, this field returns the error message. Otherwise, it is empty.|
| Create_Time      | The time when the task is created                 |
| Start_Time       | The time when the task is started                     |
| End_Time         | The time when the task is ended            |
| Created_By       | The name of the database user who creates the task         |
## Example

```sql
SHOW IMPORT JOBS;
```

```
+--------+-------------------+--------------+----------+-------+----------+------------------+---------------+----------------+----------------------------+----------------------------+----------------------------+------------+
| Job_ID | Data_Source       | Target_Table | Table_ID | Phase | Status   | Source_File_Size | Imported_Rows | Result_Message | Create_Time                | Start_Time                 | End_Time                   | Created_By |
+--------+-------------------+--------------+----------+-------+----------+------------------+---------------+----------------+----------------------------+----------------------------+----------------------------+------------+
|      1 | /path/to/file.csv | `test`.`foo` |      116 |       | finished | 11GB             |        950000 |                | 2023-06-26 11:23:59.281257 | 2023-06-26 11:23:59.484932 | 2023-06-26 13:04:30.622952 | root@%     |
|      2 | /path/to/file.csv | `test`.`bar` |      130 |       | finished | 1.194TB          |      49995000 |                | 2023-06-26 15:42:45.079237 | 2023-06-26 15:42:45.388108 | 2023-06-26 17:29:43.023568 | root@%     |
+--------+-------------------+--------------+----------+-------+----------+------------------+---------------+----------------+----------------------------+----------------------------+----------------------------+------------+
1 row in set (0.01 sec)
```

```sql
SHOW IMPORT JOB 60001;
```

```
+--------+--------------------+--------------+----------+-------+---------+------------------+---------------+----------------+----------------------------+------------+----------+------------+
| Job_ID | Data_Source        | Target_Table | Table_ID | Phase | Status  | Source_File_Size | Imported_Rows | Result_Message | Create_Time                | Start_Time | End_Time | Created_By |
+--------+--------------------+--------------+----------+-------+---------+------------------+---------------+----------------+----------------------------+------------+----------+------------+
|  60001 | /path/to/small.csv | `test`.`t`   |      361 |       | pending | 16B              |          NULL |                | 2023-06-08 15:59:37.047703 | NULL       | NULL     | root@%     |
+--------+--------------------+--------------+----------+-------+---------+------------------+---------------+----------------+----------------------------+------------+----------+------------+
1 row in set (0.01 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into)
* [`CANCEL IMPORT JOB`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-cancel-import-job)
