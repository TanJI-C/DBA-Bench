# Bypass methods for inconsistency checks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-data-inconsistency-errors.md`
- Source Title: `Troubleshoot Inconsistency Between Data and Indexes`
- Source Heading Path: `Troubleshoot Inconsistency Between Data and Indexes > Solutions | Troubleshoot Inconsistency Between Data and Indexes > Solutions > Rewrite SQL | Troubleshoot Inconsistency Between Data and Indexes > Solutions > Disable error checks`
- Source Line Ranges: `85-114`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `bypass-checks`, `sql-rewrite`, `session-variables`, `mutation-checker`, `txn-assertion`, `support-guidance`, `admin-check`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0526_14b22e0b2b`
- Source ID: `tidb-docs-8.1:troubleshoot-data-inconsistency-errors.md#solutions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47077a1ccacc18ca8221efa33f22468f39a28006f98e474e8bd885584c0e5a84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-data-inconsistency-errors#solutions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-data-inconsistency-errors.md

## Retrieval Guidance

- Use When: Use this when you need the documented ways to bypass certain data inconsistency checks, including specific session variables and the note about which checks cannot be bypassed.
- Retrieval Keywords: Solutions, Rewrite SQL, Disable error checks, set @@tidb_enable_mutation_checker=0, set @@tidb_txn_assertion_level=OFF, ERROR 8138, ERROR 8139, ERROR 8140, ERROR 8141, ADMIN CHECK [TABLE|INDEX], bypass the check, equivalent form
- Follow-up Guidance: If the inconsistency is limited to one SQL statement, the document says you can rewrite the SQL to an equivalent form using different execution operators.
- Classification Note: This is an operation section that describes support guidance, SQL rewriting, and session variables for bypassing some inconsistency checks.

## Official Source Content

## Solutions

If you encounter a data inconsistency error, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP for troubleshooting immediately instead of dealing with the error by yourself. If your application needs to skip such errors urgently, you can use the following methods to bypass the check.

If you encounter a data inconsistency error, [contact TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support) for troubleshooting immediately instead of dealing with the error by yourself. If your application needs to skip such errors urgently, you can use the following methods to bypass the check.
### Rewrite SQL

If the data inconsistency error occurs in a particular SQL statement only, you can bypass this error by rewriting the SQL statement to another equivalent form using different execution operators.
### Disable error checks

For the following errors reported in transaction execution, you can bypass the corresponding checks:

- To bypass the checks of errors 8138, 8139, and 8140, configure `set @@tidb_enable_mutation_checker=0`.
- To bypass the checks of error 8141, configure `set @@tidb_txn_assertion_level=OFF`.

> **Note:**
>
> Disabling `tidb_enable_mutation_checker` and `tidb_txn_assertion_level` will bypass the corresponding checks of all SQL statements.

For other errors reported in transaction execution and all errors reported during the execution of the [`ADMIN CHECK [TABLE|INDEX]`](/sql-statements/sql-statement-admin-check-table-index.md) statement, you cannot bypass the corresponding check, because the data is already inconsistent.
