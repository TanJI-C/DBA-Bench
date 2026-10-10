# IMPORT INTO with log backup and TiCDC scenarios

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-compatibility-and-scenarios.md`
- Source Title: `Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup`
- Source Heading Path: `Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for `IMPORT INTO` | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for `IMPORT INTO` > Used with log backup | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for `IMPORT INTO` > Used with TiCDC`
- Source Line Ranges: `56-78`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `br`, `ticdc`, `tidb`
- Topic Tags: `import-into`, `log-backup`, `pitr`, `ticdc`, `changefeed`, `disable-precheck`, `snapshot-backup`, `downstream-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0452_64afea22cb`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-compatibility-and-scenarios.md#scenarios-for-import-into`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a00b2fdfc6535ed1abfea32e5d5d2b82dc8b4cd96de3278f38e852ea4a47aa1b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-compatibility-and-scenarios#scenarios-for-import-into
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-compatibility-and-scenarios.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented `IMPORT INTO` scenarios with log backup or TiCDC, especially compatibility check errors, `DISABLE_PRECHECK` in `WithOptions`, and what to do for downstream replication scenarios.
- Retrieval Keywords: IMPORT INTO with log backup, IMPORT INTO with TiCDC, PITR enabled compatibility check will report an error, DISABLE_PRECHECK, WithOptions, IMPORT INTO cannot be backed up via log backup, table-level snapshot backup, TiCDC changefeed, replicated downstream by TiCDC, resubmit the IMPORT INTO statement
- Follow-up Guidance: The source says that after the upstream import finishes, you can use `IMPORT INTO` to import the same data in the downstream TiDB cluster, and it also mentions table-level snapshot backup after import when backup is needed.
- Classification Note: This is classified as operation because the content gives scenario-based procedural handling for `IMPORT INTO` with log backup and TiCDC, centered on precheck behavior and follow-on import steps.

## Official Source Content

## Scenarios for `IMPORT INTO`

This section describes how to use `IMPORT INTO` together with [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) and [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).
### Used with log backup

In this scenario, if [PITR](https://docs.pingcap.com/tidb/stable/br/br-log-architecture#process-of-pitr) is enabled, the compatibility check will report an error after you submit the `IMPORT INTO` statement. If you are sure that these tables do not need backup, you can include `DISABLE_PRECHECK` (introduced in v8.0.0) in [`WithOptions`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#withoptions) of that statement, and then resubmit it. In this way, the data import task ignores the compatibility check and imports the data directly.

Data imported using `IMPORT INTO` cannot be backed up via log backup. If you need to back up the table, you can perform a table-level snapshot backup after the import, as described in [Back up a table](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-a-table).
### Used with TiCDC

You can perform in different scenarios as follows:

- Scenario 1: the table does not need to be replicated downstream by TiCDC.

    In this scenario, if TiCDC changefeed is enabled, the compatibility check will report an error after you submit the `IMPORT INTO` statement. If you are sure that these tables do not need to be replicated by TiCDC, you can include `DISABLE_PRECHECK` (introduced in v8.0.0) in [`WithOptions`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#withoptions) of that statement, and then resubmit it. In this way, the data import task ignores the compatibility check and imports the data directly.

- Scenario 2: the table needs to be replicated downstream by TiCDC.

    In this scenario, if TiCDC changefeed is enabled, the compatibility check will report an error after you submit the `IMPORT INTO` statement. You can include `DISABLE_PRECHECK` (introduced in v8.0.0) in [`WithOptions`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#withoptions) of that statement, and then resubmit it. In this way, the data import task ignores the compatibility check and imports the data directly.

    After the import task for the upstream TiDB cluster is finished, use `IMPORT INTO` to import the same data in the downstream TiDB cluster. If you have databases such as Redshift and Snowflake in the downstream, you can configure them to read CSV, SQL, or Parquet files from a cloud storage service and then write the data to the database.
