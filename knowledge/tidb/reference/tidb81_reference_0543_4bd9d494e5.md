# CANCEL IMPORT statement syntax, privileges, example, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-cancel-import-job.md`
- Source Title: `CANCEL IMPORT`
- Source Heading Path: `CANCEL IMPORT | CANCEL IMPORT > Required privileges | CANCEL IMPORT > Synopsis | CANCEL IMPORT > Example | CANCEL IMPORT > MySQL compatibility | CANCEL IMPORT > See also`
- Source Line Ranges: `5-42`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `import`, `job-cancellation`, `privileges`, `syntax`, `example`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0543_4bd9d494e5`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-cancel-import-job.md#cancel-import`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `830b92c29a26332e5cb22a72c35820348e545cf6a82ccf7da30f9f20d736dd5f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-cancel-import-job#cancel-import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-cancel-import-job.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, privilege requirement, example, or MySQL compatibility note for cancelling a TiDB data import job.
- Retrieval Keywords: CANCEL IMPORT, CANCEL IMPORT JOB, CancelImportJobsStmt, JobID, SUPER privilege, creator of the import job, cancel a data import job, CANCEL IMPORT JOB 1, TiDB extension to MySQL syntax, SHOW IMPORT JOB, IMPORT INTO
- Follow-up Guidance: The source also points to `IMPORT INTO` and `SHOW IMPORT JOB` as related statements.
- Classification Note: The classification is reference because the content defines the `CANCEL IMPORT` statement with required privileges, EBNF synopsis, an example, and a compatibility note.

## Official Source Content

# CANCEL IMPORT

The `CANCEL IMPORT` statement is used to cancel a data import job created in TiDB.
## Required privileges

To cancel a data import job, you need to be the creator of the import job or have the `SUPER` privilege.
## Synopsis

```ebnf+diagram
CancelImportJobsStmt ::=
    'CANCEL' 'IMPORT' 'JOB' JobID
```
## Example

To cancel an import job with the ID as `1`, execute the following statement:

```sql
CANCEL IMPORT JOB 1;
```

The output is as follows:

```
Query OK, 0 rows affected (0.01 sec)
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into)
* [`SHOW IMPORT JOB`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-import-job)
